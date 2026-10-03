import time
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
from PIL import Image

from .query_parser import QueryParser
from .task_planner import TaskPlanner, AgentPlan
from .tool_selector import ToolSelector
from .execution_planner import ExecutionPlanner
from .result_validator import ResultValidator
from .evidence_fusion import EvidenceFusion
from .confidence import TransparentConfidence

from ..app.database.db import get_image_record, save_analysis_job
from ..app.services.evidence import generate_visual_evidence
from ..app.services.report import generate_html_report
from ..preprocessing.metadata import extract_geospatial_metadata

class RemoteSensingAgent:
    """
    Central Agentic Controller implementing:
    USER QUERY -> AGENT PLANNING -> INPUT ANALYSIS -> TOOL SELECTION -> SPECIALIST EXECUTION -> VALIDATION/FUSION -> EVIDENCE -> FINAL ANSWER
    """
    def __init__(self):
        self.parser = QueryParser()
        self.planner = TaskPlanner()
        self.selector = ToolSelector()
        self.executor = ExecutionPlanner()
        self.validator = ResultValidator()
        self.fusion = EvidenceFusion()
        self.confidence_engine = TransparentConfidence()

    def plan_query(
        self,
        query: str,
        image1_id: Any = None,
        image2_id: Optional[str] = None,
        requested_mode: Optional[str] = None,
        inputs_override: Optional[Dict[str, bool]] = None
    ) -> AgentPlan:
        """Constructs and returns machine-readable AgentPlan without executing models."""
        img1_rec = None
        img2_rec = None

        # Handle list of inputs e.g. [{'modality': 'optical'}, ...]
        if isinstance(image1_id, list):
            items = image1_id
            img1_rec = items[0] if len(items) > 0 and isinstance(items[0], dict) else None
            img2_rec = items[1] if len(items) > 1 and isinstance(items[1], dict) else None
        elif isinstance(image1_id, dict):
            img1_rec = image1_id
            if isinstance(image2_id, dict):
                img2_rec = image2_id
            elif isinstance(image2_id, str):
                img2_rec = get_image_record(image2_id)
        elif isinstance(image1_id, str):
            img1_rec = get_image_record(image1_id)
            if image2_id and isinstance(image2_id, str):
                img2_rec = get_image_record(image2_id)

        inputs = {
            "optical": True if img1_rec and img1_rec.get("modality") == "optical" else False,
            "sar": True if (img2_rec and img2_rec.get("modality") == "sar") or (img1_rec and img1_rec.get("modality") == "sar") else False,
            "temporal_pair": True if (img2_rec and img1_rec and img1_rec.get("modality") == img2_rec.get("modality") == "optical") or requested_mode == "bi_temporal" else False
        }
        if inputs_override:
            inputs.update(inputs_override)
        if requested_mode == "optical_sar":
            inputs["optical"] = True
            inputs["sar"] = True
            inputs["temporal_pair"] = False
        elif requested_mode == "bi_temporal":
            inputs["optical"] = True
            inputs["temporal_pair"] = True

        parsed_intent = self.parser.parse(query, inputs)
        meta = img1_rec or {}
        plan = self.planner.plan(query, parsed_intent, inputs, meta)
        return plan

    plan = plan_query

    def execute_workflow(
        self,
        query: str,
        image1_id: str,
        image2_id: Optional[str] = None,
        requested_mode: Optional[str] = None,
        tiling_enabled: bool = False
    ) -> Dict[str, Any]:
        """Full end-to-end agentic workflow execution."""
        start_time = time.time()
        job_id = f"job_{uuid.uuid4().hex[:10]}"

        # 1. Inspect Inputs
        img1_rec = get_image_record(image1_id)
        if not img1_rec:
            raise FileNotFoundError(f"Image ID '{image1_id}' not found in database.")
        img2_rec = get_image_record(image2_id) if image2_id else None

        inputs = {
            "optical": True if img1_rec.get("modality") == "optical" else False,
            "sar": True if (img2_rec and img2_rec.get("modality") == "sar") or img1_rec.get("modality") == "sar" else False,
            "temporal_pair": True if (img2_rec and img1_rec.get("modality") == img2_rec.get("modality") == "optical") or requested_mode == "bi_temporal" else False
        }
        if requested_mode == "optical_sar":
            inputs["optical"] = True
            inputs["sar"] = True
            inputs["temporal_pair"] = False

        # 2. Query Understanding & Agent Planning
        parsed = self.parser.parse(query, inputs)
        plan = self.planner.plan(query, parsed, inputs, img1_rec)

        # 3. Tool Selection
        active_tools = self.selector.select(plan.selected_tools)

        # 4. Prepare Context
        fpath1 = img1_rec["file_path"]
        fpath2 = img2_rec["file_path"] if img2_rec else None

        # Load PIL representations
        pil1 = Image.open(fpath1).convert("RGB")
        pil2 = Image.open(fpath2).convert("RGB") if fpath2 else None

        context: Dict[str, Any] = {
            "query": query,
            "file_path": fpath1,
            "optical_path": fpath1,
            "sar_path": fpath2 if inputs["sar"] else None,
            "epoch1_path": fpath1,
            "epoch2_path": fpath2,
            "image1_path": fpath1,
            "image2_path": fpath2,
            "image1_pil": pil1,
            "image2_pil": pil2,
            "optical_pil": pil1,
            "sar_pil": pil2 if inputs["sar"] else None,
            "epoch1_pil": pil1,
            "epoch2_pil": pil2,
            "optical_meta": img1_rec,
            "sar_meta": img2_rec or {},
            "image1_meta": img1_rec,
            "image2_meta": img2_rec or {},
            "tiling_enabled": tiling_enabled
        }

        # 5. Execution Planning & Tool Running
        exec_out = self.executor.execute_plan(plan, active_tools, context)
        trace = exec_out["trace"]
        tool_results = exec_out["tool_results"]
        final_context = exec_out["final_context"]

        # 6. Result Validation
        validation_report = self.validator.validate(plan.intent, tool_results, final_context)

        # 7. Cross-Tool Evidence Fusion
        fused_evidence = self.fusion.fuse(plan.intent, tool_results, final_context, validation_report)

        # 8. Visual Evidence Raster Synthesis
        evidence_color = "red" if plan.intent in ["CHANGE_DETECTION", "CHANGE_VQA"] else ("cyan" if "water" in query.lower() else "amber")
        evidence_data = generate_visual_evidence(
            base_image=pil1,
            job_id=job_id,
            bboxes=fused_evidence["bboxes"],
            mask=fused_evidence["raw_mask"],
            color=evidence_color,
            change_percentage=fused_evidence["change_percentage"],
            regions_count=fused_evidence["changed_regions_count"]
        )
        evidence_data["regions"] = fused_evidence["regions"]
        evidence_data["textual_evidence"] = fused_evidence["textual_evidence"]

        # 9. Multi-Factor Transparent Confidence
        has_spatial = bool(fused_evidence["bboxes"] or (fused_evidence["raw_mask"] is not None))
        conf_breakdown = self.confidence_engine.estimate(tool_results, validation_report, has_spatial)

        total_latency = (time.time() - start_time) * 1000.0

        # Construct Analysis Result Payload
        result = {
            "job_id": job_id,
            "query": query,
            "detected_task": plan.intent,
            "workflow": "optical_sar" if inputs["optical"] and inputs["sar"] else ("bi_temporal" if inputs["temporal_pair"] else "single"),
            "selected_models": [t.definition.name for t in active_tools],
            "model_selection_rationale": plan.reasoning_summary,
            "agent_plan": plan.to_dict(),
            "answer": fused_evidence["answer"],
            "evidence": evidence_data,
            "multimodal_evidence": fused_evidence.get("multimodal_evidence"),
            "confidence": conf_breakdown,
            "execution_trace": trace,
            "total_execution_time_ms": round(total_latency, 1),
            "warnings": validation_report.get("warnings", []),
            "report_url": "",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Generate HTML report
        report_url = generate_html_report(result)
        result["report_url"] = report_url

        save_analysis_job(result)
        return result
