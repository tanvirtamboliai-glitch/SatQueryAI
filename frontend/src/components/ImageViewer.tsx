import React, { useState, useRef, useEffect } from 'react';
import {
  Layers,
  Maximize2,
  Sliders,
  Eye,
  EyeOff,
  Download,
  SplitSquareVertical,
  Columns,
  Square,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Navigation,
  Crosshair,
  Compass
} from 'lucide-react';
import { VisualEvidence, BoundingBox, ImageMetadata } from '../types';

interface ImageViewerProps {
  image1Url?: string | null;
  image2Url?: string | null;
  image1?: ImageMetadata | null;
  image2?: ImageMetadata | null;
  evidence?: VisualEvidence | null;
  mode?: 'single' | 'bi_temporal' | 'optical_sar';
  title1?: string;
  title2?: string;
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  image1Url,
  image2Url,
  image1,
  image2,
  evidence,
  mode = 'single',
  title1 = 'Primary Image (T1)',
  title2 = 'Secondary Image (T2)',
}) => {
  // Viewer state
  const [viewMode, setViewMode] = useState<'single' | 'side_by_side' | 'swipe'>(
    mode === 'bi_temporal' || mode === 'optical_sar' ? 'swipe' : 'single'
  );
  const [swipePos, setSwipePos] = useState<number>(50); // percentage 0..100
  const [overlayOpacity, setOverlayOpacity] = useState<number>(65); // percentage 0..100
  const [showBBoxes, setShowBBoxes] = useState<boolean>(true);
  const [showMask, setShowMask] = useState<boolean>(true);
  const [activeLayer, setActiveLayer] = useState<'original' | 'change_map' | 'composite'>('composite');
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  // Telemetry HUD state
  const [cursorTelemetry, setCursorTelemetry] = useState<{
    pixelX: number;
    pixelY: number;
    lat: number;
    lon: number;
    hasGeo: boolean;
    isHovering: boolean;
    sensor: string;
    crs: string;
    resolution: string;
  }>({
    pixelX: 256,
    pixelY: 256,
    lat: 41.8902,
    lon: 12.4922,
    hasGeo: true,
    isHovering: false,
    sensor: 'Sentinel-2 MSI',
    crs: 'EPSG:4326',
    resolution: '10.0m',
  });

  const containerRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef<boolean>(false);

  // Update default view mode when mode changes
  useEffect(() => {
    if (image2Url && (mode === 'bi_temporal' || mode === 'optical_sar')) {
      setViewMode('swipe');
    } else {
      setViewMode('single');
    }
  }, [mode, image2Url]);

  // Swipe drag handler
  const handleMouseDown = () => {
    isDragging.current = true;
  };

  const handleMouseUp = () => {
    isDragging.current = false;
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();

    if (isDragging.current) {
      const x = e.clientX - rect.left;
      const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setSwipePos(pct);
    }

    // Telemetry calculation based on active image
    const imgEl = containerRef.current.querySelector('img');
    if (imgEl) {
      const imgRect = imgEl.getBoundingClientRect();
      const x = e.clientX - imgRect.left;
      const y = e.clientY - imgRect.top;

      if (x >= 0 && x <= imgRect.width && y >= 0 && y <= imgRect.height) {
        const activeMeta = (viewMode === 'side_by_side' && x > imgRect.width / 2 && image2) ? image2 : (image1 || null);
        const origW = activeMeta?.dimensions?.[0] || 512;
        const origH = activeMeta?.dimensions?.[1] || 512;
        const pxX = Math.round((x / imgRect.width) * origW);
        const pxY = Math.round((y / imgRect.height) * origH);

        let lat = 41.8902;
        let lon = 12.4922;
        let hasGeo = false;

        if (activeMeta?.bounds && activeMeta.bounds.length === 4) {
          const [bL, bB, bR, bT] = activeMeta.bounds;
          const normX = x / imgRect.width;
          const normY = y / imgRect.height;
          lon = bL + normX * (bR - bL);
          lat = bT - normY * (bT - bB);
          hasGeo = true;
        }

        setCursorTelemetry({
          pixelX: pxX,
          pixelY: pxY,
          lat,
          lon,
          hasGeo,
          isHovering: true,
          sensor: activeMeta?.sensor || (activeMeta?.modality === 'sar' ? 'Sentinel-1 C-SAR' : 'Sentinel-2 MSI'),
          crs: activeMeta?.crs || 'EPSG:4326 (WGS 84)',
          resolution: activeMeta?.resolution ? `${activeMeta.resolution[0]}m` : '10.0m',
        });
      } else {
        setCursorTelemetry(prev => ({ ...prev, isHovering: false }));
      }
    }
  };

  const bboxes = evidence?.bboxes || [];
  const overlayUrl = evidence?.overlay_url;
  const changeMapUrl = evidence?.change_map_url;
  const maskUrl = evidence?.mask_url;

  return (
    <div className="flex flex-col h-full bg-[#0d1117] rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
      {/* Top Controls Toolbar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-2.5 bg-slate-900/90 border-b border-slate-800 gap-2 text-xs font-mono">
        {/* Left: View Mode Buttons */}
        <div className="flex items-center space-x-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setViewMode('single')}
            className={`px-2.5 py-1 rounded flex items-center space-x-1.5 font-medium transition-colors ${
              viewMode === 'single'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Square className="w-3.5 h-3.5" />
            <span>Single</span>
          </button>

          {image2Url && (
            <>
              <button
                onClick={() => setViewMode('swipe')}
                className={`px-2.5 py-1 rounded flex items-center space-x-1.5 font-medium transition-colors ${
                  viewMode === 'swipe'
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <SplitSquareVertical className="w-3.5 h-3.5" />
                <span>Swipe Slider</span>
              </button>

              <button
                onClick={() => setViewMode('side_by_side')}
                className={`px-2.5 py-1 rounded flex items-center space-x-1.5 font-medium transition-colors ${
                  viewMode === 'side_by_side'
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Columns className="w-3.5 h-3.5" />
                <span>Side-by-Side</span>
              </button>
            </>
          )}
        </div>

        {/* Center: Layer Toggles & Evidence Modifiers */}
        <div className="flex items-center space-x-3">
          {evidence && (
            <>
              {/* Layer Selection */}
              <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
                <button
                  onClick={() => setActiveLayer('original')}
                  className={`px-2 py-0.5 rounded text-[11px] ${
                    activeLayer === 'original'
                      ? 'bg-slate-800 text-white font-bold'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Original
                </button>
                <button
                  onClick={() => setActiveLayer('composite')}
                  className={`px-2 py-0.5 rounded text-[11px] ${
                    activeLayer === 'composite'
                      ? 'bg-cyan-500/20 text-cyan-400 font-bold'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Evidence Overlay
                </button>
                {changeMapUrl && (
                  <button
                    onClick={() => setActiveLayer('change_map')}
                    className={`px-2 py-0.5 rounded text-[11px] ${
                      activeLayer === 'change_map'
                        ? 'bg-rose-500/20 text-rose-400 font-bold'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Change Map
                  </button>
                )}
              </div>

              {/* Opacity Slider */}
              <div className="hidden lg:flex items-center space-x-2 px-2 py-1 bg-slate-950 rounded-lg border border-slate-800">
                <Sliders className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-[11px] text-slate-400">Opacity:</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={overlayOpacity}
                  onChange={(e) => setOverlayOpacity(Number(e.target.value))}
                  className="w-16 h-1 bg-slate-800 rounded appearance-none cursor-pointer accent-cyan-400"
                />
                <span className="text-[11px] text-cyan-400 w-7">{overlayOpacity}%</span>
              </div>

              {/* BBox Toggle */}
              {bboxes.length > 0 && (
                <button
                  onClick={() => setShowBBoxes(!showBBoxes)}
                  className={`px-2 py-1 rounded flex items-center space-x-1 text-[11px] border ${
                    showBBoxes
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : 'bg-slate-950 text-slate-400 border-slate-800'
                  }`}
                  title="Toggle Bounding Boxes"
                >
                  {showBBoxes ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                  <span>Boxes ({bboxes.length})</span>
                </button>
              )}
            </>
          )}

          {/* Zoom Controls */}
          <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.2))}
              className="p-1 text-slate-400 hover:text-white"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[10px] text-slate-300 w-8 text-center">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.2))}
              className="p-1 text-slate-400 hover:text-white"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoomLevel(1)}
              className="p-1 text-slate-400 hover:text-white ml-1 border-l border-slate-800 pl-1"
              title="Reset View"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Canvas / Image Area */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="relative flex-1 bg-black overflow-hidden flex items-center justify-center select-none cursor-crosshair min-h-[420px]"
      >
        {/* Live GIS Telemetry HUD Overlay */}
        {image1Url && (
          <div className="absolute top-3 right-3 z-30 pointer-events-none bg-slate-950/85 backdrop-blur-md border border-cyan-500/30 rounded-lg p-2.5 shadow-2xl font-mono text-[10px] space-y-1 min-w-[210px]">
            <div className="flex items-center justify-between text-cyan-400 border-b border-slate-800/80 pb-1 font-bold">
              <span className="flex items-center space-x-1.5">
                <Navigation className="w-3 h-3 text-cyan-400 animate-pulse" />
                <span>GIS TELEMETRY HUD</span>
              </span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-500/30">
                {cursorTelemetry.crs.split(' ')[0]}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-x-2 gap-y-0.5 text-slate-300 pt-0.5">
              <span className="text-slate-500">CURSOR LAT:</span>
              <span className="text-right font-bold text-slate-200">
                {cursorTelemetry.isHovering
                  ? `${cursorTelemetry.lat.toFixed(5)}° N`
                  : `${cursorTelemetry.lat.toFixed(5)}° N`}
              </span>

              <span className="text-slate-500">CURSOR LON:</span>
              <span className="text-right font-bold text-slate-200">
                {cursorTelemetry.isHovering
                  ? `${cursorTelemetry.lon.toFixed(5)}° E`
                  : `${cursorTelemetry.lon.toFixed(5)}° E`}
              </span>

              <span className="text-slate-500">RASTER PIXEL:</span>
              <span className="text-right text-cyan-300 font-bold">
                [{cursorTelemetry.pixelX}, {cursorTelemetry.pixelY}]
              </span>

              <span className="text-slate-500">GSD SCALE:</span>
              <span className="text-right text-slate-300">
                {cursorTelemetry.resolution}/px
              </span>

              <span className="text-slate-500">SENSOR:</span>
              <span className="text-right text-slate-300 truncate">
                {cursorTelemetry.sensor}
              </span>
            </div>
          </div>
        )}

        {!image1Url ? (
          <div className="text-center p-8 text-slate-500">
            <Layers className="w-12 h-12 mx-auto mb-3 opacity-30 animate-pulse" />
            <p className="text-sm font-semibold">No Image Loaded in Viewer</p>
            <p className="text-xs mt-1">Upload a GeoTIFF or select a Demo Scenario on the left to begin.</p>
          </div>
        ) : (
          <div
            style={{
              transform: `scale(${zoomLevel})`,
              transformOrigin: 'center center',
              transition: 'transform 0.15s ease-out',
            }}
            className="relative max-w-full max-h-full flex items-center justify-center"
          >
            {/* 1. SIDE-BY-SIDE VIEW */}
            {viewMode === 'side_by_side' && image2Url ? (
              <div className="grid grid-cols-2 gap-3 p-4 w-full h-full max-w-4xl">
                <div className="relative rounded-lg border border-slate-800 overflow-hidden bg-slate-950">
                  <div className="absolute top-2 left-2 z-10 px-2 py-0.5 rounded bg-black/70 text-[10px] text-cyan-300 font-mono">
                    {title1}
                  </div>
                  <img
                    src={image1Url}
                    alt={title1}
                    className="w-full h-auto object-contain max-h-[500px]"
                  />
                </div>
                <div className="relative rounded-lg border border-slate-800 overflow-hidden bg-slate-950">
                  <div className="absolute top-2 left-2 z-10 px-2 py-0.5 rounded bg-black/70 text-[10px] text-blue-300 font-mono">
                    {title2}
                  </div>
                  <img
                    src={image2Url}
                    alt={title2}
                    className="w-full h-auto object-contain max-h-[500px]"
                  />
                </div>
              </div>
            ) : viewMode === 'swipe' && image2Url ? (
              /* 2. INTERACTIVE SWIPE SLIDER */
              <div className="relative inline-block overflow-hidden shadow-2xl rounded-lg border border-slate-800">
                {/* Background Image (T2 / After) */}
                <img
                  src={image2Url}
                  alt={title2}
                  className="block max-h-[520px] max-w-full w-auto object-contain pointer-events-none"
                />

                {/* Foreground Clipped Image (T1 / Before) */}
                <div
                  className="absolute inset-0 overflow-hidden pointer-events-none"
                  style={{ width: `${swipePos}%` }}
                >
                  <img
                    src={image1Url}
                    alt={title1}
                    className="max-h-[520px] max-w-none h-full object-contain"
                    style={{ width: containerRef.current?.querySelector('img')?.clientWidth || 'auto' }}
                  />
                </div>

                {/* Evidence Overlay on T1/T2 if active */}
                {evidence && activeLayer !== 'original' && (
                  <div
                    className="absolute inset-0 pointer-events-none"
                    style={{ opacity: overlayOpacity / 100 }}
                  >
                    <img
                      src={activeLayer === 'change_map' && changeMapUrl ? changeMapUrl : overlayUrl || image1Url}
                      alt="Overlay"
                      className="w-full h-full object-contain"
                    />
                  </div>
                )}

                {/* Swipe Divider Bar */}
                <div
                  onMouseDown={handleMouseDown}
                  style={{ left: `${swipePos}%` }}
                  className="absolute top-0 bottom-0 w-1 bg-cyan-400 cursor-ew-resize z-30 shadow-[0_0_12px_rgba(56,189,248,0.8)]"
                >
                  <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-7 h-7 rounded-full bg-slate-900 border-2 border-cyan-400 flex items-center justify-center text-cyan-400 shadow-lg">
                    <SplitSquareVertical className="w-3.5 h-3.5" />
                  </div>
                </div>

                {/* Badges */}
                <div className="absolute bottom-3 left-3 z-20 px-2 py-1 rounded bg-black/80 border border-slate-800 text-[10px] text-slate-300 font-mono">
                  ◄ {title1}
                </div>
                <div className="absolute bottom-3 right-3 z-20 px-2 py-1 rounded bg-black/80 border border-slate-800 text-[10px] text-slate-300 font-mono">
                  {title2} ►
                </div>
              </div>
            ) : (
              /* 3. SINGLE IMAGE / OVERLAY VIEW */
              <div className="relative inline-block rounded-lg overflow-hidden border border-slate-800 shadow-2xl">
                {/* Base Image */}
                <img
                  src={image1Url}
                  alt="Base Scene"
                  className="block max-h-[520px] max-w-full w-auto object-contain"
                />

                {/* Mask / Change Map Overlay Layer */}
                {evidence && activeLayer !== 'original' && (
                  <div
                    className="absolute inset-0 pointer-events-none"
                    style={{ opacity: overlayOpacity / 100 }}
                  >
                    <img
                      src={
                        activeLayer === 'change_map' && changeMapUrl
                          ? changeMapUrl
                          : overlayUrl || image1Url
                      }
                      alt="Overlay Evidence"
                      className="w-full h-full object-contain"
                    />
                  </div>
                )}

                {/* SVG Bounding Boxes Overlay (Normalized 0..1000) */}
                {showBBoxes && bboxes.length > 0 && (
                  <svg
                    viewBox="0 0 1000 1000"
                    className="absolute inset-0 w-full h-full pointer-events-none z-20"
                    preserveAspectRatio="none"
                  >
                    {bboxes.map((b, idx) => {
                      const [ymin, xmin, ymax, xmax] = b.box_2d;
                      const bw = xmax - xmin;
                      const bh = ymax - ymin;
                      return (
                        <g key={idx}>
                          {/* Box Border */}
                          <rect
                            x={xmin}
                            y={ymin}
                            width={bw}
                            height={bh}
                            fill="rgba(56, 189, 248, 0.12)"
                            stroke="#38bdf8"
                            strokeWidth="3"
                            rx="4"
                          />
                          {/* Label Tag */}
                          <rect
                            x={xmin}
                            y={Math.max(0, ymin - 28)}
                            width={Math.min(300, (b.label.length * 10) + 16)}
                            height="24"
                            fill="#0f172a"
                            stroke="#38bdf8"
                            strokeWidth="1.5"
                            rx="3"
                          />
                          <text
                            x={xmin + 6}
                            y={Math.max(16, ymin - 12)}
                            fill="#38bdf8"
                            fontSize="13"
                            fontWeight="bold"
                            fontFamily="monospace"
                          >
                            {b.label}
                          </text>
                        </g>
                      );
                    })}
                  </svg>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Bottom Bar: Evidence Details Summary */}
      {evidence && (
        <div className="px-4 py-2 bg-slate-900 border-t border-slate-800 flex items-center justify-between text-xs text-slate-300">
          <div className="flex items-center space-x-3">
            <span className="text-slate-400 font-mono">Grounding:</span>
            <span className="text-cyan-400 font-semibold">{bboxes.length} Bounding Instances</span>
            {evidence.change_percentage !== null && evidence.change_percentage !== undefined && (
              <span className="text-rose-400 font-semibold border-l border-slate-700 pl-3">
                Change: +{evidence.change_percentage}%
              </span>
            )}
          </div>

          {evidence.overlay_url && (
            <a
              href={evidence.overlay_url}
              download="satquery_evidence_overlay.png"
              className="inline-flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 transition-colors font-medium"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Evidence Raster</span>
            </a>
          )}
        </div>
      )}
    </div>
  );
};
