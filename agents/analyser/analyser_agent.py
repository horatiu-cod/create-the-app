import os
import logging
from .tools.analyser_tool import analyze_changes

logger = logging.getLogger(__name__)

class AnalyserAgent:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir

    def process(self, summary_filename: str = "summary.md", differs_filename: str = "differs.md", output_filename: str = "raport.md"):
        summary_path = os.path.join(self.output_dir, summary_filename)
        differs_path = os.path.join(self.output_dir, differs_filename)
        output_path = os.path.join(self.output_dir, output_filename)
        return analyze_changes(summary_path, differs_path, output_path)
