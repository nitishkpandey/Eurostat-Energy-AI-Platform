/** ML forecasting page – country + indicator selector, combined historical + forecast chart. */
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ComposedChart, Line, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine,
} from "recharts";
import { fetchData, fetchForecast, type ForecastPoint } from "../api/client";
import Spinner from "../components/Spinner";
import ErrorAlert from "../components/ErrorAlert";

export default function Forecasting() {
  const [country, setCountry] = useState("DE");
  const [indicator, setIndicator] = useState("GEP");
  const [horizon, setHorizon] = useState(5);
  const [triggered, setTriggered] = useState(false);

  const { data: allData } = useQuery({
    queryKey: ["data"],
    queryFn: () => fetchData(),
    staleTime: 10 * 60 * 1000,
  });

  const {
    data: forecastData,
    isFetching,
    error,
    refetch,
  } = useQuery({
    queryKey: ["forecast", country, indicator, horizon],
    queryFn: () => fetchForecast(country, indicator, horizon),
    enabled: triggered,
    retry: false,
  });

  const handleGenerate = () => {
    setTriggered(true);
    refetch();
  };

  // Split historical vs forecast for the chart
  const lastHistoricalYear =
    forecastData?.data.filter((p: ForecastPoint) => p.type === "historical").slice(-1)[0]?.year ?? 0;

  const chartData =
    forecastData?.data.map((p: ForecastPoint) => ({
      year: p.year,
      historical: p.type === "historical" ? p.value : null,
      forecast: p.type === "forecast" ? p.value : null,
    })) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">ML Forecasting</h2>
        <p className="text-sm text-slate-400 mt-1">
          Generate future predictions using XGBoost and Exponential Smoothing. The best model is
          automatically selected based on RMSE.
        </p>
      </div>

      {/* Controls */}
      <div className="card grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Country</label>
          <select
            className="select-field"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          >
            {(allData?.countries ?? ["DE"]).map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Indicator</label>
          <select
            className="select-field"
            value={indicator}
            onChange={(e) => setIndicator(e.target.value)}
          >
            {(allData?.indicators ?? ["GEP"]).map((i) => (
              <option key={i} value={i}>{i}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">
            Forecast Horizon: {horizon} years
          </label>
          <input
            type="range"
            min={1}
            max={10}
            value={horizon}
            onChange={(e) => setHorizon(Number(e.target.value))}
            className="w-full accent-primary"
          />
        </div>
        <button
          className="btn-primary"
          onClick={handleGenerate}
          disabled={isFetching}
        >
          {isFetching ? "Generating…" : "🚀 Generate Forecast"}
        </button>
      </div>

      {/* Loading */}
      {isFetching && (
        <div className="flex items-center gap-3 text-slate-400">
          <Spinner />
          <span>Training models and generating forecast…</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <ErrorAlert message="Insufficient data to generate a forecast for this selection." />
      )}

      {/* Chart */}
      {forecastData && !isFetching && (
        <>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-slate-300">
                🔮 Forecast: {indicator} – {country}
              </h3>
              <span className="text-xs px-2 py-1 rounded-full bg-primary/20 text-primary">
                Model: {forecastData.model_used}
              </span>
            </div>
            <ResponsiveContainer width="100%" height={360}>
              <ComposedChart data={chartData} margin={{ left: 8, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="year" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#242938", border: "none", borderRadius: 8 }}
                  labelStyle={{ color: "#fff" }}
                />
                <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
                {lastHistoricalYear > 0 && (
                  <ReferenceLine
                    x={lastHistoricalYear}
                    stroke="rgba(255,255,255,0.2)"
                    strokeDasharray="4 4"
                    label={{ value: "Forecast →", fill: "#94a3b8", fontSize: 10 }}
                  />
                )}
                <Area
                  type="monotone"
                  dataKey="historical"
                  name="Historical"
                  stroke="#667eea"
                  fill="#667eea22"
                  strokeWidth={3}
                  dot={{ fill: "#667eea", r: 4 }}
                  connectNulls={false}
                />
                <Line
                  type="monotone"
                  dataKey="forecast"
                  name="Forecast"
                  stroke="#f59e0b"
                  strokeWidth={3}
                  strokeDasharray="6 3"
                  dot={{ fill: "#f59e0b", r: 5, strokeWidth: 2 }}
                  connectNulls={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Forecast table */}
          <div className="card overflow-x-auto">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">📊 Forecast Data</h3>
            <table className="w-full text-sm text-left">
              <thead>
                <tr className="border-b border-border text-slate-400">
                  <th className="pb-2 pr-8">Year</th>
                  <th className="pb-2 pr-8">Value</th>
                  <th className="pb-2">Type</th>
                </tr>
              </thead>
              <tbody>
                {forecastData.data.map((row: ForecastPoint, i: number) => (
                  <tr key={i} className="border-b border-border/50 text-slate-300 hover:bg-white/5">
                    <td className="py-2 pr-8">{row.year}</td>
                    <td className="py-2 pr-8">{row.value.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                    <td className="py-2">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          row.type === "forecast"
                            ? "bg-amber-500/20 text-amber-400"
                            : "bg-primary/20 text-primary"
                        }`}
                      >
                        {row.type}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {!triggered && (
        <div className="card text-center py-12">
          <p className="text-4xl mb-3">🔮</p>
          <p className="text-slate-400">Select options above and click Generate Forecast.</p>
        </div>
      )}
    </div>
  );
}
