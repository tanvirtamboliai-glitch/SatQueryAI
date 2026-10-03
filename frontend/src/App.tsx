import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { LandingHero } from './components/LandingHero';
import { Workspace } from './components/Workspace';
import { ArchitecturePage } from './components/ArchitecturePage';
import { EvaluationPage } from './components/EvaluationPage';
import { checkHealth, fetchModels } from './services/api';
import { Satellite, ShieldCheck } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<'workspace' | 'architecture' | 'evaluation'>('workspace');
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const [modelsCount, setModelsCount] = useState<number>(8);
  const [selectedInitialMode, setSelectedInitialMode] = useState<'single' | 'bi_temporal' | 'optical_sar'>('single');
  const [showHero, setShowHero] = useState<boolean>(true);

  // Poll backend health
  useEffect(() => {
    const poll = () => {
      checkHealth()
        .then(() => setIsBackendOnline(true))
        .catch(() => setIsBackendOnline(false));
    };
    poll();
    const interval = setInterval(poll, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch active models count
  useEffect(() => {
    fetchModels()
      .then((models) => setModelsCount(models.length))
      .catch((err) => console.log('Models not loaded yet:', err));
  }, [isBackendOnline]);

  const handleStartFromHero = (mode?: 'single' | 'bi_temporal' | 'optical_sar') => {
    if (mode) {
      setSelectedInitialMode(mode);
    }
    setActiveTab('workspace');
    setShowHero(false);
    // Smooth scroll to workspace
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#0b0f17] text-slate-100 flex flex-col selection:bg-cyan-500/30 selection:text-cyan-200">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isBackendOnline={isBackendOnline}
        modelsCount={modelsCount}
      />

      <main className="flex-1">
        {activeTab === 'workspace' && (
          <>
            {showHero && (
              <LandingHero onStart={handleStartFromHero} />
            )}
            <Workspace initialMode={selectedInitialMode} />
          </>
        )}

        {activeTab === 'architecture' && <ArchitecturePage />}

        {activeTab === 'evaluation' && <EvaluationPage />}
      </main>

      {/* Modern Scientific Footer */}
      <footer className="border-t border-slate-800/80 bg-[#090d14] py-8 text-xs text-slate-400 font-mono">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <Satellite className="w-4 h-4 text-cyan-400" />
            <span className="font-bold text-white tracking-wider">SATQUERY AI</span>
            <span>—</span>
            <span>Multimodal Remote Sensing Vision-Language Assistant</span>
          </div>

          <div className="flex items-center space-x-6 text-[11px]">
            <span>GeoChat • GeoGround • Change-Agent • Clay • Prithvi-EO-2.0</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-400 border border-slate-700">
              v1.0.0 Research Prototype
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
