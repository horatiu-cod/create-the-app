import difflib
import logging

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
