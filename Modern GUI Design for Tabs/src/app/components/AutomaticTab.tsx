import { useState } from "react";
import { Play, Square, RotateCcw, Download, Cpu, Info } from "lucide-react";

export function AutomaticTab() {
  const [frameStart, setFrameStart] = useState(1);
  const [frameEnd, setFrameEnd] = useState(122);
  const [roi, setRoi] = useState({ L: 56, R: 336, U: 4, D: 158 });
  const [realtimePlay, setRealtimePlay] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFitAndPreview = () => {
    setIsRunning(true);
    setProgress(0);
    const total = frameEnd - frameStart + 1;
    let current = 0;
    const interval = setInterval(() => {
      current += Math.floor(Math.random() * 3) + 1;
      if (current >= total) {
        current = total;
        setProgress(100);
        setIsRunning(false);
        clearInterval(interval);
      } else {
        setProgress(Math.round((current / total) * 100));
      }
    }, 80);
  };

  const handleStop = () => {
    setIsRunning(false);
    setProgress(0);
  };

  const handleClear = () => {
    setIsRunning(false);
    setProgress(0);
  };

  return (
    <div className="space-y-5 py-1">
      {/* Frame Range */}
      <div className="space-y-1.5">
        <label className="text-slate-600 text-xs font-medium">Frame Range</label>
        <div className="flex items-center gap-2">
          <input
            type="number"
            value={frameStart}
            onChange={(e) => setFrameStart(Number(e.target.value))}
            className="w-16 text-sm font-mono text-slate-700 border border-slate-200 rounded-lg px-2 py-1.5 text-center bg-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
          />
          <span className="text-slate-400 text-xs">to</span>
          <input
            type="number"
            value={frameEnd}
            onChange={(e) => setFrameEnd(Number(e.target.value))}
            className="w-16 text-sm font-mono text-slate-700 border border-slate-200 rounded-lg px-2 py-1.5 text-center bg-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
          />
          <span className="text-slate-400 text-xs">{frameEnd - frameStart + 1} frames</span>
        </div>
      </div>

      {/* Load Parameters */}
      <button className="w-full flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-600 text-xs font-medium rounded-lg px-3 py-2.5 border border-slate-200 transition-colors">
        <Download size={13} />
        Load Tuned Parameters
      </button>

      {/* ROI */}
      <div className="space-y-2">
        <span className="text-slate-600 text-xs font-medium">Region of Interest (ROI)</span>
        <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
          <div className="grid grid-cols-4 gap-2">
            {(["L", "R", "U", "D"] as const).map((key) => (
              <div key={key} className="space-y-1">
                <label className="text-slate-400 text-xs font-mono text-center block">{key}</label>
                <input
                  type="number"
                  value={roi[key]}
                  onChange={(e) => setRoi((prev) => ({ ...prev, [key]: Number(e.target.value) }))}
                  className="w-full text-xs font-mono text-slate-700 border border-slate-200 rounded px-2 py-1 text-center bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-colors"
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Realtime play toggle */}
      <div className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2.5 border border-slate-100">
        <div>
          <p className="text-slate-700 text-xs font-medium">Realtime Playback</p>
          <p className="text-slate-400 text-xs">Preview frames as they process</p>
        </div>
        <button
          onClick={() => setRealtimePlay(!realtimePlay)}
          className={`relative w-10 h-5 rounded-full transition-colors ${
            realtimePlay ? "bg-blue-500" : "bg-slate-300"
          }`}
        >
          <span
            className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
              realtimePlay ? "translate-x-5" : "translate-x-0.5"
            }`}
          />
        </button>
      </div>

      {/* Progress */}
      {(isRunning || progress > 0) && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-slate-600 text-xs font-medium flex items-center gap-1.5">
              <Cpu size={12} className={isRunning ? "text-blue-500 animate-pulse" : "text-green-500"} />
              {isRunning ? "Processing…" : "Complete"}
            </span>
            <span className="text-slate-600 text-xs font-mono">{progress}%</span>
          </div>
          <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-200 ${
                progress === 100 ? "bg-green-500" : "bg-blue-500"
              }`}
              style={{ width: `${progress}%` }}
            />
          </div>
          {progress === 100 && (
            <p className="text-green-600 text-xs">
              ✓ All {frameEnd - frameStart + 1} frames processed successfully
            </p>
          )}
        </div>
      )}

      {/* Action buttons */}
      <div className="grid grid-cols-3 gap-2 pt-1">
        <button
          onClick={handleFitAndPreview}
          disabled={isRunning}
          className="col-span-3 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-xs font-medium rounded-lg px-3 py-2.5 transition-colors shadow-sm"
        >
          <Play size={13} />
          Fitting & Preview
        </button>
        <button
          onClick={handleStop}
          disabled={!isRunning}
          className="flex items-center justify-center gap-2 bg-white hover:bg-red-50 hover:border-red-200 hover:text-red-600 disabled:opacity-40 text-slate-600 text-xs font-medium rounded-lg px-3 py-2.5 border border-slate-200 transition-colors"
        >
          <Square size={12} />
          Stop
        </button>
        <button
          onClick={handleClear}
          className="col-span-2 flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-600 text-xs font-medium rounded-lg px-3 py-2.5 border border-slate-200 transition-colors"
        >
          <RotateCcw size={12} />
          Clear & Refresh
        </button>
      </div>

      <div className="flex gap-2 bg-slate-50 border border-slate-100 rounded-lg p-3">
        <Info size={13} className="text-slate-400 mt-0.5 shrink-0" />
        <p className="text-slate-500 text-xs leading-relaxed">
          Automatic mode processes all frames using tuned parameters. Load parameters from
          Pre-tune tab before running.
        </p>
      </div>
    </div>
  );
}
