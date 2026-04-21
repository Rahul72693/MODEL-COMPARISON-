# Implementation Plan - Dual-Model Comparison System

## Overview

This plan covers the implementation of a dual-model comparison system (Gemini vs Groq) with comprehensive evaluation metrics and a modern React-based UI for research thesis work.

---

## User Review Required

> [!IMPORTANT]
> **Groq API Access**
> 
> This implementation requires a Groq API key. Please ensure you have:
> 1. Created a Groq account at https://console.groq.com
> 2. Generated an API key
> 3. Have the key ready to add to `.env` file
> 
> **Expected Costs**: Both Gemini and Groq have free tiers, but running dual models will use quota faster. Please confirm budget/quota allocation for testing.

> [!WARNING]
> **Frontend Replacement**
> 
> The current Streamlit UI (`frontend/app.py`) will be **replaced** by a new React application. The Streamlit app will remain in the codebase but won't be the primary interface. Confirm this is acceptable.

> [!CAUTION]
> **Breaking Changes**
> 
> - New API endpoints will be added (`/compare`, `/evaluate`, `/metrics/...`)
> - Backend structure will be refactored with LLM provider abstraction
> - Existing `/chat` endpoint will be modified to support model selection
> - New database will store evaluation metrics

---

## Proposed Changes

### Backend - LLM Provider System

#### [NEW] [base.py](file:///d:/Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main/backend/llm_providers/base.py)

**Purpose**: Abstract base class for LLM providers

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class ModelResponse:
    text: str
    response_time: float
    token_count: int
    cost_estimate: float
    metadata: Dict[str, Any]

@dataclass
class ModelMetrics:
    total_tokens: int
    total_cost: float
    avg_response_time: float
    query_count: int

class LLMProvider(ABC):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.metrics = ModelMetrics(0, 0.0, 0.0, 0)
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        context_snippets: List[Dict[str, Any]], 
        history: List[Dict[str, str]]
    ) -> ModelResponse:
        """Generate response from the model"""
        pass
    
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """Count tokens in text"""
        pass
    
    def update_metrics(self, response: ModelResponse):
        self.metrics.total_tokens += response.token_count
        self.metrics.total_cost += response.cost_estimate
        self.metrics.query_count += 1
        # Running average
        n = self.metrics.query_count
        self.metrics.avg_response_time = (
            (self.metrics.avg_response_time * (n-1) + response.response_time) / n
        )
```

---

#### [NEW] [gemini_provider.py](file:///d:/Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main/backend/llm_providers/gemini_provider.py)

**Purpose**: Gemini implementation of provider interface

```python
import google.generativeai as genai
import time
from .base import LLMProvider, ModelResponse

class GeminiProvider(LLMProvider):
    # Pricing per 1M tokens (approximate)
    INPUT_COST_PER_M = 0.35
    OUTPUT_COST_PER_M = 1.05
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        super().__init__(api_key, model_name)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    async def generate(self, prompt: str, context_snippets: List[Dict], history: List[Dict]) -> ModelResponse:
        start_time = time.time()
        
        # Build context (similar to existing implementation)
        context_lines = [
            f"[{i}] {snip['text']}\nSOURCE: {snip['meta']}"
            for i, snip in enumerate(context_snippets, 1)
        ]
        
        full_prompt = f"{prompt}\n\nContext:\n" + "\n\n".join(context_lines)
        
        # Convert history
        chat_history = [
            {"role": "user" if h["role"] == "user" else "model", "parts": [h["content"]]}
            for h in history[-8:]
        ]
        
        # Generate
        response = await self.model.generate_content_async(
            contents=chat_history + [{"role": "user", "parts": [full_prompt]}],
            generation_config={"temperature": 0.2}
        )
        
        response_time = time.time() - start_time
        text = response.text or "No answer generated."
        
        # Estimate tokens (Gemini doesn't always provide exact counts)
        input_tokens = self.get_token_count(full_prompt)
        output_tokens = self.get_token_count(text)
        total_tokens = input_tokens + output_tokens
        
        cost = (input_tokens * self.INPUT_COST_PER_M / 1_000_000 + 
                output_tokens * self.OUTPUT_COST_PER_M / 1_000_000)
        
        model_response = ModelResponse(
            text=text,
            response_time=response_time,
            token_count=total_tokens,
            cost_estimate=cost,
            metadata={"model": self.model_name, "temperature": 0.2}
        )
        
        self.update_metrics(model_response)
        return model_response
    
    def get_token_count(self, text: str) -> int:
        # Approximate: 1 token ≈ 4 characters
        return len(text) // 4
