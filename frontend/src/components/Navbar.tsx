import React from 'react';
import { Satellite, Cpu, Layers, BarChart3, CheckCircle2, AlertCircle } from 'lucide-react';

interface NavbarProps {
  activeTab: 'workspace' | 'architecture' | 'evaluation';
  setActiveTab: (tab: 'workspace' | 'architecture' | 'evaluation') => void;
  isBackendOnline: boolean;
  modelsCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  isBackendOnline,
  modelsCount,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-[#0c1017]/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => setActiveTab('workspace')}
          className="flex items-center space-x-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 group-hover:border-cyan-400 transition-colors">
            <Satellite className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-wider text-white">SATQUERY</span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-widest bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono tracking-tight hidden sm:block">
              Vision-Language Multimodal Earth Observation
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab('workspace')}
            className={`px-3.5 py-2 rounded-md text-xs font-semibold uppercase tracking-wider transition-colors flex items-center space-x-2 ${
              activeTab === 'workspace'
                ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Workspace</span>
          </button>

          <button
            onClick={() => setActiveTab('architecture')}
            className={`px-3.5 py-2 rounded-md text-xs font-semibold uppercase tracking-wider transition-colors flex items-center space-x-2 ${
              activeTab === 'architecture'
                ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Architecture</span>
          </button>

          <button
            onClick={() => setActiveTab('evaluation')}
            className={`px-3.5 py-2 rounded-md text-xs font-semibold uppercase tracking-wider transition-colors flex items-center space-x-2 ${
              activeTab === 'evaluation'
                ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Evaluation</span>
          </button>
        </nav>

        {/* Status Indicators */}
        <div className="flex items-center space-x-3">
          <div className="hidden md:flex items-center space-x-2 px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[11px] text-slate-300 font-mono">
            <span className="text-slate-400">Registry:</span>
            <span className="text-cyan-400 font-bold">{modelsCount || 8} Models</span>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[11px]">
            {isBackendOnline ? (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                <span className="text-emerald-400 font-mono text-[11px] font-medium">Ready</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                <span className="text-amber-400 font-mono text-[11px]">Connecting</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
