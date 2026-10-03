import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class CDVQAAdapter:
    """
    Dataset adapter for Change Detection Visual Question Answering (CDVQA).
    Provides bi-temporal image pairs with conversational questions concerning
    surface modification, building expansion, vegetation dynamics, and water shift.
    """
    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir) if root_dir else Path("data/benchmarks/cdvqa")

    def format_bitemporal_prompt(self, question: str) -> str:
        return f"<image_t1><image_t2>\nBi-temporal Analysis Question: {question}\nSynthesize change dynamics with quantitative spatial evidence."
