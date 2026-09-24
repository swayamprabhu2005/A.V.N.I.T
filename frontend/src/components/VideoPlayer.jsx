import React, { useState, useEffect, useRef } from 'react';
import { Play, Square, Video, Camera, RefreshCw, Radio } from 'lucide-react';
import { getWebSocketUrl, fetchScenarios } from '../services/api';

export default function VideoPlayer({ onTelemetryUpdate }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [sourceType, setSourceType] = useState('scenario'); // 'scenario' | 'webcam'
  const [selectedScenario, setSelectedScenario] = useState('scenario_1_valid.mp4');
  const [scenarios, setScenarios] = useState([]);
  const [fps, setFps] = useState(0);
  const [currentFrame, setCurrentFrame] = useState(null);
  const [connected, setConnected] = useState(false);

  const wsRef = useRef(null);
  const frameCountRef = useRef(0);
  const lastFpsTimeRef = useRef(Date.now());

  useEffect(() => {
    // Load available demo scenarios from backend
    fetchScenarios()
      .then(data => {
        if (data && data.length > 0) {
          setScenarios(data);
          setSelectedScenario(data[0].filename);
        }
      })
      .catch(err => console.error("Failed to fetch scenarios:", err));
  }, []);

  // Connect WebSocket
  useEffect(() => {
    const wsUrl = getWebSocketUrl();
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("[AVNIT] WebSocket connected");
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "frame") {
          setCurrentFrame(data.image);
          if (data.telemetry && data.telemetry.length > 0) {
            // Forward most prominent vehicle telemetry to parent
            onTelemetryUpdate(data.telemetry[0]);
          }

          // Measure FPS
          frameCountRef.current += 1;
          const now = Date.now();
          if (now - lastFpsTimeRef.current >= 1000) {
            setFps(frameCountRef.current);
            frameCountRef.current = 0;
            lastFpsTimeRef.current = now;
          }
        }
      } catch (err) {
        console.error("Frame parse error:", err);
      }
    };

    ws.onclose = () => {
      console.log("[AVNIT] WebSocket disconnected");
      setConnected(false);
      setIsPlaying(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "stop" }));
        ws.close();
      }
    };
  }, []);

  const handleStart = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    wsRef.current.send(JSON.stringify({
      action: "start",
      source: sourceType,
      filename: selectedScenario
    }));
    setIsPlaying(true);
  };

  const handleStop = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    wsRef.current.send(JSON.stringify({ action: "stop" }));
    setIsPlaying(false);
    setFps(0);
  };

  const handleSourceChange = (type) => {
    setSourceType(type);
    if (isPlaying) {
      handleStop();
    }
  };

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
      {/* Top Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-4 mb-4">
        <div className="flex items-center gap-2">
          <Radio className={`w-4 h-4 ${connected ? 'text-emerald-400' : 'text-rose-400'}`} />
          <h3 className="text-sm font-bold text-slate-200">Live Visual Stream</h3>
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${connected ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border-rose-500/30'}`}>
            {connected ? "AI PIPELINE ONLINE" : "OFFLINE"}
          </span>
        </div>

        {/* Source Switcher */}
        <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-border text-xs">
          <button
            onClick={() => handleSourceChange('scenario')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition ${sourceType === 'scenario' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}
          >
            <Video className="w-3.5 h-3.5" />
            <span>Demo Scenarios</span>
          </button>
          <button
            onClick={() => handleSourceChange('webcam')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition ${sourceType === 'webcam' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}
          >
            <Camera className="w-3.5 h-3.5" />
            <span>Live Webcam</span>
          </button>
        </div>
      </div>

      {/* Video Viewport */}
      <div className="relative aspect-[4/3] sm:aspect-video w-full bg-slate-950 rounded-lg overflow-hidden border border-border flex items-center justify-center shadow-inner group">
        {currentFrame ? (
          <img 
            src={currentFrame} 
            alt="Live Stream" 
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="text-center p-6 text-slate-500">
            <Video className="w-12 h-12 mx-auto mb-2 text-slate-600" />
            <p className="text-sm font-medium">Stream Inactive</p>
            <p className="text-xs text-slate-600 mt-1">Select source and click Start Feed</p>
          </div>
        )}

        {/* Live HUD Overlay */}
        {isPlaying && (
          <div className="absolute top-3 left-3 bg-black/70 backdrop-blur-md px-2.5 py-1 rounded border border-white/10 text-[11px] font-mono text-emerald-400 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>LIVE | {fps} FPS</span>
          </div>
        )}

        {/* Source Tag */}
        <div className="absolute top-3 right-3 bg-black/70 backdrop-blur-md px-2.5 py-1 rounded border border-white/10 text-[11px] font-mono text-slate-300">
          {sourceType === 'webcam' ? 'Source: USB Webcam' : `Clip: ${selectedScenario}`}
        </div>
      </div>

      {/* Bottom Scenario Selector & Buttons */}
      <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
        {sourceType === 'scenario' ? (
          <div className="w-full sm:w-auto flex-1">
            <select
              value={selectedScenario}
              onChange={(e) => {
                setSelectedScenario(e.target.value);
                if (isPlaying) handleStop();
              }}
              className="w-full bg-slate-900 border border-border text-slate-200 text-xs rounded-lg px-3 py-2 focus:ring-1 focus:ring-blue-500 outline-none"
            >
              {scenarios.map((sc) => (
                <option key={sc.filename} value={sc.filename}>
                  {sc.name}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div className="text-xs text-slate-400 flex-1">
            Pointing to default video capture device index <code className="text-blue-400 font-mono">0</code>
          </div>
        )}

        {/* Play / Stop Buttons */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          {!isPlaying ? (
            <button
              onClick={handleStart}
              disabled={!connected}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 active:scale-95 disabled:opacity-50 text-white text-xs font-semibold px-5 py-2 rounded-lg transition shadow-md shadow-emerald-500/20"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Start Feed</span>
            </button>
          ) : (
            <button
              onClick={handleStop}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 bg-rose-600 hover:bg-rose-500 active:scale-95 text-white text-xs font-semibold px-5 py-2 rounded-lg transition shadow-md shadow-rose-500/20"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>Stop Feed</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
