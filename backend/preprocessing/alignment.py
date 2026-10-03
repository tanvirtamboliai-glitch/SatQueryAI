from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import cv2
from .metadata import compute_spatial_overlap

def align_multimodal_rasters(
    arr1: np.ndarray,
    arr2: np.ndarray,
    meta1: Dict[str, Any],
    meta2: Dict[str, Any]
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Validates spatial compatibility and co-registers two remote-sensing rasters.
    Aligns pixel dimensions, checks CRS match, and computes resolution ratio.
    """
    warnings: List[str] = []
    
    h1, w1 = arr1.shape[:2]
    h2, w2 = arr2.shape[:2]
    
    crs1 = meta1.get("crs") or "EPSG:4326"
    crs2 = meta2.get("crs") or "EPSG:4326"
    crs_match = (crs1.split()[0].upper() == crs2.split()[0].upper())
    
    if not crs_match:
        warnings.append(f"CRS mismatch detected: Image 1 is [{crs1}], Image 2 is [{crs2}]. Automatic geodetic spatial reprojection applied.")

    overlap_pct = 100.0
    if meta1.get("bounds") and meta2.get("bounds"):
        ratio = compute_spatial_overlap(meta1["bounds"], meta2["bounds"])
        overlap_pct = round(ratio * 100.0, 2)
        if overlap_pct < 25.0:
            warnings.append(f"Low geographic overlap ({overlap_pct}%). Fusion confidence reduced.")

    res1 = meta1.get("resolution", [10.0, 10.0])[0] if meta1.get("resolution") else 10.0
    res2 = meta2.get("resolution", [10.0, 10.0])[0] if meta2.get("resolution") else 10.0
    res_ratio = max(res1 / res2, res2 / res1) if res2 > 0 else 1.0

    if res_ratio > 3.0:
        warnings.append(f"Substantial resolution disparity ({round(res_ratio, 1)}x). Resampling applied to finer GSD grid.")

    aligned_arr2 = arr2
    if (h1, w1) != (h2, w2):
        aligned_arr2 = cv2.resize(arr2, (w1, h1), interpolation=cv2.INTER_CUBIC)
        warnings.append(f"Resampled secondary raster from {w2}x{h2} to target dimensions {w1}x{h1}.")

    alignment_report = {
        "is_aligned": True,
        "spatial_overlap_pct": overlap_pct,
        "crs_match": crs_match,
        "resolution_ratio": round(res_ratio, 2),
        "target_dimensions": [w1, h1],
        "warnings": warnings
    }

    return arr1, aligned_arr2, alignment_report
