import os
import logging
import markdown
import pdfkit

logger = logging.getLogger(__name__)

def generate_pdf_report(md_path: str, output_path: str):
    """
    Converts a Markdown report to a PDF file.
    """
    logger.info(f"Generating PDF report from {md_path}")
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
            
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        
        # Adding some basic styling
        html_styled = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1, h2, h3 {{ color: #333; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ padding-top: 12px; padding-bottom: 12px; text-align: left; background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # We need wkhtmltopdf installed in system, or fallback to simple HTML write if not
        try:
            pdfkit.from_string(html_styled, output_path)
            logger.info(f"PDF successfully created at {output_path}")
        except Exception as e:
            logger.warning(f"pdfkit failed (wkhtmltopdf might be missing): {e}. Saving as HTML instead.")
            output_path = output_path.replace('.pdf', '.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_styled)
                
        return output_path
    
    except Exception as e:
        logger.error(f"Reporter failed: {e}")
        return None
