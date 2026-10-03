import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np

class LEVIRMCIAdapter:
    """
    Dataset adapter for LEVIR-MCI (Mask & Change Interpretation).
    Connects binary pixel-level change masks with semantic change category descriptions.
    """
    CHANGE_CATEGORIES = [
        "New Building Construction",
        "Demolition / Removal",
        "Road & Infrastructure Addition",
        "Agricultural Clearing",
        "Vegetation Regrowth",
        "Water Reservoir Variation"
    ]

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir) if root_dir else Path("data/benchmarks/levir_mci")

    def load_pair_with_mask(self, sample_id: str) -> Dict[str, Any]:
        return {
            "sample_id": sample_id,
            "t1_path": str(self.root_dir / "t1" / f"{sample_id}.png"),
            "t2_path": str(self.root_dir / "t2" / f"{sample_id}.png"),
            "mask_path": str(self.root_dir / "mask" / f"{sample_id}.png"),
            "category": "New Building Construction",
            "description": "Dense cluster of modern residential buildings erected on previously uncultivated grassland."
        }
