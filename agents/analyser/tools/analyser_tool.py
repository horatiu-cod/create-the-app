import os
import logging
from llm_client import call_llm, smart_chunk_text

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a meticulous technical auditor.
You will be provided with:
1. `summary.md`: The requested requirements.
2. `differs.md`: The actual changes made in the files.

Your task is to analyze if ALL requirements from the summary are fully and accurately implemented in the diffs, and vice-versa.
Output a detailed discrepancy markdown report. Do not produce anything outside the markdown format.
"""

def analyze_changes(summary_path: str, differs_path: str, output_path: str):
    logger.info(f"Analyzing {summary_path} and {differs_path}")
    
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary_content = f.read()
            
        with open(differs_path, 'r', encoding='utf-8') as f:
            differs_content = f.read()
    except Exception as e:
        logger.error(f"Files not found for analysis: {e}")
        with open(output_path, 'w', encoding='utf-8') as f:
             f.write("Agent execution failed due to API error or empty input. Downstream tasks might be impacted.")
        return output_path
        
    # To avoid massive prompt size, we chunk the diffs if they are extremely long,
    # but the instructions requested cross-referencing, which usually requires both contexts.
    # Assuming combined size fits in context window. If not, smart_chunking could be applied on diffs.
    
    prompt = f"=== SUMMARY (Requirements) ===\n{summary_content}\n\n=== DIFFS (Actual Changes) ===\n{differs_content}\n\n"
    prompt += "Please provide a detailed report identifying if the changes reflect the requirements, highlighting any missing implementations or undocumented modifications."
    
    report = call_llm(prompt=prompt, system_instruction=SYSTEM_PROMPT, temperature=0.2)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Analysis Report\n\n" + report)
        
    return output_path
