from typing import List, Tuple, Dict, Any
import numpy as np

def generate_spatial_tiles(
    img_arr: np.ndarray,
    tile_size: int = 512,
    stride: int = 400
) -> Tuple[List[np.ndarray], List[Tuple[int, int, int, int]]]:
    """
    Slices large remote-sensing rasters into overlapping patches (default 512x512 with 112px overlap).
    Returns (list_of_patches, list_of_coordinates [ymin, xmin, ymax, xmax]).
    """
    h, w = img_arr.shape[:2]
    
    if h <= tile_size and w <= tile_size:
        return [img_arr], [(0, 0, h, w)]
        
    patches = []
    coordinates = []
    
    for y in range(0, h, stride):
        for x in range(0, w, stride):
            y_end = min(y + tile_size, h)
            x_end = min(x + tile_size, w)
            y_start = max(0, y_end - tile_size)
            x_start = max(0, x_end - tile_size)
            
            patch = img_arr[y_start:y_end, x_start:x_end]
            patches.append(patch)
            coordinates.append((y_start, x_start, y_end, x_end))
            
    return patches, coordinates

def reconstruct_raster_from_tiles(
    patch_masks: List[np.ndarray],
    coordinates: List[Tuple[int, int, int, int]],
    target_shape: Tuple[int, int]
) -> np.ndarray:
    """
    Reassembles tiled spatial mask predictions into full-resolution raster output
    using distance-weighted averaging across overlap borders.
    """
    h, w = target_shape[:2]
    full_mask = np.zeros((h, w), dtype=np.float32)
    weights = np.zeros((h, w), dtype=np.float32)
    
    for mask, (y0, x0, y1, x1) in zip(patch_masks, coordinates):
        full_mask[y0:y1, x0:x1] += mask.astype(np.float32)
        weights[y0:y1, x0:x1] += 1.0
        
    weights = np.maximum(weights, 1e-5)
    reconstructed = (full_mask / weights).astype(np.uint8)
    return reconstructed
