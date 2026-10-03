from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..app.models.change_service import ChangeService

class ChangeDetectionTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="change_detection",
            description="Bi-temporal remote sensing change detection computing Change Vector Analysis (CVA) differences and Otsu probability masks.",
            accepted_modalities=["TEMPORAL_PAIR"],
            capabilities=["change_detection", "change_mask", "area_quantification"],
            input_requirements=["epoch1_image", "epoch2_image"],
            output_types=["change_mask", "change_percentage", "changed_regions_count", "bboxes"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="4GB"
        )
        super().__init__(defn)
        self.service = ChangeService()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        img1 = context.get("epoch1_pil") or context.get("image1_pil")
        img2 = context.get("epoch2_pil") or context.get("image2_pil")
        metadata = context.get("optical_meta") or context.get("image1_meta") or {}

        chg_res = self.service.detect_change(img1, img2, metadata)
        return {
            "result": {
                "change_percentage": chg_res["change_percentage"],
                "changed_regions_count": chg_res["changed_regions_count"],
                "bboxes": chg_res["bboxes"],
                "regions": chg_res["regions"]
            },
            "evidence": {
                "raw_mask": chg_res["raw_mask"],
                "bboxes": chg_res["bboxes"],
                "change_percentage": chg_res["change_percentage"],
                "changed_regions_count": chg_res["changed_regions_count"],
                "textual_evidence": f"Identified +{chg_res['change_percentage']}% net variation across {chg_res['changed_regions_count']} distinct region(s)."
            },
            "confidence": chg_res["confidence"]
        }
