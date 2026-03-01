import { useState } from "react";
import { FolderOpen, ChevronDown, Database } from "lucide-react";
import { PreTuneTab } from "./PreTuneTab";
import { ManualTab } from "./ManualTab";
import { AutomaticTab } from "./AutomaticTab";
import { PostProcessing } from "./PostProcessing";

type TabKey = "pretune" | "manual" | "automatic";
type ModeKey = "Pre-tune" | "Manual" | "Automatic";

const TABS: { key: TabKey; label: string }[] = [
  { key: "pretune", label: "Pre-tune" },
  { key: "manual", label: "Manual" },
  { key: "automatic", label: "Automatic" },
];

export function LeftPanel() {
  const [activeTab, setActiveTab] = useState<TabKey>("pretune");
  const [folderPath, setFolderPath] = useState("C:\\Users\\13014\\OneDrive - The Uni");
  const [imageFormat, setImageFormat] = useState("tiff");
  const [mode, setMode] = useState<ModeKey>("Pre-tune");

  const handleTabChange = (key: TabKey) => {
    setActiveTab(key);
    const modeMap: Record<TabKey, ModeKey> = {
      pretune: "Pre-tune",
      manual: "Manual",
      automatic: "Automatic",
    };
    setMode(modeMap[key]);
  };

  return (
    <aside className="w-[300px] min-w-[280px] max-w-[320px] bg-white border-r border-slate-200 flex flex-col h-full overflow-hidden">
      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-4">
          {/* Image Source */}
          <div className="space-y-2">
            <div className="flex items-center gap-1.5 mb-1">
              <div className="w-1 h-3.5 bg-blue-500 rounded-full" />
              <span className="text-slate-700 text-xs font-semibold tracking-wider uppercase">
                Image Source
              </span>
            </div>
            <div className="bg-slate-50 rounded-xl border border-slate-100 p-3 space-y-3">
              {/* Folder selector */}
              <div className="space-y-1.5">
                <label className="text-slate-500 text-xs">Image Folder</label>
                <div className="flex gap-2 items-center">
                  <button className="shrink-0 flex items-center gap-1.5 bg-white border border-slate-200 hover:border-blue-400 hover:bg-blue-50 text-slate-600 hover:text-blue-600 text-xs rounded-lg px-2.5 py-1.5 transition-colors">
                    <FolderOpen size={12} />
                    Browse
                  </button>
                  <div
                    className="flex-1 bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-mono text-slate-500 truncate"
                    title={folderPath}
                  >
                    {folderPath}
                  </div>
                </div>
              </div>

              {/* Format */}
              <div className="flex items-center justify-between">
                <label className="text-slate-500 text-xs">Format</label>
                <div className="relative">
                  <select
                    value={imageFormat}
                    onChange={(e) => setImageFormat(e.target.value)}
                    className="appearance-none bg-white border border-slate-200 text-slate-700 text-xs rounded-lg pl-3 pr-7 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-colors cursor-pointer"
                  >
                    <option value="tiff">tiff</option>
                    <option value="png">png</option>
                    <option value="jpg">jpg</option>
                    <option value="bmp">bmp</option>
                  </select>
                  <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>

          {/* Mode + Load */}
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <select
                value={mode}
                onChange={(e) => {
                  const m = e.target.value as ModeKey;
                  setMode(m);
                  const tabMap: Record<ModeKey, TabKey> = {
                    "Pre-tune": "pretune",
                    "Manual": "manual",
                    "Automatic": "automatic",
                  };
                  setActiveTab(tabMap[m]);
                }}
                className="w-full appearance-none bg-white border border-slate-200 text-slate-700 text-xs rounded-lg pl-3 pr-7 py-2 focus:outline-none focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-colors cursor-pointer"
              >
                <option>Pre-tune</option>
                <option>Manual</option>
                <option>Automatic</option>
              </select>
              <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            </div>
            <button className="shrink-0 flex items-center gap-1.5 bg-white border border-slate-200 hover:border-blue-400 hover:bg-blue-50 text-slate-600 hover:text-blue-600 text-xs rounded-lg px-2.5 py-2 transition-colors whitespace-nowrap">
              <Database size={12} />
              Load R_data
            </button>
          </div>

          {/* Tabs */}
          <div>
            {/* Tab Headers */}
            <div className="flex border-b border-slate-200 mb-4">
              {TABS.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => handleTabChange(tab.key)}
                  className={`flex-1 text-xs py-2.5 font-medium transition-all border-b-2 -mb-px ${
                    activeTab === tab.key
                      ? "text-blue-600 border-blue-600"
                      : "text-slate-400 border-transparent hover:text-slate-600 hover:border-slate-300"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div>
              {activeTab === "pretune" && <PreTuneTab />}
              {activeTab === "manual" && <ManualTab />}
              {activeTab === "automatic" && <AutomaticTab />}
            </div>
          </div>

          {/* Post Processing */}
          <PostProcessing />

          {/* Bottom padding */}
          <div className="h-4" />
        </div>
      </div>
    </aside>
  );
}
