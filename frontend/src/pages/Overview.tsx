/** Overview dashboard – KPI cards + top-10 bar chart + Germany trend line. */
import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend,
} from "recharts";
import { fetchMetrics, fetchData, type ObservationRow } from "../api/client";
import KPICard from "../components/KPICard";
import Spinner from "../components/Spinner";
import ErrorAlert from "../components/ErrorAlert";

const CHART_STYLE = {
  background: "transparent",
  fontFamily: "inherit",
};

export default function Overview() {
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
  } = useQuery({ queryKey: ["metrics"], queryFn: fetchMetrics });

  const {
    data: allData,
    isLoading: dataLoading,
    error: dataError,
  } = useQuery({ queryKey: ["data"], queryFn: () => fetchData() });

  const latestYear = metrics?.latest_year ?? 0;

  /** Top-10 countries by GEP in the latest year */
  const top10 = useMemo(() => {
    if (!allData) return [];
    const byCountry = new Map<string, { country: string; value: number }>();
    allData.records
      .filter((r: ObservationRow) => r.indicator_code === "GEP" && r.year === latestYear)
      .forEach((r: ObservationRow) => {
        const prev = byCountry.get(r.country_code)?.value ?? 0;
        byCountry.set(r.country_code, { country: r.country_name, value: prev + r.value });
      });
    return Array.from(byCountry.values())
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)
      .reverse(); // recharts horizontal bars: smallest at top
  }, [allData, latestYear]);

  /** Germany GEP year-over-year */
  const germanyTrend = useMemo(() => {
    if (!allData) return [];
    return allData.records
      .filter((r: ObservationRow) => r.country_code === "DE" && r.indicator_code === "GEP")
      .sort((a, b) => a.year - b.year)
      .map((r: ObservationRow) => ({ year: r.year, value: Math.round(r.value) }));
  }, [allData]);

  if (metricsLoading || dataLoading)
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size={40} />
      </div>
    );

  if (metricsError || dataError)
    return <ErrorAlert message="Failed to load data. Please ensure the ETL pipeline has run." />;

  if (!metrics) return null;

  const gepTrend: "up" | "down" | "neutral" =
    metrics.gep_change_pct > 0 ? "up" : metrics.gep_change_pct < 0 ? "down" : "neutral";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Overview Dashboard</h2>
        <p className="text-sm text-slate-400 mt-1">
          Latest year: <span className="text-primary font-semibold">{latestYear}</span>
        </p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total GEP (Latest Year)"
          value={`${(metrics.total_gep_latest / 1000).toFixed(1)} TWh`}
          subtitle={`${metrics.gep_change_pct > 0 ? "+" : ""}${metrics.gep_change_pct.toFixed(1)}% YoY`}
          icon="⚡"
          trend={gepTrend}
        />
        <KPICard
          title="Top Producer"
          value={metrics.top_producer_name}
          subtitle={`${(metrics.top_producer_value / 1000).toFixed(1)} TWh`}
          icon="🏆"
        />
        <KPICard
          title="Average GEP"
          value={`${(metrics.avg_gep / 1000).toFixed(1)} TWh`}
          subtitle="per country"
          icon="📊"
        />
        <KPICard
          title="Countries Reporting"
          value={String(metrics.countries_reporting)}
          icon="🌍"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Top-10 horizontal bar */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">
            🏆 Top 10 Countries by GEP ({latestYear})
          </h3>
          <ResponsiveContainer width="100%" height={320} style={CHART_STYLE}>
            <BarChart data={top10} layout="vertical" margin={{ left: 8, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis
                type="number"
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}T`}
              />
              <YAxis
                type="category"
                dataKey="country"
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                width={28}
              />
              <Tooltip
                contentStyle={{ background: "#242938", border: "none", borderRadius: 8 }}
                labelStyle={{ color: "#fff" }}
                formatter={(v) => v != null ? [`${(Number(v) / 1000).toFixed(2)} TWh`, "GEP"] : ["N/A", "GEP"]}
              />
              <Bar dataKey="value" fill="#667eea" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Germany trend */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">
            📈 Germany GEP Trend
          </h3>
          <ResponsiveContainer width="100%" height={320} style={CHART_STYLE}>
            <LineChart data={germanyTrend} margin={{ left: 8, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="year" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}T`}
              />
              <Tooltip
                contentStyle={{ background: "#242938", border: "none", borderRadius: 8 }}
                labelStyle={{ color: "#fff" }}
                formatter={(v) => v != null ? [`${(Number(v) / 1000).toFixed(2)} TWh`, "GEP"] : ["N/A", "GEP"]}
              />
              <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
              <Line
                type="monotone"
                dataKey="value"
                name="GEP (GWh)"
                stroke="#667eea"
                strokeWidth={3}
                dot={{ fill: "#667eea", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
