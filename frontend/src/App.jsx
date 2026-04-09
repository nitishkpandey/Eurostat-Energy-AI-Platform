import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiClient } from "./api/client";
import Panel from "./components/Panel";
import StatCard from "./components/StatCard";

const TABS = [
  { id: "overview", label: "Overview", tag: "01" },
  { id: "explorer", label: "Explorer", tag: "02" },
  { id: "forecast", label: "Forecast", tag: "03" },
  { id: "ai", label: "AI Analyst", tag: "04" },
];

const QUICK_QUESTIONS = [
  "Which country's GEP is rising fastest?",
  "Which regions show declining final consumption?",
  "Compare transport vs household energy trends.",
  "Show stable long-term GEP countries.",
];

const HEALTH_LABELS = {
  checking: "Checking API",
  healthy: "API Healthy",
  degraded: "API Degraded",
};

const numberFmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const compactFmt = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
});

const safeArray = (value) => (Array.isArray(value) ? value : []);

const asNumber = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const formatDateTime = (date) =>
  date.toLocaleString("en-US", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

const getTail = (arr) => (arr.length ? arr[arr.length - 1] : null);

const formatAxis = (value) => numberFmt.format(asNumber(value));

function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [clock, setClock] = useState(() => new Date());
  const [apiHealth, setApiHealth] = useState("checking");

  const [metadata, setMetadata] = useState(null);
  const [overview, setOverview] = useState(null);
  const [explorer, setExplorer] = useState(null);
  const [forecastResult, setForecastResult] = useState(null);
  const [aiResult, setAiResult] = useState(null);

  const [countryCode, setCountryCode] = useState("");
  const [indicatorCode, setIndicatorCode] = useState("");
  const [horizon, setHorizon] = useState(5);
  const [question, setQuestion] = useState("");

  const [startYear, setStartYear] = useState(0);
  const [endYear, setEndYear] = useState(0);
  const [reloadToken, setReloadToken] = useState(0);

  const [loading, setLoading] = useState({
    metadata: true,
    overview: false,
    explorer: false,
    forecast: false,
    ai: false,
  });
  const [error, setError] = useState("");

  useEffect(() => {
    const tick = window.setInterval(() => {
      setClock(new Date());
    }, 1000);

    return () => window.clearInterval(tick);
  }, []);

  useEffect(() => {
    let mounted = true;

    const probeHealth = async () => {
      try {
        const response = await apiClient.health();
        if (!mounted) {
          return;
        }
        setApiHealth(response?.status === "ok" ? "healthy" : "degraded");
      } catch {
        if (mounted) {
          setApiHealth("degraded");
        }
      }
    };

    probeHealth();
    const handle = window.setInterval(probeHealth, 20000);

    return () => {
      mounted = false;
      window.clearInterval(handle);
    };
  }, []);

  useEffect(() => {
    let mounted = true;

    const loadMetadata = async () => {
      setLoading((prev) => ({ ...prev, metadata: true }));
      setError("");

      try {
        const response = await apiClient.metadata();
        if (!mounted) {
          return;
        }
        setMetadata(response);

        if (response.min_year !== null && response.max_year !== null) {
          setStartYear(response.min_year);
          setEndYear(response.max_year);
        }

        setCountryCode((prev) => prev || response.countries?.[0]?.country_code || "");
        setIndicatorCode((prev) => prev || response.indicators?.[0] || "");
      } catch (fetchError) {
        if (mounted) {
          setError(fetchError.message);
        }
      } finally {
        if (mounted) {
          setLoading((prev) => ({ ...prev, metadata: false }));
        }
      }
    };

    loadMetadata();

    return () => {
      mounted = false;
    };
  }, [reloadToken]);

  useEffect(() => {
    if (!startYear || !endYear) {
      return;
    }

    let mounted = true;

    const loadOverview = async () => {
      setLoading((prev) => ({ ...prev, overview: true }));
      setError("");

      try {
        const response = await apiClient.overview({ startYear, endYear });
        if (mounted) {
          setOverview(response);
        }
      } catch (fetchError) {
        if (mounted) {
          setError(fetchError.message);
        }
      } finally {
        if (mounted) {
          setLoading((prev) => ({ ...prev, overview: false }));
        }
      }
    };

    loadOverview();

    return () => {
      mounted = false;
    };
  }, [startYear, endYear, reloadToken]);

  useEffect(() => {
    if (!countryCode || !indicatorCode || !startYear || !endYear) {
      return;
    }

    let mounted = true;

    const loadExplorer = async () => {
      setLoading((prev) => ({ ...prev, explorer: true }));
      setError("");

      try {
        const response = await apiClient.explorer({
          countryCode,
          indicatorCode,
          startYear,
          endYear,
        });
        if (mounted) {
          setExplorer(response);
        }
      } catch (fetchError) {
        if (mounted) {
          setError(fetchError.message);
        }
      } finally {
        if (mounted) {
          setLoading((prev) => ({ ...prev, explorer: false }));
        }
      }
    };

    loadExplorer();

    return () => {
      mounted = false;
    };
  }, [countryCode, indicatorCode, startYear, endYear, reloadToken]);

  const countries = safeArray(metadata?.countries);
  const indicators = safeArray(metadata?.indicators);
  const topProducers = safeArray(overview?.top_producers);
  const germanyTrend = safeArray(overview?.germany_trend);
  const explorerSeries = safeArray(explorer?.time_series);
  const explorerTop = safeArray(explorer?.top_countries);
  const explorerRaw = safeArray(explorer?.raw_data);
  const forecastPoints = safeArray(forecastResult?.forecast);

  const forecastChartData = useMemo(() => {
    if (!forecastPoints.length) {
      return [];
    }

    return forecastPoints.map((point) => ({
      year: point.year,
      historical: point.type === "historical" ? asNumber(point.value) : null,
      forecast: point.type === "forecast" ? asNumber(point.value) : null,
      value: asNumber(point.value),
      type: point.type,
    }));
  }, [forecastPoints]);

  const topProducerText = overview?.kpis?.top_producer
    ? `${overview.kpis.top_producer.country_name || overview.kpis.top_producer.country_code} (${compactFmt.format(
        asNumber(overview.kpis.top_producer.value)
      )})`
    : "-";

  const gepChange = asNumber(overview?.kpis?.gep_change_pct);
  const changeText = `${gepChange.toFixed(1)}% vs previous year`;

  const explorerTrendMeta = useMemo(() => {
    if (explorerSeries.length < 2) {
      return { change: 0, direction: "flat" };
    }

    const first = asNumber(explorerSeries[0].value);
    const last = asNumber(getTail(explorerSeries)?.value);
    if (!first) {
      return { change: 0, direction: "flat" };
    }

    const pct = ((last - first) / Math.abs(first)) * 100;
    return {
      change: pct,
      direction: pct > 0 ? "up" : pct < 0 ? "down" : "flat",
    };
  }, [explorerSeries]);

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

  const applyYearWindow = (years) => {
    if (!metadata?.min_year || !metadata?.max_year) {
      return;
    }

    const max = metadata.max_year;
    const min = metadata.min_year;

    if (years === null) {
      setStartYear(min);
      setEndYear(max);
      return;
    }

    setEndYear(max);
    setStartYear(Math.max(min, max - years + 1));
  };

  const jumpToProducer = (producer) => {
    setCountryCode(producer.country_code);
    setIndicatorCode("GEP");
    setActiveTab("explorer");
  };

  const handleRefresh = async () => {
    setError("");
    try {
      await apiClient.refreshCache();
      setReloadToken((prev) => prev + 1);
    } catch (refreshError) {
      setError(refreshError.message);
    }
  };

  const handleForecast = async () => {
    setLoading((prev) => ({ ...prev, forecast: true }));
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
      setLoading((prev) => ({ ...prev, forecast: false }));
    }
  };

  const handleAskAi = async () => {
    if (!question.trim()) {
      return;
    }

    setLoading((prev) => ({ ...prev, ai: true }));
    setError("");

    try {
      const response = await apiClient.askAi(question.trim());
      setAiResult(response);
    } catch (askError) {
      setError(askError.message);
    } finally {
      setLoading((prev) => ({ ...prev, ai: false }));
    }
  };

  const chooseQuestion = (candidate) => {
    setQuestion(candidate);
  };

  return (
    <div className={`app-shell mode-${activeTab}`}>
      <div className="ambient ambient--one" />
      <div className="ambient ambient--two" />
      <div className="ambient ambient--three" />

      <header className="hero">
        <div className="hero-topline">
          <span className={`status-chip status-chip--${apiHealth}`}>{HEALTH_LABELS[apiHealth]}</span>
          <span className="clock-chip">{formatDateTime(clock)}</span>
        </div>
        <h1>Energy analytics that feels like a modern control center.</h1>
        <p>
          A dynamic React interface over your ETL, forecasting, and AI workflows with a production
          style visual language.
        </p>

        <div className="hero-stats">
          <article>
            <p className="hero-stat-label">Records</p>
            <p className="hero-stat-value">{compactFmt.format(asNumber(metadata?.record_count))}</p>
          </article>
          <article>
            <p className="hero-stat-label">Countries</p>
            <p className="hero-stat-value">{countries.length}</p>
          </article>
          <article>
            <p className="hero-stat-label">Indicators</p>
            <p className="hero-stat-value">{indicators.length}</p>
          </article>
          <article>
            <p className="hero-stat-label">Window</p>
            <p className="hero-stat-value">
              {startYear && endYear ? `${startYear}-${endYear}` : "-"}
            </p>
          </article>
        </div>
      </header>

      <section className="panel control-strip">
        <div className="panel-body controls-grid">
          <label>
            Start year
            <input
              type="number"
              value={startYear}
              min={metadata?.min_year ?? 0}
              max={endYear || metadata?.max_year || 0}
              onChange={(event) => setStartYear(asNumber(event.target.value))}
            />
          </label>

          <label>
            End year
            <input
              type="number"
              value={endYear}
              min={startYear || metadata?.min_year || 0}
              max={metadata?.max_year ?? 0}
              onChange={(event) => setEndYear(asNumber(event.target.value))}
            />
          </label>

          <label>
            Country
            <select value={countryCode} onChange={(event) => setCountryCode(event.target.value)}>
              {countries.map((country) => (
                <option key={country.country_code} value={country.country_code}>
                  {country.country_name || country.country_code}
                </option>
              ))}
            </select>
          </label>

          <label>
            Indicator
            <select
              value={indicatorCode}
              onChange={(event) => setIndicatorCode(event.target.value)}
            >
              {indicators.map((indicator) => (
                <option key={indicator} value={indicator}>
                  {indicator}
                </option>
              ))}
            </select>
          </label>

          <button className="outline" onClick={handleRefresh} type="button">
            Sync Data
          </button>
        </div>

        <div className="year-presets">
          <button type="button" onClick={() => applyYearWindow(null)}>
            Full Span
          </button>
          <button type="button" onClick={() => applyYearWindow(10)}>
            Last 10 Years
          </button>
          <button type="button" onClick={() => applyYearWindow(5)}>
            Last 5 Years
          </button>
        </div>
      </section>

      <nav className="tabs" aria-label="Main sections">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={activeTab === tab.id ? "tab is-active" : "tab"}
            onClick={() => setActiveTab(tab.id)}
            type="button"
          >
            <span className="tab-tag">{tab.tag}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>

      {error ? <p className="error-banner">{error}</p> : null}
      {loading.metadata ? <p className="status">Loading metadata...</p> : null}

      {activeTab === "overview" ? (
        <div className="tab-content">
          <div className="stats-grid">
            <StatCard
              label="Total GEP"
              value={`${numberFmt.format(asNumber(overview?.kpis?.latest_gep))} GWh`}
              meta={changeText}
              tone="mint"
              trend={gepChange >= 0 ? "up" : "down"}
            />
            <StatCard label="Top Producer" value={topProducerText} tone="sun" />
            <StatCard
              label="Average GEP"
              value={`${numberFmt.format(asNumber(overview?.kpis?.avg_gep))} GWh`}
              tone="teal"
            />
            <StatCard
              label="Countries Reporting"
              value={numberFmt.format(asNumber(overview?.kpis?.countries_reporting))}
              tone="slate"
            />
          </div>

          <div className="chart-grid">
            <Panel title="Top Producers" subtitle={`Latest year: ${overview?.latest_year ?? "-"}`}>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={330}>
                  <BarChart
                    data={topProducers}
                    layout="vertical"
                    margin={{ top: 10, right: 16, left: 4, bottom: 10 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(180, 199, 220, 0.2)" />
                    <XAxis type="number" tickFormatter={formatAxis} />
                    <YAxis
                      type="category"
                      dataKey="country_name"
                      width={125}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip formatter={(value) => numberFmt.format(asNumber(value))} />
                    <Bar dataKey="value" fill="var(--mode-accent)" radius={[0, 8, 8, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Panel>

            <Panel title="Germany Trendline" subtitle="Historical GEP trajectory">
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={330}>
                  <AreaChart data={germanyTrend} margin={{ top: 16, right: 16, left: 6, bottom: 6 }}>
                    <defs>
                      <linearGradient id="overviewArea" x1="0" y1="0" x2="0" y2="1">
                        <stop
                          offset="5%"
                          stopColor="var(--mode-accent-strong)"
                          stopOpacity={0.55}
                        />
                        <stop
                          offset="95%"
                          stopColor="var(--mode-accent-strong)"
                          stopOpacity={0.02}
                        />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(180, 199, 220, 0.2)" />
                    <XAxis dataKey="year" />
                    <YAxis tickFormatter={formatAxis} />
                    <Tooltip formatter={(value) => numberFmt.format(asNumber(value))} />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="var(--mode-accent-strong)"
                      fill="url(#overviewArea)"
                      strokeWidth={2.6}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Panel>
          </div>

          <Panel title="Producer Pulse" subtitle="Jump directly into a country explorer view">
            <div className="producer-rail">
              {topProducers.slice(0, 8).map((producer, idx) => (
                <button
                  key={`${producer.country_code}-${idx}`}
                  className="producer-card"
                  type="button"
                  onClick={() => jumpToProducer(producer)}
                >
                  <p>{producer.country_name || producer.country_code}</p>
                  <strong>{compactFmt.format(asNumber(producer.value))}</strong>
                </button>
              ))}
            </div>
          </Panel>

          {loading.overview ? <p className="status">Updating overview...</p> : null}
        </div>
      ) : null}

      {activeTab === "explorer" ? (
        <div className="tab-content">
          <div className="stats-grid">
            <StatCard
              label="Selected Pair"
              value={`${countryCode || "-"} / ${indicatorCode || "-"}`}
              tone="teal"
            />
            <StatCard label="Series Points" value={numberFmt.format(explorerSeries.length)} tone="slate" />
            <StatCard
              label="Trend Shift"
              value={`${explorerTrendMeta.change.toFixed(1)}%`}
              trend={explorerTrendMeta.direction}
              tone="mint"
            />
            <StatCard label="Rows Loaded" value={numberFmt.format(explorerRaw.length)} tone="sun" />
          </div>

          <div className="chart-grid">
            <Panel title="Time Series" subtitle={`${countryCode} • ${indicatorCode}`}>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={330}>
                  <LineChart
                    data={explorerSeries}
                    margin={{ top: 10, right: 16, left: 6, bottom: 10 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(180, 199, 220, 0.22)" />
                    <XAxis dataKey="year" />
                    <YAxis tickFormatter={formatAxis} />
                    <Tooltip formatter={(value) => numberFmt.format(asNumber(value))} />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="var(--mode-accent-strong)"
                      strokeWidth={2.8}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Panel>

            <Panel title="Cross-Country Signal" subtitle={`Top countries by ${indicatorCode}`}>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={330}>
                  <BarChart data={explorerTop} margin={{ top: 10, right: 16, left: 0, bottom: 14 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(180, 199, 220, 0.22)" />
                    <XAxis dataKey="country_code" angle={-30} textAnchor="end" height={58} />
                    <YAxis tickFormatter={formatAxis} />
                    <Tooltip formatter={(value) => numberFmt.format(asNumber(value))} />
                    <Bar dataKey="value" fill="var(--mode-accent)" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Panel>
          </div>

          <Panel
            title="Data Grid"
            subtitle="Scroll the latest rows"
            actions={<span className="panel-pill">Showing {Math.min(explorerRaw.length, 50)} rows</span>}
          >
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Year</th>
                    <th>Country</th>
                    <th>Indicator</th>
                    <th>Value</th>
                    <th>Unit</th>
                  </tr>
                </thead>
                <tbody>
                  {explorerRaw.slice(0, 50).map((row, idx) => (
                    <tr key={`${row.year}-${idx}`}>
                      <td>{row.year}</td>
                      <td>{row.country_name || "-"}</td>
                      <td>{row.indicator_label || "-"}</td>
                      <td>{numberFmt.format(asNumber(row.value))}</td>
                      <td>{row.unit_label || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>

          {loading.explorer ? <p className="status">Loading explorer data...</p> : null}
        </div>
      ) : null}

      {activeTab === "forecast" ? (
        <div className="tab-content">
          <Panel
            title="Forecast Studio"
            subtitle="Models are evaluated and the lower-RMSE model is selected automatically."
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
              <button onClick={handleForecast} type="button" disabled={loading.forecast}>
                {loading.forecast ? "Generating..." : "Generate Forecast"}
              </button>
            </div>

            {forecastSummary ? (
              <div className="forecast-summary-grid">
                <StatCard label="Projection End" value={`${forecastSummary.horizonEndYear}`} tone="slate" />
                <StatCard
                  label="Projected Value"
                  value={numberFmt.format(forecastSummary.projectedValue)}
                  tone="mint"
                />
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
                <LineChart
                  data={forecastChartData}
                  margin={{ top: 10, right: 16, left: 6, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(180, 199, 220, 0.2)" />
                  <XAxis dataKey="year" />
                  <YAxis tickFormatter={formatAxis} />
                  <Tooltip formatter={(value) => numberFmt.format(asNumber(value))} />
                  <Legend />
                  <Line
                    dataKey="historical"
                    name="Historical"
                    stroke="#5ad2b3"
                    strokeWidth={2.8}
                    dot={false}
                  />
                  <Line
                    dataKey="forecast"
                    name="Forecast"
                    stroke="#ffb56b"
                    strokeWidth={2.8}
                    strokeDasharray="7 5"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Panel>
        </div>
      ) : null}

      {activeTab === "ai" ? (
        <div className="tab-content">
          <Panel title="AI Insights Assistant" subtitle="Ask trend and comparison questions in natural language.">
            <div className="quick-questions">
              {QUICK_QUESTIONS.map((candidate) => (
                <button
                  key={candidate}
                  type="button"
                  className="quick-chip"
                  onClick={() => chooseQuestion(candidate)}
                >
                  {candidate}
                </button>
              ))}
            </div>

            <div className="ai-input">
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask your question..."
                rows={5}
              />
              <button onClick={handleAskAi} type="button" disabled={loading.ai}>
                {loading.ai ? "Analyzing..." : "Ask AI"}
              </button>
            </div>

            {aiResult ? (
              <article className="ai-response">
                <p className="ai-mode">Mode: {aiResult.mode}</p>
                <p>{aiResult.answer}</p>
              </article>
            ) : null}
          </Panel>
        </div>
      ) : null}
    </div>
  );
}

export default App;
