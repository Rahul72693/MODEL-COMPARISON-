"""Metrics evaluation for comparing model responses."""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any
import re
from backend.llm_providers.base import ModelResponse


@dataclass
class QualityMetrics:
    """Quality metrics for a single response."""
    semantic_similarity: float  # Query-answer similarity
    context_relevance: float    # How well answer uses context
    citation_quality: float      # Citation accuracy
    completeness_score: float    # Answer completeness


@dataclass
class ComparisonMetrics:
    """Comparison metrics between two model responses."""
    agreement_score: float       # Semantic similarity between responses
    gemini_faster: bool          # Whether Gemini was faster
    speed_ratio: float           # Groq time / Gemini time
    cost_ratio: float            # Groq cost / Gemini cost
    gemini_quality_avg: float    # Average quality score for Gemini
    groq_quality_avg: float      # Average quality score for Groq


class MetricsEvaluator:
    """Evaluator for computing quality and comparison metrics."""
    
    def __init__(self):
        """Initialize metrics evaluator with sentence transformer model."""
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        emb1 = self.model.encode([text1])
        emb2 = self.model.encode([text2])
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(max(0.0, min(1.0, similarity)))
    
    def compute_context_relevance(
        self, 
        query: str, 
        context_snippets: List[str], 
        answer: str
    ) -> float:
        """
        Measure how well the answer uses the provided context.
        
        Args:
            query: Original question
            context_snippets: List of context strings
            answer: Model's answer
            
        Returns:
            Relevance score between 0 and 1
        """
        if not answer or not context_snippets:
            return 0.0
        
        try:
            # Embed answer and context
            answer_emb = self.model.encode([answer])
            context_embs = self.model.encode(context_snippets)
            
            # Calculate similarity between answer and each context chunk
            similarities = cosine_similarity(answer_emb, context_embs)[0]
            
            # Return average similarity
            avg_similarity = float(np.mean(similarities))
            return max(0.0, min(1.0, avg_similarity))
        except Exception:
            return 0.0
    
    def compute_citation_quality(self, answer: str, num_sources: int) -> float:
        """
        Check if answer includes proper citations.
        
        Args:
            answer: Model's answer
            num_sources: Number of available sources
            
        Returns:
            Citation quality score between 0 and 1
        """
        if num_sources == 0:
            return 0.0
        
        # Find all citations in format [1], [2], etc.
        citations = re.findall(r'\[(\d+)\]', answer)
        unique_citations = set(citations)
        
        # Quality = (unique valid citations / available sources)
        valid_citations = [int(c) for c in unique_citations if int(c) <= num_sources]
        quality = len(valid_citations) / num_sources
        
        return min(1.0, quality)
    
    def compute_completeness_score(self, answer: str, query: str) -> float:
        """
        Estimate answer completeness (simple heuristic).
        
        Args:
            answer: Model's answer
            query: Original question
            
        Returns:
            Completeness score between 0 and 1
        """
        if not answer:
            return 0.0
        
        # Simple heuristic: longer answers tend to be more complete
        # Cap at 500 characters as "complete"
        length_score = min(1.0, len(answer) / 500)
        
        # Bonus if answer is not too short (avoid "I don't know" type responses)
        min_threshold = 50
        if len(answer) < min_threshold:
            length_score *= (len(answer) / min_threshold)
        
        return length_score
    
    def evaluate_quality(
        self, 
        query: str, 
        answer: str, 
        context_snippets: List[Dict[str, Any]]
    ) -> QualityMetrics:
        """
        Compute all quality metrics for a response.
        
        Args:
            query: Original question
            answer: Model's answer
            context_snippets: Retrieved context with metadata
            
        Returns:
            QualityMetrics object
        """
        # Extract text from context snippets
        context_texts = [snip.get('text', '') for snip in context_snippets]
        
        return QualityMetrics(
            semantic_similarity=self.compute_semantic_similarity(query, answer),
            context_relevance=self.compute_context_relevance(query, context_texts, answer),
            citation_quality=self.compute_citation_quality(answer, len(context_snippets)),
            completeness_score=self.compute_completeness_score(answer, query)
        )
    
    def compare_responses(
        self, 
        gemini_response: ModelResponse,
        groq_response: ModelResponse,
        gemini_quality: QualityMetrics,
        groq_quality: QualityMetrics
    ) -> ComparisonMetrics:
        """
        Compare two model responses.
        
        Args:
            gemini_response: Gemini's response
            groq_response: Groq's response
            gemini_quality: Gemini's quality metrics
            groq_quality: Groq's quality metrics
            
        Returns:
            ComparisonMetrics object
        """
        # Agreement: semantic similarity between the two answers
        agreement = self.compute_semantic_similarity(
            gemini_response.text, 
            groq_response.text
        )
        
        # Speed comparison
        gemini_faster = gemini_response.response_time < groq_response.response_time
        speed_ratio = (
            groq_response.response_time / max(gemini_response.response_time, 0.001)
        )
        
        # Cost comparison
        cost_ratio = (
            groq_response.cost_estimate / max(gemini_response.cost_estimate, 0.0001)
        )
        
        # Average quality scores
        gemini_avg = np.mean([
            gemini_quality.semantic_similarity,
            gemini_quality.context_relevance,
            gemini_quality.citation_quality,
            gemini_quality.completeness_score
        ])
        
        groq_avg = np.mean([
            groq_quality.semantic_similarity,
            groq_quality.context_relevance,
            groq_quality.citation_quality,
            groq_quality.completeness_score
        ])
        
        return ComparisonMetrics(
            agreement_score=agreement,
            gemini_faster=gemini_faster,
            speed_ratio=speed_ratio,
            cost_ratio=cost_ratio,
            gemini_quality_avg=float(gemini_avg),
            groq_quality_avg=float(groq_avg)
        )
