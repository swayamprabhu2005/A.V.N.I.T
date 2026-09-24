import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, HelpCircle } from 'lucide-react';

export default function StatusBanner({ riskResult }) {
  if (!riskResult) {
    return (
      <div className="bg-card border border-border rounded-xl p-5 shadow-lg flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400">
            <HelpCircle className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-300">Awaiting Vehicle Observation</h3>
            <p className="text-xs text-slate-400">Stream camera feed or run a test scenario clip to initiate verification</p>
          </div>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-mono bg-slate-800 text-slate-400 border border-slate-700">
          STANDBY
        </span>
      </div>
    );
  }

  const { risk_level, risk_score, reason, plate_number } = riskResult;

  const isGreen = risk_level === "GREEN";
  const isYellow = risk_level === "YELLOW";
  const isRed = risk_level === "RED";

  let bgClass = "bg-emerald-950/30 border-emerald-500/40 text-emerald-400";
  let badgeClass = "bg-emerald-500/20 text-emerald-300 border-emerald-500/50";
  let title = "LIKELY VALID — IDENTITY CONFIRMED";
  let Icon = ShieldCheck;

  if (isYellow) {
    bgClass = "bg-amber-950/30 border-amber-500/40 text-amber-400";
    badgeClass = "bg-amber-500/20 text-amber-300 border-amber-500/50";
    title = "NEEDS REVIEW — SUSPICIOUS / UNCERTAIN";
    Icon = AlertTriangle;
  } else if (isRed) {
    bgClass = "bg-rose-950/30 border-rose-500/40 text-rose-400";
    badgeClass = "bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse";
    title = "HIGH-RISK IDENTITY MISMATCH DETECTED";
    Icon = AlertOctagon;
  }

  return (
    <div className={`border rounded-xl p-5 shadow-xl transition-all duration-300 ${bgClass}`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${badgeClass}`}>
            <Icon className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold font-mono uppercase tracking-wider border ${badgeClass}`}>
                {risk_level} ALERT
              </span>
              <span className="text-xs font-mono text-slate-300">
                Plate: <strong className="text-white text-sm bg-black/40 px-2 py-0.5 rounded border border-white/10">{plate_number}</strong>
              </span>
            </div>
            <h2 className="text-lg font-extrabold tracking-tight mt-1 text-white">
              {title}
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              {reason}
            </p>
          </div>
        </div>

        <div className="flex sm:flex-col items-center sm:items-end justify-between border-t sm:border-t-0 border-white/10 pt-3 sm:pt-0">
          <span className="text-xs uppercase tracking-wider text-slate-400 font-mono">Risk Anomaly Score</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-3xl font-black font-mono tracking-tight text-white">
              {risk_score}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
