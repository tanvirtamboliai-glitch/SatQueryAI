export interface ImageMetadata {
  file_id: string;
  filename: string;
  format: string;
  dimensions: [number, number];
  bands: number;
  crs?: string | null;
  geotransform?: number[] | null;
  bounds?: [number, number, number, number] | null;
  resolution?: [number, number] | null;
  modality: string;
  acquisition_date?: string | null;
  sensor?: string | null;
  is_valid: boolean;
  warnings: string[];
  preview_url?: string | null;
}

export interface PairValidationResult {
  valid: boolean;
  pair_type: string;
  spatial_overlap_pct: number;
  crs_match: boolean;
  resolution_ratio: number;
  warnings: string[];
  reason?: string | null;
}

export interface ValidationResponse {
  valid: boolean;
  detected_mode: 'single' | 'bi_temporal' | 'optical_sar' | 'invalid';
  image1: ImageMetadata;
  image2?: ImageMetadata | null;
  pair_validation?: PairValidationResult | null;
  suggested_workflow: string;
  warnings: string[];
}

export interface BoundingBox {
  box_2d: [number, number, number, number]; // [ymin, xmin, ymax, xmax] 0..1000
  label: string;
  confidence: number;
}

export interface RegionEvidence {
  region_id: number;
  label: string;
  change_type?: string | null;
  area_pct: number;
  bbox: [number, number, number, number];
}

export interface VisualEvidence {
  overlay_url?: string | null;
  change_map_url?: string | null;
  mask_url?: string | null;
  evidence_image_url?: string | null;
  change_percentage?: number | null;
  changed_regions_count?: number | null;
  bboxes: BoundingBox[];
  regions: RegionEvidence[];
  textual_evidence: string;
}

export interface ConfidenceBreakdown {
  model_confidence: number;
  input_compatibility: number;
  evidence_strength: number;
  answer_consistency: number;
  final_confidence: number;
  confidence_level: string;
  calibration_status: string;
}

export interface TraceStep {
  step_number: number;
  name: string;
  status: string;
  details: string;
  duration_ms: number;
  timestamp: string;
}

export interface SkippedTool {
  tool: string;
  reason: string;
}

export interface AgentPlan {
  query: string;
  intent: string;
  reasoning_summary: string;
  required_modalities: string[];
  selected_tools: string[];
  execution_order: string[];
  skipped_tools: SkippedTool[];
  estimated_latency_ms: number;
}

export interface OpticalEvidenceDetail {
  features?: string[];
  spectral_indices?: Record<string, any>;
  summary?: string;
  preview_url?: string;
  [key: string]: any;
}

export interface SAREvidenceDetail {
  backscatter_stats?: Record<string, any>;
  mechanisms?: string[];
  roughness_assessment?: string;
  summary?: string;
  preview_url?: string;
  [key: string]: any;
}

export interface MultimodalEvidence {
  optical?: OpticalEvidenceDetail | null;
  sar?: SAREvidenceDetail | null;
  fusion_type?: string | null;
  joint_findings?: string[];
  cross_modal_agreement?: number;
  discrepancies?: string[];
  [key: string]: any;
}

export interface AnalysisResult {
  job_id: string;
  query: string;
  detected_task: string;
  workflow: string;
  selected_models: string[];
  model_selection_rationale?: string | null;
  agent_plan?: AgentPlan | null;
  answer: string;
  evidence: VisualEvidence;
  multimodal_evidence?: MultimodalEvidence | null;
  confidence: ConfidenceBreakdown;
  execution_trace: TraceStep[];
  total_execution_time_ms: number;
  warnings: string[];
  report_url: string;
  created_at: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  description: string;
  mode: 'single' | 'bi_temporal' | 'optical_sar';
  image1_id: string;
  image2_id?: string | null;
  preview1: string;
  preview2?: string | null;
  query: string;
  expected_task: string;
  expected_models: string[];
}

export interface ModelDescriptor {
  id: string;
  name: string;
  role: string;
  mode: string;
  input_types: string[];
  outputs: string[];
  description: string;
  weights_path?: string | null;
  is_active: boolean;
}
