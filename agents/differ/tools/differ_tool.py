import difflib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_diff(md1_path: str, md2_path: str, output_path: str):
    """
    Compares two Markdown files and writes their diff to output_path.
    """
    try:
        with open(md1_path, 'r', encoding='utf-8') as f1, open(md2_path, 'r', encoding='utf-8') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()

        diff = difflib.unified_diff(
            lines1, lines2,
            fromfile=md1_path,
            tofile=md2_path,
            lineterm=''
        )

        diff_text = '\n'.join(diff)
        
        # Format it nicely as markdown diff
        formatted_diff = f"# Changes \n\n```diff\n{diff_text}\n```"

        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(formatted_diff)
            
        return output_path
    except FileNotFoundError as e:
        logger.error(f"Diff failed, file missing: {e}")
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(f"Agent execution failed due to API error or empty input. Downstream tasks might be impacted.\nError: {e}")
        return output_path

def main():

    #INPUT_DIR = Path(__file__).parent / "data/input"
    OUTPUT_DIR = Path(__file__).parent / "output"    
    md1_path = OUTPUT_DIR /"formular_initial.md"
    md2_path = OUTPUT_DIR /"formular_initial.md"
    output_path = OUTPUT_DIR /"differs.md"

    if not md1_path.exists():
        logger.error(f"Input document not found at {md1_path}")
        return

    output_md = generate_diff(md1_path, md2_path, output_path)

    print(output_md)

    if __name__ == "__main__":
        main()