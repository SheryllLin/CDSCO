import { CommonStageOneForm } from "./CommonStageOneForm.js";
import { BabeClinicalStageTwo } from "./stage2/BabeClinicalStageTwo.js";
import { CdtlStageTwo } from "./stage2/CdtlStageTwo.js";
import { CosmeticsStageTwo } from "./stage2/CosmeticsStageTwo.js";
import { DualUseNocStageTwo } from "./stage2/DualUseNocStageTwo.js";
import { FormulationStageTwo } from "./stage2/FormulationStageTwo.js";
import { TestLicenseStageTwo } from "./stage2/TestLicenseStageTwo.js";

const stageTwoComponentMap = {
  formulation: FormulationStageTwo,
  dual_noc: DualUseNocStageTwo,
  babe_clinical: BabeClinicalStageTwo,
  cosmetics: CosmeticsStageTwo,
  test_license: TestLicenseStageTwo,
  cdtl: CdtlStageTwo
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function formatSubmission(state) {
  return escapeHtml(
    JSON.stringify(
      {
        stage_one: state.stageOne,
        stage_two: state.stageTwo,
        submitted_at: state.submittedAt
      },
      null,
      2
    )
  );
}

function renderStageTwo(workflow, state) {
  const component = stageTwoComponentMap[workflow.key];
  if (!component) {
    return "";
  }
  return component(workflow, state.stageTwo, state.errors);
}

function renderErrorBanner(errors) {
  if (!Object.keys(errors).length) {
    return "";
  }
  return `<div class="error-banner">Please review the highlighted fields before continuing.</div>`;
}

function renderList(items) {
  if (!items?.length) {
    return "<p class=\"muted\">No analysis items available yet.</p>";
  }

  return `
    <ul class="analysis-list">
      ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
    </ul>
  `;
}

function renderAnalysisPanel(state) {
  const analysis = state.analysis;
  if (!analysis?.report?.report) {
    return "";
  }

  const report = analysis.report.report;
  return `
    <section class="summary-card analysis-card">
      <span class="section-kicker">Submission analysis</span>
      <h3>${escapeHtml(report.title)}</h3>
      <div class="analysis-metrics">
        <div class="analysis-metric">
          <span>Risk level</span>
          <strong>${escapeHtml(report.risk_level.toUpperCase())}</strong>
        </div>
        <div class="analysis-metric">
          <span>Completeness</span>
          <strong>${escapeHtml(String(analysis.validation.completeness_score))}/100</strong>
        </div>
        <div class="analysis-metric">
          <span>Severity signal</span>
          <strong>${escapeHtml(analysis.classification.predicted_label)}</strong>
        </div>
      </div>
      <div class="analysis-block">
        <h4>Summary</h4>
        ${renderList(report.summary)}
      </div>
      <div class="analysis-block">
        <h4>Reviewer attention points</h4>
        ${renderList(report.violations)}
      </div>
      <div class="analysis-block">
        <h4>Recommendations</h4>
        ${renderList(report.recommendations)}
      </div>
      <div class="button-row">
        <button id="download-report-button" class="button button-primary" type="button">Download report</button>
      </div>
    </section>
  `;
}

function renderAnalysisPlaceholder(state) {
  if (state.submitted || state.step !== 2) {
    return "";
  }

  return `
    <section class="summary-card analysis-card analysis-placeholder">
      <span class="section-kicker">Report analysis</span>
      <h3>Submit Stage 2 to generate the PDF report</h3>
      <p class="muted">Once submitted, this panel will show the analysis summary and a download button for the formatted PDF report.</p>
    </section>
  `;
}

export function WorkflowWizard(workflow, state) {
  return `
    <div class="page-shell">
      <header class="panel">
        <div class="topbar">
          <div class="brand-block">
            <span class="eyebrow">${workflow.title}</span>
            <h2>${workflow.title} workflow</h2>
            <p class="muted">${workflow.description}</p>
          </div>
          <div class="topbar-actions">
            <button id="reset-demo-button" class="button button-ghost" type="button">Reload Demo Case</button>
            <button id="dashboard-button" class="button button-secondary" type="button">Back to dashboard</button>
            <button id="logout-button" class="button button-ghost" type="button">Logout</button>
          </div>
        </div>
      </header>

      <div class="workflow-layout">
        <section class="panel">
          <div class="stage-header">
            <div>
              <span class="section-kicker">Two-stage application</span>
              <h3>${state.step === 1 ? "Stage 1: Common applicant form" : "Stage 2: Workflow-specific details"}</h3>
            </div>
            <div class="stage-indicator">
              <span class="stage-pill ${state.step === 1 ? "active" : ""}">Stage 1</span>
              <span class="stage-pill ${state.step === 2 ? "active" : ""}">Stage 2</span>
            </div>
          </div>

          ${renderErrorBanner(state.errors)}

          <form id="workflow-form" novalidate>
            ${state.step === 1 ? CommonStageOneForm(state.stageOne, state.errors) : `<div id="stage-two-fields">${renderStageTwo(workflow, state)}</div>`}
            <div class="button-row">
              ${state.step === 2 ? '<button id="stage-back-button" class="button button-secondary" type="button">Back to Stage 1</button>' : ""}
              <button class="button button-primary" type="submit" ${state.submitting ? "disabled" : ""}>${state.step === 1 ? "Continue to Stage 2" : state.submitting ? "Building report..." : "Final Submit"}</button>
            </div>
          </form>
        </section>

        <aside>
          ${state.submissionError && !state.submitted ? `<section class="summary-card"><p class="error-text">${escapeHtml(state.submissionError)}</p></section>` : ""}

          ${
            state.submitted
              ? `
                <section class="success-panel">
                  <span class="section-kicker">Submission status</span>
                  <h3>Application submitted</h3>
                  <p class="muted">The ${workflow.title} form has been submitted and reviewed through the mock workflow.</p>
                  ${state.submissionError ? `<p class="error-text">${escapeHtml(state.submissionError)}</p>` : ""}
                </section>
              `
              : ""
          }

          ${renderAnalysisPlaceholder(state)}
          ${renderAnalysisPanel(state)}
        </aside>
      </div>
    </div>
  `;
}
