import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class RSVQAAdapter:
    """
    Dataset adapter for RSVQA (Remote Sensing Visual Question Answering).
    Supports Low-Resolution (Sentinel-2) and High-Resolution aerial benchmarks
    with Presence, Count, Comparison, and Rural/Urban questions.
    """
    QUESTION_TYPES = ["presence", "count", "comparison", "area"]

    def __init__(self, variant: str = "HR", root_dir: Optional[str] = None):
        self.variant = variant
        self.root_dir = Path(root_dir) if root_dir else Path(f"data/benchmarks/rsvqa_{variant.lower()}")

    def standardize_qa_pair(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "image_id": item.get("img_id"),
            "question": item.get("question"),
            "type": item.get("type", "presence"),
            "ground_truth": item.get("answer"),
            "active_split": item.get("split", "test")
        }
