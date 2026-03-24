import os
import logging
from agents.differ.tools.differ_tool import generate_diff
from llm_client import call_llm, smart_chunk_text

logger = logging.getLogger(__name__)

class DifferAgent:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir

    def process(self, initial_md: str, modified_md: str, output_name: str = "differs.md"):
        initial_path = os.path.join(self.output_dir, initial_md)
        modified_path = os.path.join(self.output_dir, modified_md)
        out_path = os.path.join(self.output_dir, output_name)
        
        logger.info(f"DifferAgent comparing {initial_path} and {modified_path}")
        return generate_diff(initial_path, modified_path, out_path)

    def generate_diff_summary(self, initial_md: str, modified_md: str, output_name: str = "differs_summary.md"):
        initial_path = os.path.join(self.output_dir, initial_md)
        modified_path = os.path.join(self.output_dir, modified_md)
        out_path = os.path.join(self.output_dir, output_name)
        
        logger.info(f"DifferAgent comparing {initial_path} and {modified_path}")
        try:
            with open(initial_path, 'r', encoding='utf-8') as f:
                initial_content = f.read()
            with open(modified_path, 'r', encoding='utf-8') as f:
                modified_content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {initial_path} or {modified_path}: {e}")
            return output_path #TODO: handle this error, return an empty string or raise an exception
        
        prompt = f"""Please compare the following two documents according to your system instructions.

<document_1_initial>
{initial_content}
</document_1_initial>

<document_2_modified>
{modified_content}
</document_2_modified>

Generate the summary now:"""

        SYSTEM_PROMPT = """You are a meticulous technical auditor and an expert in document comparison.
Your objective is to compare two documents and generate a precise summary of their differences. The documents are provided in the prompt.

Instructions:
1. Read both documents carefully and identify all literal text modifications and semantic changes.
2. STRICTLY IGNORE the following formatting and structural changes:
   - File formatting (e.g., text alignment, bold/italics, styling).
   - Structural reordering (e.g., reordering of table rows/columns or list items, provided the content is identical).
   - Whitespace and line break variations.
3. Present the differences in a clear, concise, and highly structured format using bullet points.

Constraints:
- Output ONLY the summary of differences.
- Do not include any conversational filler, introductory text, or personal commentary.
- Be strictly deterministic, objective, and thorough."""  

        summary = call_llm(prompt, output_path, system_instruction=SYSTEM_PROMPT, temperature=0.0)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("# Analysis Report\n\n" + summary)
        logger.info(f"DifferAgent generated summary at {out_path}")
        return out_path

if __name__ == "__main__":
    OUTPUT_DIR = Path(__file__).parents[3] / "output"
    differ_agent = DifferAgent(OUTPUT_DIR)
    differ_agent.generate_diff_summary("formular_initial.md", "formular_modificat.md")

