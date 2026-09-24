import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StatusBanner from './components/StatusBanner';
import VideoPlayer from './components/VideoPlayer';
import RiskGauge from './components/RiskGauge';
import AttributeMatrix from './components/AttributeMatrix';
import DetectionHistory from './components/DetectionHistory';
import VehicleManagerModal from './components/VehicleManagerModal';
import { fetchSystemStatus, fetchStats } from './services/api';
import { Car, ShieldCheck, AlertOctagon, CheckCircle2 } from 'lucide-react';

export default function App() {
  const [statusData, setStatusData] = useState(null);
  const [stats, setStats] = useState({
    total_detections: 0,
    valid_passes: 0,
    medium_risk_alerts: 0,
    high_risk_alerts: 0,
    registered_vehicles: 5
  });
  const [currentTelemetry, setCurrentTelemetry] = useState(null);
  const [isDbModalOpen, setIsDbModalOpen] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const loadStatusAndStats = async () => {
    try {
      const [status, st] = await Promise.all([
        fetchSystemStatus(),
        fetchStats()
      ]);
      setStatusData(status);
      setStats(st);
    } catch (err) {
      console.warn("Backend not yet connected:", err);
    }
  };

  useEffect(() => {
    loadStatusAndStats();
    const interval = setInterval(loadStatusAndStats, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleTelemetryUpdate = (telemetry) => {
    setCurrentTelemetry(telemetry);
    if (telemetry?.risk_result) {
      setRefreshTrigger(prev => prev + 1);
    }
  };

  const riskResult = currentTelemetry?.risk_result || null;

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Header with AVNIT Branding */}
      <Header 
        statusData={statusData} 
        onOpenDbModal={() => setIsDbModalOpen(true)} 
      />

      {/* Main Dashboard Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-5">
        {/* Top Status Banner */}
        <StatusBanner riskResult={riskResult} />

        {/* Central Visual & Intelligence Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Left Column: Live Visual Viewport (7 Cols) */}
          <div className="lg:col-span-7">
            <VideoPlayer onTelemetryUpdate={handleTelemetryUpdate} />
          </div>

          {/* Right Column: Intelligence & Explainability Breakdown (5 Cols) */}
          <div className="lg:col-span-5 space-y-5">
            {/* Risk Engine Gauge */}
            <RiskGauge riskResult={riskResult} />

            {/* Side-by-side Attribute Matrix */}
            <AttributeMatrix riskResult={riskResult} />
          </div>
        </div>

        {/* Stats Ticker */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-card border border-border rounded-xl p-3.5 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Car className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-bold font-mono text-white">{stats.total_detections}</div>
              <div className="text-[11px] text-slate-400">Total Scans</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-3.5 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-bold font-mono text-emerald-400">{stats.valid_passes}</div>
              <div className="text-[11px] text-slate-400">Valid Identity Passes</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-3.5 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <AlertOctagon className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-bold font-mono text-rose-400">{stats.high_risk_alerts}</div>
              <div className="text-[11px] text-slate-400">Tampering / Mismatches</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-3.5 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-bold font-mono text-purple-400">{stats.registered_vehicles}</div>
              <div className="text-[11px] text-slate-400">Authorized Records</div>
            </div>
          </div>
        </div>

        {/* Audit History Trail */}
        <DetectionHistory refreshTrigger={refreshTrigger} />
      </main>

      {/* Vehicle Database Management Modal */}
      <VehicleManagerModal 
        isOpen={isDbModalOpen} 
        onClose={() => {
          setIsDbModalOpen(false);
          loadStatusAndStats();
        }} 
      />

      {/* Footer */}
      <footer className="border-t border-border/60 py-4 text-center text-xs text-slate-500">
        A.V.N.I.T. — AI-Based Vehicle Number Plate and Identity Tampering Detection Prototype &copy; 2026
      </footer>
    </div>
  );
}
