import os
import logging
from .tools.reporter_tool import generate_pdf_report

logger = logging.getLogger(__name__)

class ReportingAgent:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir

    def process(self, input_filename: str = "raport.md", output_filename: str = "raport_final.pdf"):
        input_path = os.path.join(self.output_dir, input_filename)
        output_path = os.path.join(self.output_dir, output_filename)
        return generate_pdf_report(input_path, output_path)
