import React from 'react';
import {
  BrainCircuit,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  Database
} from 'lucide-react';
import { AgentPlan } from '../types';

interface AgentPlanPanelProps {
  plan?: AgentPlan | null;
  workflow?: string;
  detectedTask?: string;
}

export const AgentPlanPanel: React.FC<AgentPlanPanelProps> = ({ plan, workflow, detectedTask }) => {
  if (!plan) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center text-slate-400">
        <BrainCircuit className="w-8 h-8 mx-auto mb-2 text-indigo-400 opacity-60 animate-pulse" />
        <p className="text-sm font-medium">No Agent Plan Available</p>
        <p className="text-xs text-slate-500 mt-1">Submit a query or load a scenario to view the autonomous decision graph.</p>
      </div>
    );
  }

  const {
    intent,
    reasoning_summary,
    required_modalities = [],
    selected_tools = [],
    execution_order = [],
    skipped_tools = [],
    estimated_latency_ms
  } = plan;

  return (
    <div className="space-y-6">
      {/* Top Banner: Intent & Core Metrics */}
      <div className="bg-gradient-to-r from-indigo-950/70 via-slate-900/90 to-purple-950/70 border border-indigo-500/30 rounded-xl p-5 shadow-lg relative overflow-hidden">
        <div className="absolute top-0 right-0 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-wrap items-center justify-between gap-3 relative z-10">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-600/30 border border-indigo-400/40 rounded-lg text-indigo-300">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase tracking-wider font-semibold text-indigo-400">Autonomous Agent Plan</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  Dynamic Controller
                </span>
              </div>
              <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                Intent: <span className="text-indigo-300 font-mono">{intent || detectedTask}</span>
              </h3>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono text-slate-300">
            {estimated_latency_ms ? (
              <div className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1.5 rounded-md border border-slate-700/60">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                <span>Est. Latency: {estimated_latency_ms} ms</span>
              </div>
            ) : null}
            <div className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1.5 rounded-md border border-slate-700/60">
              <Layers className="w-3.5 h-3.5 text-amber-400" />
              <span>Workflow: {workflow || 'Adaptive'}</span>
            </div>
          </div>
        </div>

        {/* Reasoning Narrative */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 text-sm text-slate-300 leading-relaxed">
          <div className="flex items-start gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
            <p><span className="font-semibold text-slate-200">Planner Rationale: </span>{reasoning_summary}</p>
          </div>
        </div>

        {/* Modality Chips */}
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Input Analysis Required:</span>
          {required_modalities.map((mod) => (
            <span
              key={mod}
              className="px-2.5 py-0.5 rounded text-xs font-mono font-medium bg-cyan-950/60 text-cyan-300 border border-cyan-700/50 uppercase"
            >
              {mod}
            </span>
          ))}
        </div>
      </div>

      {/* Execution Sequence Flow */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
        <h4 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          Planned Tool Execution Chain ({selected_tools.length} Tools)
        </h4>

        <div className="flex flex-wrap items-center gap-2">
          {(execution_order.length > 0 ? execution_order : selected_tools).map((toolName, idx, arr) => (
            <React.Fragment key={toolName}>
              <div className="flex items-center gap-2 bg-slate-800/90 hover:bg-slate-800 border border-emerald-500/30 hover:border-emerald-500/60 px-3.5 py-2 rounded-lg transition-all shadow-sm">
                <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono text-xs flex items-center justify-center font-bold">
                  {idx + 1}
                </span>
                <span className="font-mono text-xs font-semibold text-emerald-300">
                  {toolName}
                </span>
              </div>
              {idx < arr.length - 1 && (
                <ArrowRight className="w-4 h-4 text-slate-500 shrink-0" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Skipped Tools & Reasons */}
      <div className="bg-slate-900/80 border border-amber-500/20 rounded-xl p-5">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-semibold text-amber-300 uppercase tracking-wider flex items-center gap-2">
            <XCircle className="w-4 h-4 text-amber-400" />
            Skipped Specialist Tools & Rationale ({skipped_tools.length})
          </h4>
          <span className="text-[11px] text-slate-400 font-mono bg-amber-950/40 px-2 py-0.5 rounded border border-amber-500/30">
            Compute Optimization
          </span>
        </div>
        <p className="text-xs text-slate-400 mb-4">
          To prevent redundant computation, modality mismatches, and hallucinations, the agent actively pruned the following specialist models:
        </p>

        {skipped_tools.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No specialist models were pruned for this input combination.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {skipped_tools.map((skip, idx) => (
              <div
                key={idx}
                className="bg-slate-950/60 border border-slate-800/80 hover:border-slate-700/80 rounded-lg p-3 text-xs transition-colors"
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="font-mono font-bold text-slate-300 bg-slate-800/90 px-2 py-0.5 rounded text-[11px]">
                    {skip.tool}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase bg-amber-500/10 text-amber-400 border border-amber-500/30">
                    Pruned
                  </span>
                </div>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  <span className="text-slate-500 font-medium">Reason: </span>
                  {skip.reason}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
