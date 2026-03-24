import difflib
import sys
import os

def generate_comparison_report(file1_path, file2_path, output_html="output/comparison_report.html"):
    """
    Compares two Markdown files (containing both text and tables) 
    and generates a side-by-side HTML report highlighting the differences.
    """
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        print(f"Error: One or both files do not exist {file1_path} or {file2_path}.")
        print(f"File 1: {file1_path} (Exists: {os.path.exists(file1_path)})")
        print(f"File 2: {file2_path} (Exists: {os.path.exists(file2_path)})")
        return

    # Read the markdown files. Markdown tables and text are both just text lines.
    with open(file1_path, 'r', encoding='utf-8') as f1:
        lines1 = f1.readlines()
        
    with open(file2_path, 'r', encoding='utf-8') as f2:
        lines2 = f2.readlines()

    # HtmlDiff automatically handles comparing text paragraphs and markdown table structures line-by-line
    # wrapcolumn ensures long paragraphs or wide tables don't break the layout
    html_differ = difflib.HtmlDiff(wrapcolumn=90)
    
    html_content = html_differ.make_file(
        lines1, 
        lines2, 
        fromdesc=f"Original: {file1_path}", 
        todesc=f"Modified: {file2_path}",
        context=False # Set to True if you only want to show lines with changes
    )
    
    # Write the beautiful side-by-side comparison to an HTML file
    with open(output_html, 'w', encoding='utf-8') as f_out:
        f_out.write(html_content)
        
    print(f"Successfully compared '{file1_path}' and '{file2_path}'.")
    print(f"--> Open this file in your browser to see the text and table diffs: {os.path.abspath(output_html)}")


if __name__ == "__main__":
    # --- INSTRUCTIONS ---
    # Put the paths to your two markdown files here:
    file_old = "output/formular_initial.md"
    file_new = "output/formular_modificat.md"
    
    generate_comparison_report(file_old, file_new)
