const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const buildQueryString = (params = {}) => {
  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });

  const query = search.toString();
  return query ? `?${query}` : "";
};

const request = async (path, options = {}) => {
  const method = String(options.method ?? "GET").toUpperCase();
  const retries = method === "GET" ? 2 : 0;
  const delayMs = 400;

  let lastError;

  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      const response = await fetch(`${API_BASE}${path}`, {
        headers: {
          "Content-Type": "application/json",
          ...(options.headers ?? {}),
        },
        ...options,
      });

      if (!response.ok) {
        let message = "Request failed";
        try {
          const payload = await response.json();
          message = payload.detail ?? message;
        } catch {
          message = `${message} (${response.status})`;
        }
        throw new Error(message);
      }

      return response.json();
    } catch (error) {
      lastError = error;
      if (attempt < retries && (error instanceof TypeError || error?.message === "Failed to fetch")) {
        await sleep(delayMs * (attempt + 1));
        continue;
      }
      throw error;
    }
  }

  throw lastError;
};

export const apiClient = {
  health: () => request("/api/health"),

  metadata: () => request("/api/metadata"),

  overview: ({ startYear, endYear }) =>
    request(`/api/overview${buildQueryString({ start_year: startYear, end_year: endYear })}`),

  explorer: ({ countryCode, indicatorCode, startYear, endYear }) =>
    request(
      `/api/explorer${buildQueryString({
        country_code: countryCode,
        indicator_code: indicatorCode,
        start_year: startYear,
        end_year: endYear,
      })}`
    ),

  forecast: ({ countryCode, indicatorCode, horizon }) =>
    request("/api/forecast", {
      method: "POST",
      body: JSON.stringify({
        country_code: countryCode,
        indicator_code: indicatorCode,
        horizon,
      }),
    }),

  askAi: (question, history = []) =>
    request("/api/ai/ask", {
      method: "POST",
      body: JSON.stringify({ question, history }),
    }),

  refreshCache: () =>
    request("/api/cache/refresh", {
      method: "POST",
    }),
};
