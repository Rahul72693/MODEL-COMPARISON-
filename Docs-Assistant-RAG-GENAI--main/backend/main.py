# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
load_dotenv()

from extraction.extractor import extract_file
from extraction.vectorizer import vectorize_and_store, search_top_k

# Import new provider system
from backend.llm_providers import GeminiProvider, GroqProvider
from backend.comparison import ComparisonEngine
from backend.evaluation import MetricsEvaluator
from backend.database import init_db, get_db, EvaluationRun, ModelResponseDB, QualityMetricDB

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Global instances (initialized on startup)
gemini_provider = None
groq_provider = None
comparison_engine = None
metrics_evaluator = None

# Initialize FastAPI app
app = FastAPI(title="Medical Document Backend - Model Comparison")

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory session store for chat history
SESSION_HISTORY: Dict[str, List[Dict[str, str]]] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize database and LLM providers on startup."""
    global gemini_provider, groq_provider, comparison_engine, metrics_evaluator
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Initialize providers
    if GEMINI_API_KEY:
        gemini_provider = GeminiProvider(GEMINI_API_KEY, "gemini-2.0-flash")
        print("✅ Gemini provider initialized")
    else:
        print("⚠️ GEMINI_API_KEY not set")
    
    if GROQ_API_KEY:
        groq_provider = GroqProvider(GROQ_API_KEY, "llama-3.3-70b-versatile")
        print("✅ Groq provider initialized")
    else:
        print("⚠️ GROQ_API_KEY not set")
    
    # Initialize comparison engine
    if gemini_provider and groq_provider:
        comparison_engine = ComparisonEngine(gemini_provider, groq_provider)
        print("✅ Comparison engine initialized")
    else:
        print("⚠️ Comparison engine not initialized - missing API keys")
    
    # Initialize metrics evaluator
    metrics_evaluator = MetricsEvaluator()
    print("✅ Metrics evaluator initialized")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "gemini_ready": gemini_provider is not None,
        "groq_ready": groq_provider is not None,
        "comparison_ready": comparison_engine is not None
    }


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """
    Extract and vectorize a document.
    
    Supports: PDF, DOCX, PNG
    """
    try:
        contents = await file.read()
        result = extract_file(contents, file.filename)
        vec_status = vectorize_and_store(result)
        return JSONResponse({
            "file_name": file.filename,
            "extraction_status": "done",
            "vectorizer_status": vec_status
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(payload: Dict[str, Any]):
    """
    Single model chat (Gemini only for backward compatibility).
    
    Expects: { "session_id": str, "message": str }
    Returns: { "answer": str, "sources": [...] }
    """
    try:
        session_id = payload.get("session_id")
        message = payload.get("message")
        
        if not session_id or not message:
            raise HTTPException(status_code=400, detail="session_id and message are required.")
        
        if not gemini_provider:
            raise HTTPException(status_code=503, detail="Gemini provider not configured.")
        
        # Ensure history exists
        if session_id not in SESSION_HISTORY:
            SESSION_HISTORY[session_id] = []
        
        # 1) Retrieve top-5 relevant chunks
        top_snips = search_top_k(message, k=5)
        
        # 2) Generate response with Gemini
        history = SESSION_HISTORY[session_id]
        response = await gemini_provider.generate(message, top_snips, history)
        
        # 3) Update memory
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response.text})
        
        return JSONResponse({
            "answer": response.text,
            "sources": top_snips,
            "metrics": {
                "response_time": response.response_time,
                "tokens": response.token_count,
                "cost": response.cost_estimate
            }
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
async def compare_models(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Compare both models on the same query.
    
    Expects: { "session_id": str, "message": str }
    Returns: { "gemini": {...}, "groq": {...}, "comparison": {...}, "sources": [...] }
    """
    try:
        session_id = payload.get("session_id")
        message = payload.get("message")
        
        if not session_id or not message:
            raise HTTPException(status_code=400, detail="session_id and message are required.")
        
        if not comparison_engine:
            raise HTTPException(status_code=503, detail="Comparison engine not configured. Check API keys.")
        
        # Ensure history exists
        if session_id not in SESSION_HISTORY:
            SESSION_HISTORY[session_id] = []
        
        # 1) Retrieve context
        top_snips = search_top_k(message, k=5)
        
        # 2) Compare models (runs in parallel)
        history = SESSION_HISTORY[session_id]
        result = await comparison_engine.compare(message, top_snips, history, session_id)
        
        # 3) Evaluate quality
        gemini_quality = metrics_evaluator.evaluate_quality(
            message, result.gemini_response.text, top_snips
        )
        groq_quality = metrics_evaluator.evaluate_quality(
            message, result.groq_response.text, top_snips
        )
        comparison_metrics = metrics_evaluator.compare_responses(
            result.gemini_response, result.groq_response,
            gemini_quality, groq_quality
        )
        
        # 4) Store in database
        eval_run = EvaluationRun(
            session_id=session_id,
            query=message,
            document_name="current_document"  # TODO: track actual document name
        )
        db.add(eval_run)
        db.flush()  # Get the ID
        
        # Store Gemini response
        gemini_db = ModelResponseDB(
            run_id=eval_run.id,
            model_name="gemini-2.0-flash",
            response_text=result.gemini_response.text,
            response_time=result.gemini_response.response_time,
            token_count=result.gemini_response.token_count,
            cost_estimate=result.gemini_response.cost_estimate
        )
        db.add(gemini_db)
        db.flush()
        
        gemini_quality_db = QualityMetricDB(
            response_id=gemini_db.id,
            semantic_similarity=gemini_quality.semantic_similarity,
            context_relevance=gemini_quality.context_relevance,
            citation_quality=gemini_quality.citation_quality,
            completeness_score=gemini_quality.completeness_score
        )
        db.add(gemini_quality_db)
        
        # Store Groq response
        groq_db = ModelResponseDB(
            run_id=eval_run.id,
            model_name="llama-3.3-70b-versatile",
            response_text=result.groq_response.text,
            response_time=result.groq_response.response_time,
            token_count=result.groq_response.token_count,
            cost_estimate=result.groq_response.cost_estimate
        )
        db.add(groq_db)
        db.flush()
        
        groq_quality_db = QualityMetricDB(
            response_id=groq_db.id,
            semantic_similarity=groq_quality.semantic_similarity,
            context_relevance=groq_quality.context_relevance,
            citation_quality=groq_quality.citation_quality,
            completeness_score=groq_quality.completeness_score
        )
        db.add(groq_quality_db)
        
        db.commit()
        
        # 5) Update history (use Gemini response by default)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": result.gemini_response.text})
        
        # 6) Return comparison result
        return JSONResponse({
            "gemini": {
                "answer": result.gemini_response.text,
                "response_time": result.gemini_response.response_time,
                "tokens": result.gemini_response.token_count,
                "cost": result.gemini_response.cost_estimate,
                "quality": {
                    "semantic_similarity": gemini_quality.semantic_similarity,
                    "context_relevance": gemini_quality.context_relevance,
                    "citation_quality": gemini_quality.citation_quality,
                    "completeness_score": gemini_quality.completeness_score
                }
            },
            "groq": {
                "answer": result.groq_response.text,
                "response_time": result.groq_response.response_time,
                "tokens": result.groq_response.token_count,
                "cost": result.groq_response.cost_estimate,
                "quality": {
                    "semantic_similarity": groq_quality.semantic_similarity,
                    "context_relevance": groq_quality.context_relevance,
                    "citation_quality": groq_quality.citation_quality,
                    "completeness_score": groq_quality.completeness_score
                }
            },
            "comparison": {
                "agreement_score": comparison_metrics.agreement_score,
                "gemini_faster": comparison_metrics.gemini_faster,
                "speed_ratio": comparison_metrics.speed_ratio,
                "cost_ratio": comparison_metrics.cost_ratio,
                "gemini_quality_avg": comparison_metrics.gemini_quality_avg,
                "groq_quality_avg": comparison_metrics.groq_quality_avg
            },
            "sources": top_snips,
            "run_id": eval_run.id
        })
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/summary")
async def get_metrics_summary(session_id: str, db: Session = Depends(get_db)):
    """
    Get aggregated metrics for a session.
    
    Returns summary statistics for all queries in a session.
    """
    try:
        # Query all runs for this session
        runs = db.query(EvaluationRun).filter(
            EvaluationRun.session_id == session_id
        ).all()
        
        if not runs:
            return JSONResponse({"message": "No data for this session", "summary": {}})
        
        # Aggregate metrics
        total_queries = len(runs)
        gemini_responses = []
        groq_responses = []
        
        for run in runs:
            for response in run.responses:
                if "gemini" in response.model_name.lower():
                    gemini_responses.append(response)
                elif "groq" in response.model_name.lower() or "llama" in response.model_name.lower():
                    groq_responses.append(response)
        
        # Calculate averages
        def calc_avg(responses, field):
            if not responses:
                return 0.0
            return sum(getattr(r, field, 0) for r in responses) / len(responses)
        
        summary = {
            "session_id": session_id,
            "total_queries": total_queries,
            "gemini": {
                "avg_response_time": calc_avg(gemini_responses, "response_time"),
                "total_tokens": sum(r.token_count for r in gemini_responses),
                "total_cost": sum(r.cost_estimate for r in gemini_responses),
                "query_count": len(gemini_responses)
            },
            "groq": {
                "avg_response_time": calc_avg(groq_responses, "response_time"),
                "total_tokens": sum(r.token_count for r in groq_responses),
                "total_cost": sum(r.cost_estimate for r in groq_responses),
                "query_count": len(groq_responses)
            }
        }
        
        return JSONResponse(summary)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/history")
