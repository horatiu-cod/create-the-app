# Multi-Agent PDF Digest Implementation Plan

## Problem Statement
The user needs to process multiple specific PDF files (`memoriu.pdf`, `formular_initial.pdf`, `formular_modificat.pdf`) using a multi-agent system, and display the side-by-side comparison of the initial and modified forms in the final report via a Streamlit UI.

## Proposed Changes
- Added a `compare_md.py` script that compares standard and tabular markdown using Python's `difflib.HtmlDiff` to generate a visual HTML report.
- Modified `user/upload_file.py` to check for and load `comparison_report.html` from the `output` directory when processing completes.
- Embedded the HTML directly into the Streamlit application using `streamlit.components.v1.html` for a seamless user experience.

## Verification
- Run the Streamlit application and process the PDFs.
- Verify that "Visual Comparison Report" appears at the bottom.
- Ensure the diff highlights additions and removals correctly within the text and tables.
