import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiClient } from "../../shared/api/client";
import { Panel } from "../../shared/ui/Panel";
import { StatCard } from "../../shared/ui/StatCard";
import { asNumber, getTail, safeArray } from "../../shared/utils/data";
import { compactFmt, formatAxis, numberFmt } from "../../shared/utils/formats";

export function ForecastPage({ countryCode, indicatorCode }) {
  const [horizon, setHorizon] = useState(5);
  const [forecastResult, setForecastResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const forecastPoints = safeArray(forecastResult?.forecast);

  const chartData = useMemo(() => {
    if (!forecastPoints.length) {
      return [];
    }

    return forecastPoints.map((point) => ({
      year: point.year,
      historical: point.type === "historical" ? asNumber(point.value) : null,
      forecast: point.type === "forecast" ? asNumber(point.value) : null,
    }));
  }, [forecastPoints]);

  const forecastSummary = useMemo(() => {
    if (!forecastPoints.length) {
      return null;
    }

    const historical = forecastPoints.filter((point) => point.type === "historical");
    const projected = forecastPoints.filter((point) => point.type === "forecast");
    const histLast = getTail(historical);
    const projLast = getTail(projected);

    if (!histLast || !projLast) {
      return null;
    }

    const histValue = asNumber(histLast.value);
    const projValue = asNumber(projLast.value);
    const deltaPct = histValue ? ((projValue - histValue) / Math.abs(histValue)) * 100 : 0;

    return {
      horizonEndYear: projLast.year,
      projectedValue: projValue,
      deltaPct,
      direction: deltaPct > 0 ? "up" : deltaPct < 0 ? "down" : "flat",
    };
  }, [forecastPoints]);

  const handleForecast = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await apiClient.forecast({
        countryCode,
        indicatorCode,
        horizon,
      });
      setForecastResult(response);
    } catch (forecastError) {
      setError(forecastError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tab-content">
      <div className="page-header">
        <p className="page-kicker">Predictive Studio</p>
        <h2>Forecast</h2>
        <p>Run model-backed projections and compare forecast trajectories with historical signals.</p>
      </div>

      <section className="info-strip" aria-label="Forecast context">
        <p>
          Active scope: <strong>{countryCode || "No country selected"}</strong> / <strong>{indicatorCode || "No indicator selected"}</strong>
        </p>
      </section>

      {error ? <p className="error-banner">{error}</p> : null}

      <Panel
        title="Forecast Studio"
        eyebrow="Model Runner"
        subtitle="The service selects the best model based on RMSE performance."
        actions={<span className="panel-pill">{forecastResult?.model_used ?? "No model yet"}</span>}
      >
        <div className="forecast-actions">
          <label>
            Forecast horizon (years)
            <input
              type="number"
              min={1}
              max={20}
              value={horizon}
              onChange={(event) => setHorizon(asNumber(event.target.value))}
            />
          </label>

          <button onClick={handleForecast} type="button" disabled={loading || !countryCode || !indicatorCode}>
            {loading ? "Generating..." : "Generate Forecast"}
          </button>
        </div>

        {!countryCode || !indicatorCode ? (
          <p className="status-banner">Select both country and indicator in Global Filters to enable forecasting.</p>
        ) : null}

        {forecastSummary ? (
          <div className="forecast-summary-grid">
            <StatCard label="Projection End" value={`${forecastSummary.horizonEndYear}`} tone="slate" />
            <StatCard label="Projected Value" value={numberFmt.format(forecastSummary.projectedValue)} tone="mint" />
            <StatCard
              label="Shift vs Last Historical"
              value={`${forecastSummary.deltaPct.toFixed(1)}%`}
              trend={forecastSummary.direction}
              tone="sun"
            />
          </div>
        ) : null}

        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={360}>
            <LineChart data={chartData} margin={{ top: 12, right: 16, left: 8, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 49, 49, 0.18)" />
              <XAxis
                dataKey="year"
                tick={{ fill: "var(--text)", fontSize: 12 }}
                tickMargin={10}
                minTickGap={22}
                interval="preserveStartEnd"
              />
              <YAxis
                width={72}
                tickMargin={10}
                tick={{ fill: "var(--text)", fontSize: 12 }}
                tickFormatter={(value) => compactFmt.format(asNumber(value))}
              />
              <Tooltip formatter={(value) => numberFmt.format(asNumber(value))} />
              <Legend />
              <Line dataKey="historical" name="Historical" stroke="var(--text)" strokeWidth={2.8} dot={false} />
              <Line
                dataKey="forecast"
                name="Forecast"
                stroke="#ff3131"
                strokeWidth={2.8}
                strokeDasharray="7 5"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Panel>
    </div>
  );
}

export default ForecastPage;
