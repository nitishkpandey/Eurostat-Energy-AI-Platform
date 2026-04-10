export function GlobalFilters({
  minYear,
  maxYear,
  startYear,
  endYear,
  countryCode,
  indicatorCode,
  countries,
  indicators,
  onStartYearChange,
  onEndYearChange,
  onCountryChange,
  onIndicatorChange,
  onApplyYears,
  onSync,
}) {
  const effectiveStartYear = startYear || minYear;
  const effectiveEndYear = endYear || maxYear;
  const selectedCountry = countries.find((country) => country.country_code === countryCode) || null;
  const countryLabel = selectedCountry?.country_name || countryCode || "Country";

  const isPresetActive = (years) => {
    if (years === null) {
      return effectiveStartYear === minYear && effectiveEndYear === maxYear;
    }

    const expectedStart = Math.max(minYear, maxYear - years + 1);
    return effectiveStartYear === expectedStart && effectiveEndYear === maxYear;
  };

  return (
    <section className="global-filters scope-dock" aria-label="Data scope controls">
      <div className="scope-dock-head">
        <div className="scope-dock-title-wrap">
          <p className="scope-dock-kicker">Data Scope</p>
          <h3>Control Dock</h3>
        </div>

        <div className="scope-dock-pills" aria-label="Current scope summary">
          <span className="scope-pill">{effectiveStartYear} - {effectiveEndYear}</span>
          <span className="scope-pill">{countryLabel}</span>
          <span className="scope-pill">{indicatorCode || "Indicator"}</span>
        </div>

        <button type="button" className="sync-button sync-button--dock" onClick={onSync}>
          Sync Data
          <span>Refresh backend cache</span>
        </button>
      </div>

      <div className="global-filters-grid scope-dock-grid">
        <label className="filter-field">
          <span className="filter-label">From year</span>
          <input
            type="number"
            min={minYear}
            max={endYear || maxYear}
            value={effectiveStartYear}
            onChange={(event) => onStartYearChange(event.target.value)}
          />
        </label>

        <label className="filter-field">
          <span className="filter-label">To year</span>
          <input
            type="number"
            min={startYear || minYear}
            max={maxYear}
            value={effectiveEndYear}
            onChange={(event) => onEndYearChange(event.target.value)}
          />
        </label>

        <label className="filter-field">
          <span className="filter-label">Country</span>
          <select value={countryCode} onChange={(event) => onCountryChange(event.target.value)}>
            {countries.map((country) => (
              <option key={country.country_code} value={country.country_code}>
                {country.country_name || country.country_code}
              </option>
            ))}
          </select>
        </label>

        <label className="filter-field">
          <span className="filter-label">Indicator</span>
          <select value={indicatorCode} onChange={(event) => onIndicatorChange(event.target.value)}>
            {indicators.map((indicator) => (
              <option key={indicator} value={indicator}>
                {indicator}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="year-presets year-presets--dock">
        <button
          type="button"
          className={isPresetActive(null) ? "outline-button is-active" : "outline-button"}
          onClick={() => onApplyYears(null)}
        >
          Full Span
        </button>
        <button
          type="button"
          className={isPresetActive(10) ? "outline-button is-active" : "outline-button"}
          onClick={() => onApplyYears(10)}
        >
          Last 10 Years
        </button>
        <button
          type="button"
          className={isPresetActive(5) ? "outline-button is-active" : "outline-button"}
          onClick={() => onApplyYears(5)}
        >
          Last 5 Years
        </button>
      </div>
    </section>
  );
}

export default GlobalFilters;
