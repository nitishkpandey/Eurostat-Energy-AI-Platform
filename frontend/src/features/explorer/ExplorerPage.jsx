import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Panel } from "../../shared/ui/Panel";
import { StatCard } from "../../shared/ui/StatCard";
import { asNumber, getTail, safeArray } from "../../shared/utils/data";
import { compactFmt, formatAxis, numberFmt } from "../../shared/utils/formats";

export function ExplorerPage({
  explorer,
  loading,
  country,
  indicator,
  countries,
  indicators,
  countryCode,
  onCountryChange,
  onIndicatorChange,
}) {
  const series = safeArray(explorer?.time_series);
  const topCountries = safeArray(explorer?.top_countries);
  const rawRows = safeArray(explorer?.raw_data);
  const countryOptions = safeArray(countries);
  const indicatorOptions = safeArray(indicators);

  const selectedCountryCode = countryCode || country?.country_code || "";
  const selectedCountryName = country?.country_name || country?.country_code || "-";

  const trendMeta = useMemo(() => {
    if (series.length < 2) {
      return { change: 0, direction: "flat" };
    }

    const first = asNumber(series[0].value);
    const last = asNumber(getTail(series)?.value);

    if (!first) {
      return { change: 0, direction: "flat" };
    }

    const pct = ((last - first) / Math.abs(first)) * 100;
    return {
      change: pct,
      direction: pct > 0 ? "up" : pct < 0 ? "down" : "flat",
    };
  }, [series]);

  return (
    <div className="tab-content">
      <div className="page-header">
        <p className="page-kicker">Deep Dive Analytics</p>
        <h2>Explorer</h2>
        <p>Detailed country and indicator analysis with raw data and trend context.</p>
      </div>

      <section className="info-strip" aria-label="Explorer context">
        <p>
          Comparing <strong>{country?.country_name || country?.country_code || "selected country"}</strong> across
          {" "}
          <strong>{indicator || "indicator"}</strong> in the active time window.
        </p>
      </section>

      <div className="stats-grid">
        <StatCard label="Selected Country" value={selectedCountryCode || "-"} meta={selectedCountryName} tone="teal" />
        <StatCard label="Indicator" value={indicator || "-"} tone="slate" />
        <StatCard
          label="Trend Shift"
          value={`${trendMeta.change.toFixed(1)}%`}
          trend={trendMeta.direction}
          tone="mint"
        />
        <StatCard label="Series Points" value={numberFmt.format(series.length)} tone="sun" />
      </div>

      <details className="explorer-filter-toggle">
        <summary>
          <span>Choose and Filter</span>
          <span className="explorer-filter-summary">{selectedCountryCode || "No country"} / {indicator || "No indicator"}</span>
        </summary>

        <div className="explorer-filter-grid">
          <label className="filter-field">
            <span className="filter-label">Country</span>
            <select value={selectedCountryCode} onChange={(event) => onCountryChange(event.target.value)}>
              {countryOptions.map((option) => (
                <option key={option.country_code} value={option.country_code}>
                  {option.country_name || option.country_code}
                </option>
              ))}
            </select>
          </label>

          <label className="filter-field">
            <span className="filter-label">Indicator</span>
            <select value={indicator || ""} onChange={(event) => onIndicatorChange(event.target.value)}>
              {indicatorOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        </div>
      </details>

      <div className="chart-grid">
        <Panel
          title="Time Series"
          eyebrow="Signal Over Time"
          subtitle={`${country?.country_name || country?.country_code || "-"} | ${indicator || "-"}`}
        >
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={series} margin={{ top: 12, right: 16, left: 8, bottom: 16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 49, 49, 0.18)" />
                <XAxis dataKey="year" tick={{ fill: "var(--text)", fontSize: 12 }} tickMargin={10} minTickGap={22} />
                <YAxis
                  width={72}
                  tickMargin={10}
                  tick={{ fill: "var(--text)", fontSize: 12 }}
                  tickFormatter={(value) => compactFmt.format(asNumber(value))}
                />
                <Tooltip formatter={(value) => numberFmt.format(asNumber(value))} />
                <Line type="monotone" dataKey="value" stroke="var(--accent-strong)" strokeWidth={2.6} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel
          title="Cross-Country Signal"
          eyebrow="Benchmark View"
          subtitle={`Top countries by ${indicator || "selected indicator"}`}
        >
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={340}>
              <BarChart data={topCountries} margin={{ top: 12, right: 16, left: 10, bottom: 24 }} barCategoryGap="26%">
                <defs>
                  <linearGradient id="explorerBars" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ff6868" />
                    <stop offset="55%" stopColor="#ff3131" />
                    <stop offset="100%" stopColor="#b91f1f" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 49, 49, 0.18)" />
                <XAxis
                  dataKey="country_code"
                  angle={-24}
                  textAnchor="end"
                  height={62}
                  tick={{ fill: "var(--text)", fontSize: 12 }}
                  tickMargin={8}
                />
                <YAxis
                  width={72}
                  tickMargin={10}
                  tick={{ fill: "var(--text)", fontSize: 12 }}
                  tickFormatter={(value) => compactFmt.format(asNumber(value))}
                />
                <Tooltip formatter={(value) => numberFmt.format(asNumber(value))} />
                <Bar dataKey="value" fill="url(#explorerBars)" radius={[10, 10, 4, 4]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <Panel
        title="Raw Data"
        eyebrow="Source Records"
        subtitle={`${rawRows.length} rows loaded`}
        actions={
          <button type="button" className="outline-button">
            Download CSV
          </button>
        }
      >
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Year</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              {rawRows.map((row) => (
                <tr key={`${row.year}-${row.value}`}>
                  <td>{row.year}</td>
                  <td>{numberFmt.format(asNumber(row.value))}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {loading.explorer ? <p className="status-banner">Refreshing explorer data...</p> : null}
    </div>
  );
}

export default ExplorerPage;
