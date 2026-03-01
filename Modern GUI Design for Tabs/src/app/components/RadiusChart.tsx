import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

const generateChartData = () => {
  const data: { frame: number; radius: number }[] = [];
  const points = [
    { frame: 1, radius: 22.1 },
    { frame: 3, radius: 28.4 },
    { frame: 5, radius: 35.7 },
    { frame: 7, radius: 44.2 },
    { frame: 9, radius: 51.8 },
    { frame: 11, radius: 58.3 },
    { frame: 13, radius: 63.9 },
    { frame: 15, radius: 68.1 },
    { frame: 17, radius: 71.4 },
    { frame: 19, radius: 74.2 },
    { frame: 21, radius: 76.5 },
    { frame: 23, radius: 77.8 },
    { frame: 25, radius: 78.9 },
    { frame: 27, radius: 79.4 },
    { frame: 29, radius: 79.8 },
    { frame: 31, radius: 80.1 },
    { frame: 33, radius: 80.3 },
    { frame: 35, radius: 80.2 },
    { frame: 37, radius: 79.9 },
    { frame: 39, radius: 79.7 },
    { frame: 41, radius: 79.5 },
  ];
  return points;
};

const chartData = generateChartData();

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-slate-200 rounded-lg px-3 py-2 shadow-lg">
        <p className="text-slate-500 text-xs">Frame {payload[0]?.payload?.frame}</p>
        <p className="text-slate-800 text-sm font-mono">
          R = {payload[0]?.payload?.radius} px
        </p>
      </div>
    );
  }
  return null;
};

export function RadiusChart() {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-slate-800 text-sm font-semibold tracking-wide">
            Radius–Time Curve
          </h3>
          <p className="text-slate-400 text-xs mt-0.5">Bubble radius vs. frame number</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-0.5 bg-red-500 rounded" />
            <span className="text-slate-400 text-xs">Measured</span>
          </div>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 8, right: 24, bottom: 32, left: 16 }}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#F1F5F9"
              strokeOpacity={1}
            />
            <XAxis
              dataKey="frame"
              type="number"
              name="Frame"
              domain={[1, 121]}
              ticks={[1, 21, 41, 61, 81, 101, 121]}
              tick={{ fontSize: 11, fill: "#94A3B8", fontFamily: "monospace" }}
              axisLine={{ stroke: "#E2E8F0" }}
              tickLine={{ stroke: "#E2E8F0" }}
              label={{
                value: "Frame No.",
                position: "insideBottom",
                offset: -20,
                style: { fontSize: 11, fill: "#94A3B8" },
              }}
            />
            <YAxis
              dataKey="radius"
              type="number"
              name="Radius"
              domain={[1, 181]}
              ticks={[1, 21, 41, 61, 81, 101, 121, 141, 161, 181]}
              tick={{ fontSize: 11, fill: "#94A3B8", fontFamily: "monospace" }}
              axisLine={{ stroke: "#E2E8F0" }}
              tickLine={{ stroke: "#E2E8F0" }}
              label={{
                value: "Radius [px]",
                angle: -90,
                position: "insideLeft",
                offset: 8,
                style: { fontSize: 11, fill: "#94A3B8" },
              }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "transparent" }} />
            <Scatter
              data={chartData}
              fill="#EF4444"
              shape={(props: any) => {
                const { cx, cy } = props;
                return (
                  <line
                    key={`cross-${cx}-${cy}`}
                    x1={cx - 4}
                    y1={cy - 4}
                    x2={cx + 4}
                    y2={cy + 4}
                    stroke="#EF4444"
                    strokeWidth={1.5}
                  />
                );
              }}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
