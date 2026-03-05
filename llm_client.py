import os
import time
import re
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

def smart_chunk_text(md_content: str, max_chars_per_chunk: int = 4000) -> List[str]:
    """Splits text on paragraph boundaries rather than raw character counts for better context."""
    paragraphs = md_content.split('\n\n') 
    """
    Splits a markdown string into sections based on headers.
    paragraphs = split_markdown_by_sections(md_content)
    """
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

def split_markdown_by_sections(md_content):
    """
    Splits a markdown string into sections based on headers.
    Includes any text before the first header as a 'preamble' section.
    """
    # Pattern matches lines starting with #, ##, etc. at the beginning of a line
    # re.MULTILINE allows ^ to match the start of every line
    header_pattern = re.compile(r'^(#+ .*)$', re.MULTILINE)
    
    # Find all matches for headers
    matches = list(header_pattern.finditer(md_content))
    
    sections = []
    
    # Handle text before the first header (preamble)
    if matches and matches[0].start() > 0:
        preamble = md_content[:matches[0].start()].strip()
        if preamble:
            sections.append(preamble)
            
    # Iterate through matches to slice the text
    for i in range(len(matches)):
        start_pos = matches[i].start()
        # The section ends where the next header starts, or at the end of the file
        end_pos = matches[i+1].start() if i + 1 < len(matches) else len(md_content)
        
        section_content = md_content[start_pos:end_pos].strip()
        if section_content:
            sections.append(section_content)
            
    return sections
