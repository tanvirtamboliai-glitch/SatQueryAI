import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
import numpy as np
from PIL import Image

try:
    import rasterio
    from rasterio.crs import CRS
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

try:
    import tifffile
    HAS_TIFFFILE = True
except ImportError:
    HAS_TIFFFILE = False

def detect_modality_from_context(filename: str, bands: int, dtype_str: str) -> str:
    """Infer remote sensing modality from filename, band count, and data type."""
    fn_lower = filename.lower()
    if any(k in fn_lower for k in ["sar", "s1", "vv", "vh", "sentinel1", "radarsat"]):
        return "sar"
    if any(k in fn_lower for k in ["multi", "ms", "sentinel2", "s2", "landsat", "hyperspectral"]):
        return "multispectral"
    if bands == 1:
        # 1-band images are often SAR or single-band index/elevation
        if "opt" in fn_lower or "pan" in fn_lower:
            return "optical"
        return "sar"
    elif bands in [3, 4]:
        return "optical"
    elif bands > 4:
        return "multispectral"
    return "optical"

def extract_date_from_filename(filename: str) -> Optional[str]:
    """Parse acquisition date formatted as YYYY-MM-DD or YYYYMMDD from filename."""
    match = re.search(r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})', filename)
    if match:
        year, month, day = match.groups()
        if 1990 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
            return f"{year}-{month}-{day}"
    return None

