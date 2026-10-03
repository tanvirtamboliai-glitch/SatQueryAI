from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image
import cv2

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

def apply_speckle_filter(img_arr: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    Speckle-reduction filtering for SAR backscatter (Lee / Adaptive Median filter approximation).
    Suppresses granular radar noise while preserving building & water edges.
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    filtered = cv2.medianBlur(img_arr.astype(np.uint8), kernel_size)
    return filtered

def linear_to_db(amplitude_arr: np.ndarray) -> np.ndarray:
    """
    Convert raw SAR linear digital numbers/amplitude to sigma-naught backscatter (dB):
    sigma_0_dB = 10 * log10(DN^2 + eps)
    """
    safe_arr = np.maximum(amplitude_arr.astype(np.float32), 1e-5)
    power = np.square(safe_arr)
    db = 10.0 * np.log10(power + 1e-6)
    return db

def process_sar_image(file_path: str) -> Tuple[np.ndarray, Image.Image, Dict[str, Any]]:
    """
    Dedicated SAR Preprocessing Pipeline:
    1. Reads SAR GeoTIFF / raw amplitude matrix.
    2. Identifies radar polarization channels (e.g. VV co-pol, VH cross-pol).
    3. Converts linear power to calibrated decibel scale (dB) to expose microwave backscatter dynamics.
    4. Applies speckle-aware spatial noise filtering.
    5. Maps backscatter dynamics:
       - Specular reflection (Dark, < -18 dB): Calm water, runways
       - Volume scattering (Medium, -15 to -8 dB): Dense vegetation canopy
       - Double-bounce corner reflection (Bright, > -4 dB): Urban structures, buildings
    """
    meta = extract_geospatial_metadata(file_path)
    meta["modality"] = "sar"
    if not meta.get("sensor"):
        meta["sensor"] = "Sentinel-1 C-SAR"

    ext = Path(file_path).suffix.lower().lstrip(".")
    raw_sar = None

    if HAS_RASTERIO and ext in ["tif", "tiff"]:
        try:
            with rasterio.open(file_path) as src:
                raw_sar = src.read()
        except Exception:
            pass

    if raw_sar is None and HAS_TIFFFILE and ext in ["tif", "tiff"]:
        try:
            raw_sar = tifffile.imread(file_path)
            if raw_sar.ndim == 2:
                raw_sar = np.expand_dims(raw_sar, axis=0)
            elif raw_sar.ndim == 3 and raw_sar.shape[-1] in [1, 2, 3]:
                raw_sar = np.transpose(raw_sar, (2, 0, 1))
        except Exception:
            pass

    if raw_sar is None:
        with Image.open(file_path) as img:
            gray = np.array(img.convert("L"))
            raw_sar = np.expand_dims(gray, axis=0)

    num_bands = raw_sar.shape[0]
    if num_bands == 1:
        pols = ["VV (Co-polarization)"]
        amplitude = raw_sar[0].astype(np.float32)
    elif num_bands >= 2:
        pols = ["VV (Co-polarization)", "VH (Cross-polarization)"]
        amplitude = raw_sar[0].astype(np.float32)
    else:
        pols = ["Single-channel SAR"]
        amplitude = raw_sar.squeeze().astype(np.float32)

    meta["polarizations"] = pols

    db_arr = linear_to_db(amplitude)
    meta["backscatter_min_db"] = float(np.min(db_arr))
    meta["backscatter_max_db"] = float(np.max(db_arr))
    meta["backscatter_mean_db"] = float(np.mean(db_arr))

    db_clipped = np.clip(db_arr, -25.0, 5.0)
    norm_sar = ((db_clipped - (-25.0)) / 30.0 * 255.0).astype(np.uint8)

    despeckled = apply_speckle_filter(norm_sar, kernel_size=3)

    water_mask = (db_arr < -16.0)
    urban_double_bounce = (db_arr > -3.0)
    vegetation_vol = (~water_mask) & (~urban_double_bounce)

    meta["sar_metrics"] = {
        "specular_low_pct": round(float(np.sum(water_mask) / water_mask.size * 100), 2),
        "double_bounce_high_pct": round(float(np.sum(urban_double_bounce) / urban_double_bounce.size * 100), 2),
        "volume_scattering_pct": round(float(np.sum(vegetation_vol) / vegetation_vol.size * 100), 2),
        "mean_backscatter_db": round(float(np.mean(db_arr)), 2)
    }

    if num_bands >= 2:
        vh_db = linear_to_db(raw_sar[1])
        vh_norm = np.clip(((vh_db - (-30.0)) / 30.0 * 255.0), 0, 255).astype(np.uint8)
        vh_despeckled = apply_speckle_filter(vh_norm, kernel_size=3)
        ratio = np.clip(np.abs(despeckled.astype(float) - vh_despeckled.astype(float)), 0, 255).astype(np.uint8)
        sar_rgb = np.stack([despeckled, vh_despeckled, ratio], axis=-1)
    else:
        sar_rgb = np.stack([despeckled, despeckled, despeckled], axis=-1)

    pil_img = Image.fromarray(sar_rgb)
    return sar_rgb, pil_img, meta
