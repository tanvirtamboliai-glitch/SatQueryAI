import time
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path
from PIL import Image
import numpy as np

from ..schemas.schemas import AnalysisResult, VisualEvidence, ConfidenceBreakdown, TraceStep
from ..database.db import get_image_record, save_analysis_job
from .input_validator import inspect_image, validate_image_pair
from .preprocessing import load_and_preprocess_image, align_pair
from .model_registry import MODEL_REGISTRY
from .confidence import compute_aggregated_confidence
from .evidence import generate_visual_evidence
from .report import generate_html_report

from ..models.geochat_service import GeoChatService
from ..models.geoground_service import GeoGroundService
from ..models.change_service import ChangeService
from ..models.change_vqa_service import ChangeVQAService
from ..models.clay_service import ClayService
from ..models.prithvi_service import PrithviService
from ..models.remoteclip_service import RemoteCLIPService

class AgentController:
    """
    Central Agentic Controller orchestrating a 3-layer hybrid routing architecture
    and controlled remote sensing specialist tool execution.
    """
    def __init__(self):
        self.geochat = GeoChatService()
        self.geoground = GeoGroundService()
        self.change_service = ChangeService()
        self.change_vqa = ChangeVQAService()
        self.clay = ClayService()
        self.prithvi = PrithviService()
        self.remoteclip = RemoteCLIPService()

    def _classify_query_intent(self, query: str, config_mode: str) -> str:
        """
        Layer 2: Natural-Language Intent Classification.
        Determines semantic intent among VQA, captioning, grounding, change detection,
        change VQA, or optical-SAR analysis.
        """
        q = query.lower()

        # Bi-temporal inquiries
        if config_mode == "bi_temporal":
            if any(k in q for k in ["has ", "did ", "is there ", "increased", "decreased", "where did", "why", "how much"]):
                return "change_vqa"
            elif any(k in q for k in ["what changed", "detect change", "difference", "compare", "variation"]):
                return "change_detection"
            return "change_vqa"

        # Optical + SAR inquiries
        if config_mode == "optical_sar":
            return "optical_sar"

        # Single image inquiries
        if any(k in q for k in ["highlight", "where is", "locate", "ground", "find the", "localize", "demarcate", "show me"]):
            return "grounding"
        if any(k in q for k in ["describe", "caption", "summary", "overview", "scene description", "tell me about"]):
            return "captioning"
        if any(k in q for k in ["similar", "retrieve", "rank", "match"]):
            return "retrieval"
        
        return "vqa"

    def execute_workflow(
        self,
        query: str,
        image1_id: str,
        image2_id: Optional[str] = None,
        requested_mode: Optional[str] = None,
        tiling_enabled: bool = False
    ) -> Dict[str, Any]:
        """
        Executes full end-to-end agentic workflow with observable execution traces,
        specialist models, visual evidence, and confidence aggregation.
        """
        start_time = time.time()
        job_id = f"job_{uuid.uuid4().hex[:10]}"
        trace: List[Dict[str, Any]] = []
        step_num = 1
        warnings: List[str] = []

        def log_step(name: str, details: str, s_time: float, status: str = "completed"):
            nonlocal step_num
            duration = (time.time() - s_time) * 1000.0
            trace.append({
                "step_number": step_num,
                "name": name,
                "status": status,
                "details": details,
                "duration_ms": round(duration, 1),
                "timestamp": time.strftime("%H:%M:%S")
            })
            step_num += 1

        # STAGE 1: Input Validation
        t0 = time.time()
        img1_rec = get_image_record(image1_id)
        if not img1_rec:
            raise FileNotFoundError(f"Image ID '{image1_id}' not found in database.")

        img2_rec = get_image_record(image2_id) if image2_id else None

        # Determine configuration mode (Layer 1: Input-based routing)
        if img2_rec:
            pair_val = validate_image_pair(img1_rec, img2_rec)
            if not pair_val["valid"]:
                raise ValueError(f"Pair validation failure: {pair_val['reason']}")
            warnings.extend(pair_val.get("warnings", []))
            config_mode = pair_val["pair_type"]
            input_desc = f"2 GeoTIFFs | Modality: {img1_rec['modality']} + {img2_rec['modality']} | Overlap: {pair_val['spatial_overlap_pct']}%"
        else:
            config_mode = "single"
            input_desc = f"1 Image | Modality: {img1_rec['modality']} | Dimensions: {img1_rec['width']}x{img1_rec['height']} | CRS: {img1_rec.get('crs') or 'EPSG:4326'}"

        log_step("Input Validation & Inspection", f"Validated: {input_desc}", t0)

        # STAGE 2: Query Classification & Routing (Layer 2)
        t0 = time.time()
        task = self._classify_query_intent(query, config_mode)
        log_step("3-Layer Query Routing", f"Determined Task: '{task}' via Intent Classifier (Configuration: {config_mode})", t0)

        # STAGE 3: Specialist Model Selection
        t0 = time.time()
        selected_models = []
        selection_rationale = ""
        if task == "vqa":
            selected_models = ["GeoChat"]
            selection_rationale = f"Single scene ({img1_rec['modality'].upper()}) inspected. Query requires radiometric scene understanding and land-cover classification. The Agent routed to GeoChat-7B for zero-shot remote-sensing vision-language question answering."
        elif task == "captioning":
            selected_models = ["GeoChat"]
            selection_rationale = f"Single scene ({img1_rec['modality'].upper()}) inspected. Query requests dense scene summary. The Agent assigned GeoChat-7B to extract dominant land-use patterns, structural densities, and surface canopy characteristics."
        elif task == "grounding":
            selected_models = ["GeoGround", "GeoChat"]
            selection_rationale = f"Query contains spatial referring expressions requesting localized demarcation. The Agent orchestrated GeoGround-v1.2 for text-guided contour and bounding coordinate extraction, coupled with GeoChat for contextual label validation."
        elif task == "change_detection":
            selected_models = ["Change-Agent"]
            selection_rationale = f"Bi-temporal image pair validated across epochs. The Agent selected Change-Agent-v2.0 (Siamese difference & Change Vector Analysis) to compute pixel-level probability distributions and Otsu morphological change masks."
        elif task == "change_vqa":
            selected_models = ["Change-Agent", "ChangeChat"]
            selection_rationale = f"Bi-temporal image pair validated. Query demands temporal directional reasoning regarding surface modification. The Agent orchestrated Change-Agent (for spatial change mask extraction) and ChangeChat (for quantitative temporal question answering)."
        elif task == "optical_sar":
            selected_models = ["Clay", "Prithvi-EO-2.0"]
            selection_rationale = f"Co-registered Optical ({img1_rec['modality']}) + SAR ({img2_rec['modality'] if img2_rec else 'sar'}) pair detected. The Agent selected Clay Foundation Model + Prithvi-EO-2.0 to execute intermediate latent feature fusion, leveraging SAR microwave backscatter to penetrate optical shadows and resolve double-bounce structural footprints."
        elif task == "retrieval":
            selected_models = ["RemoteCLIP"]
            selection_rationale = f"Semantic retrieval query identified. The Agent assigned RemoteCLIP for domain-adapted contrastive image-text cosine similarity alignment."

        log_step("Autonomous Model Selection", f"Orchestrated Specialist Models: {', '.join(selected_models)} | Rationale: {selection_rationale}", t0)

        # STAGE 4: Remote Sensing Preprocessing
        t0 = time.time()
        raw1, pil1, _ = load_and_preprocess_image(img1_rec["file_path"])
        pil2 = None
        if img2_rec:
            raw2, pil2, _ = load_and_preprocess_image(img2_rec["file_path"])
            raw1, raw2 = align_pair(raw1, raw2)
            pil1 = Image.fromarray(raw1)
            pil2 = Image.fromarray(raw2)
            prep_desc = f"Aligned scenes to {raw1.shape[1]}x{raw1.shape[0]}, calibrated radiometric normalization."
        else:
            prep_desc = f"Extracted 3-band radiometric profile ({raw1.shape[1]}x{raw1.shape[0]}), percentile-clipped."
        
        log_step("Remote Sensing Preprocessing", prep_desc, t0)

        # STAGE 5: Specialist Execution & Evidence Generation
        t0 = time.time()
        answer = ""
        textual_evidence = ""
        raw_mask = None
        bboxes = []
        regions = []
        change_pct = None
        regions_count = None
        model_conf = 0.91

        if task == "vqa":
            vqa_res = self.geochat.answer_vqa(pil1, query, img1_rec)
            answer = vqa_res["answer"]
            textual_evidence = vqa_res["evidence_text"]
            model_conf = vqa_res["confidence"]

        elif task == "captioning":
            cap_res = self.geochat.generate_caption(pil1, img1_rec)
            answer = cap_res["caption"]
            textual_evidence = f"Identified concepts: {', '.join(cap_res['key_concepts'])}."
            model_conf = cap_res["confidence"]

        elif task == "grounding":
            ground_res = self.geoground.ground(pil1, query, metadata=img1_rec)
            bboxes = ground_res["bboxes"]
            regions = ground_res["regions"]
            raw_mask = ground_res["raw_mask"]
            answer = f"Successfully localized {len(bboxes)} spatial instance(s) matching '{query}' with high precision bounding coordinates."
            textual_evidence = f"Identified target entity '{ground_res['label']}' with {len(bboxes)} demarcated boundaries."
            model_conf = ground_res["confidence"]

        elif task in ["change_detection", "change_vqa"]:
            chg_res = self.change_service.detect_change(pil1, pil2, img1_rec)
            raw_mask = chg_res["raw_mask"]
            bboxes = chg_res["bboxes"]
            regions = chg_res["regions"]
            change_pct = chg_res["change_percentage"]
            regions_count = chg_res["changed_regions_count"]

            if task == "change_vqa":
                vqa_chg = self.change_vqa.answer_change_query(pil1, pil2, query, chg_res, img1_rec)
                answer = vqa_chg["answer"]
                textual_evidence = vqa_chg["evidence_text"]
                model_conf = vqa_chg["confidence"]
            else:
                answer = chg_res["description"]
                textual_evidence = f"CVA and Siamese difference extraction revealed +{change_pct}% surface modification across {regions_count} regions."
                model_conf = chg_res["confidence"]

        elif task == "optical_sar":
            opt_sar_res = self.clay.analyze_optical_sar_pair(pil1, pil2, query, img1_rec)
            answer = opt_sar_res["answer"]
            textual_evidence = opt_sar_res["evidence_text"]
            model_conf = opt_sar_res["confidence"]

        elif task == "retrieval":
            ret_res = self.remoteclip.compute_similarity(pil1, query)
            answer = f"Semantic similarity score between scene and '{query}' is {ret_res['cosine_similarity']} ({ret_res['normalized_score']}% alignment)."
            textual_evidence = "RemoteCLIP contrastive vision-language representation alignment."
            model_conf = 0.90

        log_step(f"Specialist Execution ({selected_models[0]})", f"Generated grounded output and raw spatial features", t0)

        # STAGE 6: Visual Evidence Extraction
        t0 = time.time()
        evidence_color = "red" if task in ["change_detection", "change_vqa"] else ("cyan" if "water" in query.lower() else "amber")
        evidence_data = generate_visual_evidence(
            base_image=pil1,
            job_id=job_id,
            bboxes=bboxes,
            mask=raw_mask,
            color=evidence_color,
            change_percentage=change_pct,
            regions_count=regions_count
        )
        evidence_data["regions"] = regions
        evidence_data["textual_evidence"] = textual_evidence

        log_step("Evidence Grounding & Overlay", f"Synthesized spatial overlay, {len(bboxes)} bounding tags, and high-res evidence raster", t0)

        # STAGE 7: Multi-Factor Calibrated Confidence
        t0 = time.time()
        has_spatial = bool(bboxes or (raw_mask is not None))
        conf_breakdown = compute_aggregated_confidence(
            model_conf=model_conf,
            input_compatibility=1.00 if not warnings else 0.90,
            evidence_strength=0.94 if has_spatial else 0.85,
            answer_consistency=0.93,
            has_mask_or_bbox=has_spatial
        )
        log_step("Confidence Calibration", f"Computed composite confidence: {int(conf_breakdown['final_confidence']*100)}% ({conf_breakdown['confidence_level']})", t0)

        total_latency = (time.time() - start_time) * 1000.0

        # Construct Final Result Object
        final_result = {
            "job_id": job_id,
            "query": query,
            "detected_task": task.upper(),
            "workflow": config_mode,
            "selected_models": selected_models,
            "model_selection_rationale": selection_rationale,
            "answer": answer,
            "evidence": evidence_data,
            "confidence": conf_breakdown,
            "execution_trace": trace,
            "total_execution_time_ms": round(total_latency, 1),
            "warnings": warnings,
            "report_url": "",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Generate HTML report
        report_url = generate_html_report(final_result)
        final_result["report_url"] = report_url

        # Save to SQLite DB
        save_analysis_job(final_result)

        return final_result
