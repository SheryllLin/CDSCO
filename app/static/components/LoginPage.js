export function LoginPage() {
  return `
    <div class="login-shell">
      <section class="login-card">
        <div class="login-info">
          <span class="eyebrow">CDSCO Application Portal</span>
          <h1>Unified workflow access for regulated submissions.</h1>
          <p class="muted">
            Sign in to review available application tracks, complete the common applicant stage, and continue with the
            workflow-specific submission details.
          </p>
          <ul class="login-features">
            <li>Secure entry screen with basic validation</li>
            <li>Dashboard access to six application workflows</li>
            <li>Reusable stage-one registration and dynamic stage-two forms</li>
          </ul>
        </div>
        <div class="login-form-panel">
          <span class="section-kicker">Sign In</span>
          <h2>Login to continue</h2>
          <p class="muted">Use your email ID and password to access the dashboard.</p>
          <form id="login-form" class="field-grid" novalidate>
            <div class="field">
              <label for="email">Email</label>
              <input id="email" name="email" type="email" value="review.officer@cdsco.gov.in" placeholder="officer@example.gov.in" autocomplete="username" />
            </div>
            <div class="field">
              <label for="password">Password</label>
              <input id="password" name="password" type="password" value="cdsco123" placeholder="Enter your password" autocomplete="current-password" />
            </div>
            <div id="login-error" class="error-banner hidden" aria-live="polite"></div>
            <button class="button button-primary" type="submit">Login</button>
          </form>
        </div>
      </section>
    </div>
  `;
}
