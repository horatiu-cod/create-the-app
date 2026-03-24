import difflib
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def generate_diff(md1_path: str, md2_path: str, output_path: str):
    """
    Compares two Markdown files and writes their diff to output_path.
    """
    try:
        with open(md1_path, 'r', encoding='utf-8') as f1, open(md2_path, 'r', encoding='utf-8') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()
        logger.info("started to compare files")
        diff = difflib.unified_diff(
            lines1, lines2,
            fromfile=str(md1_path),
            tofile=str(md2_path),
            lineterm='',
            n=0 # Setting n=0 removes all context lines at the generator level! 
        )
        labeled_diff = []

        for line in diff:
            if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                # Keep the standard diff headers as they are
                labeled_diff.append(line)
            elif line.startswith('-'):
                # Line removed from the first file
                labeled_diff.append(f"[{md1_path}] \n{line}")
            elif line.startswith('+'):
                # Line added to the second file
                labeled_diff.append(f"[{md2_path}] \n{line}")
            else:
                # Context lines (unchanged)
                labeled_diff.append(line)

        differ = difflib.ndiff(lines1, lines2)
        last_origin_line = ""

        labeled_differ = []
        for line in diff:
            code = line[:2]  # The prefix: '+ ', '- ', '? ', or '  '
            content = line[2:].strip()
            
            if code == '- ':
                # Line removed from file 1
                last_origin_line = content
                labeled_differ.append(f"[{md1_path}] - {content}")
                
            elif code == '+ ':
                # Line added to file 2
                labeled_differ.append(f"[{md2_path}] + {content}")
                
            elif code == '? ':
                # Character-level highlight line (points to changes in the line above)
                # We attribute this highlight to the file that just had the change
                prefix = f"[{md2_path}]" if '+' in line else f"[{md1_path}]"
                labeled_differ.append(f"{prefix}   {content}")

        diff_text = '\n'.join(labeled_diff)
       
        # Format it nicely as markdown diff
        formatted_diff = f"# Changes \n\n```diff\n{diff_text}\n```"

        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(formatted_diff)
            
        return output_path
    except FileNotFoundError as e:
        logger.error(f"Differentiating failed, input file missing: {e}")
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(f"Agent execution failed due to API error or empty input. Downstream tasks might be impacted.\nError: {e}")
        return output_path
"""
def main():

    #INPUT_DIR = Path(__file__).parent / "data/input"
    OUTPUT_DIR = Path(__file__).parents[3] / "output"
    md1_path = OUTPUT_DIR /"formular_initial.md"
    md2_path = OUTPUT_DIR /"formular_modificat.md"
    output_path = OUTPUT_DIR /"differs_formular_2.md"

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if not md1_path.exists() and not md2_path.exists() and not output_path.exists():
        logger.error(f"Input document not found at {md1_path}")
        return
    logger.info(f"Comparing {md1_path} and {md2_path}, output will be saved to {output_path}")
    output_md = generate_diff(md1_path, md2_path, output_path)

    print(output_md)

if __name__ == "__main__":
     main()

"""