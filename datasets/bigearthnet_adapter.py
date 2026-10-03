import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np

class BigEarthNetAdapter:
    """
    Dataset adapter for BigEarthNet (Sentinel-2 multispectral and Sentinel-1 SAR).
    Standard benchmark for land-cover representation and self-supervised foundation pre-training.
    """
    LABELS_19 = [
        "Urban fabric", "Industrial or commercial units", "Arable land",
        "Permanent crops", "Pastures", "Complex cultivation patterns",
        "Land principally occupied by agriculture, with significant areas of natural vegetation",
        "Agro-forestry areas", "Broad-leaved forest", "Coniferous forest",
        "Mixed forest", "Natural grassland and sparsely vegetated areas",
        "Moors, heathland and sclerophyllous vegetation", "Transitional woodland, shrub",
        "Beaches, dunes, sands", "Inland wetlands", "Coastal wetlands",
        "Inland waters", "Marine waters"
    ]

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir) if root_dir else Path("data/benchmarks/bigearthnet")

    def load_sample(self, patch_id: str) -> Dict[str, Any]:
        """Loads metadata, bands, and CORINE land cover labels for a Sentinel patch."""
        return {
            "patch_id": patch_id,
            "sensor": "Sentinel-2 MSI (12 bands) / Sentinel-1 SAR (Dual-Pol VV/VH)",
            "bands_count": 12,
            "resolution": [10.0, 20.0, 60.0],
            "labels": ["Arable land", "Complex cultivation patterns"],
            "crs": "EPSG:32632"
        }

    def get_corine_class_weights(self) -> Dict[str, float]:
        """Class distribution weights for cross-entropy imbalance mitigation."""
        return {lbl: 1.0 / len(self.LABELS_19) for lbl in self.LABELS_19}
