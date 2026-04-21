"""Gemini LLM provider implementation."""

from google import genai
import time
import asyncio
from typing import List, Dict, Any
from .base import LLMProvider, ModelResponse


class GeminiProvider(LLMProvider):
    """Google Gemini implementation of LLM provider."""
    
    # Pricing per 1M tokens (approximate for gemini-1.5-flash)
    INPUT_COST_PER_M = 0.35
    OUTPUT_COST_PER_M = 1.05
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key
            model_name: Gemini model name (default: gemini-2.0-flash)
        """
        super().__init__(api_key, model_name)
        self.client = genai.Client(api_key=api_key)
    
    async def generate(
        self, 
        prompt: str, 
        context_snippets: List[Dict[str, Any]], 
        history: List[Dict[str, str]]
    ) -> ModelResponse:
        """Generate response using Gemini."""
        start_time = time.time()
        
        # Build context with citations
        context_lines = []
        for i, snip in enumerate(context_snippets, 1):
            meta = snip.get("meta", {})
            src = f'{meta.get("file_name", "")}, p.{meta.get("page_number", "?")}, {meta.get("chunk_type", "")}'
            context_lines.append(f"[{i}] {snip['text']}\nSOURCE: {src}")
        
        # Build full prompt
        system_msg = (
            "You are a helpful assistant for medical documents. "
            "Answer ONLY using the provided context snippets. "
            "If the answer is not in the context, say 'not enough information'. "
            "Be concise and precise. Respond in a conversational way."
        )
        
        full_prompt = (
            f"{system_msg}\n\n"
            f"Context snippets:\n" +
            "\n\n".join(context_lines) +
            f"\n\nUser question:\n{prompt}\n\n"
            f"Instructions: Cite the snippets by their bracket numbers when relevant (e.g., [1], [3])."
        )
        
        # Convert history for google-genai
        # The new SDK takes contents as a list of parts or a list of Content objects
        contents = []
        for h in history[-8:]:  # Last 8 turns
            role = "user" if h["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h["content"]}]})
        
        # Add the current prompt
        contents.append({"role": "user", "parts": [{"text": full_prompt}]})
        
        # Generate response
        try:
            # Use run_in_executor if the SDK is synchronous, but actually google-genai 
            # has an async client if needed. For simplicity, let's use the sync one 
            # in a thread if it doesn't have a direct async method on the main client.
            # Actually, the standard genai.Client is sync.
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config={
                        "temperature": 0.2,
                        "max_output_tokens": 1024
                    }
                )
            )
            
            response_time = time.time() - start_time
            text = response.text if response.text else "No answer generated."
            
            # Get token counts if available
            input_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else self.get_token_count(full_prompt)
            output_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else self.get_token_count(text)
            
        except Exception as e:
            response_time = time.time() - start_time
            text = f"Error generating response: {str(e)}"
            input_tokens = self.get_token_count(full_prompt)
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
        Approximate token count for Gemini.
        Rule of thumb: ~4 characters per token.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        return max(1, len(text) // 4)
