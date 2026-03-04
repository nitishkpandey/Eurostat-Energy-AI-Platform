import React, { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useQuery } from "@tanstack/react-query";
import Sidebar from "./components/Sidebar";
import Overview from "./pages/Overview";
import DataExplorer from "./pages/DataExplorer";
import Forecasting from "./pages/Forecasting";
import AIInsights from "./pages/AIInsights";
import { fetchData } from "./api/client";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 5 * 60 * 1000 } },
});

function AppInner() {
  const [activePage, setActivePage] = useState("overview");

  const { data: allData } = useQuery({
    queryKey: ["data"],
    queryFn: () => fetchData(),
    staleTime: 10 * 60 * 1000,
  });

  const dataInfo = allData
    ? {
        total: allData.total,
        countries: allData.countries.length,
        indicators: allData.indicators.length,
        yearSpan: `${allData.min_year} – ${allData.max_year}`,
      }
    : undefined;

  const pageMap: Record<string, React.ReactElement> = {
    overview: <Overview />,
    explorer: <DataExplorer />,
    forecast: <Forecasting />,
    insights: <AIInsights />,
  };

  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      <Sidebar active={activePage} onChange={setActivePage} dataInfo={dataInfo} />

      <main className="flex-1 overflow-y-auto p-6">
        {/* Page header */}
        <header className="mb-6 pb-4 border-b border-border">
          <h1 className="text-2xl font-extrabold gradient-text">
            ⚡ Eurostat Energy AI Platform
          </h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Advanced Analytics · ML Forecasting · AI-Powered Insights
          </p>
        </header>

        {pageMap[activePage] ?? <Overview />}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppInner />
    </QueryClientProvider>
  );
}
