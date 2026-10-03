import React, { useState, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Loader2,
  CheckCircle2,
  Clock,
  Cpu,
  Layers,
  ShieldCheck,
  Zap,
  ArrowRight
} from 'lucide-react';

interface QueryPanelProps {
  query: string;
  setQuery: (q: string) => void;
  onSubmit: () => void;
  isAnalyzing: boolean;
  mode: 'single' | 'bi_temporal' | 'optical_sar';
  canSubmit: boolean;
}

interface SpecialistPrediction {
  modelName: string;
  taskName: string;
  rationale: string;
  confidenceTag: string;
  badgeClass: string;
}

export const QueryPanel: React.FC<QueryPanelProps> = ({
  query,
  setQuery,
  onSubmit,
  isAnalyzing,
  mode,
  canSubmit,
}) => {
  // Live stage tracking during analysis
  const [activeStage, setActiveStage] = useState<number>(1);
  const [elapsedMs, setElapsedMs] = useState<number>(0);

  const stages = [
    { id: 1, name: 'Validating Input & GIS Extent', desc: 'CRS matching, spatial overlap check, band radiometric calibration' },
    { id: 2, name: '3-Layer Intent Routing', desc: 'Classifying semantic query intent across VQA, Grounding, Change, or Fusion' },
    { id: 3, name: 'Loading Specialist Weights', desc: 'Activating domain specialist architecture from Registry' },
    { id: 4, name: 'Executing Tensor Inference', desc: 'Radiometric feature extraction, CVA difference, or latent cross-attention' },
    { id: 5, name: 'Extracting Spatial Evidence', desc: 'Generating Otsu morphological masks and [ymin, xmin, ymax, xmax] tags' },
    { id: 6, name: 'Calibrating Multi-Factor Confidence', desc: 'Computing logit variance, GIS compatibility, and dossier generation' },
  ];

  useEffect(() => {
    let timer: any;
    let ticker: any;

    if (isAnalyzing) {
      setActiveStage(1);
      setElapsedMs(0);
      const startTime = Date.now();

      ticker = setInterval(() => {
        setElapsedMs(Date.now() - startTime);
      }, 100);

      timer = setInterval(() => {
        setActiveStage((prev) => (prev < 6 ? prev + 1 : prev));
      }, 350);
    } else {
      setActiveStage(1);
      setElapsedMs(0);
    }

    return () => {
      clearInterval(timer);
      clearInterval(ticker);
    };
  }, [isAnalyzing]);

  // Mode-specific example queries
  const examples = {
    single: [
      'Describe the land cover and major objects visible in this image.',
      'Highlight the water body.',
      'Identify built-up regions.',
      'What type of land cover is visible?'
    ],
    bi_temporal: [
      'What changed between these two dates?',
      'Has the built-up area increased?',
      'Where did construction occur?',
      'Did vegetation decrease?'
    ],
    optical_sar: [
      'Use the optical and SAR images together to identify built-up and water-covered regions.',
      'What additional information does SAR provide?',
      'Which regions are structurally different?'
    ]
  };

  const activeExamples = examples[mode] || examples.single;

  // Real-time Agent Specialist Model Routing Predictor
  const predictSpecialist = (text: string, currentMode: string): SpecialistPrediction => {
    const q = text.toLowerCase();

    if (currentMode === 'optical_sar' || q.includes('optical') || q.includes('sar') || q.includes('radar') || q.includes('backscatter') || q.includes('microwave') || q.includes('penetrate')) {
      return {
        modelName: 'Clay Foundation Model + Prithvi-EO-2.0',
        taskName: 'Cross-Sensor Latent Fusion',
        rationale: 'Fuses optical multi-spectral reflectance with SAR microwave backscatter to resolve surface footprints & penetrating radar signatures.',
        confidenceTag: 'Deep Latent MLP Fusion',
        badgeClass: 'text-emerald-400 bg-emerald-950/40 border-emerald-500/40'
      };
    }

    if (currentMode === 'bi_temporal' || q.includes('change') || q.includes('increased') || q.includes('decreased') || q.includes('what changed') || q.includes('construction') || q.includes('vegetation loss') || q.includes('difference') || q.includes('compare')) {
      return {
        modelName: 'Change-Agent-v2.0 + ChangeChat',
        taskName: 'Bi-Temporal Change Detection & VQA',
        rationale: 'Applies Siamese feature difference and Change Vector Analysis (CVA) with Otsu segmentation to quantify temporal area dynamics.',
        confidenceTag: 'Differential Siamese CVA',
        badgeClass: 'text-rose-400 bg-rose-950/40 border-rose-500/40'
      };
    }

    if (q.includes('highlight') || q.includes('locate') || q.includes('where') || q.includes('find') || q.includes('localize') || q.includes('demarcate') || q.includes('bound') || q.includes('outline') || q.includes('box')) {
      return {
        modelName: 'GeoGround-v1.2 + GeoChat-7B',
        taskName: 'Language-Guided Spatial Grounding',
        rationale: 'Performs natural-language spatial referring segmentation, extracting high-resolution contours and 0..1000 bounding coordinates.',
        confidenceTag: 'Referring Spatial Contours',
        badgeClass: 'text-amber-400 bg-amber-950/40 border-amber-500/40'
      };
    }

    if (q.includes('describe') || q.includes('caption') || q.includes('summary') || q.includes('overview') || q.includes('tell me about')) {
      return {
        modelName: 'GeoChat-7B Remote-Sensing VLM',
        taskName: 'Dense Remote Sensing Captioning',
        rationale: 'Extracts multi-scale radiometric tokens to construct comprehensive Earth Observation scene summaries & land-use classifications.',
        confidenceTag: 'Multi-Scale Radiometric VLM',
        badgeClass: 'text-cyan-400 bg-cyan-950/40 border-cyan-500/40'
      };
    }

    if (q.includes('similar') || q.includes('retrieve') || q.includes('rank') || q.includes('match')) {
      return {
        modelName: 'RemoteCLIP Contrastive',
        taskName: 'Domain-Adapted Representation Retrieval',
        rationale: 'Evaluates cosine similarity alignment in shared remote sensing vision-language embedding space.',
        confidenceTag: 'Contrastive Embedding Cosine',
        badgeClass: 'text-purple-400 bg-purple-950/40 border-purple-500/40'
      };
    }

    return {
      modelName: 'GeoChat-7B Remote-Sensing VLM',
      taskName: 'Radiometric Visual Question Answering',
      rationale: 'Instruction-tuned for remote sensing radiometric understanding, land cover reasoning, and terrain spatial questions.',
      confidenceTag: 'Zero-Shot Vision-Language',
      badgeClass: 'text-cyan-400 bg-cyan-950/40 border-cyan-500/40'
    };
  };

  const prediction = predictSpecialist(query, mode);

  return (
    <div className="bg-slate-900/95 border border-slate-800 rounded-xl p-4 flex flex-col space-y-3.5 shadow-xl">
      <div className="flex items-center justify-between">
        <span className="font-bold uppercase tracking-wider text-slate-300 font-mono text-[11px] flex items-center space-x-1.5">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Natural Language Remote Sensing Query</span>
        </span>
        <span className="text-[10px] text-slate-400 font-mono flex items-center space-x-1">
          <Zap className="w-3 h-3 text-amber-400" />
          <span>Real-Time Intent Routing Active</span>
        </span>
      </div>

      {/* Query Textarea & Submit */}
      <div className="relative">
        <textarea
          rows={2}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey && canSubmit && !isAnalyzing) {
              e.preventDefault();
              onSubmit();
            }
          }}
          placeholder="Ask SatQuery AI about land cover, surface modifications, water bodies, or temporal change..."
          className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-lg p-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/50 resize-none font-sans"
        />

        <button
          onClick={onSubmit}
          disabled={!canSubmit || isAnalyzing || !query.trim()}
          className={`absolute right-2.5 bottom-3 px-3.5 py-1.5 rounded-md text-xs font-bold flex items-center space-x-1.5 transition-all shadow-md ${
            canSubmit && !isAnalyzing && query.trim()
              ? 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 hover:shadow-cyan-500/20 cursor-pointer'
              : 'bg-slate-800 text-slate-500 cursor-not-allowed'
          }`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Executing...</span>
            </>
          ) : (
            <>
              <span>Execute</span>
              <Send className="w-3 h-3" />
            </>
          )}
        </button>
      </div>

      {/* Real-time Agent Specialist Model Routing Predictor Banner */}
      <div className={`p-2.5 rounded-lg border font-mono text-[11px] flex flex-col sm:flex-row sm:items-center justify-between gap-2 transition-all ${prediction.badgeClass}`}>
        <div className="flex items-start sm:items-center space-x-2">
          <Cpu className="w-3.5 h-3.5 flex-shrink-0 mt-0.5 sm:mt-0" />
          <div>
            <span className="font-bold uppercase tracking-wider text-[10px] mr-1.5 opacity-80">
              Agent Router:
            </span>
            <strong className="text-white">{prediction.modelName}</strong>
            <span className="text-slate-400 text-[10px] ml-1 hidden md:inline">
              ({prediction.taskName})
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-[10px] self-end sm:self-auto flex-shrink-0">
          <span className="px-2 py-0.5 rounded bg-black/40 border border-current font-semibold">
            {prediction.confidenceTag}
          </span>
        </div>
      </div>

      {/* Clickable Example Queries */}
      <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
        <span className="text-[10px] text-slate-400 font-mono mr-1">Suggestions:</span>
        {activeExamples.map((ex, i) => (
          <button
            key={i}
            onClick={() => setQuery(ex)}
            className="text-[11px] px-2.5 py-1 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/40 text-slate-300 hover:text-cyan-300 transition-all text-left cursor-pointer"
          >
            {ex}
          </button>
        ))}
      </div>

      {/* Observable Live 6-Stage Telemetry Stepper when running */}
      {isAnalyzing && (
        <div className="p-3.5 rounded-xl bg-slate-950 border border-cyan-500/40 text-[11px] font-mono space-y-2.5 shadow-2xl animate-in fade-in duration-200">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span>Orchestrating Specialist Pipeline</span>
            </div>
            <div className="text-[10px] text-slate-400 flex items-center space-x-2">
              <span>Elapsed: <strong className="text-cyan-300">{elapsedMs}ms</strong></span>
              <span className="px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/30">
                Step {activeStage}/6
              </span>
            </div>
          </div>

          {/* 6-Stage Progression Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
            {stages.map((st) => {
              const isDone = activeStage > st.id;
              const isCurrent = activeStage === st.id;
              return (
                <div
                  key={st.id}
                  className={`p-2 rounded-lg border transition-all flex items-start space-x-2 ${
                    isDone
                      ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
                      : isCurrent
                      ? 'bg-cyan-950/30 border-cyan-500/50 text-cyan-200 shadow-md'
                      : 'bg-slate-900/40 border-slate-800/60 text-slate-500'
                  }`}
                >
                  <div className="mt-0.5 flex-shrink-0">
                    {isDone ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    ) : isCurrent ? (
                      <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
                    ) : (
                      <Clock className="w-3.5 h-3.5 text-slate-600" />
                    )}
                  </div>
                  <div className="min-w-0">
                    <div className="font-bold text-[11px] truncate flex items-center justify-between">
                      <span>{st.name}</span>
                      {isDone && <span className="text-[9px] text-emerald-400 font-normal">OK</span>}
                    </div>
                    <div className="text-[9px] text-slate-400 truncate mt-0.5">
                      {st.desc}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
