import re
from typing import Dict, Any, List, Optional

class QueryParser:
    """
    Parses natural language remote-sensing queries into structured intent,
    target geographic entities, and analysis modalities.
    """
    INTENTS = [
        "VQA",
        "SCENE_DESCRIPTION",
        "OBJECT_DETECTION",
        "GROUNDING",
        "LAND_COVER_ANALYSIS",
        "WATER_DETECTION",
        "BUILT_UP_ANALYSIS",
        "OPTICAL_SAR_FUSION",
        "CHANGE_DETECTION",
        "CHANGE_DESCRIPTION",
        "CHANGE_VQA",
        "QUANTIFICATION",
        "COMPARISON"
    ]

    def parse(self, query: str, inputs: Dict[str, bool]) -> Dict[str, Any]:
        q = query.lower().strip()

        # 1. Check for explicit cross-modal fusion
        if inputs.get("sar") and inputs.get("optical"):
            if any(k in q for k in ["both", "together", "fusion", "optical and sar", "sar and optical", "microwave", "penetrate", "structural"]):
                return {
                    "intent": "OPTICAL_SAR_FUSION",
                    "target_entity": self._extract_entities(q),
                    "is_multimodal": True,
                    "is_temporal": False,
                    "modality_required": "OPTICAL_SAR"
                }

        # 2. Check for bi-temporal change analysis
        if inputs.get("temporal_pair"):
            if any(k in q for k in ["has ", "did ", "is there ", "increased", "decreased", "where did", "how much"]):
                return {
                    "intent": "CHANGE_VQA",
                    "target_entity": self._extract_entities(q),
                    "is_multimodal": False,
                    "is_temporal": True,
                    "modality_required": "TEMPORAL_PAIR"
                }
            elif any(k in q for k in ["describe change", "tell me what changed", "change summary"]):
                return {
                    "intent": "CHANGE_DESCRIPTION",
                    "target_entity": self._extract_entities(q),
                    "is_multimodal": False,
                    "is_temporal": True,
                    "modality_required": "TEMPORAL_PAIR"
                }
            else:
                return {
                    "intent": "CHANGE_DETECTION",
                    "target_entity": self._extract_entities(q),
                    "is_multimodal": False,
                    "is_temporal": True,
                    "modality_required": "TEMPORAL_PAIR"
                }

        # 3. Spatial referring expression / Grounding
        if any(k in q for k in ["where", "find", "locate", "highlight", "localize", "demarcate", "show me", "outline", "box"]):
            return {
                "intent": "GROUNDING",
                "target_entity": self._extract_entities(q),
                "is_multimodal": False,
                "is_temporal": False,
                "modality_required": "OPTICAL"
            }

        # 4. Dense scene captioning / description
        if any(k in q for k in ["describe", "caption", "overview", "summary", "tell me about", "scene description"]):
            return {
                "intent": "SCENE_DESCRIPTION",
                "target_entity": "scene",
                "is_multimodal": False,
                "is_temporal": False,
                "modality_required": "OPTICAL"
            }

        # 5. Land cover / water / built-up analysis
        if any(k in q for k in ["water", "river", "lake", "ocean", "wetland"]):
            return {
                "intent": "WATER_DETECTION",
                "target_entity": "water body",
                "is_multimodal": False,
                "is_temporal": False,
                "modality_required": "OPTICAL"
            }
            
        if any(k in q for k in ["building", "built-up", "urban", "settlement", "construction", "roof"]):
            return {
                "intent": "BUILT_UP_ANALYSIS",
                "target_entity": "built-up region",
                "is_multimodal": False,
                "is_temporal": False,
                "modality_required": "OPTICAL"
            }

        if any(k in q for k in ["land cover", "classes", "partition", "segment", "distribution"]):
            return {
                "intent": "LAND_COVER_ANALYSIS",
                "target_entity": "land cover",
                "is_multimodal": False,
                "is_temporal": False,
                "modality_required": "OPTICAL"
            }

        # 6. Default Remote Sensing Visual Question Answering
        return {
            "intent": "VQA",
            "target_entity": self._extract_entities(q),
            "is_multimodal": False,
            "is_temporal": False,
            "modality_required": "OPTICAL"
        }

    def _extract_entities(self, query: str) -> str:
        tokens = ["water body", "river", "lake", "buildings", "built-up area", "vegetation", "agricultural field", "forest", "roads", "airport", "industrial area"]
        for t in tokens:
            if t in query:
                return t
        return "geographic feature"
