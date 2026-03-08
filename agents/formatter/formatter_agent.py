import os
import logging
from .tools.pdf_formatter import convert_pdf_to_md

logger = logging.getLogger(__name__)

class FormatterAgent:
    def __init__(self, input_dir: str = "data/input", output_dir: str = "output"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def process(self, files_to_process: list[str] = None):
        """
        Process the listed PDF files. If none provided, processes all .pdf files in input_dir.
        """
        if files_to_process is None:
            files_to_process = [f for f in os.listdir(self.input_dir) if f.endswith(".pdf")]

        results = []
        for file in files_to_process:
            input_path = os.path.join(self.input_dir, file)
            logger.info(f"FormatterAgent processing: {input_path}")
            try:
                md_path = convert_pdf_to_md(input_path, self.output_dir)
                results.append(md_path)
                logger.info(f"Successfully converted to {md_path}")
            except Exception as e:
                logger.error(f"Failed to convert this file: {file}: {e}")
        return results
