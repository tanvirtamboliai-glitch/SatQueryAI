from typing import Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class SkippedTool:
    tool: str
    reason: str

@dataclass
class AgentPlan:
    intent: str
    reasoning_summary: str
    required_modalities: List[str]
    selected_tools: List[str]
    skipped_tools: List[Dict[str, str]]
    execution_steps: List[str]
    expected_outputs: List[str]
    validation_rules: List[str]
    fallback_tools: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "reasoning_summary": self.reasoning_summary,
            "required_modalities": self.required_modalities,
            "selected_tools": self.selected_tools,
            "skipped_tools": self.skipped_tools,
            "execution_steps": self.execution_steps,
            "expected_outputs": self.expected_outputs,
            "validation_rules": self.validation_rules,
            "fallback_tools": self.fallback_tools
        }

class TaskPlanner:
    """
    Autonomous planning engine that constructs an operational AgentPlan,
    deciding which specialist tools are required, their execution sequence,
    and explicitly which tools are omitted with technical justifications.
    """
    def plan(
        self,
        query: str,
        parsed_intent: Dict[str, Any],
        inputs: Dict[str, bool],
        metadata: Dict[str, Any]
    ) -> AgentPlan:
        intent = parsed_intent["intent"]
        has_optical = inputs.get("optical", False)
        has_sar = inputs.get("sar", False)
        has_temporal = inputs.get("temporal_pair", False)

        selected_tools: List[str] = []
        skipped_tools: List[Dict[str, str]] = []
        execution_steps: List[str] = []
        expected_outputs: List[str] = []
        validation_rules: List[str] = []

        # 1. OPTICAL + SAR FUSION
        if intent == "OPTICAL_SAR_FUSION" or (has_optical and has_sar and not has_temporal):
            reasoning = "Query requires cross-sensor multimodal feature fusion combining optical multi-spectral reflectance with SAR microwave backscatter to resolve surface footprints and shadow penetration."
            required_modalities = ["OPTICAL", "SAR"]
            selected_tools = [
                "geospatial",
                "optical_analysis",
                "sar_analysis",
                "multimodal_alignment",
                "multimodal_fusion",
                "clay",
                "segmentation"
            ]
            skipped_tools = [
                {"tool": "change_detection", "reason": "Bi-temporal second epoch not provided or requested."},
                {"tool": "change_vqa", "reason": "Temporal dynamic reasoning inapplicable to single-timestamp fusion."},
                {"tool": "geoground", "reason": "Spatial referring expression was not requested; joint land-cover partitioning required."}
            ]
            execution_steps = [
                "1. Inspect and validate geospatial metadata & CRS projection for both sensors",
                "2. Preprocess optical reflectance and compute spectral NDVI/NDWI indices",
                "3. Preprocess SAR radar amplitudes, convert to calibrated dB scale, and apply despeckle filtering",
                "4. Coregister and align spatial grids, checking overlap percentage and CRS match",
                "5. Extract deep multisensor foundation embeddings via Clay",
                "6. Execute intermediate latent feature fusion projection",
                "7. Compute fused land-cover classification and synthesize cross-modal evidence"
            ]
            expected_outputs = ["fused_landcover_distribution", "optical_evidence", "sar_evidence", "joint_explanation"]
            validation_rules = [
                "Verify spatial overlap > 50% between Optical and SAR rasters",
                "Ensure SAR double-bounce metrics confirm urban structures in optical shadows",
                "Cross-check optical NDWI with SAR specular low backscatter (< -16 dB)"
            ]

        # 2. BI-TEMPORAL CHANGE DETECTION / VQA
        elif intent in ["CHANGE_DETECTION", "CHANGE_VQA", "CHANGE_DESCRIPTION"] or has_temporal:
            reasoning = f"Bi-temporal scene pair identified. Orchestrating Siamese difference modeling, Change Vector Analysis (CVA), and Otsu thresholding for temporal surface dynamic analysis ({intent})."
            required_modalities = ["TEMPORAL_PAIR"]
            selected_tools = [
                "geospatial",
                "optical_analysis",
                "multimodal_alignment",
                "change_detection",
                "change_captioning",
                "change_vqa"
            ]
            skipped_tools = [
                {"tool": "sar_analysis", "reason": "No SAR microwave sensor uploaded; optical bi-temporal pair provided."},
                {"tool": "multimodal_fusion", "reason": "Cross-sensor optical-SAR fusion omitted for dual-epoch optical change."},
                {"tool": "geoground", "reason": "Temporal change polygons extracted via CVA difference rather than referring expression."}
            ]
            execution_steps = [
                "1. Inspect baseline Epoch T1 and comparison Epoch T2 metadata",
                "2. Align pixel grids and calibrate radiometric normalization between dates",
                "3. Compute Siamese feature difference and Change Vector Analysis (CVA)",
                "4. Apply Otsu morphological segmentation to isolate changed polygons",
                "5. Calculate net modified surface percentage and extract bounding regions",
                "6. Generate non-hallucinated grounded change description & answer temporal VQA"
            ]
            expected_outputs = ["change_percentage", "changed_regions_count", "change_mask", "temporal_answer"]
            validation_rules = [
                "Verify spatial overlap >= 75% across epochs",
                "Ensure change description strictly references detected change polygons without hallucinating absent variations"
            ]

        # 3. SPATIAL GROUNDING / LOCALIZATION
        elif intent in ["GROUNDING", "WATER_DETECTION", "BUILT_UP_ANALYSIS"]:
            target = parsed_intent.get("target_entity", "geographic entity")
            reasoning = f"Query contains spatial referring expressions targeting '{target}'. Orchestrating GeoGround-v1.2 for text-guided contour and bounding box extraction, validated by GeoChat."
            required_modalities = ["OPTICAL"]
            selected_tools = [
                "geospatial",
                "optical_analysis",
                "geoground",
                "geochat",
                "segmentation"
            ]
            skipped_tools = [
                {"tool": "change_detection", "reason": "Single scene provided; temporal change analysis omitted."},
                {"tool": "sar_analysis", "reason": "SAR microwave backscatter not provided for optical grounding query."},
                {"tool": "multimodal_fusion", "reason": "Single optical sensor sufficient for spatial referring expression."}
            ]
            execution_steps = [
                "1. Inspect GeoTIFF CRS and calibrate optical 3-band radiometric profile",
                "2. Execute GeoGround text-guided segmentation for referred spatial entity",
                "3. Extract normalized [ymin, xmin, ymax, xmax] coordinates and polygon masks",
                "4. Validate detected regions using GeoChat vision-language reasoning",
                "5. Synthesize visual evidence overlay with spatial bounding tags"
            ]
            expected_outputs = ["bounding_boxes", "segmentation_mask", "spatial_answer"]
            validation_rules = [
                "Ensure at least one bounding instance is grounded if entity is present",
                "Check that GeoChat visual claims are supported by non-empty GeoGround bounding boxes"
            ]

        # 4. SINGLE-IMAGE VQA / DENSE SCENE DESCRIPTION
        else:
            reasoning = "Single optical scene inspected. Orchestrating GeoChat-7B for zero-shot remote-sensing vision-language question answering, supplemented by RemoteCLIP semantic verification."
            required_modalities = ["OPTICAL"]
            selected_tools = [
                "geospatial",
                "optical_analysis",
                "geochat",
                "remoteclip",
                "segmentation"
            ]
            skipped_tools = [
                {"tool": "change_detection", "reason": "Single observation provided; temporal difference inapplicable."},
                {"tool": "sar_analysis", "reason": "No SAR sensor input available or requested."},
                {"tool": "multimodal_fusion", "reason": "Optical multi-spectral imagery sufficient for radiometric VQA."}
            ]
            execution_steps = [
                "1. Inspect raster CRS and radiometric band distribution",
                "2. Preprocess multi-band reflectance and percentile-normalize pixels",
                "3. Compute RemoteCLIP domain-adapted semantic alignment score",
                "4. Execute GeoChat-7B vision-language instruction inference",
                "5. Segment dominant land-cover classes and synthesize grounded answer"
            ]
            expected_outputs = ["direct_answer", "land_cover_breakdown", "semantic_score"]
            validation_rules = [
                "Verify answer consistency against extracted spectral indices",
                "Ensure confidence score reflects model certainty and input quality"
            ]

        return AgentPlan(
            intent=intent,
            reasoning_summary=reasoning,
            required_modalities=required_modalities,
            selected_tools=selected_tools,
            skipped_tools=skipped_tools,
            execution_steps=execution_steps,
            expected_outputs=expected_outputs,
            validation_rules=validation_rules
        )
