/** Interactive data explorer – country + indicator selector, time-series + comparison chart. */
import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { fetchData, type ObservationRow } from "../api/client";
import Spinner from "../components/Spinner";
import ErrorAlert from "../components/ErrorAlert";

export default function DataExplorer() {
  const [yearRange, setYearRange] = useState<[number, number] | null>(null);

  const { data: allData, isLoading, error } = useQuery({
    queryKey: ["data"],
    queryFn: () => fetchData(),
    staleTime: 10 * 60 * 1000,
  });

  const minYear = allData?.min_year ?? 2000;
  const maxYear = allData?.max_year ?? 2023;
  const effectiveRange = yearRange ?? [minYear, maxYear];

  const [selectedCountry, setSelectedCountry] = useState<string>("");
  const [selectedIndicator, setSelectedIndicator] = useState<string>("");

  // Set defaults once data arrives
  useEffect(() => {
    if (allData && !selectedCountry && allData.countries.length > 0) {
      setSelectedCountry(allData.countries[0]);
    }
    if (allData && !selectedIndicator && allData.indicators.length > 0) {
      setSelectedIndicator(allData.indicators[0]);
    }
  }, [allData, selectedCountry, selectedIndicator]);

  /** Time series for selected country + indicator */
  const timeSeries = useMemo(() => {
    if (!allData || !selectedCountry || !selectedIndicator) return [];
    return allData.records
      .filter(
        (r: ObservationRow) =>
          r.country_code === selectedCountry &&
          r.indicator_code === selectedIndicator &&
          r.year >= effectiveRange[0] &&
          r.year <= effectiveRange[1]
      )
      .sort((a, b) => a.year - b.year)
      .map((r: ObservationRow) => ({ year: r.year, value: Math.round(r.value) }));
  }, [allData, selectedCountry, selectedIndicator, effectiveRange]);

  /** Top-10 countries for selected indicator */
  const top10 = useMemo(() => {
    if (!allData || !selectedIndicator) return [];
    const avg = new Map<string, { name: string; total: number; count: number }>();
    allData.records
      .filter(
        (r: ObservationRow) =>
          r.indicator_code === selectedIndicator &&
          r.year >= effectiveRange[0] &&
          r.year <= effectiveRange[1]
      )
      .forEach((r: ObservationRow) => {
        const prev = avg.get(r.country_code) ?? { name: r.country_name, total: 0, count: 0 };
        avg.set(r.country_code, { name: prev.name, total: prev.total + r.value, count: prev.count + 1 });
      });
    return Array.from(avg.entries())
      .map(([, v]) => ({ country: v.name, value: Math.round(v.total / v.count) }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);
  }, [allData, selectedIndicator, effectiveRange]);

  /** Raw table rows */
  const tableRows = useMemo(() => {
    if (!allData || !selectedCountry || !selectedIndicator) return [];
    return allData.records
      .filter(
        (r: ObservationRow) =>
          r.country_code === selectedCountry &&
          r.indicator_code === selectedIndicator &&
          r.year >= effectiveRange[0] &&
          r.year <= effectiveRange[1]
      )
      .sort((a, b) => b.year - a.year);
  }, [allData, selectedCountry, selectedIndicator, effectiveRange]);

  if (isLoading)
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size={40} />
      </div>
    );

  if (error)
    return <ErrorAlert message="Failed to load data. Please ensure the ETL pipeline has run." />;

  if (!allData) return null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Data Explorer</h2>
        <p className="text-sm text-slate-400 mt-1">
          Explore energy data by country and indicator.
        </p>
      </div>

      {/* Filters */}
      <div className="card grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Country</label>
          <select
            className="select-field"
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
          >
            {allData.countries.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Indicator</label>
          <select
            className="select-field"
            value={selectedIndicator}
            onChange={(e) => setSelectedIndicator(e.target.value)}
          >
            {allData.indicators.map((i) => (
              <option key={i} value={i}>{i}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">
            Year Range: {effectiveRange[0]} – {effectiveRange[1]}
          </label>
          <div className="flex gap-2 items-center">
            <input
              type="range"
              min={minYear}
              max={maxYear}
              value={effectiveRange[0]}
              onChange={(e) => setYearRange([Number(e.target.value), effectiveRange[1]])}
              className="w-full accent-primary"
            />
            <input
              type="range"
              min={minYear}
              max={maxYear}
              value={effectiveRange[1]}
              onChange={(e) => setYearRange([effectiveRange[0], Number(e.target.value)])}
              className="w-full accent-primary"
            />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">
            📈 Time Series – {selectedCountry} / {selectedIndicator}
          </h3>
          {timeSeries.length === 0 ? (
            <p className="text-slate-500 text-sm">No data for this selection.</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={timeSeries} margin={{ left: 8, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="year" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#242938", border: "none", borderRadius: 8 }}
                  labelStyle={{ color: "#fff" }}
                />
                <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
                <Line
                  type="monotone"
                  dataKey="value"
                  name={selectedIndicator}
                  stroke="#667eea"
                  strokeWidth={3}
                  dot={{ fill: "#667eea", r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">
            🌐 Top 10 Countries – {selectedIndicator}
          </h3>
          {top10.length === 0 ? (
            <p className="text-slate-500 text-sm">No comparison data available.</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={top10} margin={{ left: 8, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="country" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#242938", border: "none", borderRadius: 8 }}
                  labelStyle={{ color: "#fff" }}
                />
                <Bar dataKey="value" fill="#764ba2" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Raw data table */}
      <div className="card overflow-x-auto">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">📋 Raw Data</h3>
        {tableRows.length === 0 ? (
          <p className="text-slate-500 text-sm">No data for this selection.</p>
        ) : (
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="border-b border-border text-slate-400">
                <th className="pb-2 pr-4">Year</th>
                <th className="pb-2 pr-4">Country</th>
                <th className="pb-2 pr-4">Indicator</th>
                <th className="pb-2 pr-4">Value</th>
                <th className="pb-2">Unit</th>
              </tr>
            </thead>
            <tbody>
              {tableRows.slice(0, 50).map((r, i) => (
                <tr key={i} className="border-b border-border/50 text-slate-300 hover:bg-white/5">
                  <td className="py-2 pr-4">{r.year}</td>
                  <td className="py-2 pr-4">{r.country_name}</td>
                  <td className="py-2 pr-4">{r.indicator_label || r.indicator_code}</td>
                  <td className="py-2 pr-4">{r.value.toLocaleString()}</td>
                  <td className="py-2">{r.unit_label}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {tableRows.length > 50 && (
          <p className="text-xs text-slate-500 mt-2">Showing 50 of {tableRows.length} rows.</p>
        )}
      </div>
    </div>
  );
}
