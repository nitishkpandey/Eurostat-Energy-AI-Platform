import { useEffect, useMemo, useState } from "react";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";

import { GlobalFilters } from "../features/filters/GlobalFilters";
import { AiAgentPage } from "../features/ai-agent/AiAgentPage";
import { ExplorerPage } from "../features/explorer/ExplorerPage";
import { ForecastPage } from "../features/forecast/ForecastPage";
import { OverviewPage } from "../features/overview/OverviewPage";
import { apiClient } from "../shared/api/client";
import { Layout } from "../shared/ui/Layout";
import { asNumber, safeArray } from "../shared/utils/data";

const HEALTH_LABELS = {
  checking: "Checking API",
  healthy: "API Healthy",
  degraded: "API Degraded",
};

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const [metadata, setMetadata] = useState(null);
  const [overview, setOverview] = useState(null);
  const [explorer, setExplorer] = useState(null);

  const [countryCode, setCountryCode] = useState("");
  const [indicatorCode, setIndicatorCode] = useState("");

  const [startYear, setStartYear] = useState(0);
  const [endYear, setEndYear] = useState(0);
  const [reloadToken, setReloadToken] = useState(0);

  const [loading, setLoading] = useState({
    metadata: true,
    overview: false,
    explorer: false,
  });

  const [error, setError] = useState("");
  const apiHealth = loading.metadata ? "checking" : error ? "degraded" : "healthy";

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
  const visibleCountries = countries;
  const showGlobalFilters = !location.pathname.startsWith("/ai-agent") && !location.pathname.startsWith("/explorer");

  const selectedCountry = useMemo(
    () => countries.find((country) => country.country_code === countryCode) || null,
    [countries, countryCode]
  );

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

  const handleRefresh = async () => {
    setError("");
    try {
      await apiClient.refreshCache();
      setReloadToken((prev) => prev + 1);
    } catch (refreshError) {
      setError(refreshError.message);
    }
  };

  const handleProducerClick = (producer) => {
    setCountryCode(producer.country_code);
    setIndicatorCode("GEP");
    navigate("/explorer");
  };

  return (
    <>
      <Layout
        apiHealth={apiHealth}
        healthLabel={HEALTH_LABELS[apiHealth]}
      >
        {showGlobalFilters ? (
          <GlobalFilters
            minYear={metadata?.min_year ?? 0}
            maxYear={metadata?.max_year ?? 0}
            startYear={startYear}
            endYear={endYear}
            countryCode={countryCode}
            indicatorCode={indicatorCode}
            countries={visibleCountries}
            indicators={indicators}
            onStartYearChange={(value) => setStartYear(asNumber(value))}
            onEndYearChange={(value) => setEndYear(asNumber(value))}
            onCountryChange={setCountryCode}
            onIndicatorChange={setIndicatorCode}
            onApplyYears={applyYearWindow}
            onSync={handleRefresh}
          />
        ) : null}

        {error ? <p className="error-banner">{error}</p> : null}
        {loading.metadata ? <p className="status-banner">Loading metadata...</p> : null}

        <Routes>
          <Route
            path="/"
            element={
              <OverviewPage
                overview={overview}
                loading={loading}
                startYear={startYear}
                endYear={endYear}
                onProducerClick={handleProducerClick}
              />
            }
          />
          <Route
            path="/explorer"
            element={
              <ExplorerPage
                explorer={explorer}
                loading={loading}
                country={selectedCountry}
                indicator={indicatorCode}
                countries={visibleCountries}
                indicators={indicators}
                countryCode={countryCode}
                onCountryChange={setCountryCode}
                onIndicatorChange={setIndicatorCode}
              />
            }
          />
          <Route path="/forecast" element={<ForecastPage countryCode={countryCode} indicatorCode={indicatorCode} />} />
          <Route path="/ai-agent" element={<AiAgentPage />} />
        </Routes>
      </Layout>
    </>
  );
}

export default App;
