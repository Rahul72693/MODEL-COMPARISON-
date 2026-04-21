"""Comparison engine for orchestrating dual-model queries."""

import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from backend.llm_providers.base import LLMProvider, ModelResponse


@dataclass
class ComparisonResult:
    """Result from comparing two models on the same query."""
    query: str
    gemini_response: ModelResponse
    groq_response: ModelResponse
    context_snippets: List[Dict[str, Any]]
    timestamp: str
    session_id: str = ""


class ComparisonEngine:
    """Engine for comparing multiple LLM providers."""
    
    def __init__(self, gemini_provider: LLMProvider, groq_provider: LLMProvider):
        """
        Initialize comparison engine.
        
        Args:
            gemini_provider: Gemini LLM provider instance
            groq_provider: Groq LLM provider instance
        """
        self.gemini = gemini_provider
        self.groq = groq_provider
    
    async def compare(
        self, 
        query: str, 
        context_snippets: List[Dict[str, Any]], 
        history: List[Dict[str, str]],
        session_id: str = ""
    ) -> ComparisonResult:
        """
        Query both models concurrently and return comparison result.
        
        Args:
            query: User's question
            context_snippets: Retrieved context from FAISS
            history: Conversation history
            session_id: Session identifier
            
        Returns:
            ComparisonResult with responses from both models
        """
        # Build standardized prompt
        prompt = self._build_prompt(query)
        
        # Query both models in parallel for faster comparison
        gemini_task = self.gemini.generate(prompt, context_snippets, history)
        groq_task = self.groq.generate(prompt, context_snippets, history)
        
        # Wait for both to complete
        gemini_response, groq_response = await asyncio.gather(
            gemini_task, 
            groq_task,
            return_exceptions=True  # Don't fail if one model errors
        )
        
        # Handle exceptions
        if isinstance(gemini_response, Exception):
            gemini_response = ModelResponse(
                text=f"Error: {str(gemini_response)}",
                response_time=0.0,
                token_count=0,
                cost_estimate=0.0,
                metadata={"error": True}
            )
        
        if isinstance(groq_response, Exception):
            groq_response = ModelResponse(
                text=f"Error: {str(groq_response)}",
                response_time=0.0,
                token_count=0,
                cost_estimate=0.0,
                metadata={"error": True}
            )
        
        return ComparisonResult(
            query=query,
            gemini_response=gemini_response,
            groq_response=groq_response,
            context_snippets=context_snippets,
            timestamp=datetime.now().isoformat(),
            session_id=session_id
        )
    
    def _build_prompt(self, query: str) -> str:
        """
        Build standardized prompt for both models.
        
        Args:
            query: User's question
            
        Returns:
            Formatted prompt string
        """
        return query  # Providers will handle context formatting
