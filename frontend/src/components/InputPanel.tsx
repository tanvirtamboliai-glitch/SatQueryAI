import React, { useRef, useState } from 'react';
import {
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Layers,
  Compass,
  Zap,
  Globe2,
  Trash2,
  FolderOpen,
  ChevronDown,
  ChevronUp,
  Cpu
} from 'lucide-react';
import { ImageMetadata, ValidationResponse, DemoScenario } from '../types';

interface InputPanelProps {
  mode: 'single' | 'bi_temporal' | 'optical_sar';
  setMode: (mode: 'single' | 'bi_temporal' | 'optical_sar') => void;
  image1: ImageMetadata | null;
  image2: ImageMetadata | null;
  validation: ValidationResponse | null;
  onFileUpload: (file: File, target: 'image1' | 'image2') => void;
  onMultiFileUpload?: (files: FileList | File[]) => void;
  onRemoveSlot?: (slot: 'image1' | 'image2') => void;
  isUploading: boolean;
  demoSamples: DemoScenario[];
  onSelectDemo: (demo: DemoScenario) => void;
  onClear: () => void;
}

export const InputPanel: React.FC<InputPanelProps> = ({
  mode,
  setMode,
  image1,
  image2,
  validation,
  onFileUpload,
  onMultiFileUpload,
  onRemoveSlot,
  isUploading,
  demoSamples,
  onSelectDemo,
  onClear
}) => {
  const fileInputRef1 = useRef<HTMLInputElement>(null);
  const fileInputRef2 = useRef<HTMLInputElement>(null);
  const [showPresets, setShowPresets] = useState<boolean>(false);
  const [dragActive1, setDragActive1] = useState<boolean>(false);
  const [dragActive2, setDragActive2] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, target: 'image1' | 'image2') => {
    if (e.target.files && e.target.files.length > 0) {
      if (e.target.files.length > 1 && onMultiFileUpload) {
        onMultiFileUpload(e.target.files);
      } else {
        onFileUpload(e.target.files[0], target);
      }
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>, target: 'image1' | 'image2') => {
    e.preventDefault();
    e.stopPropagation();
    if (target === 'image1') setDragActive1(false);
    else setDragActive2(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (e.dataTransfer.files.length > 1 && onMultiFileUpload) {
        onMultiFileUpload(e.dataTransfer.files);
      } else {
        onFileUpload(e.dataTransfer.files[0], target);
      }
    }
  };

  return (
    <div className="flex flex-col space-y-4 bg-slate-900/95 border border-slate-800 rounded-xl p-4 text-xs shadow-xl">
      {/* Platform Header & Workflow Mode */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="font-bold uppercase tracking-wider text-slate-300 font-mono text-[11px] flex items-center space-x-1.5">
            <Globe2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Satellite Input Pipeline</span>
          </span>
          {(image1 || image2) && (
            <button
              onClick={onClear}
              className="text-[11px] text-slate-400 hover:text-rose-400 flex items-center space-x-1 transition-colors"
            >
              <Trash2 className="w-3 h-3" />
              <span>Clear</span>
            </button>
          )}
        </div>

        {/* Workflow Switcher */}
        <div className="grid grid-cols-3 gap-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800 font-mono text-[11px]">
          <button
            onClick={() => setMode('single')}
            className={`py-1.5 px-2 rounded font-medium transition-all text-center ${
              mode === 'single'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 font-bold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Single Scene
          </button>
          <button
            onClick={() => setMode('bi_temporal')}
            className={`py-1.5 px-2 rounded font-medium transition-all text-center ${
              mode === 'bi_temporal'
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/40 font-bold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Bi-Temporal
          </button>
          <button
            onClick={() => setMode('optical_sar')}
            className={`py-1.5 px-2 rounded font-medium transition-all text-center ${
              mode === 'optical_sar'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-bold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Optical + SAR
          </button>
        </div>
      </div>

      {/* Primary Imagery Upload Dropzone (Slot 1) */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <span className="font-bold text-slate-300">
            {mode === 'bi_temporal' ? 'Epoch T1 Baseline Imagery' : mode === 'optical_sar' ? 'Optical Radiometric Sensor' : 'Primary Remote Sensing Scene'}
          </span>
          {image1 && (
            <span className="text-emerald-400 flex items-center font-bold">
              <CheckCircle2 className="w-3 h-3 mr-0.5" /> Validated
            </span>
          )}
        </div>

        <input
          type="file"
          ref={fileInputRef1}
          onChange={(e) => handleFileChange(e, 'image1')}
          accept=".tif,.tiff,.png,.jpg,.jpeg"
          className="hidden"
        />

        {!image1 ? (
          <div
            onClick={() => fileInputRef1.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragActive1(true); }}
            onDragLeave={() => setDragActive1(false)}
            onDrop={(e) => handleDrop(e, 'image1')}
            className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all ${
              dragActive1
                ? 'border-cyan-400 bg-cyan-950/30'
                : 'border-slate-700/80 hover:border-cyan-500/60 bg-slate-950/60 hover:bg-slate-950'
            }`}
          >
            <UploadCloud className="w-7 h-7 mx-auto mb-2 text-cyan-400" />
            <p className="font-bold text-slate-200 text-xs">Drop Remote Sensing Imagery Here</p>
            <p className="text-[10px] text-slate-400 mt-1 font-mono">
              GeoTIFF (.tif, .tiff), PNG, JPEG • Auto-extracts CRS &amp; bands
            </p>
          </div>
        ) : (
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 flex flex-col space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 overflow-hidden">
                <img
                  src={image1.preview_url || undefined}
                  alt="Scene 1 Preview"
                  className="w-14 h-14 rounded-lg object-cover border border-slate-800 bg-black flex-shrink-0"
                />
                <div className="overflow-hidden flex-1">
                  <p className="font-bold text-slate-100 truncate text-xs">{image1.filename}</p>
                  <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono mt-1">
                    <span className="px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 font-bold uppercase">
                      {image1.modality}
                    </span>
                    <span className="text-slate-400">{image1.dimensions[0]}×{image1.dimensions[1]}</span>
                    <span className="text-slate-500">•</span>
                    <span className="text-slate-400">{image1.bands} bands</span>
                  </div>
                </div>
              </div>

              {onRemoveSlot && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveSlot('image1');
                  }}
                  title="Remove Image 1"
                  className="p-1.5 rounded text-slate-500 hover:text-rose-400 hover:bg-slate-900 transition-colors ml-1 cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Detailed GIS Telemetry */}
            <div className="pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400">
              <div>Sensor: <span className="text-slate-200">{image1.sensor || 'Sentinel/Aerial'}</span></div>
              <div>Format: <span className="text-slate-200">{image1.format}</span></div>
              <div className="col-span-2 truncate">CRS: <span className="text-slate-300">{image1.crs || 'EPSG:4326'}</span></div>
            </div>
          </div>
        )}
      </div>

      {/* Secondary Imagery Upload Dropzone (Slot 2) */}
      {(mode === 'bi_temporal' || mode === 'optical_sar') && (
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span className="font-bold text-slate-300">
              {mode === 'bi_temporal' ? 'Epoch T2 Comparison Imagery' : 'SAR Microwave Sensor (Sentinel-1)'}
            </span>
            {image2 && (
              <span className="text-emerald-400 flex items-center font-bold">
                <CheckCircle2 className="w-3 h-3 mr-0.5" /> Validated
              </span>
            )}
          </div>

          <input
            type="file"
            ref={fileInputRef2}
            onChange={(e) => handleFileChange(e, 'image2')}
            accept=".tif,.tiff,.png,.jpg,.jpeg"
            className="hidden"
          />

          {!image2 ? (
            <div
              onClick={() => fileInputRef2.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragActive2(true); }}
              onDragLeave={() => setDragActive2(false)}
              onDrop={(e) => handleDrop(e, 'image2')}
              className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all ${
                dragActive2
                  ? 'border-blue-400 bg-blue-950/30'
                  : 'border-slate-700/80 hover:border-blue-500/60 bg-slate-950/60 hover:bg-slate-950'
              }`}
            >
              <UploadCloud className="w-7 h-7 mx-auto mb-2 text-blue-400" />
              <p className="font-bold text-slate-200 text-xs">
                {mode === 'bi_temporal' ? 'Upload Second Temporal Epoch' : 'Upload Co-Registered SAR Raster'}
              </p>
              <p className="text-[10px] text-slate-400 mt-1 font-mono">
                Will verify geographic extent &amp; resolution ratio
              </p>
            </div>
          ) : (
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 flex flex-col space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 overflow-hidden">
                  <img
                    src={image2.preview_url || undefined}
                    alt="Scene 2 Preview"
                    className="w-14 h-14 rounded-lg object-cover border border-slate-800 bg-black flex-shrink-0"
                  />
                  <div className="overflow-hidden flex-1">
                    <p className="font-bold text-slate-100 truncate text-xs">{image2.filename}</p>
                    <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono mt-1">
                      <span className="px-1.5 py-0.2 rounded bg-blue-500/20 text-blue-300 font-bold uppercase">
                        {image2.modality}
                      </span>
                      <span className="text-slate-400">{image2.dimensions[0]}×{image2.dimensions[1]}</span>
                      <span className="text-slate-500">•</span>
                      <span className="text-slate-400">{image2.bands} bands</span>
                    </div>
                  </div>
                </div>

                {onRemoveSlot && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveSlot('image2');
                    }}
                    title="Remove Image 2"
                    className="p-1.5 rounded text-slate-500 hover:text-rose-400 hover:bg-slate-900 transition-colors ml-1 cursor-pointer"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Detailed GIS Telemetry */}
              <div className="pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400">
                <div>Sensor: <span className="text-slate-200">{image2.sensor || 'Sentinel-1 C-SAR'}</span></div>
                <div>Format: <span className="text-slate-200">{image2.format}</span></div>
                <div className="col-span-2 truncate">CRS: <span className="text-slate-300">{image2.crs || 'EPSG:4326'}</span></div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Agent Autonomy Workflow Banner */}
      {validation && validation.suggested_workflow && (
        <div className="p-2.5 rounded-lg bg-cyan-950/25 border border-cyan-500/40 text-cyan-300 font-mono text-[11px] flex items-center space-x-2">
          <Cpu className="w-3.5 h-3.5 flex-shrink-0 text-cyan-400 animate-pulse" />
          <span className="truncate">
            Agent Mode: <strong className="text-white">{validation.suggested_workflow}</strong>
          </span>
        </div>
      )}

      {/* Spatial Pair Validation Badge */}
      {validation && validation.pair_validation && (
        <div className={`p-3 rounded-xl border font-mono text-[11px] ${
          validation.pair_validation.valid
            ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-300'
            : 'bg-rose-950/20 border-rose-500/40 text-rose-300'
        }`}>
          <div className="flex items-center justify-between font-bold mb-1">
            <span className="flex items-center space-x-1.5">
              {validation.pair_validation.valid ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              )}
              <span>Pair Alignment: {validation.pair_validation.valid ? 'COMPATIBLE' : 'DISJOINT'}</span>
            </span>
            <span className="text-cyan-400">{validation.pair_validation.spatial_overlap_pct}% Overlap</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1 flex justify-between">
            <span>CRS: {validation.pair_validation.crs_match ? 'Matching' : 'Auto-resampled'}</span>
            <span>Ratio: {validation.pair_validation.resolution_ratio}x</span>
          </div>
        </div>
      )}

      {/* Pre-Indexed Benchmark Presets (Collapsible) */}
      <div className="pt-2 border-t border-slate-800">
        <button
          onClick={() => setShowPresets(!showPresets)}
          className="w-full flex items-center justify-between py-2 text-slate-400 hover:text-slate-200 font-mono text-[11px] transition-colors"
        >
          <span className="flex items-center space-x-1.5">
            <FolderOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span>Pre-Indexed Satellite Datasets ({demoSamples.length})</span>
          </span>
          {showPresets ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {showPresets && (
          <div className="space-y-1.5 mt-2">
            {demoSamples.map((demo) => (
              <button
                key={demo.id}
                onClick={() => {
                  onSelectDemo(demo);
                  setShowPresets(false);
                }}
                className="w-full text-left px-3 py-2 rounded-lg bg-slate-950 hover:bg-slate-800/80 border border-slate-800 hover:border-cyan-500/50 transition-all flex items-center justify-between group"
              >
                <div className="truncate mr-2">
                  <div className="text-slate-200 font-bold truncate group-hover:text-cyan-400 transition-colors text-[11px]">
                    {demo.title}
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono truncate">{demo.expected_task}</div>
                </div>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300 font-mono group-hover:bg-cyan-500 group-hover:text-slate-950 font-bold">
                  Load
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
