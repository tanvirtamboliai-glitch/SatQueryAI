import React, { useState, useEffect } from 'react';
import { InputPanel } from './InputPanel';
import { ImageViewer } from './ImageViewer';
import { QueryPanel } from './QueryPanel';
import { ResultsPanel } from './ResultsPanel';
import {
  ImageMetadata,
  ValidationResponse,
  AnalysisResult,
  DemoScenario
} from '../types';
import {
  uploadImageFile,
  validateImagePair,
  submitAnalysis,
  fetchSamples
} from '../services/api';

interface WorkspaceProps {
  initialMode?: 'single' | 'bi_temporal' | 'optical_sar';
}

export const Workspace: React.FC<WorkspaceProps> = ({ initialMode = 'single' }) => {
  const [mode, setMode] = useState<'single' | 'bi_temporal' | 'optical_sar'>(initialMode);
  const [image1, setImage1] = useState<ImageMetadata | null>(null);
  const [image2, setImage2] = useState<ImageMetadata | null>(null);
  const [validation, setValidation] = useState<ValidationResponse | null>(null);
  const [query, setQuery] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [demoSamples, setDemoSamples] = useState<DemoScenario[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load demo samples on mount
  useEffect(() => {
    fetchSamples()
      .then((samples) => {
        setDemoSamples(samples);
        // Default load Demo 1 so user immediately sees an active scene
        if (samples.length > 0 && !image1) {
          handleSelectDemo(samples[0]);
        }
      })
      .catch((err) => console.error('Failed to load demo samples:', err));
  }, []);

  // Update mode when initialMode changes
  useEffect(() => {
    setMode(initialMode);
  }, [initialMode]);

  // Handle uploading files
  const handleFileUpload = async (file: File, target: 'image1' | 'image2') => {
    setIsUploading(true);
    setErrorMessage(null);
    try {
      const meta = await uploadImageFile(file);
      if (target === 'image1') {
        setImage1(meta);
        if (image2) {
          const val = await validateImagePair(meta.file_id, image2.file_id);
          setValidation(val);
          if (val.detected_mode !== 'invalid') {
            setMode(val.detected_mode as any);
          }
        }
      } else {
        setImage2(meta);
        if (image1) {
          const val = await validateImagePair(image1.file_id, meta.file_id);
          setValidation(val);
          if (val.detected_mode !== 'invalid') {
            setMode(val.detected_mode as any);
          }
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  // Multi-file drag and drop (e.g. dropping 1 or 2 files at once)
  const handleMultiFileUpload = async (files: FileList | File[]) => {
    if (!files || files.length === 0) return;
    setIsUploading(true);
    setErrorMessage(null);

    try {
      if (files.length === 1) {
        await handleFileUpload(files[0], !image1 ? 'image1' : 'image2');
      } else {
        // User dropped 2 files simultaneously!
        const meta1 = await uploadImageFile(files[0]);
        const meta2 = await uploadImageFile(files[1]);
        setImage1(meta1);
        setImage2(meta2);

        const val = await validateImagePair(meta1.file_id, meta2.file_id);
        setValidation(val);
        if (val.detected_mode !== 'invalid') {
          setMode(val.detected_mode as any);
        } else {
          setMode('bi_temporal');
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Multi-file upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  // Remove individual slot
  const handleRemoveSlot = (slot: 'image1' | 'image2') => {
    if (slot === 'image1') {
      setImage1(image2);
      setImage2(null);
      setMode('single');
      setValidation(null);
    } else {
      setImage2(null);
      setMode('single');
      setValidation(null);
    }
    setResult(null);
  };

  // Select pre-configured demo scenario
  const handleSelectDemo = (demo: DemoScenario) => {
    setMode(demo.mode);
    setQuery(demo.query);
    setResult(null);
    setErrorMessage(null);

    const m1: ImageMetadata = {
      file_id: demo.image1_id,
      filename: demo.image1_id.replace('sample_', '').replace(/_/g, '.'),
      format: 'GeoTIFF',
      dimensions: [512, 512],
      bands: demo.mode === 'optical_sar' ? 3 : 3,
      crs: 'EPSG:4326',
      geotransform: [12.45, 0.0001, 0.0, 41.95, 0.0, -0.0001],
      bounds: [12.45, 41.85, 12.55, 41.95],
      resolution: [10.0, 10.0],
      modality: 'optical',
      acquisition_date: demo.mode === 'bi_temporal' ? '2022-05-10' : '2024-08-12',
      sensor: 'Sentinel-2 MSI',
      is_valid: true,
      warnings: [],
      preview_url: demo.preview1,
    };

    let m2: ImageMetadata | null = null;
    if (demo.image2_id) {
      m2 = {
        file_id: demo.image2_id,
        filename: demo.image2_id.replace('sample_', '').replace(/_/g, '.'),
        format: 'GeoTIFF',
        dimensions: [512, 512],
        bands: demo.mode === 'optical_sar' ? 1 : 3,
        crs: 'EPSG:4326',
        geotransform: [12.45, 0.0001, 0.0, 41.95, 0.0, -0.0001],
        bounds: [12.45, 41.85, 12.55, 41.95],
        resolution: [10.0, 10.0],
        modality: demo.mode === 'optical_sar' ? 'sar' : 'optical',
        acquisition_date: demo.mode === 'bi_temporal' ? '2025-06-15' : '2024-08-12',
        sensor: demo.mode === 'optical_sar' ? 'Sentinel-1 C-SAR' : 'Sentinel-2 MSI',
        is_valid: true,
        warnings: [],
        preview_url: demo.preview2,
      };
    }

    setImage1(m1);
    setImage2(m2);

    if (m2) {
      setValidation({
        valid: true,
        detected_mode: demo.mode,
        image1: m1,
        image2: m2,
        pair_validation: {
          valid: true,
          pair_type: demo.mode,
          spatial_overlap_pct: 100.0,
          crs_match: true,
          resolution_ratio: 1.0,
          warnings: [],
        },
        suggested_workflow: demo.expected_task,
        warnings: [],
      });
    } else {
      setValidation({
        valid: true,
        detected_mode: 'single',
        image1: m1,
        suggested_workflow: demo.expected_task,
        warnings: [],
      });
    }
  };

  const handleClear = () => {
    setImage1(null);
    setImage2(null);
    setValidation(null);
    setResult(null);
    setQuery('');
    setErrorMessage(null);
  };

  const handleAnalyze = async () => {
    if (!image1 || !query.trim()) return;
    setIsAnalyzing(true);
    setErrorMessage(null);

    try {
      const res = await submitAnalysis(
        query,
        image1.file_id,
        image2?.file_id,
        mode
      );
      setResult(res);
    } catch (err: any) {
      setErrorMessage(err.message || 'Analysis failed. Check server logs.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const canSubmit = Boolean(
    image1 &&
    ((mode === 'single') || (image2 && (mode === 'bi_temporal' || mode === 'optical_sar')))
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {errorMessage && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-500/50 text-rose-300 text-xs font-mono flex items-center justify-between">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} className="text-rose-400 font-bold ml-2">
            Dismiss
          </button>
        </div>
      )}

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Input Panel (4 Cols) */}
        <div className="lg:col-span-4 space-y-4">
          <InputPanel
            mode={mode}
            setMode={setMode}
            image1={image1}
            image2={image2}
            validation={validation}
            onFileUpload={handleFileUpload}
            onMultiFileUpload={handleMultiFileUpload}
            onRemoveSlot={handleRemoveSlot}
            isUploading={isUploading}
            demoSamples={demoSamples}
            onSelectDemo={handleSelectDemo}
            onClear={handleClear}
          />
        </div>

        {/* Right Column: Viewer + Query + Results (8 Cols) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Viewer */}
          <ImageViewer
            image1Url={image1?.preview_url}
            image2Url={image2?.preview_url}
            image1={image1}
            image2={image2}
            evidence={result?.evidence}
            mode={mode}
            title1={mode === 'bi_temporal' ? 'Epoch T1' : mode === 'optical_sar' ? 'Optical (S2)' : 'Scene'}
            title2={mode === 'bi_temporal' ? 'Epoch T2' : mode === 'optical_sar' ? 'SAR (S1)' : 'Secondary'}
          />

          {/* Query Bar */}
          <QueryPanel
            query={query}
            setQuery={setQuery}
            onSubmit={handleAnalyze}
            isAnalyzing={isAnalyzing}
            mode={mode}
            canSubmit={canSubmit}
          />

          {/* Results Panel */}
          <ResultsPanel result={result} />
        </div>
      </div>
    </div>
  );
};
