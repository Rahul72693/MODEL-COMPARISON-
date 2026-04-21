"""Groq LLM provider implementation."""

from groq import AsyncGroq
import time
from typing import List, Dict, Any
from .base import LLMProvider, ModelResponse


class GroqProvider(LLMProvider):
    """Groq implementation of LLM provider."""
    
    # Pricing per 1M tokens (example pricing - please verify with Groq's actual pricing)
    INPUT_COST_PER_M = 0.05
    OUTPUT_COST_PER_M = 0.08
    
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key
            model_name: Groq model name (default: llama-3.3-70b-versatile)
        """
        super().__init__(api_key, model_name)
        self.client = AsyncGroq(api_key=api_key)
    
    async def generate(
        self, 
        prompt: str, 
        context_snippets: List[Dict[str, Any]], 
        history: List[Dict[str, str]]
    ) -> ModelResponse:
        """Generate response using Groq."""
        start_time = time.time()
        
        # Build context with citations
        context_lines = []
        for i, snip in enumerate(context_snippets, 1):
            meta = snip.get("meta", {})
            src = f'{meta.get("file_name", "")}, p.{meta.get("page_number", "?")}, {meta.get("chunk_type", "")}'
            context_lines.append(f"[{i}] {snip['text']}\nSOURCE: {src}")
        
        # Build messages
        system_msg = (
            "You are a helpful assistant for medical documents. "
            "Answer ONLY using the provided context snippets. "
            "Cite sources by bracket numbers [1], [2], etc. "
            "Be concise and precise."
        )
        
        messages = [{"role": "system", "content": system_msg}]
        
        # Add conversation history
        for h in history[-8:]:  # Last 8 turns
            messages.append({"role": h["role"], "content": h["content"]})
        
        # Add current query with context
        user_message = (
            f"{prompt}\n\n"
            f"Context:\n" +
            "\n\n".join(context_lines)
        )
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2,
                max_tokens=1024
            )
            
            response_time = time.time() - start_time
            text = response.choices[0].message.content
            
            # Groq provides actual token counts
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
        except Exception as e:
            response_time = time.time() - start_time
            text = f"Error generating response: {str(e)}"
            # Fallback token estimation
            input_tokens = self.get_token_count(user_message)
            output_tokens = self.get_token_count(text)
            total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        cost = (
            input_tokens * self.INPUT_COST_PER_M / 1_000_000 + 
            output_tokens * self.OUTPUT_COST_PER_M / 1_000_000
        )
        
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
        """
        Approximate token count for Groq models.
        Rule of thumb: ~4 characters per token.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        return max(1, len(text) // 4)
