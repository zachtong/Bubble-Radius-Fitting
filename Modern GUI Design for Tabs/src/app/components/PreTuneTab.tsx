import { useState } from "react";
import { Settings2, RotateCcw, Play, Info } from "lucide-react";

interface SliderInputProps {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  unit?: string;
}

function SliderInput({ label, value, onChange, min = 0, max = 100, unit }: SliderInputProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-slate-600 text-xs font-medium">{label}</span>
        <div className="flex items-center gap-1.5">
          <input
            type="number"
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            className="w-16 text-xs font-mono text-slate-700 border border-slate-200 rounded px-2 py-1 text-right bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-colors"
            step={0.1}
            min={min}
            max={max}
          />
          {unit && <span className="text-slate-400 text-xs">{unit}</span>}
        </div>
      </div>
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step={0.1}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(to right, #3B82F6 0%, #3B82F6 ${(value / max) * 100}%, #E2E8F0 ${(value / max) * 100}%, #E2E8F0 100%)`,
          }}
        />
        <div className="flex justify-between mt-1">
          <span className="text-slate-300 text-xs font-mono">{min}</span>
          <span className="text-slate-300 text-xs font-mono">{max}</span>
        </div>
      </div>
    </div>
  );
}

interface CheckboxGroupProps {
  label: string;
  options: { key: string; label: string; checked: boolean }[];
  onChange: (key: string, val: boolean) => void;
}

function CheckboxGroup({ label, options, onChange }: CheckboxGroupProps) {
  return (
    <div className="space-y-1.5">
      <span className="text-slate-600 text-xs font-medium">{label}</span>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <label
            key={opt.key}
            className="flex items-center gap-1.5 cursor-pointer group"
          >
            <div
              onClick={() => onChange(opt.key, !opt.checked)}
              className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all ${
                opt.checked
                  ? "bg-blue-500 border-blue-500"
                  : "border-slate-300 bg-white hover:border-blue-400"
              }`}
            >
              {opt.checked && (
                <svg className="w-2.5 h-2.5 text-white" viewBox="0 0 10 10" fill="none">
                  <path d="M1.5 5L4 7.5L8.5 2.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </div>
            <span className="text-slate-600 text-xs group-hover:text-slate-800 transition-colors">{opt.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

export function PreTuneTab() {
  const [imageNum, setImageNum] = useState(20);
  const [roi, setRoi] = useState({ L: 56, R: 336, U: 4, D: 158 });
  const [threshold, setThreshold] = useState(63.5);
  const [removingFactor, setRemovingFactor] = useState(63.1);
  const [edges, setEdges] = useState({
    Left: false,
    Right: false,
    Top: true,
    Down: false,
  });

  const handleEdgeChange = (key: string, val: boolean) => {
    setEdges((prev) => ({ ...prev, [key]: val }));
  };

  return (
    <div className="space-y-5 py-1">
      {/* Image Number */}
      <div className="space-y-1.5">
        <label className="text-slate-600 text-xs font-medium">Preview Image #</label>
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

      {/* ROI */}
      <div className="space-y-2">
        <div className="flex items-center gap-1.5">
          <span className="text-slate-600 text-xs font-medium">Region of Interest (ROI)</span>
          <div className="group relative cursor-help">
            <Info size={12} className="text-slate-300 hover:text-slate-500" />
          </div>
        </div>
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

      {/* Bubble crosses edges */}
      <CheckboxGroup
        label="Bubble crosses green edge?"
        options={Object.entries(edges).map(([key, checked]) => ({
          key,
          label: key,
          checked,
        }))}
        onChange={handleEdgeChange}
      />

      {/* Sliders */}
      <div className="space-y-4 bg-slate-50 rounded-lg p-3 border border-slate-100">
        <SliderInput
          label="Threshold"
          value={threshold}
          onChange={setThreshold}
        />
        <div className="border-t border-slate-200" />
        <SliderInput
          label="Removing Factor"
          value={removingFactor}
          onChange={setRemovingFactor}
        />
      </div>

      {/* Tip */}
      <div className="flex gap-2 bg-blue-50 border border-blue-100 rounded-lg p-3">
        <Info size={13} className="text-blue-400 mt-0.5 shrink-0" />
        <p className="text-blue-600 text-xs leading-relaxed">
          Adjust the sliders to distinguish the bubble (white) and background (black).
        </p>
      </div>

      {/* Buttons */}
      <div className="grid grid-cols-2 gap-2 pt-1">
        <button className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg px-3 py-2.5 transition-colors shadow-sm">
          <Play size={13} />
          Fitting & Preview
        </button>
        <button className="flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-600 text-xs font-medium rounded-lg px-3 py-2.5 border border-slate-200 transition-colors">
          <RotateCcw size={12} />
          Clear & Refresh
        </button>
      </div>
    </div>
  );
}
