from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..preprocessing.alignment import align_multimodal_rasters

class MultimodalAlignmentTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="multimodal_alignment",
            description="Verifies spatial extent overlap, CRS projection compatibility, and co-registers optical + SAR imagery.",
            accepted_modalities=["OPTICAL_SAR", "TEMPORAL_PAIR"],
            capabilities=["spatial_coregistration", "crs_verification", "overlap_validation"],
            input_requirements=["raster1", "raster2", "meta1", "meta2"],
            output_types=["aligned_raster1", "aligned_raster2", "alignment_report"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="2GB"
        )
        super().__init__(defn)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        arr1 = context.get("optical_arr") or context.get("image1_arr")
        arr2 = context.get("sar_arr") or context.get("image2_arr")
        meta1 = context.get("optical_meta") or context.get("image1_meta") or {}
        meta2 = context.get("sar_meta") or context.get("image2_meta") or {}

        if arr1 is None or arr2 is None:
            raise ValueError("Both rasters required for multimodal alignment.")

        aligned1, aligned2, report = align_multimodal_rasters(arr1, arr2, meta1, meta2)
        return {
            "result": report,
            "evidence": {
                "aligned_arr1": aligned1,
                "aligned_arr2": aligned2,
                "textual_evidence": f"Spatial coregistration completed: {report['spatial_overlap_pct']}% geographic overlap, CRS match: {report['crs_match']}."
            },
            "confidence": 1.0 if report["spatial_overlap_pct"] > 50 else 0.80
        }
