import os
import logging
from llm_client import call_llm, smart_chunk_text

logger = logging.getLogger(__name__)

class DifferAgent:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir

    def generate_diff_summary(self, initial_md: str, modified_md: str, output_name: str = "differs_summary.md", model="deepseek-v3.1:671b-cloud", stream=False):
        chunks = model.split("-")
        initial_path = os.path.join(self.output_dir, initial_md)
        modified_path = os.path.join(self.output_dir, modified_md)
        out_path = os.path.join(self.output_dir, chunks[0], output_name)
        
        logger.info(f"DifferAgent comparing {initial_path} and {modified_path}")
        try:
            with open(initial_path, 'r', encoding='utf-8') as f:
                initial_content = f.read()
            with open(modified_path, 'r', encoding='utf-8') as f:
                modified_content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {initial_path} or {modified_path}: {e}")
            return output_path #TODO: handle this error, return an empty string or raise an exception
        
        #print(f"initial_content: {initial_content}")
        #print(f"modified_content: {modified_content}")
        
        prompt = f"""Please compare the following two documents according to system_prompt instructions.

<document_1_initial>
{initial_content}
</document_1_initial>

<document_2_modified>
{modified_content}
</document_2_modified>

Generate the summary now."""

        system_prompt = f"""You are a meticulous technical auditor and an expert in document comparison.
Your objective is to compare two documents and generate a precise summary of their differences. The documents are provided in the PROMPT.


INSTRUCTIONS:
1. Read both documents carefully and identify all literal text modifications, tables rows/columns content modifications. Be aware of the fact that the documents are in Romanian language, and the document format is markdown.
2. Compare the following two documents according to below INSTRUCTIONS, CONSTRAINTS and IMPORTANT sections.
3. STRICTLY IGNORE the following formatting and structural changes:
   - File formatting (e.g., text alignment, bold/italics, styling).
   - Structural reordering (e.g., reordering of table rows/columns or list items, provided the content is identical).
   - Whitespace and line break variations.
4. Present all the differences in a clear, concise, and highly structured format using bullet points.
5. Mention the position/section in the document where the difference is located.

CONSTRAINTS:
- Output ALL the differences, except the ones mentioned in the above instructions.
- Do not include any conversational filler, introductory text, or personal commentary.
- Be strictly deterministic, objective, and thorough.

IMPORTANT: Focus on changes that affect the content's substance, such as:
- Numerical value changes (e.g., budget amounts, dates, quantities).
- Textual modifications (e.g., additions, deletions, or rewording of sentences).
- Changes in project details (e.g., objectives, activities, indicators).
- Modifications in legal or financial information.

Generate the summary in romanian language now.
"""  

        summary = call_llm(prompt=prompt, system_instruction=system_prompt, temperature=0.0, model=model, stream=stream)
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("# Analysis Report\n\n" + summary)
        logger.info(f"DifferAgent generated summary at {out_path}")
        return out_path

if __name__ == "__main__":
    model = "deepseek-v3.1:671b-cloud"
    OUTPUT_DIR = "output"
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    differ_agent = DifferAgent(OUTPUT_DIR)
    differ_agent.generate_diff_summary("formular_initial.md", "formular_modificat.md", model=model, stream=False)