async def get_metrics_history(limit: int = 50, db: Session = Depends(get_db)):
    """
    Get historical comparison data.
    
    Returns last N evaluation runs with metrics.
    """
    try:
        runs = db.query(EvaluationRun).order_by(
            EvaluationRun.timestamp.desc()
        ).limit(limit).all()
        
        history = []
        for run in runs:
            run_data = {
                "run_id": run.id,
                "session_id": run.session_id,
                "query": run.query,
                "timestamp": run.timestamp.isoformat(),
                "responses": []
            }
            
            for response in run.responses:
                response_data = {
                    "model_name": response.model_name,
                    "response_time": response.response_time,
                    "tokens": response.token_count,
                    "cost": response.cost_estimate
                }
                
                if response.quality:
                    response_data["quality"] = {
                        "semantic_similarity": response.quality.semantic_similarity,
                        "context_relevance": response.quality.context_relevance,
                        "citation_quality": response.quality.citation_quality,
                        "completeness_score": response.quality.completeness_score
                    }
                
                run_data["responses"].append(response_data)
            
            history.append(run_data)
        
        return JSONResponse({"history": history, "count": len(history)})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/providers/metrics")
async def get_provider_metrics():
    """Get aggregate metrics from LLM providers."""
    return JSONResponse({
        "gemini": gemini_provider.get_metrics().__dict__ if gemini_provider else None,
        "groq": groq_provider.get_metrics().__dict__ if groq_provider else None
    })
