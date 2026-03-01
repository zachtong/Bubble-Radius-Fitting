import { useState } from "react";
import { ZoomIn, ZoomOut, RefreshCw, Maximize2 } from "lucide-react";

interface ImagePanelProps {
  title: string;
  subtitle?: string;
  type: "original" | "binary";
  frameNumber?: number;
}

function BubbleImage({ type }: { type: "original" | "binary" }) {
  if (type === "original") {
    return (
      <svg
        viewBox="0 0 280 210"
        className="w-full h-full"
        style={{ background: "#2a2a2a" }}
      >
        {/* Background noise */}
        <rect width="280" height="210" fill="#1a1a1a" />
        {/* Subtle gradient background */}
        <radialGradient id="bgGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#2d2d2d" />
          <stop offset="100%" stopColor="#151515" />
        </radialGradient>
        <rect width="280" height="210" fill="url(#bgGrad)" />

        {/* Green ROI rectangle */}
        <rect
          x="40"
          y="20"
          width="200"
          height="160"
          fill="none"
          stroke="#22C55E"
          strokeWidth="2"
          opacity="0.9"
        />

        {/* Dark bubble body */}
        <circle cx="140" cy="100" r="72" fill="#0d0d0d" />

        {/* Red circle (bubble edge detection) */}
        <circle
          cx="140"
          cy="100"
          r="68"
          fill="none"
          stroke="#EF4444"
          strokeWidth="2.5"
          opacity="0.9"
        />

        {/* Blue circle (fitted circle) */}
        <circle
          cx="140"
          cy="84"
          r="76"
          fill="none"
          stroke="#3B82F6"
          strokeWidth="2.5"
          opacity="0.9"
        />

        {/* White bubble highlight (small bright spot) */}
        <circle cx="140" cy="72" r="14" fill="#f0f0f0" opacity="0.95" />
        <circle cx="140" cy="72" r="10" fill="#ffffff" />
        <circle cx="136" cy="68" r="4" fill="#ffffff" opacity="0.6" />

        {/* Subtle background texture streaks */}
        <line x1="0" y1="30" x2="280" y2="35" stroke="#252525" strokeWidth="8" opacity="0.5" />
        <line x1="0" y1="80" x2="280" y2="75" stroke="#222" strokeWidth="6" opacity="0.3" />
        <line x1="0" y1="150" x2="280" y2="155" stroke="#252525" strokeWidth="10" opacity="0.4" />
      </svg>
    );
  }

  // Binary mask
  return (
    <svg
      viewBox="0 0 280 210"
      className="w-full h-full"
      style={{ background: "#000000" }}
    >
      <rect width="280" height="210" fill="#000000" />
      {/* White bubble */}
      <circle cx="140" cy="100" r="72" fill="#ffffff" />
      {/* Clip top slightly */}
      <rect x="0" y="0" width="280" height="28" fill="#000000" />
    </svg>
  );
}

export function ImagePanel({ title, type, frameNumber = 41 }: ImagePanelProps) {
  const [zoom, setZoom] = useState(100);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden h-full">
      {/* Header */}
      <div className="px-4 py-2.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
        <div>
          <span className="text-slate-700 text-xs font-semibold tracking-wide">{title}</span>
          <span className="ml-2 text-slate-400 text-xs font-mono">Frame #{frameNumber}</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setZoom(Math.max(50, zoom - 25))}
            className="p-1 rounded hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <ZoomOut size={13} />
          </button>
          <span className="text-slate-400 text-xs font-mono w-9 text-center">{zoom}%</span>
          <button
            onClick={() => setZoom(Math.min(200, zoom + 25))}
            className="p-1 rounded hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <ZoomIn size={13} />
          </button>
          <button
            onClick={() => setZoom(100)}
            className="p-1 rounded hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors ml-1"
          >
            <RefreshCw size={12} />
          </button>
        </div>
      </div>

      {/* Image area */}
      <div className="flex-1 overflow-hidden relative bg-slate-900/5 flex items-center justify-center p-2">
        <div
          className="overflow-hidden rounded"
          style={{ width: `${zoom}%`, height: `${zoom}%`, maxWidth: "100%", maxHeight: "100%" }}
        >
          <BubbleImage type={type} />
        </div>
      </div>

      {/* Axis labels */}
      <div className="px-4 py-1.5 border-t border-slate-100 bg-slate-50/40 flex items-center justify-between">
        <span className="text-slate-400 text-xs font-mono">X [px]</span>
        <span className="text-slate-400 text-xs font-mono">Y [px]</span>
      </div>
    </div>
  );
}
