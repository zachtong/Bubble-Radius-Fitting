import { useState } from "react";
import { Activity, Settings, HelpCircle, Layers, ChevronLeft, ChevronRight } from "lucide-react";
import { LeftPanel } from "./components/LeftPanel";
import { ImagePanel } from "./components/ImagePanel";
import { RadiusChart } from "./components/RadiusChart";

export default function App() {
  const [frameNumber, setFrameNumber] = useState(41);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex flex-col h-screen bg-slate-50 overflow-hidden">
      {/* Top Navigation Bar */}
      <header className="bg-slate-900 border-b border-slate-800 px-5 py-0 flex items-center justify-between shrink-0 h-12">
        <div className="flex items-center gap-3">
          {/* Logo / App name */}
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-blue-500 rounded-lg flex items-center justify-center shadow">
              <Activity size={15} className="text-white" />
            </div>
            <div>
              <span className="text-white text-sm font-semibold tracking-tight">BubbleTrack</span>
              <span className="text-slate-500 text-xs ml-2">v2.0</span>
            </div>
          </div>

          <div className="w-px h-5 bg-slate-700 mx-1" />

          {/* Status */}
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            <span className="text-slate-400 text-xs">Ready</span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors">
            <Layers size={15} />
          </button>
          <button className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors">
            <Settings size={15} />
          </button>
          <button className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors">
            <HelpCircle size={15} />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <div
          className={`relative flex shrink-0 transition-all duration-300 ${
            sidebarCollapsed ? "w-0 overflow-hidden" : "w-[300px]"
          }`}
        >
          {!sidebarCollapsed && <LeftPanel />}
        </div>

        {/* Sidebar Toggle */}
        <div className="relative z-10 flex items-center">
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="absolute -right-3 top-1/2 -translate-y-1/2 z-20 w-6 h-12 bg-white border border-slate-200 rounded-r-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors shadow-sm"
          >
            {sidebarCollapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
          </button>
        </div>

        {/* Right Content Area */}
        <main className="flex-1 overflow-hidden flex flex-col p-4 gap-4 min-w-0">
          {/* Image viewers row */}
          <div className="flex gap-4 flex-1 min-h-0">
            {/* Original image with detection overlay */}
            <div className="flex-1 min-w-0">
              <ImagePanel
                title="Original Image"
                type="original"
                frameNumber={frameNumber}
              />
            </div>

            {/* Binary mask */}
            <div className="flex-1 min-w-0">
              <ImagePanel
                title="Binary Mask"
                type="binary"
                frameNumber={frameNumber}
              />
            </div>
          </div>

          {/* Frame scrubber */}
          <div className="shrink-0 bg-white rounded-xl border border-slate-200 shadow-sm px-5 py-3 flex items-center gap-4">
            <span className="text-slate-500 text-xs font-medium whitespace-nowrap">Frame</span>
            <input
              type="range"
              min={1}
              max={122}
              value={frameNumber}
              onChange={(e) => setFrameNumber(Number(e.target.value))}
              className="flex-1 h-1.5 rounded-full appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, #3B82F6 0%, #3B82F6 ${((frameNumber - 1) / 121) * 100}%, #E2E8F0 ${((frameNumber - 1) / 121) * 100}%, #E2E8F0 100%)`,
              }}
            />
            <span className="text-slate-700 text-xs font-mono w-14 text-right">
              {frameNumber} / 122
            </span>
          </div>

          {/* Radius-time chart */}
          <div className="h-52 shrink-0">
            <RadiusChart />
          </div>
        </main>
      </div>

      {/* Bottom status bar */}
      <footer className="bg-slate-900 border-t border-slate-800 px-5 py-1.5 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <span className="text-slate-500 text-xs font-mono">
            Frame: <span className="text-slate-300">{frameNumber}</span>
          </span>
          <span className="text-slate-500 text-xs font-mono">
            Format: <span className="text-slate-300">tiff</span>
          </span>
          <span className="text-slate-500 text-xs font-mono">
            Scale: <span className="text-slate-300">3.2 μm/px</span>
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-slate-500 text-xs">
            ROI: <span className="text-slate-300 font-mono">L56 R336 U4 D158</span>
          </span>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full" />
            <span className="text-slate-400 text-xs">Pre-tune mode</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
