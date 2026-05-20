import { useState, useEffect } from "react";
import { apiClient } from "../api/client";

export function useApiHealth() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    let mounted = true;

    const checkHealth = async () => {
      try {
        await apiClient.health();
        if (mounted) setStatus("healthy");
      } catch {
        if (mounted) setStatus("degraded");
      }
    };

    checkHealth();

    return () => {
      mounted = false;
    };
  }, []);

  return status;
}

export function useMetadata(reloadToken) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    const loadMetadata = async () => {
      setLoading(true);
      setError("");

      try {
        const response = await apiClient.metadata();
        if (!mounted) return;
        setData(response);
      } catch (fetchError) {
        if (mounted) setError(fetchError.message);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    loadMetadata();

    return () => {
      mounted = false;
    };
  }, [reloadToken]);

  return { data, loading, error };
}

export function useOverview(startYear, endYear, reloadToken) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!startYear || !endYear) return;

    let mounted = true;

    const loadOverview = async () => {
      setLoading(true);
      setError("");

      try {
        const response = await apiClient.overview({ startYear, endYear });
        if (mounted) setData(response);
      } catch (fetchError) {
        if (mounted) setError(fetchError.message);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    loadOverview();

    return () => {
      mounted = false;
    };
  }, [startYear, endYear, reloadToken]);

  return { data, loading, error };
}

export function useExplorer(countryCode, indicatorCode, startYear, endYear, reloadToken) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!countryCode || !indicatorCode || !startYear || !endYear) return;

    let mounted = true;

    const loadExplorer = async () => {
      setLoading(true);
      setError("");

      try {
        const response = await apiClient.explorer({
          countryCode,
          indicatorCode,
          startYear,
          endYear,
        });
        if (mounted) setData(response);
      } catch (fetchError) {
        if (mounted) setError(fetchError.message);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    loadExplorer();

    return () => {
      mounted = false;
    };
  }, [countryCode, indicatorCode, startYear, endYear, reloadToken]);

  return { data, loading, error };
}
