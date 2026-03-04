import os
import time
from typing import Optional, List
from openai import OpenAI, RateLimitError
from tenacity import retry, wait_exponential, retry_if_exception_type, stop_after_attempt
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fallback string
FALLBACK_MESSAGE = "Agent execution failed due to API error or empty input. Downstream tasks might be impacted."

def get_client() -> OpenAI:
    """Initialize standard OpenAI client (can point to vllm/ollama via base_url in .env)"""
    api_key = os.getenv("OPENAI_API_KEY", "dummy_key_for_local")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=api_key, base_url=base_url)

@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=5, min=5, max=15),
    stop=stop_after_attempt(4),
    reraise=True
)
def _call_llm_with_retry(client: OpenAI, messages: List[dict], temperature: float = 0.3, model="gpt-4o-mini") -> str:
    """Internal function to call the LLM with exponential backoff on rate limits."""
    logger.info("Calling LLM API...")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

def call_llm(prompt: str, system_instruction: str = "You are a helpful assistant.", temperature: float = 0.3) -> str:
    """
    Calls the LLM API with smart fallback handling.
    If the prompt is empty or API fully fails (non-rate limit, or after max retries), returns a fallback message.
    """
    if not prompt or not prompt.strip():
        logger.warning("Empty prompt provided to call_llm.")
        return FALLBACK_MESSAGE

    client = get_client()
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt}
    ]
    
    try:
        return _call_llm_with_retry(client, messages, temperature=temperature)
    except Exception as e:
        logger.error(f"LLM API call failed: {e}")
        return FALLBACK_MESSAGE

def smart_chunk_text(text: str, max_chars_per_chunk: int = 4000) -> List[str]:
    """Splits text on paragraph boundaries rather than raw character counts for better context."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars_per_chunk:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks
