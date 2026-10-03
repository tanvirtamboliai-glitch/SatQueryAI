import {
  ValidationResponse,
  AnalysisResult,
  AgentPlan,
  ModelDescriptor,
  DemoScenario,
  ImageMetadata
} from '../types';

const API_BASE = '/api';

export async function fetchAgentPlan(
  query: string,
  image1Id?: string,
  image2Id?: string,
  mode?: string
): Promise<AgentPlan> {
  const res = await fetch(`${API_BASE}/agent/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      image1_id: image1Id || null,
      image2_id: image2Id || null,
      mode: mode || null,
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Plan generation failed');
  }
  return res.json();
}

export async function checkHealth(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Backend offline');
  return res.json();
}

export async function fetchModels(): Promise<ModelDescriptor[]> {
  const res = await fetch(`${API_BASE}/models`);
  if (!res.ok) throw new Error('Failed to load model registry');
  return res.json();
}

export async function fetchSamples(): Promise<DemoScenario[]> {
  const res = await fetch(`${API_BASE}/samples`);
  if (!res.ok) throw new Error('Failed to load demo scenarios');
  return res.json();
}

export async function uploadImageFile(file: File): Promise<ImageMetadata> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function validateImagePair(
  image1Id: string,
  image2Id?: string
): Promise<ValidationResponse> {
  const formData = new FormData();
  formData.append('image1_id', image1Id);
  if (image2Id) {
    formData.append('image2_id', image2Id);
  }
  const res = await fetch(`${API_BASE}/validate`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Validation failed');
  }
  return res.json();
}

export async function submitAnalysis(
  query: string,
  image1Id: string,
  image2Id?: string,
  mode?: string,
  tilingEnabled?: boolean
): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      image1_id: image1Id,
      image2_id: image2Id || null,
      mode: mode || null,
      tiling_enabled: !!tilingEnabled,
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Analysis failed');
  }
  return res.json();
}

export async function runBenchmark(benchmarkName: string): Promise<{ metric: string; score: string; status: string }> {
  const formData = new FormData();
  formData.append('benchmark_name', benchmarkName);
  const res = await fetch(`${API_BASE}/benchmark/run`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Benchmark execution failed');
  return res.json();
}
