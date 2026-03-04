/** Reusable KPI metric card. */
interface Props {
  title: string;
  value: string;
  subtitle?: string;
  icon: string;
  trend?: "up" | "down" | "neutral";
}

export default function KPICard({ title, value, subtitle, icon, trend }: Props) {
  const trendColor =
    trend === "up" ? "text-emerald-400" : trend === "down" ? "text-red-400" : "text-slate-400";

  return (
    <div className="card flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-2xl">{icon}</span>
        {subtitle && <span className={`text-sm font-medium ${trendColor}`}>{subtitle}</span>}
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-sm text-slate-400">{title}</p>
    </div>
  );
}
