import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_visual_evidence(
    base_image: Image.Image,
    job_id: str,
    bboxes: List[Dict[str, Any]] = [],
    mask: Optional[np.ndarray] = None,
    color: str = "red",  # "red", "cyan", "green", "amber"
    change_percentage: Optional[float] = None,
    regions_count: Optional[int] = None,
    title: str = "Evidence Overlay"
) -> Dict[str, Any]:
    """
    Renders bounding box and segmentation overlay images and saves them to static results.
    Returns relative public URLs for the frontend.
    """
    img_arr = np.array(base_image.convert("RGB"))
    h, w = img_arr.shape[:2]

    overlay_arr = img_arr.copy()
    mask_saved_rel = None
    overlay_saved_rel = None
    change_map_saved_rel = None

    # Color palette
    color_map = {
        "red": (255, 45, 85),
        "cyan": (0, 220, 255),
        "green": (50, 215, 75),
        "amber": (255, 179, 0)
    }
    bgr_color = color_map.get(color, (255, 45, 85))

    # 1. Render segmentation mask overlay if mask exists
    if mask is not None:
        # Resize mask if needed
        if mask.shape[:2] != (h, w):
            mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)

        # Save standalone binary mask
        mask_fn = f"{job_id}_mask.png"
        mask_path = RESULTS_DIR / mask_fn
        cv2.imwrite(str(mask_path), mask)
        mask_saved_rel = f"/results/{mask_fn}"

        # Create colored heat / change map
        colored_mask = np.zeros_like(img_arr)
        colored_mask[mask > 0] = bgr_color
        change_map_fn = f"{job_id}_changemap.png"
        change_map_path = RESULTS_DIR / change_map_fn
        cv2.imwrite(str(change_map_path), cv2.cvtColor(colored_mask, cv2.COLOR_RGB2BGR))
        change_map_saved_rel = f"/results/{change_map_fn}"

        # Alpha blend overlay (0.55 image + 0.45 color mask)
        blended = cv2.addWeighted(overlay_arr, 0.65, colored_mask, 0.35, 0)
        overlay_arr = np.where(np.expand_dims(mask > 0, -1), blended, overlay_arr)

    # 2. Draw bounding boxes and labels
    for bbox_item in bboxes:
        ymin, xmin, ymax, xmax = bbox_item["box_2d"]
        pt1 = (int((xmin / 1000.0) * w), int((ymin / 1000.0) * h))
        pt2 = (int((xmax / 1000.0) * w), int((ymax / 1000.0) * h))
        
        cv2.rectangle(overlay_arr, pt1, pt2, bgr_color, 2)
        
        label_text = bbox_item.get("label", "Region")
        # Draw label background tag
        label_size, _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        tag_pt2 = (pt1[0] + label_size[0] + 10, max(0, pt1[1] - label_size[1] - 8))
        cv2.rectangle(overlay_arr, (pt1[0], pt1[1]), tag_pt2, (20, 24, 33), -1)
        cv2.rectangle(overlay_arr, (pt1[0], pt1[1]), tag_pt2, bgr_color, 1)
        cv2.putText(overlay_arr, label_text, (pt1[0] + 5, pt1[1] - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    # Save final composite evidence overlay
    overlay_fn = f"{job_id}_overlay.png"
    overlay_path = RESULTS_DIR / overlay_fn
    cv2.imwrite(str(overlay_path), cv2.cvtColor(overlay_arr, cv2.COLOR_RGB2BGR))
    overlay_saved_rel = f"/results/{overlay_fn}"

    return {
        "overlay_url": overlay_saved_rel,
        "mask_url": mask_saved_rel,
        "change_map_url": change_map_saved_rel,
        "evidence_image_url": overlay_saved_rel,
        "change_percentage": change_percentage,
        "changed_regions_count": regions_count,
        "bboxes": bboxes
    }