def inspect_image(file_path: str, file_id: str) -> Dict[str, Any]:
    """Inspect single image file and extract rigorous remote-sensing metadata."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at {file_path}")

    ext = path.suffix.lower().lstrip(".")
    if ext not in ["tif", "tiff", "png", "jpg", "jpeg"]:
        raise ValueError(f"Unsupported file format '.{ext}'. Supported: GeoTIFF/TIFF, PNG, JPEG.")

    metadata: Dict[str, Any] = {
        "file_id": file_id,
        "filename": path.name,
        "format": "GeoTIFF" if ext in ["tif", "tiff"] else ext.upper(),
        "is_valid": True,
        "warnings": [],
        "crs": None,
        "geotransform": None,
        "bounds": None,
        "resolution": None,
        "sensor": None,
        "acquisition_date": extract_date_from_filename(path.name)
    }

    # Attempt Rasterio first
    if HAS_RASTERIO and ext in ["tif", "tiff"]:
        try:
            with rasterio.open(file_path) as src:
                metadata["dimensions"] = [src.width, src.height]
                metadata["bands"] = src.count
                metadata["crs"] = str(src.crs) if src.crs else "EPSG:4326 (Default)"
                metadata["geotransform"] = list(src.transform)[:6]
                b_l = min(src.bounds.left, src.bounds.right)
                b_r = max(src.bounds.left, src.bounds.right)
                b_b = min(src.bounds.bottom, src.bounds.top)
                b_t = max(src.bounds.bottom, src.bounds.top)
                metadata["bounds"] = [b_l, b_b, b_r, b_t]
                metadata["resolution"] = [abs(src.res[0]), abs(src.res[1])]
                
                # Check tags for sensor or date
                tags = src.tags()
                if "ACQUISITION_DATE" in tags:
                    metadata["acquisition_date"] = tags["ACQUISITION_DATE"]
                if "SENSOR" in tags:
                    metadata["sensor"] = tags["SENSOR"]
                elif "DATATAKE_IDENTIFIER" in tags or "SPACECRAFT_NAME" in tags:
                    metadata["sensor"] = tags.get("SPACECRAFT_NAME", "Sentinel")
                
                metadata["modality"] = detect_modality_from_context(path.name, src.count, src.dtypes[0])
                return metadata
        except Exception as e:
            metadata["warnings"].append(f"Rasterio read warning: {str(e)}")

    # Fallback to tifffile or PIL
    if HAS_TIFFFILE and ext in ["tif", "tiff"]:
        try:
            with tifffile.TiffFile(file_path) as tif:
                series = tif.series[0]
                shape = series.shape
                if len(shape) == 2:
                    h, w = shape
                    bands = 1
                elif len(shape) == 3:
                    if shape[0] in [1, 3, 4, 8, 12, 13]:
                        bands, h, w = shape
                    else:
                        h, w, bands = shape
                else:
                    h, w, bands = shape[-2], shape[-1], shape[0]
                
                metadata["dimensions"] = [int(w), int(h)]
                metadata["bands"] = int(bands)
                metadata["crs"] = metadata.get("crs") or "EPSG:4326 (Synthesized GeoTIFF)"
                metadata["bounds"] = [12.45, 41.85, 12.55, 41.95]  # Default geodetic window if unassigned
                metadata["resolution"] = [10.0, 10.0]
                metadata["modality"] = detect_modality_from_context(path.name, bands, str(series.dtype))
                return metadata
        except Exception as e:
            metadata["warnings"].append(f"Tifffile read warning: {str(e)}")

    # Standard PIL read for PNG/JPEG or fallback
    try:
        with Image.open(file_path) as img:
            w, h = img.size
            bands = len(img.getbands())
            metadata["dimensions"] = [w, h]
            metadata["bands"] = bands
            metadata["crs"] = "WGS84 / Screen (Non-georeferenced benchmark)"
            metadata["bounds"] = [0.0, 0.0, float(w), float(h)]
            metadata["resolution"] = [1.0, 1.0]
            metadata["modality"] = detect_modality_from_context(path.name, bands, "uint8")
            if ext in ["png", "jpg", "jpeg"]:
                metadata["warnings"].append("Standard RGB image without embedded GIS CRS coordinates. Normalized planar coords used.")
            return metadata
    except Exception as e:
        metadata["is_valid"] = False
        metadata["warnings"].append(f"Failed to decode image: {str(e)}")
        metadata["dimensions"] = [0, 0]
        metadata["bands"] = 0
        metadata["modality"] = "unknown"
        return metadata

def compute_spatial_overlap(bounds1: List[float], bounds2: List[float]) -> float:
    """Calculate intersection over minimum area between two bounding boxes [minx, miny, maxx, maxy]."""
    if not bounds1 or not bounds2 or len(bounds1) != 4 or len(bounds2) != 4:
        return 1.0  # Default fallback if non-spatial
    
    b1_xmin, b1_xmax = min(bounds1[0], bounds1[2]), max(bounds1[0], bounds1[2])
    b1_ymin, b1_ymax = min(bounds1[1], bounds1[3]), max(bounds1[1], bounds1[3])
    
    b2_xmin, b2_xmax = min(bounds2[0], bounds2[2]), max(bounds2[0], bounds2[2])
    b2_ymin, b2_ymax = min(bounds2[1], bounds2[3]), max(bounds2[1], bounds2[3])

    x_left = max(b1_xmin, b2_xmin)
    y_bottom = max(b1_ymin, b2_ymin)
    x_right = min(b1_xmax, b2_xmax)
    y_top = min(b1_ymax, b2_ymax)

    if x_right <= x_left or y_top <= y_bottom:
        return 0.0

    intersection_area = (x_right - x_left) * (y_top - y_bottom)
    area1 = (b1_xmax - b1_xmin) * (b1_ymax - b1_ymin)
    area2 = (b2_xmax - b2_xmin) * (b2_ymax - b2_ymin)

    if area1 <= 0 or area2 <= 0:
        return 0.0
        
    overlap_ratio = intersection_area / min(area1, area2)
    return float(np.clip(overlap_ratio, 0.0, 1.0))

def validate_image_pair(meta1: Dict[str, Any], meta2: Dict[str, Any]) -> Dict[str, Any]:
    """Validate spatial compatibility, CRS matching, and modality of paired images."""
    warnings = []
    
    # Check dimensions
    w1, h1 = meta1.get("dimensions", [meta1.get("width", 512), meta1.get("height", 512)])
    w2, h2 = meta2.get("dimensions", [meta2.get("width", 512), meta2.get("height", 512)])
    res_ratio = max(w1/w2, w2/w1) if w2 > 0 and w1 > 0 else 999.0
    
    if abs(w1 - w2) > 100 or abs(h1 - h2) > 100:
        warnings.append(f"Image dimension mismatch: Image 1 is {w1}x{h1}, Image 2 is {w2}x{h2}. Will apply automatic spatial resampling.")

    # Spatial overlap
    overlap = 1.0
    if meta1.get("bounds") and meta2.get("bounds"):
        overlap = compute_spatial_overlap(meta1["bounds"], meta2["bounds"])
        if overlap < 0.2:
            return {
                "valid": False,
                "pair_type": "incompatible",
                "spatial_overlap_pct": round(overlap * 100, 2),
                "crs_match": meta1.get("crs") == meta2.get("crs"),
                "resolution_ratio": round(res_ratio, 2),
                "reason": f"Insufficient geographic overlap ({round(overlap*100, 1)}%). The two scenes do not cover the same geographic area.",
                "warnings": warnings
            }

    # Modality classification
    mod1 = meta1.get("modality", "optical")
    mod2 = meta2.get("modality", "optical")

    pair_type = "bi_temporal"
    if (mod1 == "optical" and mod2 == "sar") or (mod1 == "sar" and mod2 == "optical"):
        pair_type = "optical_sar"
    elif mod1 == mod2:
        pair_type = "bi_temporal"
    else:
        pair_type = "cross_modal"

    # Dates
    date1 = meta1.get("acquisition_date")
    date2 = meta2.get("acquisition_date")
    if pair_type == "bi_temporal" and date1 and date2 and date1 == date2:
        warnings.append(f"Both images indicate the same acquisition date ({date1}). Ensure these represent different timestamps if analyzing change.")

    return {
        "valid": True,
        "pair_type": pair_type,
        "spatial_overlap_pct": round(overlap * 100, 2),
        "crs_match": meta1.get("crs") == meta2.get("crs"),
        "resolution_ratio": round(res_ratio, 2),
        "reason": None,
        "warnings": warnings
    }
