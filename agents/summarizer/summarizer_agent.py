import os
import logging
from .tools.summarize_tool import generate_summary

logger = logging.getLogger(__name__)

class SummarizerAgent:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir

    def process(self, input_filename: str = "memoriu.md", output_filename: str = "summary.md"):
        input_path = os.path.join(self.output_dir, input_filename)
        output_path = os.path.join(self.output_dir, output_filename)
        return generate_summary(input_path, output_path)
