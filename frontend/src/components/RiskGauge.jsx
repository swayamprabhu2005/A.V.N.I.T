import React from 'react';
import { Gauge, CheckCircle2, XCircle } from 'lucide-react';

export default function RiskGauge({ riskResult }) {
  const score = riskResult ? riskResult.risk_score : 0;
  const factors = riskResult?.factor_scores || {
    type_match: 1.0,
    color_match: 1.0,
    ocr_confidence: 1.0,
    make_model_match: 1.0
  };

  const getScoreColor = (val) => {
    if (val < 25) return "#10B981"; // Emerald
    if (val <= 60) return "#F59E0B"; // Amber
    return "#EF4444"; // Red
  };

  const strokeColor = getScoreColor(score);
  // Circle radius & circumference
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
      <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Gauge className="w-4 h-4 text-blue-400" />
          <span>4-Factor Risk Engine Breakdown</span>
        </h3>
        <span className="text-[11px] font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-border">
          Algorithm v1.0
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 items-center">
        {/* Circular Gauge */}
        <div className="flex flex-col items-center justify-center">
          <div className="relative w-36 h-36 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="72"
                cy="72"
                r={radius}
                className="text-slate-800 stroke-current"
                strokeWidth="12"
                fill="transparent"
              />
              <circle
                cx="72"
                cy="72"
                r={radius}
                style={{
                  stroke: strokeColor,
                  strokeDasharray: circumference,
                  strokeDashoffset: strokeDashoffset,
                  transition: "stroke-dashoffset 0.5s ease, stroke 0.5s ease"
                }}
                strokeWidth="12"
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-2xl font-black font-mono text-white tracking-tight">
                {score}%
              </span>
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">
                Anomaly
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400 mt-2">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span>&lt;25% Safe</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500"></span>25-60% Mid</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-rose-500"></span>&gt;60% Danger</span>
          </div>
        </div>

        {/* 4 Factor Bars */}
        <div className="space-y-3">
          {/* Factor 1: Vehicle Type (35%) */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 font-medium">Vehicle Type Match (35%)</span>
              <span className="font-mono text-slate-400">
                {factors.type_match >= 1.0 ? "100% Match" : "0% Mismatch"}
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${factors.type_match >= 1.0 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                style={{ width: `${factors.type_match * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Factor 2: Vehicle Color (20%) */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 font-medium">Color Match (20%)</span>
              <span className="font-mono text-slate-400">
                {Math.round(factors.color_match * 100)}%
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${factors.color_match >= 0.7 ? 'bg-emerald-500' : factors.color_match >= 0.4 ? 'bg-amber-500' : 'bg-rose-500'}`}
                style={{ width: `${factors.color_match * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Factor 3: OCR Confidence (20%) */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 font-medium">Plate OCR Confidence (20%)</span>
              <span className="font-mono text-slate-400">
                {Math.round(factors.ocr_confidence * 100)}%
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div 
                className="bg-blue-500 h-full transition-all duration-500" 
                style={{ width: `${factors.ocr_confidence * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Factor 4: Make & Model (25%) */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 font-medium">Make & Model (25%)</span>
              <span className="font-mono text-slate-400">
                {Math.round(factors.make_model_match * 100)}%
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div 
                className="bg-purple-500 h-full transition-all duration-500" 
                style={{ width: `${factors.make_model_match * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
