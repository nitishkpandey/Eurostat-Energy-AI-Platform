export default function Panel({ title, subtitle, actions, className = "", children }) {
  const rootClassName = ["panel", className].filter(Boolean).join(" ");

  return (
    <section className={rootClassName}>
      <header className="panel-header">
        <div>
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
        {actions ? <div className="panel-actions">{actions}</div> : null}
      </header>
      <div className="panel-body">{children}</div>
    </section>
  );
}
