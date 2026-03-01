import { useState } from "react";
import { FolderOpen, Download, ChevronDown, ChevronUp, FlaskConical } from "lucide-react";

export function PostProcessing() {
  const [exportPath, setExportPath] = useState("");
  const [fps, setFps] = useState("1e+06");
  const [rmax, setRmax] = useState(11);
  const [umPerPx, setUmPerPx] = useState(3.2);
  const [isOpen, setIsOpen] = useState(true);
  const [exportStatus, setExportStatus] = useState<"idle" | "success">("idle");
  const [convertStatus, setConvertStatus] = useState<"idle" | "success">("idle");

  const handleExport = () => {
    setExportStatus("success");
    setTimeout(() => setExportStatus("idle"), 2000);
  };

  const handleConvert = () => {
    setConvertStatus("success");
    setTimeout(() => setConvertStatus("idle"), 2000);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 border-b border-slate-200 hover:bg-slate-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <FlaskConical size={14} className="text-slate-500" />
          <span className="text-slate-700 text-xs font-semibold tracking-wide">Post Processing</span>
        </div>
        {isOpen ? (
          <ChevronUp size={14} className="text-slate-400" />
        ) : (
          <ChevronDown size={14} className="text-slate-400" />
        )}
      </button>

      {isOpen && (
        <div className="p-4 space-y-4">
          {/* Export R_data.mat */}
          <div className="space-y-3">
            <p className="text-slate-500 text-xs font-medium">
              Export to{" "}
              <code className="bg-slate-100 text-slate-600 px-1 py-0.5 rounded text-xs font-mono">
                R_data.mat
              </code>
            </p>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={exportPath}
                  onChange={(e) => setExportPath(e.target.value)}
                  placeholder="Export path (default)"
                  className="flex-1 text-xs font-mono text-slate-700 border border-slate-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-colors placeholder:text-slate-300"
                />
                <button className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-400 hover:text-slate-600 transition-colors">
                  <FolderOpen size={14} />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setExportPath("")}
                  className="text-xs text-slate-500 hover:text-slate-700 border border-slate-200 rounded-lg px-3 py-2 hover:bg-slate-50 transition-colors text-center"
                >
                  Use Default Path
                </button>
                <button
                  onClick={handleExport}
                  className={`flex items-center justify-center gap-1.5 text-xs font-medium rounded-lg px-3 py-2 transition-colors ${
                    exportStatus === "success"
                      ? "bg-green-500 text-white"
                      : "bg-blue-600 hover:bg-blue-700 text-white"
                  }`}
                >
                  <Download size={12} />
                  {exportStatus === "success" ? "Exported ✓" : "Export"}
                </button>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-100" />

          {/* Convert to physical units */}
          <div className="space-y-3">
            <p className="text-slate-500 text-xs font-medium">
              Convert to physical units →{" "}
              <code className="bg-slate-100 text-slate-600 px-1 py-0.5 rounded text-xs font-mono">
                RofTdata.mat
              </code>
            </p>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-slate-400 text-xs">FPS</label>
                <input
                  type="text"
                  value={fps}
                  onChange={(e) => setFps(e.target.value)}
                  className="w-full text-xs font-mono text-slate-700 border border-slate-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-colors"
                />
              </div>
              <div className="space-y-1">
                <label className="text-slate-400 text-xs">R_max fit window</label>
                <input
                  type="number"
                  value={rmax}
                  onChange={(e) => setRmax(Number(e.target.value))}
                  className="w-full text-xs font-mono text-slate-700 border border-slate-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-colors"
                />
              </div>
              <div className="space-y-1 col-span-2">
                <label className="text-slate-400 text-xs">Scale (μm/px)</label>
                <input
                  type="number"
                  value={umPerPx}
                  step={0.1}
                  onChange={(e) => setUmPerPx(Number(e.target.value))}
                  className="w-full text-xs font-mono text-slate-700 border border-slate-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-colors"
                />
              </div>
            </div>

            <button
              onClick={handleConvert}
              className={`w-full flex items-center justify-center gap-1.5 text-xs font-medium rounded-lg px-3 py-2.5 transition-colors ${
                convertStatus === "success"
                  ? "bg-green-500 text-white"
                  : "bg-slate-700 hover:bg-slate-800 text-white"
              }`}
            >
              <Download size={12} />
              {convertStatus === "success" ? "Converted & Exported ✓" : "Convert & Export"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
