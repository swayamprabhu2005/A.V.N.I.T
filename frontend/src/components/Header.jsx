import React from 'react';
import { Shield, Database, Cpu, Activity } from 'lucide-react';

export default function Header({ statusData, onOpenDbModal }) {
  const isOnline = statusData?.status === "online";
  const plateLoaded = statusData?.models?.plate_detector?.loaded;
  const colorLoaded = statusData?.models?.color_classifier?.loaded;
  const ocrLoaded = statusData?.models?.plate_ocr?.loaded;

  return (
    <header className="bg-card border-b border-border px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4 sticky top-0 z-40 shadow-xl backdrop-blur-md bg-opacity-95">
      <div className="flex items-center gap-4">
        <div className="relative">
          <img 
            src="/AVNIT.png" 
            alt="AVNIT Logo" 
            className="w-12 h-12 rounded-xl object-contain shadow-lg ring-2 ring-blue-500/30"
          />
          <span className="absolute -bottom-1 -right-1 flex h-3 w-3">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isOnline ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
            <span className={`relative inline-flex rounded-full h-3 w-3 ${isOnline ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
          </span>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              A.V.N.I.T.
            </h1>
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
              AI Identity Tampering Detection
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time Registration Attribute Verification & Visual Anomaly Scoring
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        {/* Model Status Indicators */}
        <div className="flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-border text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-slate-400">YOLO Plate:</span>
            <span className={plateLoaded ? "text-emerald-400" : "text-amber-400"}>
              {plateLoaded ? "Colab Model" : "Active (Heuristic)"}
            </span>
          </div>
          <span className="text-slate-600">|</span>
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Color CNN:</span>
            <span className={colorLoaded ? "text-emerald-400" : "text-amber-400"}>
              {colorLoaded ? "Colab Model" : "Active (CV)"}
            </span>
          </div>
          <span className="text-slate-600">|</span>
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">OCR NN:</span>
            <span className={ocrLoaded ? "text-emerald-400" : "text-amber-400"}>
              {ocrLoaded ? "Colab Model" : "Active (EasyOCR)"}
            </span>
          </div>
        </div>

        {/* Database Management Trigger */}
        <button
          onClick={onOpenDbModal}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white px-3.5 py-1.5 rounded-lg text-xs font-medium transition shadow-md shadow-blue-500/20"
        >
          <Database className="w-4 h-4" />
          <span>Vehicle Database</span>
        </button>
      </div>
    </header>
  );
}
