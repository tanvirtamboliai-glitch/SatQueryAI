from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..app.models.geochat_service import GeoChatService

class GeoChatTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="geochat",
            description="Remote-sensing vision-language model for zero-shot VQA, land-cover reasoning, and dense scene description.",
            accepted_modalities=["OPTICAL", "MULTISPECTRAL"],
            capabilities=["vqa", "scene_description", "land_cover_reasoning"],
            input_requirements=["optical_image", "query"],
            output_types=["textual_answer", "scene_summary", "key_concepts"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="6GB"
        )
        super().__init__(defn)
        self.service = GeoChatService()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        image = context.get("optical_pil") or context.get("image1_pil")
        query = context.get("query", "Describe this scene.")
        metadata = context.get("optical_meta") or context.get("image1_meta") or {}

        # Check whether query is dense description or question answering
        is_caption = any(k in query.lower() for k in ["describe", "caption", "overview", "summary", "tell me about"])
        if is_caption:
            cap_res = self.service.generate_caption(image, metadata)
            return {
                "result": {
                    "answer": cap_res["caption"],
                    "key_concepts": cap_res["key_concepts"]
                },
                "evidence": {
                    "textual_evidence": f"Identified dominant land-use patterns: {', '.join(cap_res['key_concepts'])}."
                },
                "confidence": cap_res["confidence"]
            }
        else:
            vqa_res = self.service.answer_vqa(image, query, metadata)
            return {
                "result": {
                    "answer": vqa_res["answer"],
                    "direct_response": vqa_res["answer"]
                },
                "evidence": {
                    "textual_evidence": vqa_res["evidence_text"]
                },
                "confidence": vqa_res["confidence"]
            }
