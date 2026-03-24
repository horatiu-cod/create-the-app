import os
import logging
from llm_client import call_llm, smart_chunk_text

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert technical summarizer.
Your task is to concisely summarize the provided architectural or technical memorandum.
Focus strictly on the key requirements, changes requested, and new specifications.
Be deterministic and thorough."""

def generate_summary(input_path: str, output_path: str):
    logger.info(f"Generating summary for {input_path}")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read {input_path}: {e}")
        return output_path #TODO: handle this error, return an empty string or raise an exception
        
    chunks = smart_chunk_text(content)
    
    # If it's a huge document, we might need a map-reduce summarization.
    # For simplicity, if we have chunks, we summarize them incrementally or just the first.
    # We will try to summarize all chunks into one large prompt if feasible, 
    # but since chunking was requested, let's summarize chunk by chunk and combine.
    
    full_summary = ""
    for i, chunk in enumerate(chunks):
        prompt = f"Summarize the following section of the memorandum (part {i+1} of {len(chunks)}):\n\n{chunk}"
        summary_part = call_llm(prompt=prompt, system_instruction=SYSTEM_PROMPT, temperature=0.3)
        full_summary += summary_part + "\n\n"
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Summary of Memorandum\n\n" + full_summary)
        
    return output_path
