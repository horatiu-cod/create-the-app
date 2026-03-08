import os
import logging
from markdown_pdf import MarkdownPdf, Section

logger = logging.getLogger(__name__)

def generate_pdf_report(md_path: str, output_path: str):
    """
    Converts a Markdown report to a PDF file.
    """
    logger.info(f"Generating PDF report from {md_path}")
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        pdf = MarkdownPdf()
        pdf.add_section(Section(md_content, toc=False))
        pdf.save(output_path)
        
        logger.info(f"PDF successfully created at {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Reporter failed: {e}")
        return None
