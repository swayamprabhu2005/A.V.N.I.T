import React, { useState, useEffect } from 'react';
import { History, RefreshCw, AlertTriangle, ShieldCheck, AlertOctagon } from 'lucide-react';
import { fetchAlerts } from '../services/api';

export default function DetectionHistory({ refreshTrigger }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const data = await fetchAlerts(25);
      setAlerts(data);
    } catch (err) {
      console.error("Failed to load alerts:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [refreshTrigger]);

  const getVerdictBadge = (level) => {
    if (level === "GREEN") {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          <ShieldCheck className="w-3 h-3" /> VALID
        </span>
      );
    }
    if (level === "YELLOW") {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-amber-500/20 text-amber-400 border border-amber-500/30">
          <AlertTriangle className="w-3 h-3" /> REVIEW
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-rose-500/20 text-rose-400 border border-rose-500/30">
        <AlertOctagon className="w-3 h-3" /> MISMATCH
      </span>
    );
  };

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-bold text-slate-200">Identity Verification Audit Log</h3>
        </div>
        <button
          onClick={loadAlerts}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition"
          title="Refresh log"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="overflow-x-auto max-h-72">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-card border-b border-border text-[11px] font-mono uppercase text-slate-400">
            <tr>
              <th className="py-2.5 px-3">Time</th>
              <th className="py-2.5 px-3">Plate Number</th>
              <th className="py-2.5 px-3">Observed Visuals</th>
              <th className="py-2.5 px-3 text-center">Risk</th>
              <th className="py-2.5 px-3">Verdict</th>
              <th className="py-2.5 px-3">Reason / Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {alerts.length > 0 ? (
              alerts.map((al) => (
                <tr key={al.alert_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-2.5 px-3 text-slate-400 font-mono whitespace-nowrap">
                    {new Date(al.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td className="py-2.5 px-3 font-mono font-bold text-slate-100">
                    {al.plate_number}
                  </td>
                  <td className="py-2.5 px-3 font-mono capitalize text-slate-300">
                    {al.observed_color} {al.observed_type}
                  </td>
                  <td className="py-2.5 px-3 text-center font-mono font-bold">
                    <span className={al.risk_score > 60 ? 'text-rose-400' : al.risk_score > 25 ? 'text-amber-400' : 'text-emerald-400'}>
                      {al.risk_score}%
                    </span>
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    {getVerdictBadge(al.risk_level)}
                  </td>
                  <td className="py-2.5 px-3 text-slate-400 max-w-xs truncate" title={al.reason}>
                    {al.reason}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="py-8 text-center text-slate-500">
                  No vehicle audit records logged yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
