/** Navigation sidebar with tab links. */
import { BarChart2, Database, TrendingUp, Bot } from "lucide-react";

const NAV_ITEMS = [
  { label: "Overview", icon: BarChart2, id: "overview" },
  { label: "Data Explorer", icon: Database, id: "explorer" },
  { label: "Forecasting", icon: TrendingUp, id: "forecast" },
  { label: "AI Insights", icon: Bot, id: "insights" },
];

interface Props {
  active: string;
  onChange: (id: string) => void;
  dataInfo?: { total: number; countries: number; indicators: number; yearSpan: string };
}

export default function Sidebar({ active, onChange, dataInfo }: Props) {
  return (
    <aside className="w-64 shrink-0 bg-card border-r border-border flex flex-col gap-6 p-5">
      {/* Branding */}
      <div className="flex items-center gap-3 pb-4 border-b border-border">
        <span className="text-3xl">⚡</span>
        <div>
          <p className="text-sm font-bold text-white leading-tight">Eurostat Energy</p>
          <p className="text-xs text-slate-400">AI Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map(({ label, icon: Icon, id }) => (
          <button
            key={id}
            onClick={() => onChange(id)}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all
              ${active === id
                ? "bg-gradient-to-r from-primary to-primary-dark text-white shadow-md shadow-primary/30"
                : "text-slate-400 hover:text-white hover:bg-white/5"
              }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>

      {/* Data stats */}
      {dataInfo && (
        <div className="mt-auto pt-4 border-t border-border space-y-3">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Data Info</p>
          <Stat label="Records" value={dataInfo.total.toLocaleString()} />
          <Stat label="Countries" value={String(dataInfo.countries)} />
          <Stat label="Indicators" value={String(dataInfo.indicators)} />
          <Stat label="Year Span" value={dataInfo.yearSpan} />
        </div>
      )}
    </aside>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-slate-400">{label}</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}
