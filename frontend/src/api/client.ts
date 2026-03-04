/**
 * Typed API client for the Eurostat Energy AI Platform backend.
 * All requests go to /api (proxied to FastAPI by Vite in dev, by Nginx in production).
 */
import axios from "axios";

const BASE = import.meta.env.VITE_API_URL ?? "/api";

export const apiClient = axios.create({ baseURL: BASE });

// ── Types ──────────────────────────────────────────────────────────────────

export interface ObservationRow {
  year: number;
  country_code: string;
  country_name: string;
  indicator_code: string;
  indicator_label: string;
  unit_label: string;
  value: number;
}

export interface DataResponse {
  records: ObservationRow[];
  total: number;
  min_year: number;
  max_year: number;
  countries: string[];
  indicators: string[];
}

export interface MetricsResponse {
  total_gep_latest: number;
  top_producer_name: string;
  top_producer_value: number;
  avg_gep: number;
  countries_reporting: number;
  gep_change_pct: number;
  latest_year: number;
}

export interface ForecastPoint {
  year: number;
  value: number;
  type: "historical" | "forecast";
}

export interface ForecastResponse {
  model_used: string;
  data: ForecastPoint[];
}

export interface InsightResponse {
  answer: string;
  mode: string;
}

// ── API calls ──────────────────────────────────────────────────────────────

export const fetchData = async (minYear?: number, maxYear?: number): Promise<DataResponse> => {
  const params: Record<string, number> = {};
  if (minYear !== undefined) params.min_year = minYear;
  if (maxYear !== undefined) params.max_year = maxYear;
  const { data } = await apiClient.get<DataResponse>("/data/", { params });
  return data;
};

export const fetchMetrics = async (): Promise<MetricsResponse> => {
  const { data } = await apiClient.get<MetricsResponse>("/data/metrics");
  return data;
};

export const fetchForecast = async (
  country: string,
  indicator: string,
  horizon = 5
): Promise<ForecastResponse> => {
  const { data } = await apiClient.get<ForecastResponse>("/forecast/", {
    params: { country, indicator, horizon },
  });
  return data;
};

export const askInsight = async (question: string): Promise<InsightResponse> => {
  const { data } = await apiClient.post<InsightResponse>("/insights/ask", { question });
  return data;
};