```

---

#### [NEW] [groq_provider.py](file:///d:/Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main/backend/llm_providers/groq_provider.py)

**Purpose**: Groq implementation of provider interface

```python
from groq import AsyncGroq
import time
from .base import LLMProvider, ModelResponse

class GroqProvider(LLMProvider):
    # Groq pricing (free tier, then paid)
    INPUT_COST_PER_M = 0.05  # Example pricing
    OUTPUT_COST_PER_M = 0.08
    
    def __init__(self, api_key: str, model_name: str = "llama3-70b-8192"):
        super().__init__(api_key, model_name)
        self.client = AsyncGroq(api_key=api_key)
    
    async def generate(self, prompt: str, context_snippets: List[Dict], history: List[Dict]) -> ModelResponse:
        start_time = time.time()
        
        # Build context
        context_lines = [
            f"[{i}] {snip['text']}\nSOURCE: {snip['meta']}"
            for i, snip in enumerate(context_snippets, 1)
        ]
        
        system_msg = (
            "You are a helpful assistant for medical documents. "
            "Answer ONLY using the provided context snippets. "
            "Cite sources by bracket numbers [1], [2], etc."
        )
        
        messages = [{"role": "system", "content": system_msg}]
        
        # Add history
        for h in history[-8:]:
            messages.append({"role": h["role"], "content": h["content"]})
        
        # Add current query with context
        user_message = f"{prompt}\n\nContext:\n" + "\n\n".join(context_lines)
        messages.append({"role": "user", "content": user_message})
        
        # Generate
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.2,
            max_tokens=1024
        )
        
        response_time = time.time() - start_time
        text = response.choices[0].message.content
        
        # Groq provides token counts
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        
        cost = (input_tokens * self.INPUT_COST_PER_M / 1_000_000 + 
                output_tokens * self.OUTPUT_COST_PER_M / 1_000_000)
        
        model_response = ModelResponse(
            text=text,
            response_time=response_time,
            token_count=total_tokens,
            cost_estimate=cost,
            metadata={
                "model": self.model_name,
                "temperature": 0.2,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
        )
        
        self.update_metrics(model_response)
        return model_response
    
    def get_token_count(self, text: str) -> int:
        # Use Groq's tokenizer if available, else approximate
        return len(text) // 4
```

---

### Backend - Comparison Engine

#### [NEW] [engine.py](file:///d:/Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main/backend/comparison/engine.py)

**Purpose**: Orchestrate dual-model queries and comparison

```python
import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
from backend.llm_providers.base import LLMProvider, ModelResponse

@dataclass
class ComparisonResult:
    query: str
    gemini_response: ModelResponse
    groq_response: ModelResponse
    context_snippets: List[Dict[str, Any]]
    timestamp: str

class ComparisonEngine:
    def __init__(self, gemini_provider: LLMProvider, groq_provider: LLMProvider):
        self.gemini = gemini_provider
        self.groq = groq_provider
    
    async def compare(
        self, 
        query: str, 
        context_snippets: List[Dict[str, Any]], 
        history: List[Dict[str, str]]
    ) -> ComparisonResult:
        """Query both models concurrently"""
        
        # Build prompt for both
        prompt = self._build_prompt(query, context_snippets)
        
        # Query both models in parallel
        gemini_task = self.gemini.generate(prompt, context_snippets, history)
        groq_task = self.groq.generate(prompt, context_snippets, history)
        
        gemini_response, groq_response = await asyncio.gather(
            gemini_task, 
            groq_task
        )
        
        return ComparisonResult(
            query=query,
            gemini_response=gemini_response,
            groq_response=groq_response,
            context_snippets=context_snippets,
            timestamp=datetime.now().isoformat()
        )
    
    def _build_prompt(self, query: str, context_snippets: List[Dict]) -> str:
        """Build standardized prompt for both models"""
        return (
            f"You are a helpful assistant for medical documents. "
            f"Answer the following question using ONLY the provided context. "
            f"Cite sources by their bracket numbers.\n\n"
            f"Question: {query}"
        )
```

---

### Backend - Evaluation Metrics

#### [NEW] [metrics.py](file:///d:/Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main/backend/evaluation/metrics.py)

**Purpose**: Compute quality and comparison metrics

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dataclasses import dataclass

@dataclass
class QualityMetrics:
    semantic_similarity: float
    context_relevance: float
    citation_quality: float
    completeness_score: float

@dataclass
class ComparisonMetrics:
    agreement_score: float
    gemini_faster: bool
    speed_ratio: float
    cost_ratio: float

class MetricsEvaluator:
    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """Cosine similarity between two texts"""
        emb1 = self.model.encode([text1])
        emb2 = self.model.encode([text2])
        return float(cosine_similarity(emb1, emb2)[0][0])
    
    def compute_context_relevance(
        self, 
        query: str, 
        context_snippets: List[str], 
        answer: str
    ) -> float:
        """How well the answer uses the provided context"""
        query_emb = self.model.encode([query])
        answer_emb = self.model.encode([answer])
        context_embs = self.model.encode(context_snippets)
        
        # Average similarity between answer and context
        similarities = cosine_similarity(answer_emb, context_embs)[0]
        return float(np.mean(similarities))
    
    def compute_citation_quality(self, answer: str, num_sources: int) -> float:
        """Check if answer includes citations"""
        import re
        citations = re.findall(r'\[(\d+)\]', answer)
        unique_citations = len(set(citations))
        
        # Quality = (unique citations / available sources)
        if num_sources == 0:
            return 0.0
        return min(1.0, unique_citations / num_sources)
    
    def compute_agreement_score(self, answer1: str, answer2: str) -> float:
        """Semantic similarity between two model answers"""
        return self.compute_semantic_similarity(answer1, answer2)
    
    def evaluate_quality(
        self, 
        query: str, 
        answer: str, 
        context_snippets: List[Dict]
    ) -> QualityMetrics:
        """Compute all quality metrics for a response"""
        
        context_texts = [snip['text'] for snip in context_snippets]
        
        return QualityMetrics(
            semantic_similarity=self.compute_semantic_similarity(query, answer),
            context_relevance=self.compute_context_relevance(query, context_texts, answer),
            citation_quality=self.compute_citation_quality(answer, len(context_snippets)),
            completeness_score=min(1.0, len(answer) / 500)  # Simple heuristic
        )
    
    def compare_responses(
        self, 
        gemini_response: ModelResponse, 
        groq_response: ModelResponse
    ) -> ComparisonMetrics:
        """Compare two model responses"""
        
        agreement = self.compute_agreement_score(
            gemini_response.text, 
            groq_response.text
        )
        
        gemini_faster = gemini_response.response_time < groq_response.response_time
        speed_ratio = groq_response.response_time / gemini_response.response_time
        cost_ratio = groq_response.cost_estimate / max(gemini_response.cost_estimate, 0.0001)
        
        return ComparisonMetrics(
            agreement_score=agreement,
            gemini_faster=gemini_faster,
            speed_ratio=speed_ratio,
            cost_ratio=cost_ratio
        )
```

---

### Backend - Database

#### [NEW] [database.py](file:///d:/Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main/backend/database/database.py)

**Purpose**: SQLAlchemy models and database setup

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./metrics.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    query = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    document_name = Column(String)
    
    responses = relationship("ModelResponse", back_populates="run")

class ModelResponse(Base):
    __tablename__ = "model_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("evaluation_runs.id"))
    model_name = Column(String)
    response_text = Column(Text)
    response_time = Column(Float)
    token_count = Column(Integer)
    cost_estimate = Column(Float)
    
    run = relationship("EvaluationRun", back_populates="responses")
    quality = relationship("QualityMetric", uselist=False, back_populates="response")

class QualityMetric(Base):
    __tablename__ = "quality_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("model_responses.id"))
    semantic_similarity = Column(Float)
    context_relevance = Column(Float)
    citation_quality = Column(Float)
    completeness_score = Column(Float)
    
    response = relationship("ModelResponse", back_populates="quality")

def init_db():
    Base.metadata.create_all(bind=engine)
```

---

### Backend - API Endpoints

#### [MODIFY] [main.py](file:///d:/Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main/backend/main.py)

**Changes**:
1. Add imports for new providers and comparison engine
2. Initialize providers on startup
3. Add new `/compare` endpoint
4. Add `/metrics/*` endpoints
5. Modify existing `/chat` to optionally use specific model

**New endpoints to add**:

```python
@app.on_event("startup")
async def startup_event():
    # Initialize database
    from backend.database.database import init_db
    init_db()
    
    # Initialize providers
    global gemini_provider, groq_provider, comparison_engine, metrics_evaluator
    
    gemini_provider = GeminiProvider(os.getenv("GEMINI_API_KEY"), "gemini-1.5-flash")
    groq_provider = GroqProvider(os.getenv("GROQ_API_KEY"), "llama3-70b-8192")
    comparison_engine = ComparisonEngine(gemini_provider, groq_provider)
    metrics_evaluator = MetricsEvaluator()

@app.post("/compare")
async def compare_models(payload: Dict[str, Any]):
    """
    Compare both models on the same query
    Expects: { "session_id": str, "message": str }
    Returns: { "gemini": {...}, "groq": {...}, "metrics": {...} }
    """
    session_id = payload.get("session_id")
    message = payload.get("message")
    
    # Get history
    history = SESSION_HISTORY.get(session_id, [])
    
    # Retrieve context
    top_snips = search_top_k(message, k=5)
    
    # Compare models
    result = await comparison_engine.compare(message, top_snips, history)
    
    # Evaluate quality
    gemini_quality = metrics_evaluator.evaluate_quality(
        message, result.gemini_response.text, top_snips
    )
    groq_quality = metrics_evaluator.evaluate_quality(
        message, result.groq_response.text, top_snips
    )
    comparison_metrics = metrics_evaluator.compare_responses(
        result.gemini_response, result.groq_response
    )
    
    # Store in database
    # ... (database insertion code)
    
    # Update history
    history.append({"role": "user", "content": message})
    
    return JSONResponse({
        "gemini": {
            "answer": result.gemini_response.text,
            "response_time": result.gemini_response.response_time,
            "tokens": result.gemini_response.token_count,
            "cost": result.gemini_response.cost_estimate,
            "quality": gemini_quality.__dict__
        },
        "groq": {
            "answer": result.groq_response.text,
            "response_time": result.groq_response.response_time,
            "tokens": result.groq_response.token_count,
            "cost": result.groq_response.cost_estimate,
            "quality": groq_quality.__dict__
        },
        "comparison": comparison_metrics.__dict__,
        "sources": top_snips
    })

@app.get("/metrics/summary")
async def get_metrics_summary(session_id: str):
    """Get aggregated metrics for a session"""
    # Query database and return summary
    pass

@app.get("/metrics/history")
async def get_metrics_history(limit: int = 50):
    """Get historical comparison data"""
    # Query database and return historical metrics
    pass
```

---

### Frontend - React Application

#### Project Initialization

```bash
cd Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main
npx -y create-vite@latest frontend-react -- --template react-ts
cd frontend-react
npm install react-router-dom axios recharts framer-motion @headlessui/react @heroicons/react react-dropzone
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### [NEW] Directory Structure

```
frontend-react/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── TabNavigation.tsx
│   │   ├── upload/
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── TextInput.tsx
│   │   ├── comparison/
│   │   │   ├── QueryInput.tsx
│   │   │   ├── ModelResponseCard.tsx
│   │   │   └── SideBySideView.tsx
│   │   ├── metrics/
│   │   │   ├── MetricsDashboard.tsx
│   │   │   ├── PerformanceChart.tsx
│   │   │   └── ComparisonTable.tsx
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       └── LoadingSpinner.tsx
│   ├── pages/
│   │   ├── DocumentInput.tsx
│   │   ├── Comparison.tsx
│   │   └── Metrics.tsx
│   ├── services/
│   │   └── api.ts
│   ├── hooks/
│   │   └── useComparison.ts
│   ├── types/
│   │   └── index.ts
│   ├── styles/
│   │   └── theme.css
│   └── App.tsx
├── package.json
└── vite.config.ts
```

(Full React component implementations will be provided in execution phase)

---

## Verification Plan

### Backend Testing

#### 1. Unit Tests for LLM Providers

**Test File**: `tests/test_llm_providers.py`

```python
import pytest
from backend.llm_providers.gemini_provider import GeminiProvider
from backend.llm_providers.groq_provider import GroqProvider

@pytest.mark.asyncio
async def test_gemini_provider():
    """Test Gemini provider generates response"""
    provider = GeminiProvider(os.getenv("GEMINI_API_KEY"))
    response = await provider.generate(
        "What is the capital of France?",
        [{"text": "Paris is the capital of France.", "meta": {}}],
        []
    )
    assert response.text
    assert response.response_time > 0
    assert response.token_count > 0

@pytest.mark.asyncio
async def test_groq_provider():
    """Test Groq provider generates response"""
    provider = GroqProvider(os.getenv("GROQ_API_KEY"))
    response = await provider.generate(
        "What is the capital of France?",
        [{"text": "Paris is the capital of France.", "meta": {}}],
        []
    )
    assert response.text
    assert response.response_time > 0
    assert response.token_count > 0
```

**Run Command**:
```bash
cd Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main
.venv\Scripts\activate
pip install pytest pytest-asyncio
pytest tests/test_llm_providers.py -v
```

#### 2. Integration Test for Comparison Engine

**Test File**: `tests/test_comparison_engine.py`

```python
@pytest.mark.asyncio
async def test_comparison_engine():
    """Test that comparison engine queries both models"""
    gemini = GeminiProvider(os.getenv("GEMINI_API_KEY"))
    groq = GroqProvider(os.getenv("GROQ_API_KEY"))
    engine = ComparisonEngine(gemini, groq)
    
    result = await engine.compare(
        "What is NAFLD?",
        [{"text": "NAFLD is non-alcoholic fatty liver disease.", "meta": {}}],
        []
    )
    
    assert result.gemini_response.text
    assert result.groq_response.text
    assert result.gemini_response.response_time > 0
    assert result.groq_response.response_time > 0
```

**Run Command**:
```bash
pytest tests/test_comparison_engine.py -v
```

#### 3. API Endpoint Tests

**Test File**: `tests/test_api.py`

```python
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_compare_endpoint():
    """Test /compare endpoint"""
    response = client.post("/compare", json={
        "session_id": "test-session",
        "message": "What is NAFLD?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "gemini" in data
    assert "groq" in data
    assert "comparison" in data
```

**Run Command**:
```bash
pytest tests/test_api.py -v
```

### Backend Manual Testing

#### 1. Start Backend Server

```bash
cd Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main
.venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```

#### 2. Test Endpoints with curl

**Upload Document**:
```bash
curl -X POST http://127.0.0.1:8000/extract -F "file=@Research on Non-alcoholic Fatty Liver Disease.pdf"
```

**Compare Models**:
```bash
curl -X POST http://127.0.0.1:8000/compare -H "Content-Type: application/json" -d "{\"session_id\": \"test\", \"message\": \"What are the risk factors for NAFLD?\"}"
```

**Expected Response**: JSON with both model responses, metrics, and comparison data.

### Frontend Testing

#### 1. Development Server

```bash
cd Docs-Assistant-RAG-GENAI--main/Docs-Assistant-RAG-GENAI--main/frontend-react
npm run dev
```

**Expected**: Server runs on http://localhost:5173

#### 2. Component Tests

**Test File**: `frontend-react/src/components/__tests__/DocumentUpload.test.tsx`

```typescript
import { render, screen } from '@testing-library/react';
import DocumentUpload from '../upload/DocumentUpload';

test('renders upload component', () => {
  render(<DocumentUpload />);
  expect(screen.getByText(/upload/i)).toBeInTheDocument();
});
```
