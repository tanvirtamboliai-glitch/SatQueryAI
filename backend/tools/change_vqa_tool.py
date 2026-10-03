from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..app.models.change_vqa_service import ChangeVQAService

class ChangeVQATool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="change_vqa",
            description="Specialized vision-language temporal reasoning answering questions regarding temporal land-use increase, decrease, and dynamics.",
            accepted_modalities=["TEMPORAL_PAIR"],
            capabilities=["change_vqa", "directional_reasoning", "quantification"],
            input_requirements=["epoch1_image", "epoch2_image", "query", "change_result"],
            output_types=["directional_answer", "change_metrics"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="4GB"
        )
        super().__init__(defn)
        self.service = ChangeVQAService()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        img1 = context.get("epoch1_pil") or context.get("image1_pil")
        img2 = context.get("epoch2_pil") or context.get("image2_pil")
        query = context.get("query", "What changed?")
        chg_data = context.get("change_result") or {}
        metadata = context.get("optical_meta") or context.get("image1_meta") or {}

        vqa_res = self.service.answer_change_query(img1, img2, query, chg_data, metadata)
        return {
            "result": {
                "answer": vqa_res["answer"]
            },
            "evidence": {
                "textual_evidence": vqa_res["evidence_text"]
            },
            "confidence": vqa_res["confidence"]
        }
