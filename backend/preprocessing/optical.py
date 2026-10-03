from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image

from .metadata import extract_geospatial_metadata

try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

try:
    import tifffile
    HAS_TIFFFILE = True
except ImportError:
    HAS_TIFFFILE = False

def normalize_band(arr: np.ndarray, lower_pct: float = 2.0, upper_pct: float = 98.0) -> np.ndarray:
    """Robust percentile radiometric normalization for optical bands (removes cloud saturation & solar glint)."""
    valid = arr[~np.isnan(arr)]
    if valid.size == 0:
        return np.zeros_like(arr, dtype=np.uint8)
    
    p_low, p_high = np.percentile(valid, (lower_pct, upper_pct))
    if p_high == p_low:
        p_low = np.min(valid)
        p_high = np.max(valid) if np.max(valid) > p_low else p_low + 1.0

    clipped = np.clip(arr, p_low, p_high)
    normalized = (clipped - p_low) / (p_high - p_low) * 255.0
    return normalized.astype(np.uint8)

def compute_spectral_indices(raw_bands: np.ndarray) -> Dict[str, np.ndarray]:
    """Compute standard remote-sensing spectral indices (NDVI, NDWI) if sufficient bands exist."""
    indices = {}
    if raw_bands.ndim == 3 and raw_bands.shape[0] >= 3:
        r = raw_bands[0].astype(np.float32)
        g = raw_bands[1].astype(np.float32)
        nir = raw_bands[2].astype(np.float32)

        denom_w = g + nir + 1e-6
        ndwi = (g - nir) / denom_w
        indices["ndwi"] = np.clip(ndwi, -1.0, 1.0)

        denom_v = nir + r + 1e-6
        ndvi = (nir - r) / denom_v
        indices["ndvi"] = np.clip(ndvi, -1.0, 1.0)
    return indices

def process_optical_image(file_path: str) -> Tuple[np.ndarray, Image.Image, Dict[str, Any]]:
    """
    Dedicated Optical Processing Pipeline:
    1. Reads GeoTIFF preserving CRS and geotransform.
    2. Inspects multi-band reflectance.
    3. Handles NoData and clips outliers via 2%-98% radiometric calibration.
    4. Computes spectral features and outputs high-fidelity RGB PIL and metadata.
    """
    meta = extract_geospatial_metadata(file_path)
    ext = Path(file_path).suffix.lower().lstrip(".")
    raw_data = None
    rgb_arr = None

    if HAS_RASTERIO and ext in ["tif", "tiff"]:
        try:
            with rasterio.open(file_path) as src:
                raw_data = src.read()
                bands, h, w = raw_data.shape
                
                if bands >= 3:
                    r = normalize_band(raw_data[0])
                    g = normalize_band(raw_data[1])
                    b = normalize_band(raw_data[2])
                    rgb_arr = np.stack([r, g, b], axis=-1)
                elif bands == 1:
                    gray = normalize_band(raw_data[0])
                    rgb_arr = np.stack([gray, gray, gray], axis=-1)
                elif bands == 2:
                    b1 = normalize_band(raw_data[0])
                    b2 = normalize_band(raw_data[1])
                    b3 = ((b1.astype(np.float32) + b2.astype(np.float32)) / 2).astype(np.uint8)
                    rgb_arr = np.stack([b1, b2, b3], axis=-1)
        except Exception:
            pass

    if rgb_arr is None and HAS_TIFFFILE and ext in ["tif", "tiff"]:
        try:
            arr = tifffile.imread(file_path)
            raw_data = arr
            if arr.ndim == 2:
                gray = normalize_band(arr)
                rgb_arr = np.stack([gray, gray, gray], axis=-1)
            elif arr.ndim == 3:
                if arr.shape[0] in [1, 2, 3, 4]:
                    r = normalize_band(arr[0])
                    g = normalize_band(arr[1] if arr.shape[0] > 1 else arr[0])
                    b = normalize_band(arr[2] if arr.shape[0] > 2 else arr[0])
                    rgb_arr = np.stack([r, g, b], axis=-1)
                else:
                    r = normalize_band(arr[:, :, 0])
                    g = normalize_band(arr[:, :, 1] if arr.shape[2] > 1 else arr[:, :, 0])
                    b = normalize_band(arr[:, :, 2] if arr.shape[2] > 2 else arr[:, :, 0])
                    rgb_arr = np.stack([r, g, b], axis=-1)
        except Exception:
            pass

    if rgb_arr is None:
        with Image.open(file_path) as img:
            rgb_img = img.convert("RGB")
            rgb_arr = np.array(rgb_img)
            raw_data = rgb_arr

    pil_img = Image.fromarray(rgb_arr)
    meta["optical_indices"] = compute_spectral_indices(raw_data) if raw_data is not None else {}
    return rgb_arr, pil_img, meta
