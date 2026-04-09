export default function StatCard({ label, value, meta, tone = "neutral", trend = "" }) {
  const rootClassName = ["stat-card", `stat-card--${tone}`].join(" ");
  const metaClassName = ["stat-meta", trend ? `stat-meta--${trend}` : ""].filter(Boolean).join(" ");

  return (
    <article className={rootClassName}>
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
      {meta ? <p className={metaClassName}>{meta}</p> : null}
    </article>
  );
}
