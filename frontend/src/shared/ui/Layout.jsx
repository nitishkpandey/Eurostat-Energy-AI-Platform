import { useState } from "react";
import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Overview", short: "OV" },
  { to: "/explorer", label: "Explorer", short: "EX" },
  { to: "/forecast", label: "Forecast", short: "FC" },
  { to: "/ai-agent", label: "AI Agent", short: "AI" },
];

export function Layout({
  children,
  apiHealth,
  healthLabel,
}) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarCollapsed((prev) => !prev);
  };

  return (
    <div className={isSidebarCollapsed ? "layout-shell sidebar-collapsed" : "layout-shell"}>
      <aside className="sidebar">
        <div className="sidebar-brand">
          <p className="sidebar-eyebrow">Energy Command Center</p>
          <p className="sidebar-title">{isSidebarCollapsed ? "Eurostat" : "Eurostat Energy"}</p>
          <p className="sidebar-subtitle">AI Platform</p>
        </div>

        <button
          type="button"
          className="sidebar-collapse-sign"
          onClick={toggleSidebar}
          aria-label={isSidebarCollapsed ? "Expand navigation" : "Collapse navigation"}
          title={isSidebarCollapsed ? "Expand navigation" : "Collapse navigation"}
        >
          <span aria-hidden="true">{isSidebarCollapsed ? "›" : "‹"}</span>
        </button>

        <nav className="sidebar-nav" aria-label="Primary navigation">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? "sidebar-link sidebar-link--active" : "sidebar-link"
              }
            >
              <span className="sidebar-link-dot" aria-hidden="true" />
              <span className="sidebar-link-label">{item.label}</span>
              <span className="sidebar-link-short">{item.short}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-meta">
          <p className="sidebar-meta-label">Platform status</p>
          <span className={`status-pill status-pill--${apiHealth}`}>{healthLabel}</span>
        </div>

      </aside>

      <div className="workspace">
        <section className="workspace-brand" aria-label="Platform banner">
          <p className="workspace-brand-eyebrow">European Energy Intelligence</p>
          <h1 className="workspace-brand-title">Eurostat Energy AI Platform</h1>
          <p className="workspace-brand-subtitle">
            Explore production, consumption, and forecasting signals from a single command center.
          </p>
        </section>

        <main className="workspace-main">{children}</main>
      </div>
    </div>
  );
}

export default Layout;
