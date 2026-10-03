import React from 'react';
import {
  Layers,
  Cpu,
  ArrowDown,
  CheckCircle2,
  FileCheck2,
  GitBranch,
  ShieldCheck,
  Zap,
  Activity,
  Maximize2
} from 'lucide-react';

export const ArchitecturePage: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto py-10 px-4 sm:px-6 lg:px-8 font-sans">
      {/* Title */}
      <div className="text-center mb-12">
        <span className="px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-400 text-xs font-mono">
          System Architecture & Routing Topology
        </span>
        <h1 className="text-3xl sm:text-4xl font-black text-white mt-3">
          SatQuery AI Technical Architecture
        </h1>
        <p className="text-sm text-slate-400 max-w-2xl mx-auto mt-2">
          A multi-tier agentic framework combining deterministic input validation, 3-layer query routing, specialist foundation models, and multi-factor confidence auditing.
        </p>
      </div>

      {/* Visual Topology Diagram */}
      <div className="bg-[#0d1117] border border-slate-800 rounded-2xl p-6 sm:p-10 shadow-2xl mb-12">
        <div className="flex flex-col items-center space-y-6 max-w-3xl mx-auto">
          {/* Level 1: Input Query */}
          <div className="w-full max-w-md p-4 rounded-xl bg-slate-900 border border-slate-700 text-center shadow-lg">
            <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider">Input Layer</span>
            <h3 className="text-sm font-bold text-white mt-0.5">User Natural-Language Query + Remote Sensing Imagery</h3>
            <p className="text-[11px] text-slate-400 mt-1 font-mono">Single Optical • Bi-temporal Pair • Optical + SAR</p>
          </div>

          <ArrowDown className="w-5 h-5 text-cyan-400 animate-bounce" />

          {/* Level 2: Input Validator */}
          <div className="w-full max-w-md p-4 rounded-xl bg-slate-900 border border-slate-700 text-center shadow-lg">
            <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase tracking-wider">Rigorous GIS Inspection</span>
            <h3 className="text-sm font-bold text-white mt-0.5">GeoTIFF / Rasterio Input Validator</h3>
            <p className="text-[11px] text-slate-400 mt-1 font-mono">CRS (EPSG) • Spatial Resolution • Extent Overlap &gt;80% • Modality Detection</p>
          </div>

          <ArrowDown className="w-5 h-5 text-emerald-400" />

          {/* Level 3: Agentic Controller */}
          <div className="w-full max-w-lg p-5 rounded-xl bg-gradient-to-r from-slate-900 via-cyan-950/40 to-slate-900 border border-cyan-500/50 text-center shadow-xl">
            <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider">Autonomous Brain</span>
            <h3 className="text-base font-black text-white mt-0.5">3-Layer Agentic Controller & Query Router</h3>
            <div className="grid grid-cols-3 gap-2 mt-3 text-[11px] text-slate-300 font-mono">
              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-cyan-400 font-bold">L1:</span> Input Modality
              </div>
              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-blue-400 font-bold">L2:</span> Intent Classifier
              </div>
              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-emerald-400 font-bold">L3:</span> Tool Registry
              </div>
            </div>
          </div>

          <ArrowDown className="w-5 h-5 text-cyan-400" />

          {/* Level 4: Specialist Model Registry (3 Pillars) */}
          <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Pillar A */}
            <div className="p-4 rounded-xl bg-slate-900 border border-cyan-500/40 text-center">
              <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase">Vision-Language</span>
              <h4 className="text-sm font-bold text-white mt-1">GeoChat & GeoGround</h4>
              <p className="text-[11px] text-slate-400 mt-2 font-mono">
                Single-Image VQA, Dense Captioning, Text-Guided Region Grounding & BBoxes
              </p>
            </div>

            {/* Pillar B */}
            <div className="p-4 rounded-xl bg-slate-900 border border-blue-500/40 text-center">
              <span className="text-[10px] font-mono text-blue-400 font-bold uppercase">Temporal Dynamics</span>
              <h4 className="text-sm font-bold text-white mt-1">Change-Agent & ChangeChat</h4>
              <p className="text-[11px] text-slate-400 mt-2 font-mono">
                Siamese Difference, CVA Probability, Otsu Binary Masks & Change VQA
              </p>
            </div>

            {/* Pillar C */}
            <div className="p-4 rounded-xl bg-slate-900 border border-emerald-500/40 text-center">
              <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase">Cross-Modal EO</span>
              <h4 className="text-sm font-bold text-white mt-1">Clay & Prithvi-EO-2.0</h4>
              <p className="text-[11px] text-slate-400 mt-2 font-mono">
                Optical + SAR Latent Fusion, Double-Bounce Analysis, Multi-Spectral Features
              </p>
            </div>
          </div>

          <ArrowDown className="w-5 h-5 text-slate-500" />

          {/* Level 5: Evidence & Confidence Engine */}
          <div className="w-full max-w-md p-4 rounded-xl bg-slate-900 border border-slate-700 text-center shadow-lg">
            <span className="text-[10px] font-mono text-purple-400 font-bold uppercase tracking-wider">Multi-Factor Engine</span>
            <h3 className="text-sm font-bold text-white mt-0.5">Spatial Evidence & Confidence Aggregator</h3>
            <p className="text-[11px] text-slate-400 mt-1 font-mono">
              Composite Overlays • Bounding Coordinates • Multi-Factor Confidence Formulation
            </p>
          </div>

          <ArrowDown className="w-5 h-5 text-purple-400" />

          {/* Level 6: Output Response */}
          <div className="w-full max-w-md p-4 rounded-xl bg-gradient-to-r from-cyan-950/40 to-blue-950/40 border border-cyan-500/60 text-center shadow-xl">
            <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider">Grounded Deliverable</span>
            <h3 className="text-sm font-bold text-white mt-0.5">Verified Answer + Visual Overlay + Audit Dossier</h3>
            <p className="text-[11px] text-slate-400 mt-1 font-mono">Observable Trace • Standalone HTML/PDF Report</p>
          </div>
        </div>
      </div>

      {/* Deep-Dive Architectural Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-mono text-xs">
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-sm font-bold text-cyan-400 mb-2 font-sans">Controlled Specialist Tool Registry</h3>
          <p className="text-slate-300 leading-relaxed font-sans text-xs">
            Unlike naive chatbots, SatQuery AI does not allow the language model to write or execute arbitrary Python code. 
            All operations are channeled through a sandboxed, deterministic tool registry with explicit input schemas, spatial bounds checks, and type-safe arguments.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-sm font-bold text-emerald-400 mb-2 font-sans">Multi-Factor Confidence Calibration</h3>
          <p className="text-slate-300 leading-relaxed font-sans text-xs">
            Confidence is mathematically aggregated from:
            <br />
            • Model classification logit confidence (35%)
            <br />
            • GIS input CRS &amp; spatial overlap compatibility (25%)
            <br />
            • Contour &amp; bounding box evidence strength (25%)
            <br />
            • Temporal &amp; spectral cross-consistency (15%)
          </p>
        </div>
      </div>
    </div>
  );
};
