"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class ModelResponse:
    """Response from an LLM provider."""
    text: str
    response_time: float
    token_count: int
    cost_estimate: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ModelMetrics:
    """Aggregate metrics for a model."""
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    query_count: int = 0


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the provider.
        
        Args:
            api_key: API key for the provider
            model_name: Name of the model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.metrics = ModelMetrics()
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        context_snippets: List[Dict[str, Any]], 
        history: List[Dict[str, str]]
    ) -> ModelResponse:
        """
        Generate a response from the model.
        
        Args:
            prompt: The user's query
            context_snippets: Retrieved context chunks from FAISS
            history: Conversation history
            
        Returns:
            ModelResponse with the generated text and metadata
        """
        pass
    
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Count tokens in a text string.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        pass
    
    def update_metrics(self, response: ModelResponse):
        """
        Update aggregate metrics after a response.
        
        Args:
            response: The model response to add to metrics
        """
        self.metrics.total_tokens += response.token_count
        self.metrics.total_cost += response.cost_estimate
        self.metrics.query_count += 1
        
        # Calculate running average for response time
        n = self.metrics.query_count
        self.metrics.avg_response_time = (
            (self.metrics.avg_response_time * (n - 1) + response.response_time) / n
        )
    
    def get_metrics(self) -> ModelMetrics:
        """
        Get current aggregate metrics.
        
        Returns:
            ModelMetrics object
        """
        return self.metrics
