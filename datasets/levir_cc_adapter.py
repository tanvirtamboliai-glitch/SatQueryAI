import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class LEVIRCCAdapter:
    """
    Dataset adapter for LEVIR-CC (Change Captioning Benchmark).
    Provides dual-temporal aerial image pairs accompanied by natural language
    descriptions of newly built structures, road expansion, and vegetation changes.
    """
    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir) if root_dir else Path("data/benchmarks/levir_cc")

    def load_annotations(self, pair_id: str) -> List[str]:
        """Loads reference sentences describing changes between T1 and T2."""
        return [
            "Several new residential buildings were constructed in the open field.",
            "Vegetation was cleared to construct building foundations and driveways."
        ]
