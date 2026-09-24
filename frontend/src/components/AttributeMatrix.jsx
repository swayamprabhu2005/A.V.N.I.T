import React from 'react';
import { Columns, Check, X, AlertCircle } from 'lucide-react';

export default function AttributeMatrix({ riskResult }) {
  const obs = riskResult?.observed_attributes || {
    type: "—",
    color: "—",
    make: "—",
    model: "—",
    ocr_confidence: 0.0
  };

  const reg = riskResult?.registration_record || {
    plate_number: "—",
    vehicle_type: "—",
    color: "—",
    make: "—",
    model: "—",
    registration_status: "—"
  };

  const registered = riskResult?.registered ?? false;

  const compareRow = (label, observedVal, registeredVal, isMatch) => {
    return (
      <tr className="border-b border-border/50 hover:bg-slate-800/30 transition text-xs">
        <td className="py-2.5 px-3 font-medium text-slate-300">{label}</td>
        <td className="py-2.5 px-3 font-mono capitalize">
          <span className="bg-slate-800 px-2 py-0.5 rounded border border-border text-slate-200">
            {observedVal}
          </span>
        </td>
        <td className="py-2.5 px-3 font-mono capitalize">
          <span className={`px-2 py-0.5 rounded border ${registered ? 'bg-slate-800 border-border text-slate-200' : 'bg-rose-950/40 border-rose-500/30 text-rose-300'}`}>
            {registered ? registeredVal : "Unregistered"}
          </span>
        </td>
        <td className="py-2.5 px-3 text-right">
          {registered ? (
            isMatch ? (
              <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                <Check className="w-3.5 h-3.5" /> Match
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-rose-400 font-medium">
                <X className="w-3.5 h-3.5" /> Mismatch
              </span>
            )
          ) : (
            <span className="inline-flex items-center gap-1 text-rose-400 font-medium">
              <AlertCircle className="w-3.5 h-3.5" /> Not in DB
            </span>
          )}
        </td>
      </tr>
    );
  };

  const typeMatched = obs.type.toLowerCase() === reg.vehicle_type?.toLowerCase();
  const colorMatched = obs.color.toLowerCase() === reg.color?.toLowerCase();

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between border-b border-border pb-3 mb-3">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Columns className="w-4 h-4 text-purple-400" />
          <span>Explainability Attribute Matrix</span>
        </h3>
        <span className="text-[11px] font-mono text-slate-400">
          Observed vs Registered
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-border text-[11px] font-mono uppercase text-slate-400 tracking-wider">
              <th className="py-2 px-3">Vehicle Attribute</th>
              <th className="py-2 px-3">Observed (Vision AI)</th>
              <th className="py-2 px-3">Registered (Database)</th>
              <th className="py-2 px-3 text-right">Audit Verdict</th>
            </tr>
          </thead>
          <tbody>
            {compareRow(
              "Number Plate",
              riskResult ? riskResult.plate_number : "—",
              reg.plate_number,
              registered
            )}
            {compareRow("Vehicle Type", obs.type, reg.vehicle_type, typeMatched)}
            {compareRow("Vehicle Color", obs.color, reg.color, colorMatched)}
            {compareRow("Make & Model", `${obs.make} ${obs.model}`, `${reg.make} ${reg.model}`, true)}
            {compareRow("Registration Status", "Active Observation", reg.registration_status, reg.registration_status === "Active")}
          </tbody>
        </table>
      </div>
    </div>
  );
}
