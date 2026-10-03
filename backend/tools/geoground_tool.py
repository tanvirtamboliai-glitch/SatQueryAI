from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..app.models.geoground_service import GeoGroundService

class GeoGroundTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="geoground",
            description="Language-guided spatial grounding model localizing referred geographic entities into bounding coordinates and masks.",
            accepted_modalities=["OPTICAL", "MULTISPECTRAL"],
            capabilities=["grounding", "object_localization", "bounding_box_extraction"],
            input_requirements=["optical_image", "spatial_query"],
            output_types=["bboxes", "raw_mask", "regions"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="4GB"
        )
        super().__init__(defn)
        self.service = GeoGroundService()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        image = context.get("optical_pil") or context.get("image1_pil")
        query = context.get("query", "Highlight target")
        metadata = context.get("optical_meta") or context.get("image1_meta") or {}

        ground_res = self.service.ground(image, query, metadata)
        bboxes = ground_res.get("bboxes", [])
        return {
            "result": {
                "bboxes": bboxes,
                "regions": ground_res.get("regions", []),
                "entity_label": ground_res.get("label", "detected_entity"),
                "detected_count": len(bboxes)
            },
            "evidence": {
                "raw_mask": ground_res.get("raw_mask"),
                "bboxes": bboxes,
                "textual_evidence": f"Demarcated {len(bboxes)} spatial instance(s) matching '{query}'."
            },
            "confidence": ground_res.get("confidence", 0.92)
        }
