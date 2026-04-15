export function Dashboard(routes) {
  const cards = routes
    .map(
      (route, index) => `
        <article class="dashboard-card">
          <span class="section-kicker">Workflow 0${index + 1}</span>
          <h3>${route.title}</h3>
          <p>${route.description}</p>
          <button class="card-button" type="button" data-route="${route.path}">Open workflow</button>
        </article>
      `
    )
    .join("");

  return `
    <div class="page-shell">
      <header class="hero">
        <div class="hero-copy">
          <div class="topbar">
            <div class="brand-block">
              <span class="eyebrow">Post-login dashboard</span>
              <h1>Choose the application workflow to begin.</h1>
            </div>
            <div class="topbar-actions">
              <button id="reset-all-button" class="button button-ghost" type="button">Reload Demo Cases</button>
              <button id="logout-button" class="button button-secondary" type="button">Logout</button>
            </div>
          </div>
          <p class="muted">
            Each workflow opens the same applicant registration stage first, followed by a dedicated second stage for the
            application-specific details.
          </p>
        </div>
        <aside class="hero-panel">
          <div class="hero-stat">
            <span class="section-kicker">Application Count</span>
            <strong>6 available submission paths</strong>
          </div>
          <div class="hero-stat">
            <span class="section-kicker">Reusable Intake</span>
            <strong>Common applicant stage shared across all workflows</strong>
          </div>
          <div class="hero-stat">
            <span class="section-kicker">Submission Flow</span>
            <strong>Dashboard to Stage 1 to Stage 2 with state retention</strong>
          </div>
        </aside>
      </header>

      <section class="panel">
        <div class="section-heading">
          <span class="section-kicker">Available workflows</span>
          <h2>Application modules</h2>
          <p>Select one of the options below to continue the filing process. Each workflow already contains one pre-filled MVP demo case.</p>
        </div>
        <div class="dashboard-grid">
          ${cards}
        </div>
      </section>
    </div>
  `;
}
