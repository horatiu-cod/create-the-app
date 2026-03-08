from pathlib import Path
import logging
import sys
from ollama_pipeline_api_model import run_ollama_document_converter

try:
    from docling.document_converter import DocumentConverter
    HAS_DOCLING = True
except ImportError:
    HAS_DOCLING = False

"""
if 'docling' in sys.modules:
    HAS_DOCLING = True
else:
    HAS_DOCLING = False 
"""
logger = logging.getLogger(__name__)

def convert_pdf_to_md(pdf_path: str, output_dir: str) -> str:
    """
    Converts a PDF file to a Markdown representation.
    Returns the path to the newly saved markdown file.
    """
    logger.info(f"Converting {pdf_path} to Markdown...")
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF {pdf_path} not found.")

    output_path = Path(output_dir) / f"{pdf_file.stem}.md"
    
    if HAS_DOCLING:
        logger.info(f"Using docling to convert {pdf_path}")
        #converter = DocumentConverter()
        #md_content = converter.convert_pdf_to_md(pdf_path)
        doc = run_ollama_document_converter(pdf_path, model_name="ibm/granite-docling-258m")
        md_content = doc.export_to_markdown()
    else:
        logger.warning(f"Docling not available. Falling back to simple text extraction for {pdf_path}")
        # Very simple fallback for demonstration
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            md_content = f"# Extracted content from {pdf_file.name}\n\n"
            for page in reader.pages:
                md_content += page.extract_text() + "\n\n"
        except ImportError:
            md_content = f"# Mock extracted content from {pdf_file.name}\nPlease install docling or pypdf."

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return str(output_path)
