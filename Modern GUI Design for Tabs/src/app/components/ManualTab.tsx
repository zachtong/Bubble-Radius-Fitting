import { useState } from "react";
import { MousePointer2, RotateCcw, Info, CheckCircle2 } from "lucide-react";

export function ManualTab() {
  const [imageNum, setImageNum] = useState(1);
  const [pointsSelected, setPointsSelected] = useState(0);
  const [isSelecting, setIsSelecting] = useState(false);

  const handleStartSelection = () => {
    setIsSelecting(true);
    setPointsSelected(0);
    // Simulate point selection
    let count = 0;
    const interval = setInterval(() => {
      count++;
      setPointsSelected(count);
      if (count >= 5) {
        clearInterval(interval);
        setIsSelecting(false);
      }
    }, 600);
  };

  const handleClear = () => {
    setPointsSelected(0);
    setIsSelecting(false);
  };

  return (
    <div className="space-y-5 py-1">
      {/* Image Number */}
      <div className="space-y-1.5">
        <label className="text-slate-600 text-xs font-medium">Image #</label>
        <div className="flex items-center gap-2">
          <input
            type="number"
            value={imageNum}
            onChange={(e) => setImageNum(Number(e.target.value))}
            className="w-20 text-sm font-mono text-slate-700 border border-slate-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
          />
          <span className="text-slate-400 text-xs">of 122 frames</span>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-amber-50 border border-amber-100 rounded-lg p-3 space-y-2">
        <div className="flex items-center gap-2">
          <MousePointer2 size={13} className="text-amber-500" />
          <span className="text-amber-700 text-xs font-medium">Manual Selection Mode</span>
        </div>
        <p className="text-amber-600 text-xs leading-relaxed">
          Click on the image to select at least <strong>3 edge points</strong> on the bubble boundary.
          More points yield better circle fitting.
        </p>
      </div>

      {/* Point counter */}
      <div className="bg-slate-50 rounded-lg p-3 border border-slate-100 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-slate-600 text-xs font-medium">Edge Points Selected</span>
          <div className="flex items-center gap-1.5">
            {pointsSelected >= 3 && (
              <CheckCircle2 size={13} className="text-green-500" />
            )}
            <span
              className={`text-sm font-mono font-semibold ${
                pointsSelected >= 3 ? "text-green-600" : "text-slate-400"
              }`}
            >
              {pointsSelected}
            </span>
            <span className="text-slate-400 text-xs">/ min 3</span>
          </div>
        </div>
        {/* Progress dots */}
        <div className="flex gap-1.5">
          {Array.from({ length: Math.max(5, pointsSelected) }).map((_, i) => (
            <div
              key={i}
              className={`h-1.5 flex-1 rounded-full transition-all ${
                i < pointsSelected
                  ? i < 3
                    ? "bg-blue-500"
                    : "bg-green-500"
                  : "bg-slate-200"
              }`}
            />
          ))}
        </div>
        <p className="text-slate-400 text-xs">
          {pointsSelected === 0
            ? "No points selected yet"
            : pointsSelected < 3
            ? `Need ${3 - pointsSelected} more point${3 - pointsSelected > 1 ? "s" : ""}`
            : `${pointsSelected} points — ready to fit`}
        </p>
      </div>

      {/* Actions */}
      <div className="space-y-2 pt-1">
        <button
          onClick={handleStartSelection}
          disabled={isSelecting}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-xs font-medium rounded-lg px-3 py-2.5 transition-colors shadow-sm"
        >
          <MousePointer2 size={13} />
          {isSelecting ? "Selecting… click on image" : "Manually Select Bubble Edge Points"}
        </button>
        <button
          onClick={handleClear}
          className="w-full flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-600 text-xs font-medium rounded-lg px-3 py-2.5 border border-slate-200 transition-colors"
        >
          <RotateCcw size={12} />
          Clear & Refresh
        </button>
      </div>

      {/* Info */}
      <div className="flex gap-2 bg-slate-50 border border-slate-100 rounded-lg p-3">
        <Info size={13} className="text-slate-400 mt-0.5 shrink-0" />
        <p className="text-slate-500 text-xs leading-relaxed">
          Manual mode is useful for frames where automatic detection fails. Selected points are
          used to fit the best-fit circle.
        </p>
      </div>
    </div>
  );
}
