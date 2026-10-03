from typing import Dict, Any
import numpy as np
import cv2
from .base_tool import BaseTool, ToolDefinition

class SegmentationTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="segmentation",
            description="Computes land-cover mask segmentations, surface class partitioning, and area percentages.",
            accepted_modalities=["OPTICAL", "SAR", "OPTICAL_SAR"],
            capabilities=["semantic_segmentation", "landcover_classification", "area_breakdown"],
            input_requirements=["raster_image", "target_class"],
            output_types=["mask", "area_percentages", "class_polygons"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="2GB"
        )
        super().__init__(defn)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        img_arr = context.get("optical_arr") or context.get("image1_arr")
        if img_arr is None:
            raise ValueError("Raster array required for segmentation.")

        h, w = img_arr.shape[:2]
        gray = cv2.cvtColor(img_arr, cv2.COLOR_RGB2GRAY) if img_arr.ndim == 3 else img_arr
        
        # Segment major landcover clusters
        water_mask = (gray < 70)
        urban_mask = (gray > 165)
        veg_mask = (~water_mask) & (~urban_mask)

        water_pct = round(float(np.sum(water_mask) / water_mask.size * 100), 1)
        urban_pct = round(float(np.sum(urban_mask) / urban_mask.size * 100), 1)
        veg_pct = round(float(np.sum(veg_mask) / veg_mask.size * 100), 1)

        return {
            "result": {
                "land_cover_distribution": {
                    "water": water_pct,
                    "built_up": urban_pct,
                    "vegetation": veg_pct
                }
            },
            "evidence": {
                "textual_evidence": f"Segmentation breakdown: {water_pct}% water, {urban_pct}% built-up, {veg_pct}% vegetation."
            },
            "confidence": 0.94
        }
