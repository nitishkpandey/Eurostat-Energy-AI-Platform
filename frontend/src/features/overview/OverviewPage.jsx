import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiClient } from "../../shared/api/client";
import { Panel } from "../../shared/ui/Panel";
import { StatCard } from "../../shared/ui/StatCard";
import { asNumber, safeArray } from "../../shared/utils/data";
import { compactFmt, formatAxis, numberFmt } from "../../shared/utils/formats";

export function OverviewPage({
  overview,
  loading,
  startYear,
  endYear,
  onProducerClick,
}) {
  const topProducers = safeArray(overview?.top_producers);
  const topProducerChartData = topProducers.map((producer) => ({
    ...producer,
    country_label: producer.country_name || producer.country_code || "Unknown",
    country_short_label:
      producer.country_code === "EU27_2020"
        ? "EU27"
        : producer.country_code || (producer.country_name || "UNK").slice(0, 8).toUpperCase(),
  }));
  const countryTrends = overview?.country_trends || {};
  const [fallbackTrends, setFallbackTrends] = useState({});
  const [selectedCountryCode, setSelectedCountryCode] = useState(
    overview?.selected_country_code || topProducers[0]?.country_code || null
  );

  useEffect(() => {
    const nextDefault = overview?.selected_country_code || topProducers[0]?.country_code || null;
    setSelectedCountryCode(nextDefault);
  }, [overview?.selected_country_code, topProducers]);

  useEffect(() => {
    setFallbackTrends({});
  }, [startYear, endYear]);

  const selectedEmbeddedTrend = safeArray(countryTrends?.[selectedCountryCode]);
  const selectedFallbackTrend = safeArray(fallbackTrends?.[selectedCountryCode]);
  const hasEmbeddedTrend = selectedEmbeddedTrend.length > 0;
  const hasFallbackTrend = selectedFallbackTrend.length > 0;
  const hasFallbackCache = selectedCountryCode
    ? Object.prototype.hasOwnProperty.call(fallbackTrends, selectedCountryCode)
    : false;

  useEffect(() => {
    let cancelled = false;

    const loadTrendFallback = async () => {
      if (!selectedCountryCode) {
        return;
      }

      if (hasEmbeddedTrend || hasFallbackTrend || hasFallbackCache) {
        return;
      }

      try {
        const response = await apiClient.explorer({
          countryCode: selectedCountryCode,
          indicatorCode: "GEP",
          startYear,
          endYear,
        });

        if (cancelled) {
          return;
        }

        setFallbackTrends((prev) => ({
          ...prev,
          [selectedCountryCode]: safeArray(response?.time_series),
        }));
      } catch {
        if (cancelled) {
          return;
        }

        setFallbackTrends((prev) => ({
          ...prev,
          [selectedCountryCode]: [],
        }));
      }
    };

    loadTrendFallback();

    return () => {
      cancelled = true;
    };
  }, [selectedCountryCode, startYear, endYear, hasEmbeddedTrend, hasFallbackTrend, hasFallbackCache]);

  const trendSeries =
    selectedEmbeddedTrend.length
      ? selectedEmbeddedTrend
      : selectedFallbackTrend.length
        ? selectedFallbackTrend
        : safeArray(overview?.germany_trend);

  const selectedProducer = topProducers.find((producer) => producer.country_code === selectedCountryCode) || null;
  const selectedCountryLabel = selectedProducer?.country_name || selectedCountryCode || "Selected country";

  const handleTopProducerSelect = (datum) => {
    const nextCode = datum?.country_code || datum?.payload?.country_code || null;
    if (!nextCode) {
      return;
    }
    setSelectedCountryCode(nextCode);
  };

  const topProducerText = overview?.kpis?.top_producer
    ? `${overview.kpis.top_producer.country_name || overview.kpis.top_producer.country_code} (${compactFmt.format(
        asNumber(overview.kpis.top_producer.value)
      )})`
    : "-";

  const gepChange = asNumber(overview?.kpis?.gep_change_pct);
  const changeText = `${gepChange.toFixed(1)}% vs previous year`;

  return (
    <div className="tab-content overview-page">
      <div className="page-header">
        <p className="page-kicker">Realtime Briefing</p>
        <h2>Overview</h2>
      </div>

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

      <div className="chart-grid chart-grid--stack">
        <Panel
          title="Top Producers"
          eyebrow="Ranked Output"
          subtitle={`Latest year: ${overview?.latest_year ?? "-"} | click a bar to switch signal`}
        >
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart
                data={topProducerChartData}
                layout="vertical"
                margin={{ top: 10, right: 16, left: 4, bottom: 10 }}
                barCategoryGap="24%"
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 49, 49, 0.18)" />
                <XAxis type="number" tickFormatter={formatAxis} tick={{ fill: "var(--text)", fontSize: 12 }} tickMargin={8} />
                <YAxis
                  type="category"
                  dataKey="country_short_label"
                  width={74}
                  interval={0}
                  tickMargin={10}
                  tick={{ fontSize: 13, fill: "var(--text-muted)" }}
                />
                <Tooltip
                  labelFormatter={(_, payload) => payload?.[0]?.payload?.country_label || "Country"}
                  formatter={(value) => numberFmt.format(asNumber(value))}
                />
                <Bar
                  dataKey="value"
                  fill="var(--accent)"
                  radius={[0, 6, 6, 0]}
                  barSize={22}
                  cursor="pointer"
                  onClick={handleTopProducerSelect}
                >
                  {topProducers.map((producer, index) => (
                    <Cell
                      key={`${producer.country_code || producer.country_name || "producer"}-${index}`}
                      fill={
                        producer.country_code === selectedCountryCode
                          ? "var(--accent)"
                          : "rgba(255, 49, 49, 0.62)"
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel
          title={`${selectedCountryLabel} Trendline`}
          eyebrow="Historical Signal"
          subtitle="Historical GEP trajectory (click a producer above to switch)"
        >
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={320}>
                <AreaChart data={trendSeries} margin={{ top: 16, right: 16, left: 8, bottom: 16 }}>
                <defs>
                  <linearGradient id="overviewArea" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--accent-strong)" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="var(--accent-strong)" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 49, 49, 0.18)" />
                  <XAxis dataKey="year" tick={{ fill: "var(--text)", fontSize: 12 }} tickMargin={10} minTickGap={22} />
                  <YAxis
                    width={72}
                    tickMargin={10}
                    tick={{ fill: "var(--text)", fontSize: 12 }}
                    tickFormatter={(value) => compactFmt.format(asNumber(value))}
                  />
                <Tooltip formatter={(value) => numberFmt.format(asNumber(value))} />
                <Area type="monotone" dataKey="value" stroke="var(--accent-strong)" fill="url(#overviewArea)" strokeWidth={2.4} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <Panel title="Producer Pulse" eyebrow="Quick Jump" subtitle="Jump directly into Explorer">
        <div className="producer-rail">
          {topProducers.slice(0, 8).map((producer, index) => (
            <button
              key={`${producer.country_code || producer.country_name}-${index}`}
              className="producer-card"
              type="button"
              onClick={() => onProducerClick(producer)}
            >
              <p>{producer.country_name || producer.country_code}</p>
              <strong>{compactFmt.format(asNumber(producer.value))}</strong>
            </button>
          ))}
        </div>
      </Panel>

      {loading.overview ? <p className="status-banner">Updating overview...</p> : null}
    </div>
  );
}

export default OverviewPage;
