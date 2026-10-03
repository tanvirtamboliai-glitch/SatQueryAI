from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ImageMetadata(BaseModel):
    file_id: str
    filename: str
    format: str
    dimensions: List[int] = Field(description="[width, height]")
    bands: int
    crs: Optional[str] = None
    geotransform: Optional[List[float]] = None
    bounds: Optional[List[float]] = Field(default=None, description="[minx, miny, maxx, maxy]")
    resolution: Optional[List[float]] = None
    modality: str = Field(default="optical", description="optical, sar, multispectral")
    acquisition_date: Optional[str] = None
    sensor: Optional[str] = None
    is_valid: bool = True
    warnings: List[str] = []
    preview_url: Optional[str] = None

class PairValidationResult(BaseModel):
    valid: bool
    pair_type: str = Field(description="bi_temporal, optical_sar, or incompatible")
    spatial_overlap_pct: float
    crs_match: bool
    resolution_ratio: float
    warnings: List[str] = []
    reason: Optional[str] = None

class ValidationResponse(BaseModel):
    valid: bool
    detected_mode: str = Field(description="single, bi_temporal, optical_sar, invalid")
    image1: ImageMetadata
    image2: Optional[ImageMetadata] = None
    pair_validation: Optional[PairValidationResult] = None
    suggested_workflow: str
    warnings: List[str] = []

class QueryRequest(BaseModel):
    query: str
    image1_id: str
    image2_id: Optional[str] = None
    mode: Optional[str] = None  # auto, single, bi_temporal, optical_sar
    tiling_enabled: Optional[bool] = False
    tile_size: Optional[int] = 512

class BoundingBox(BaseModel):
    box_2d: List[float] = Field(description="[ymin, xmin, ymax, xmax] normalized 0..1000")
    label: str
    confidence: float

class RegionEvidence(BaseModel):
    region_id: int
    label: str
    change_type: Optional[str] = None
    area_pct: float
    bbox: List[float] = Field(description="[ymin, xmin, ymax, xmax]")
    coordinates_geo: Optional[Dict[str, Any]] = None

class VisualEvidence(BaseModel):
    overlay_url: Optional[str] = None
    change_map_url: Optional[str] = None
    mask_url: Optional[str] = None
    evidence_image_url: Optional[str] = None
    change_percentage: Optional[float] = None
    changed_regions_count: Optional[int] = None
    bboxes: List[BoundingBox] = []
    regions: List[RegionEvidence] = []
    textual_evidence: str

class ConfidenceBreakdown(BaseModel):
    model_confidence: float
    input_compatibility: float
    evidence_strength: float
    answer_consistency: float
    final_confidence: float
    confidence_level: str = "High confidence"
    calibration_status: str = "Calibrated multi-factor score"

class TraceStep(BaseModel):
    step_number: int
    name: str
    status: str = "completed"  # completed, in_progress, warning, failed
    details: str
    duration_ms: float
    timestamp: str

class PlanRequest(BaseModel):
    query: str
    image1_id: Optional[str] = None
    image2_id: Optional[str] = None
    mode: Optional[str] = None

class SkippedTool(BaseModel):
    tool: str
    reason: str

class AgentPlanResponse(BaseModel):
    query: Optional[str] = None
    intent: str
    reasoning_summary: str
    required_modalities: List[str] = []
    selected_tools: List[str] = []
    execution_order: Optional[List[str]] = None
    execution_steps: Optional[List[str]] = None
    skipped_tools: List[Dict[str, Any]] = []
    expected_outputs: Optional[List[str]] = None
    validation_rules: Optional[List[str]] = None
    fallback_tools: Optional[List[str]] = None
    estimated_latency_ms: Optional[float] = 350.0

class MultimodalEvidenceSchema(BaseModel):
    optical: Optional[Dict[str, Any]] = None
    sar: Optional[Dict[str, Any]] = None
    fusion_type: Optional[str] = None
    joint_findings: Optional[List[str]] = None
    cross_modal_agreement: Optional[float] = None
    discrepancies: Optional[List[str]] = None

class AnalysisResult(BaseModel):
    job_id: str
    query: str
    detected_task: str
    workflow: str
    selected_models: List[str]
    model_selection_rationale: Optional[str] = None
    agent_plan: Optional[Dict[str, Any]] = None
    answer: str
    evidence: VisualEvidence
    multimodal_evidence: Optional[Dict[str, Any]] = None
    confidence: ConfidenceBreakdown
    execution_trace: List[TraceStep]
    total_execution_time_ms: float
    warnings: List[str] = []
    report_url: str
    created_at: str

class ModelDescriptor(BaseModel):
    id: str
    name: str
    role: str
    mode: str = Field(description="local, api, calibrated_fallback")
    input_types: List[str]
    outputs: List[str]
    description: str
    weights_path: Optional[str] = None
    is_active: bool = True
