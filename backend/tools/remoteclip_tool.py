from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..app.models.remoteclip_service import RemoteCLIPService

class RemoteCLIPTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="remoteclip",
            description="Domain-adapted contrastive vision-language model evaluating semantic text-image similarity alignment.",
            accepted_modalities=["OPTICAL"],
            capabilities=["semantic_verification", "image_text_similarity", "zero_shot_retrieval"],
            input_requirements=["optical_image", "query"],
            output_types=["cosine_similarity", "normalized_alignment_score"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="4GB"
        )
        super().__init__(defn)
        self.service = RemoteCLIPService()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        image = context.get("optical_pil") or context.get("image1_pil")
        query = context.get("query", "Earth observation scene")

        clip_res = self.service.compute_similarity(image, query)
        return {
            "result": {
                "cosine_similarity": clip_res["cosine_similarity"],
                "normalized_score": clip_res["normalized_score"]
            },
            "evidence": {
                "textual_evidence": f"RemoteCLIP semantic alignment score: {clip_res['normalized_score']}%."
            },
            "confidence": 0.91
        }
