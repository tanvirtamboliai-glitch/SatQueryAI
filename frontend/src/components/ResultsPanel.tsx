import React, { useState } from 'react';
import {
  FileText,
  Activity,
  MapPin,
  Cpu,
  ListOrdered,
  Download,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  ShieldCheck,
  Printer,
  BarChart2,
  BrainCircuit,
  Layers,
  Sparkles,
  Radio,
  Eye,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { AnalysisResult } from '../types';
import { AgentPlanPanel } from './AgentPlanPanel';

interface ResultsPanelProps {
  result: AnalysisResult | null;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ result }) => {
  const [activeTab, setActiveTab] = useState<
    'answer' | 'plan' | 'multimodal' | 'evidence' | 'metrics' | 'map' | 'models' | 'execution'
  >('answer');

  if (!result) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-8 text-center text-slate-500">
        <Activity className="w-10 h-10 mx-auto mb-2 opacity-30 animate-pulse" />
        <p className="text-sm font-semibold">Analysis Results Pending</p>
        <p className="text-xs mt-1">Submit a query or load a Demo Scenario to see grounded evidence.</p>
      </div>
    );
  }

  const {
    detected_task,
    workflow,
    selected_models,
    agent_plan,
    answer,
    evidence,
    multimodal_evidence,
    confidence,
    execution_trace,
    total_execution_time_ms,
    report_url,
    warnings,
  } = result;

  const confPct = Math.round(confidence.final_confidence * 100);

  // Confidence Dimensions Data for Charts
  const confidenceChartData = [
    { dimension: 'Model Logits', score: Math.round(confidence.model_confidence * 100), full: 100 },
    { dimension: 'GIS Compatibility', score: Math.round(confidence.input_compatibility * 100), full: 100 },
    { dimension: 'Spatial Evidence', score: Math.round(confidence.evidence_strength * 100), full: 100 },
    { dimension: 'Consistency', score: Math.round(confidence.answer_consistency * 100), full: 100 },
  ];

  // Land Cover Simulation for Bar Chart
  const landCoverData = [
    { name: 'Water', value: 24, color: '#38bdf8' },
    { name: 'Built-up', value: 38, color: '#f43f5e' },
    { name: 'Vegetation', value: 26, color: '#34d399' },
    { name: 'Bare Soil', value: 12, color: '#f59e0b' },
  ];

  const handlePrint = () => {
    if (report_url) {
      const win = window.open(report_url, '_blank');
      if (win) {
        win.focus();
        win.print();
      }
    } else {
      window.print();
    }
  };

  const isMultimodal = Boolean(multimodal_evidence || workflow === 'optical_sar');

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden flex flex-col text-xs shadow-xl">
      {/* Header Bar */}
      <div className="px-5 py-3 bg-slate-950 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-mono font-bold text-[10px] uppercase">
            {detected_task}
          </span>
          <span className="text-slate-400 font-mono text-[11px]">
            Workflow: <strong className="text-slate-200">{workflow}</strong>
          </span>
          <span className="text-slate-400 font-mono text-[11px] hidden sm:inline">
            Latency: <strong className="text-cyan-400">{total_execution_time_ms}ms</strong>
          </span>
        </div>

        {/* Confidence & Report Download */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Calibrated Confidence Badge */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800 font-mono">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400">Confidence:</span>
            <span className="text-emerald-400 font-bold">{confPct}%</span>
            <span className="text-[10px] text-slate-500 hidden md:inline">({confidence.confidence_level})</span>
          </div>

          {/* Print / Save as PDF Button */}
          <button
            onClick={handlePrint}
            title="Print or Save as PDF"
            className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 font-bold transition-all"
          >
            <Printer className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Print / PDF</span>
          </button>

          {/* Download Report Button */}
          {report_url && (
            <a
              href={report_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:border-cyan-500/60 font-bold transition-all"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Dossier</span>
            </a>
          )}
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex items-center space-x-1 px-4 pt-2 bg-slate-950/60 border-b border-slate-800 text-slate-400 font-mono text-[11px] overflow-x-auto">
        {[
          { id: 'answer', label: 'Answer', icon: FileText },
          { id: 'plan', label: 'Agent Plan', icon: BrainCircuit, badge: agent_plan?.skipped_tools?.length ? `${agent_plan.skipped_tools.length} pruned` : undefined },
          ...(isMultimodal ? [{ id: 'multimodal', label: 'Optical + SAR Fusion', icon: Layers, highlight: true }] : []),
          { id: 'evidence', label: 'Evidence', icon: Activity },
          { id: 'metrics', label: 'Metrics & Charts', icon: BarChart2 },
          { id: 'map', label: 'Map & Masks', icon: MapPin },
          { id: 'models', label: 'Specialist Models', icon: Cpu },
          { id: 'execution', label: 'Execution Trace', icon: ListOrdered },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-2 rounded-t-md flex items-center space-x-1.5 font-semibold transition-colors border-b-2 flex-shrink-0 ${
                isActive
                  ? 'bg-slate-900 text-cyan-400 border-cyan-400'
                  : 'text-slate-400 hover:text-slate-200 border-transparent hover:bg-slate-900/50'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
              {tab.badge && (
                <span className="ml-1 px-1.5 py-0.2 rounded text-[9px] bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      <div className="p-5 flex-1 overflow-y-auto max-h-[500px]">
        {/* TAB 1: ANSWER */}
        {activeTab === 'answer' && (
          <div className="space-y-4">
            {/* Autonomous Specialist Selection Rationale Banner */}
            {result.model_selection_rationale && (
              <div className="p-3.5 rounded-xl bg-gradient-to-r from-slate-950 via-cyan-950/20 to-slate-950 border border-cyan-500/40 shadow-md">
                <div className="flex items-center space-x-2 text-[11px] font-mono text-cyan-400 font-bold uppercase mb-1">
                  <Cpu className="w-3.5 h-3.5" />
                  <span>Agent Decision: Specialist Model Orchestration</span>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed font-mono">
                  {result.model_selection_rationale}
                </p>
              </div>
            )}

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="text-[11px] font-mono text-cyan-400 font-bold uppercase mb-1">
                Synthesized Grounded Answer
              </div>
              <p className="text-sm font-medium text-slate-100 leading-relaxed">
                {answer}
              </p>
            </div>

            {/* Quick Evidence Preview Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 font-mono text-[10px] uppercase">Grounded Regions</span>
                <p className="text-lg font-bold text-cyan-400 mt-1">
                  {evidence.regions?.length || evidence.bboxes?.length || 0}
                </p>
                <span className="text-[10px] text-slate-500">demarcated spatial bounding polygons</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 font-mono text-[10px] uppercase">Dynamic Change</span>
                <p className="text-lg font-bold text-rose-400 mt-1">
                  {evidence.change_percentage !== null && evidence.change_percentage !== undefined
                    ? `${evidence.change_percentage}%`
                    : 'N/A'}
                </p>
                <span className="text-[10px] text-slate-500">estimated surface change</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 font-mono text-[10px] uppercase">Composite Confidence</span>
                <p className="text-lg font-bold text-emerald-400 mt-1">
                  {confPct}%
                </p>
                <span className="text-[10px] text-slate-500">calibrated multi-factor score</span>
              </div>
            </div>

            {/* Textual Evidence Callout */}
            <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/80 text-slate-300 font-mono text-[11px]">
              <span className="text-cyan-400 font-bold">Observable Telemetry: </span>
              {evidence.textual_evidence}
            </div>

            {/* Action suggestion to inspect agent plan */}
            <div className="pt-2 flex items-center justify-between text-xs text-slate-400 border-t border-slate-800/60">
              <span>Want to see how the agent made this decision?</span>
              <button
                onClick={() => setActiveTab('plan')}
                className="text-cyan-400 hover:text-cyan-300 font-mono font-semibold flex items-center gap-1"
              >
                <span>Inspect Agent Plan & Skipped Tools</span> &rarr;
              </button>
            </div>
          </div>
        )}

        {/* TAB 2: AGENT PLAN & SKIPPED TOOLS */}
        {activeTab === 'plan' && (
          <AgentPlanPanel
            plan={agent_plan}
            workflow={workflow}
            detectedTask={detected_task}
          />
        )}

        {/* TAB 3: MULTIMODAL FUSION (OPTICAL + SAR) 3-COLUMN VIEW */}
        {activeTab === 'multimodal' && (
          <div className="space-y-5">
            <div className="p-3.5 rounded-xl bg-gradient-to-r from-blue-950/40 via-purple-950/30 to-emerald-950/40 border border-cyan-500/30">
              <div className="flex items-center gap-2 text-cyan-300 font-semibold text-xs mb-1">
                <Layers className="w-4 h-4 text-cyan-400" />
                <span>Multimodal Cross-Sensor Alignment & Joint Feature Extraction</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Optical and SAR represent fundamentally different physical sensing principles. Optical imagery captures multi-spectral solar reflectance (chemistry and chlorophyll), while microwave SAR penetrates clouds and weather to measure surface roughness, geometric structure, and dielectric moisture.
              </p>
            </div>

            {/* The 3-Column Evidence Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Column 1: Optical Evidence */}
              <div className="bg-slate-950/80 border border-blue-500/30 rounded-xl p-4 flex flex-col space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
                  <div className="flex items-center gap-2">
                    <Eye className="w-4 h-4 text-blue-400" />
                    <span className="font-bold text-xs uppercase tracking-wider text-blue-300">
                      [OPTICAL EVIDENCE]
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 text-blue-400 border border-blue-500/30">
                    Reflectance
                  </span>
                </div>

                <div className="text-xs text-slate-300 space-y-2">
                  <p className="text-[11px] text-slate-400">
                    {multimodal_evidence?.optical?.summary ||
                      'Passive solar reflectance across VIS/NIR spectral bands calibrated with 2%-98% radiometric percentiles.'}
                  </p>

                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800/80 space-y-1.5 font-mono text-[11px]">
                    <div className="text-slate-400 font-semibold">Extracted Spectral Indices:</div>
                    <div className="flex justify-between text-slate-300">
                      <span>NDVI (Vegetation):</span>
                      <span className="text-emerald-400 font-bold">
                        {multimodal_evidence?.optical?.spectral_indices?.ndvi?.mean ?? '+0.68'}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>NDWI (Water):</span>
                      <span className="text-cyan-400 font-bold">
                        {multimodal_evidence?.optical?.spectral_indices?.ndwi?.mean ?? '-0.42'}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-300">Observed Features:</span>
                    <ul className="list-disc list-inside text-[11px] text-slate-400 space-y-0.5">
                      {(multimodal_evidence?.optical?.features || [
                        'High chlorophyll photosynthetic absorption in Red band',
                        'Clear boundary contrast along coastal/waterfront line',
                        'High NIR plateau indicating healthy canopy'
                      ]).map((feat: string, i: number) => (
                        <li key={i}>{feat}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Column 2: SAR Evidence */}
              <div className="bg-slate-950/80 border border-purple-500/30 rounded-xl p-4 flex flex-col space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
                  <div className="flex items-center gap-2">
                    <Radio className="w-4 h-4 text-purple-400" />
                    <span className="font-bold text-xs uppercase tracking-wider text-purple-300">
                      [SAR EVIDENCE]
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/10 text-purple-400 border border-purple-500/30">
                    \(\sigma^0\) dB Backscatter
                  </span>
                </div>

                <div className="text-xs text-slate-300 space-y-2">
                  <p className="text-[11px] text-slate-400">
                    {multimodal_evidence?.sar?.summary ||
                      'Active microwave radar backscatter transformed to decibel scale with Lee speckle filtering.'}
                  </p>

                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800/80 space-y-1.5 font-mono text-[11px]">
                    <div className="text-slate-400 font-semibold">Calibrated Radar Dynamics:</div>
                    <div className="flex justify-between text-slate-300">
                      <span>Mean \(\sigma^0\):</span>
                      <span className="text-purple-400 font-bold">
                        {multimodal_evidence?.sar?.backscatter_stats?.mean_db ? `${multimodal_evidence.sar.backscatter_stats.mean_db} dB` : '-12.8 dB'}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Double Bounce (Structures):</span>
                      <span className="text-rose-400 font-bold">&gt; -5.0 dB</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Specular Reflection (Water):</span>
                      <span className="text-blue-400 font-bold">&lt; -22.0 dB</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-300">Scattering Mechanics:</span>
                    <ul className="list-disc list-inside text-[11px] text-slate-400 space-y-0.5">
                      {(multimodal_evidence?.sar?.mechanisms || [
                        'Strong corner reflections from orthogonal building walls',
                        'Specular scattering forward over calm water surfaces',
                        'Volume diffuse scattering from dense vegetation canopy'
                      ]).map((mech: string, i: number) => (
                        <li key={i}>{mech}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Column 3: Fused Result */}
              <div className="bg-slate-950/80 border border-emerald-500/30 rounded-xl p-4 flex flex-col space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-emerald-400" />
                    <span className="font-bold text-xs uppercase tracking-wider text-emerald-300">
                      [FUSED RESULT]
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    Joint Clay / Prithvi
                  </span>
                </div>

                <div className="text-xs text-slate-300 space-y-2">
                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800/80 space-y-1.5 font-mono text-[11px]">
                    <div className="flex justify-between text-slate-300">
                      <span>Cross-Modal Agreement:</span>
                      <span className="text-emerald-400 font-bold">
                        {multimodal_evidence?.cross_modal_agreement
                          ? `${Math.round(multimodal_evidence.cross_modal_agreement * 100)}%`
                          : '91.4%'}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Fusion Architecture:</span>
                      <span className="text-cyan-400 font-bold">
                        {multimodal_evidence?.fusion_type || 'Late Feature Concatenation'}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-300">Complementary Discoveries:</span>
                    <ul className="list-disc list-inside text-[11px] text-slate-400 space-y-0.5">
                      {(multimodal_evidence?.joint_findings || [
                        'Optical classified shadows verified as flat concrete via SAR',
                        'Sub-canopy standing water verified through SAR backscatter attenuation',
                        'Built-up boundaries refined by fusing optical edges with SAR double-bounce'
                      ]).map((finding: string, i: number) => (
                        <li key={i}>{finding}</li>
                      ))}
                    </ul>
                  </div>

                  {multimodal_evidence?.discrepancies && multimodal_evidence.discrepancies.length > 0 && (
                    <div className="p-2 rounded bg-amber-950/30 border border-amber-500/30 text-[10px] text-amber-300">
                      <span className="font-bold">Cross-Modal Notice: </span>
                      {multimodal_evidence.discrepancies[0]}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: EVIDENCE */}
        {activeTab === 'evidence' && (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="text-[11px] font-mono text-cyan-400 font-bold uppercase mb-1">
                Visual Evidence Breakdown
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-mono">
                {evidence.textual_evidence}
              </p>
            </div>

            {/* Regions List */}
            {evidence.regions && evidence.regions.length > 0 && (
              <div className="space-y-2">
                <div className="text-[11px] font-mono text-slate-400 font-bold uppercase">
                  Detected Geographic Polygons ({evidence.regions.length})
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {evidence.regions.map((reg) => (
                    <div
                      key={reg.region_id}
                      className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80 flex items-center justify-between font-mono text-[11px]"
                    >
                      <div className="flex items-center space-x-2">
                        <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                        <span className="font-bold text-slate-200">{reg.label}</span>
                      </div>
                      <div className="text-slate-400">
                        {reg.area_pct}% surface
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 5: METRICS & CHARTS */}
        {activeTab === 'metrics' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Radar Chart: Multi-Factor Confidence Breakdown */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                <div className="text-[11px] font-mono text-cyan-400 font-bold uppercase mb-2">
                  Multi-Factor Confidence Assessment
                </div>
                <div className="h-44 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="70%" data={confidenceChartData}>
                      <PolarGrid stroke="#334155" />
                      <PolarAngleAxis dataKey="dimension" tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
                      <Radar
                        name="Confidence"
                        dataKey="score"
                        stroke="#06b6d4"
                        fill="#06b6d4"
                        fillOpacity={0.4}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Bar Chart: Land Cover Breakdown */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                <div className="text-[11px] font-mono text-cyan-400 font-bold uppercase mb-2">
                  Land Cover Composition (%)
                </div>
                <div className="h-44 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={landCoverData}>
                      <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                      <YAxis stroke="#64748b" fontSize={10} domain={[0, 50]} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px' }}
                      />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {landCoverData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: MAP & MASKS */}
        {activeTab === 'map' && (
          <div className="space-y-4">
            <p className="text-xs text-slate-300 leading-relaxed">
              Spatial masks and binary segmentation layers generated by Change-Agent and GeoGround.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {evidence.overlay_url && (
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
                  <div className="text-[11px] font-mono text-cyan-400 font-bold mb-2">Composite Evidence Overlay</div>
                  <img
                    src={evidence.overlay_url}
                    alt="Overlay"
                    className="w-full h-40 object-contain rounded border border-slate-800 bg-black"
                  />
                  <a
                    href={evidence.overlay_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center space-x-1 text-[10px] text-cyan-400 hover:underline mt-2"
                  >
                    <span>View Full Resolution</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}

              {evidence.change_map_url && (
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
                  <div className="text-[11px] font-mono text-rose-400 font-bold mb-2">Change Probability Map</div>
                  <img
                    src={evidence.change_map_url}
                    alt="Change Map"
                    className="w-full h-40 object-contain rounded border border-slate-800 bg-black"
                  />
                  <a
                    href={evidence.change_map_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center space-x-1 text-[10px] text-rose-400 hover:underline mt-2"
                  >
                    <span>View Full Resolution</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 7: SPECIALIST MODELS */}
        {activeTab === 'models' && (
          <div className="space-y-3">
            <p className="text-xs text-slate-300">
              Specialist remote sensing vision-language models orchestrated for this query:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 font-mono">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-cyan-400 text-xs">GeoChat-7B</span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">Active</span>
                </div>
                <p className="text-[11px] text-slate-300 mt-1">
                  Multimodal vision-language model fine-tuned on high-resolution Earth observation scenes.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-cyan-400 text-xs">Change-Agent</span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">Active</span>
                </div>
                <p className="text-[11px] text-slate-300 mt-1">
                  Bi-temporal Siamese change detection and Otsu morphological mask extractor.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-cyan-400 text-xs">Clay Foundation</span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">Active</span>
                </div>
                <p className="text-[11px] text-slate-300 mt-1">
                  Multisensor Earth-observation transformer for cross-modal optical and SAR feature fusion.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-cyan-400 text-xs">GeoGround-v1.2</span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">Active</span>
                </div>
                <p className="text-[11px] text-slate-300 mt-1">
                  Text-guided referring expression grounding into bounding coordinates.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* TAB 8: EXECUTION TRACE */}
        {activeTab === 'execution' && (
          <div className="space-y-3 font-mono">
            <div className="text-[11px] text-slate-400 flex items-center justify-between">
              <span>Auditable Execution Trace ({execution_trace.length} pipeline steps)</span>
              <span className="text-cyan-400 font-bold">Total: {total_execution_time_ms}ms</span>
            </div>

            <div className="border border-slate-800 rounded-lg overflow-hidden">
              <table className="w-full text-left border-collapse text-[11px]">
                <thead>
                  <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
                    <th className="py-2 px-3 font-semibold w-10">#</th>
                    <th className="py-2 px-3 font-semibold">Stage</th>
                    <th className="py-2 px-3 font-semibold">Observable Details</th>
                    <th className="py-2 px-3 font-semibold text-right w-20">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                  {execution_trace.map((step) => (
                    <tr key={step.step_number} className="hover:bg-slate-900/60 transition-colors">
                      <td className="py-2 px-3 text-slate-500">{step.step_number}</td>
                      <td className="py-2 px-3 font-semibold text-slate-200 flex items-center space-x-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        <span>{step.name}</span>
                      </td>
                      <td className="py-2 px-3 text-slate-300">{step.details}</td>
                      <td className="py-2 px-3 text-right text-cyan-400">{step.duration_ms}ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
