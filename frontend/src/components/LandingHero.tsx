import React from 'react';
import { Eye, GitCompare, Radio, ArrowRight, UploadCloud, MessageSquare, CheckCircle2, ShieldCheck } from 'lucide-react';

interface LandingHeroProps {
  onStart: (mode?: 'single' | 'bi_temporal' | 'optical_sar') => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onStart }) => {
  return (
    <div className="relative border-b border-slate-800 bg-gradient-to-b from-[#0b0f17] via-[#0e1420] to-[#0b0f17] py-12 sm:py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto text-center">
        {/* Top Tag */}
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-400 text-xs font-mono mb-6">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Production-Grade Agentic Earth Observation Platform</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white mb-4">
          <span className="bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            SatQuery AI
          </span>
        </h1>
        <p className="text-base sm:text-xl text-slate-300 max-w-3xl mx-auto font-normal leading-relaxed mb-8">
          Ask questions. Analyze Earth observation imagery. Get evidence-grounded answers.
        </p>

        {/* 3 Primary Modes Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 text-left mb-10">
          {/* Mode 1 */}
          <div 
            onClick={() => onStart('single')}
            className="group cursor-pointer p-5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/60 transition-all hover:shadow-lg hover:shadow-cyan-500/5 flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 flex items-center justify-center mb-4 group-hover:bg-cyan-500/20 transition-colors">
                <Eye className="w-5 h-5" />
              </div>
              <h3 className="text-white font-bold text-base mb-1">Single Image</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-3">
                VQA, dense scene captioning, and text-guided region grounding with GeoChat & GeoGround.
              </p>
            </div>
            <div className="flex items-center text-xs font-semibold text-cyan-400 group-hover:translate-x-1 transition-transform">
              <span>Launch Mode</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          {/* Mode 2 */}
          <div 
            onClick={() => onStart('bi_temporal')}
            className="group cursor-pointer p-5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-blue-500/60 transition-all hover:shadow-lg hover:shadow-blue-500/5 flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400 flex items-center justify-center mb-4 group-hover:bg-blue-500/20 transition-colors">
                <GitCompare className="w-5 h-5" />
              </div>
              <h3 className="text-white font-bold text-base mb-1">Change Analysis</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-3">
                Bi-temporal surface modification, change maps, and temporal question answering with Change-Agent & ChangeChat.
              </p>
            </div>
            <div className="flex items-center text-xs font-semibold text-blue-400 group-hover:translate-x-1 transition-transform">
              <span>Launch Mode</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          {/* Mode 3 */}
          <div 
            onClick={() => onStart('optical_sar')}
            className="group cursor-pointer p-5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-emerald-500/60 transition-all hover:shadow-lg hover:shadow-emerald-500/5 flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mb-4 group-hover:bg-emerald-500/20 transition-colors">
                <Radio className="w-5 h-5" />
              </div>
              <h3 className="text-white font-bold text-base mb-1">Optical + SAR</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-3">
                Cross-modal latent fusion penetrating cloud shadows and resolving structural double-bounce with Clay & Prithvi.
              </p>
            </div>
            <div className="flex items-center text-xs font-semibold text-emerald-400 group-hover:translate-x-1 transition-transform">
              <span>Launch Mode</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>
        </div>

        {/* 3-Step Process Flow */}
        <div className="border-t border-slate-800/80 pt-8 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 text-cyan-400 font-mono text-xs font-bold flex items-center justify-center mb-2">
                01
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">Upload Imagery</h4>
              <p className="text-[11px] text-slate-400 mt-1 max-w-xs">
                Provide Optical, Multispectral, SAR, or Temporal GeoTIFF/TIFF rasters with spatial headers.
              </p>
            </div>

            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 text-cyan-400 font-mono text-xs font-bold flex items-center justify-center mb-2">
                02
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">Natural-Language Query</h4>
              <p className="text-[11px] text-slate-400 mt-1 max-w-xs">
                Inquire freely about land use, built-up expansion, localized targets, or temporal shifts.
              </p>
            </div>

            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 text-cyan-400 font-mono text-xs font-bold flex items-center justify-center mb-2">
                03
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">Grounded Synthesis</h4>
              <p className="text-[11px] text-slate-400 mt-1 max-w-xs">
                SatQuery routes models, generates spatial overlays, audits confidence, and exports dossiers.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
