import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class VRSBenchAdapter:
    """
    Dataset adapter for VRSBench (Vision-Language Remote Sensing Benchmark).
    Provides paired multi-task instructions: Captioning, Visual Question Answering, and Grounding.
    """
    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir) if root_dir else Path("data/benchmarks/vrsbench")

    def format_vqa_prompt(self, question: str) -> str:
        return f"<image>\nQuestion: {question}\nAnswer based on remote sensing evidence with spatial certainty."

    def format_grounding_prompt(self, target: str) -> str:
        return f"<image>\nLocate and demarcate all coordinates matching: {target}."

    def parse_grounding_annotation(self, ann: Dict[str, Any]) -> Dict[str, Any]:
        """Convert VRSBench polygon/bbox annotations to normalized [ymin, xmin, ymax, xmax] 0..1000 format."""
        bbox = ann.get("bbox", [0, 0, 100, 100])
        # x, y, w, h
        x, y, w, h = bbox
        img_w = ann.get("image_width", 512)
        img_h = ann.get("image_height", 512)
        
        ymin = (y / img_h) * 1000.0
        xmin = (x / img_w) * 1000.0
        ymax = ((y + h) / img_h) * 1000.0
        xmax = ((x + w) / img_w) * 1000.0

        return {
            "label": ann.get("category", "object"),
            "box_2d": [round(ymin, 1), round(xmin, 1), round(ymax, 1), round(xmax, 1)]
        }
