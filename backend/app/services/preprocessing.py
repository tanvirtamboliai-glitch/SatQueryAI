import os
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
from PIL import Image
import cv2

try:
    import rasterio
    from rasterio.windows import Window
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

try:
    import tifffile
    HAS_TIFFFILE = True
except ImportError:
    HAS_TIFFFILE = False

def normalize_band(arr: np.ndarray, lower_pct: float = 2.0, upper_pct: float = 98.0) -> np.ndarray:
    """Robust percentile normalization for remote sensing bands (handles cloud reflections & radar speckle)."""
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

def load_and_preprocess_image(file_path: str, target_size: Optional[Tuple[int, int]] = None) -> Tuple[np.ndarray, Image.Image, Dict[str, Any]]:
    """
    Loads remote sensing raster, extracts RGB representation, normalizes,
    and returns (raw_array, pil_rgb_image, metadata).
    """
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    raw_data = None
    rgb_arr = None

    if HAS_RASTERIO and ext in ["tif", "tiff"]:
        try:
            with rasterio.open(file_path) as src:
                # Read all bands
                raw_data = src.read()  # (bands, H, W)
                bands, h, w = raw_data.shape
                
                if bands >= 3:
                    # Select RGB (typically bands 1, 2, 3 or 3, 2, 1)
                    r = normalize_band(raw_data[0])
                    g = normalize_band(raw_data[1])
                    b = normalize_band(raw_data[2])
                    rgb_arr = np.stack([r, g, b], axis=-1)
                elif bands == 1:
                    # Single band (SAR backscatter or panchromatic)
                    gray = normalize_band(raw_data[0])
                    # Apply false-color or grayscale to RGB
                    rgb_arr = np.stack([gray, gray, gray], axis=-1)
                elif bands == 2:
                    b1 = normalize_band(raw_data[0])
                    b2 = normalize_band(raw_data[1])
                    b3 = ((b1.astype(np.float32) + b2.astype(np.float32)) / 2).astype(np.uint8)
                    rgb_arr = np.stack([b1, b2, b3], axis=-1)
        except Exception as e:
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
        except Exception as e:
            pass

    if rgb_arr is None:
        # Standard PIL loading
        with Image.open(file_path) as img:
            rgb_img = img.convert("RGB")
            rgb_arr = np.array(rgb_img)
            raw_data = rgb_arr

    if target_size and (rgb_arr.shape[1] != target_size[0] or rgb_arr.shape[0] != target_size[1]):
        rgb_arr = cv2.resize(rgb_arr, target_size, interpolation=cv2.INTER_AREA)

    pil_img = Image.fromarray(rgb_arr)
    meta = {
        "width": rgb_arr.shape[1],
        "height": rgb_arr.shape[0],
        "channels": 3
    }
    return rgb_arr, pil_img, meta

def align_pair(img1_arr: np.ndarray, img2_arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Resample/pad/crop images so they have identical dimensions for pixel-level comparisons."""
    h1, w1 = img1_arr.shape[:2]
    h2, w2 = img2_arr.shape[:2]

    if (h1, w1) == (h2, w2):
        return img1_arr, img2_arr

    target_w = max(w1, w2)
    target_h = max(h1, h2)

    img1_aligned = cv2.resize(img1_arr, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
    img2_aligned = cv2.resize(img2_arr, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
    return img1_aligned, img2_aligned

def generate_tiles(image_arr: np.ndarray, tile_size: int = 512, overlap: int = 64) -> List[Dict[str, Any]]:
    """
    Split large remote sensing scenes (e.g. 4096x4096) into overlapping tiles for high-res inference.
    """
    h, w = image_arr.shape[:2]
    tiles = []
    stride = tile_size - overlap

    for y in range(0, h, stride):
        for x in range(0, w, stride):
            y_end = min(y + tile_size, h)
            x_end = min(x + tile_size, w)
            y_start = max(0, y_end - tile_size)
            x_start = max(0, x_end - tile_size)

            tile_crop = image_arr[y_start:y_end, x_start:x_end]
            tiles.append({
                "window": (x_start, y_start, x_end, y_end),
                "tile_image": Image.fromarray(tile_crop),
                "tile_array": tile_crop
            })
            if x_end >= w:
                break
        if y_end >= h:
            break

    return tiles
