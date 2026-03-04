import os
import logging
from .tools.differ_tool import generate_diff

logger = logging.getLogger(__name__)

class DifferAgent:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir

    def process(self, initial_md: str, modified_md: str, output_name: str = "differs.md"):
        initial_path = os.path.join(self.output_dir, initial_md)
        modified_path = os.path.join(self.output_dir, modified_md)
        out_path = os.path.join(self.output_dir, output_name)
        
        logger.info(f"DifferAgent comparing {initial_path} and {modified_path}")
        return generate_diff(initial_path, modified_path, out_path)
