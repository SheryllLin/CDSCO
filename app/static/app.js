const samplePayload = {
  documentType: "sae_case",
  checklistType: "sae_report",
  portal: "SUGAM",
  pseudonymize: false,
  mainText:
    "Patient Mr. Rajesh Kumar, male, 58 years old, was admitted to ICU after a fatal adverse reaction to DrugX. Case ID: SAE-001. Reporter: Dr. Meena Shah. Follow-up causality assessment is pending at Sunrise Hospital.",
  comparisonText:
    "Patient was admitted after an adverse reaction to DrugX. Case ID: SAE-001. Follow-up review was in progress.",
  duplicateText:
    "DOC-1::Patient admitted to ICU after a fatal adverse reaction to DrugX.\n\nDOC-2::Patient admitted to ICU after a fatal adverse reaction to DrugX.\n\nDOC-3::Patient recovered after a mild rash and outpatient observation.",
  formData: {
    case_id: "SAE-001",
    patient_age: "58",
    gender: "male",
    reporter_name: "Dr. Meena Shah",
    suspect_product: "DrugX"
  }
};

const ui = {
  documentType: document.getElementById("document-type"),
  checklistType: document.getElementById("checklist-type"),
  portal: document.getElementById("portal"),
  pseudonymize: document.getElementById("pseudonymize"),
  mainText: document.getElementById("main-text"),
  comparisonText: document.getElementById("comparison-text"),
  duplicateText: document.getElementById("duplicate-text"),
  formData: document.getElementById("form-data"),
  runAnalysis: document.getElementById("run-analysis"),
  downloadReport: document.getElementById("download-report"),
  statusBanner: document.getElementById("status-banner"),
  reportTitle: document.getElementById("report-title"),
  reportPortal: document.getElementById("report-portal"),
  reportDocument: document.getElementById("report-document"),
  reportView: document.getElementById("report-view"),
  anonymizedView: document.getElementById("anonymized-view"),
  digestView: document.getElementById("digest-view"),
  validationView: document.getElementById("validation-view"),
  classificationView: document.getElementById("classification-view"),
  comparisonView: document.getElementById("comparison-view"),
  riskPill: document.getElementById("risk-pill"),
  supportNote: document.getElementById("support-note"),
  completenessStat: document.getElementById("completeness-stat"),
  severityStat: document.getElementById("severity-stat"),
  duplicatesStat: document.getElementById("duplicates-stat"),
  changesStat: document.getElementById("changes-stat"),
  completenessMeterLabel: document.getElementById("completeness-meter-label"),
  completenessMeterFill: document.getElementById("completeness-meter-fill"),
  loadSample: document.getElementById("load-sample")
};

const severityIds = ["death", "disability", "hospitalization", "other"];
let latestReportText = "";
let latestAnalysis = null;

function setStatus(message, isError = false) {
  ui.statusBanner.textContent = message;
  ui.statusBanner.classList.remove("hidden", "error");
  if (isError) {
    ui.statusBanner.classList.add("error");
  }
}

function clearStatus() {
  ui.statusBanner.classList.add("hidden");
  ui.statusBanner.classList.remove("error");
}

function loadSample() {
  ui.documentType.value = samplePayload.documentType;
  ui.checklistType.value = samplePayload.checklistType;
  ui.portal.value = samplePayload.portal;
  ui.pseudonymize.checked = samplePayload.pseudonymize;
  ui.mainText.value = samplePayload.mainText;
  ui.comparisonText.value = samplePayload.comparisonText;
  ui.duplicateText.value = samplePayload.duplicateText;
  ui.formData.value = JSON.stringify(samplePayload.formData, null, 2);
  setStatus("Sample case loaded. Click the main analysis button to generate the dashboard and report.");
}

function parseFormData() {
  const raw = ui.formData.value.trim();
  if (!raw) {
    return {};
  }
  return JSON.parse(raw);
}

function parseDuplicateDocuments() {
  const raw = ui.duplicateText.value.trim();
  if (!raw) {
    return [];
  }
  return raw
    .split(/\n\s*\n/)
    .map((block, index) => {
      const [first, ...rest] = block.split("::");
      if (rest.length === 0) {
        return { document_id: `DOC-${index + 1}`, text: block.trim() };
      }
      return { document_id: first.trim(), text: rest.join("::").trim() };
    })
    .filter((item) => item.text);
}

function buildPipelinePayload() {
  return {
    text: ui.mainText.value.trim(),
    form_data: parseFormData(),
    comparison_text: ui.comparisonText.value.trim() || null,
    documents: parseDuplicateDocuments(),
    pseudonymize: ui.pseudonymize.checked,
    document_type: ui.documentType.value,
    checklist_type: ui.checklistType.value,
    metadata: {
      portal: ui.portal.value,
      submission_id: `${ui.portal.value.replace(/\s+/g, "-").toUpperCase()}-AUTO-001`
    }
  };
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok) {
    const detail = data.detail || "Request failed";
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function titleCase(value) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function renderList(element, items, emptyText) {
  if (!items || items.length === 0) {
    element.innerHTML = `<li>${escapeHtml(emptyText)}</li>`;
    return;
  }
  element.innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function formatValidation(validation) {
  const missing = validation.missing_fields?.length
    ? validation.missing_fields.map((item) => titleCase(item)).join(", ")
    : "None";
  const invalid = Object.keys(validation.invalid_fields || {}).length
    ? Object.entries(validation.invalid_fields)
        .map(([field, issue]) => `${titleCase(field)}: ${issue}`)
        .join("<br />")
    : "None";
  const flags = validation.consistency_flags?.length
    ? validation.consistency_flags.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
    : "<li>No consistency flags detected.</li>";

  ui.validationView.innerHTML = `
    <p><strong>Checklist:</strong> ${escapeHtml(titleCase(validation.checklist_type))}</p>
    <p><strong>Missing fields:</strong> ${escapeHtml(missing)}</p>
    <p><strong>Invalid fields:</strong><br />${invalid}</p>
    <p><strong>Consistency review:</strong></p>
    <ul class="compact-list">${flags}</ul>
  `;
}

function formatClassification(classification) {
  const scores = classification.scores
    .map(
      (item) =>
        `<li><strong>${escapeHtml(item.label)}</strong> support score: ${escapeHtml((item.score * 100).toFixed(1))}%</li>`
    )
    .join("");

  ui.classificationView.innerHTML = `
    <p><strong>Suggested severity signal:</strong> ${escapeHtml(classification.predicted_label)}</p>
    <p><strong>Support scores:</strong></p>
    <ul class="compact-list">${scores}</ul>
  `;
}

function formatComparison(data) {
  const duplicates = data.deduplication?.duplicates?.length
    ? data.deduplication.duplicates
        .map(
          (item) =>
            `<li>${escapeHtml(item.document_id_a)} and ${escapeHtml(item.document_id_b)} may be related (${escapeHtml(item.duplicate_type)}, similarity ${escapeHtml(item.similarity)})</li>`
        )
        .join("")
    : "<li>No potential duplicates detected.</li>";

  const changeBlock = data.comparison
    ? `
      <p><strong>Version differences:</strong></p>
      <ul class="compact-list">
        <li>Added segments: ${escapeHtml(data.comparison.change_summary.added_count)}</li>
        <li>Removed segments: ${escapeHtml(data.comparison.change_summary.removed_count)}</li>
        <li>Modified segments: ${escapeHtml(data.comparison.change_summary.modified_count)}</li>
      </ul>
    `
    : "<p><strong>Version differences:</strong> No comparison text submitted.</p>";

  ui.comparisonView.innerHTML = `
    <p><strong>Potential duplicates:</strong></p>
    <ul class="compact-list">${duplicates}</ul>
    ${changeBlock}
  `;
}

function createSection(title, items) {
  const listItems = items.length
    ? items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
    : "<li>No items available.</li>";
  return `
    <section class="report-section">
      <h4>${escapeHtml(title)}</h4>
      <ul>${listItems}</ul>
    </section>
  `;
}

function buildReportMarkup(report, data) {
  const completeness = data.validation?.completeness_score ?? 0;
  const duplicates = data.deduplication?.duplicates?.length ?? 0;
  const changes = data.comparison
    ? data.comparison.change_summary.added_count +
      data.comparison.change_summary.removed_count +
      data.comparison.change_summary.modified_count
    : 0;

  return `
    <div class="report-highlight">
      <div class="highlight-box">
        <span class="stat-label">Completeness</span>
        <strong>${escapeHtml(completeness)}/100</strong>
      </div>
      <div class="highlight-box">
        <span class="stat-label">Potential Duplicates</span>
        <strong>${escapeHtml(duplicates)}</strong>
      </div>
      <div class="highlight-box">
        <span class="stat-label">Version Change Count</span>
        <strong>${escapeHtml(changes)}</strong>
      </div>
    </div>
    ${createSection("Summary", report.summary)}
    ${createSection("Observations", report.observations)}
    ${createSection("Reviewer Attention Points", report.violations)}
    ${createSection("Recommendations", report.recommendations)}
    ${createSection("Next Actions", report.next_actions)}
  `;
}

function formatReportText(report, data) {
  const completeness = data.validation?.completeness_score ?? 0;
  const duplicates = data.deduplication?.duplicates?.length ?? 0;
  const changes = data.comparison
    ? data.comparison.change_summary.added_count +
      data.comparison.change_summary.removed_count +
      data.comparison.change_summary.modified_count
    : 0;

  return [
    report.title,
    "",
    `Risk level: ${report.risk_level.toUpperCase()}`,
    `Completeness: ${completeness}/100`,
    `Potential duplicates: ${duplicates}`,
    `Version change count: ${changes}`,
    "",
    "Summary:",
    ...report.summary.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Observations:",
    ...report.observations.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Reviewer Attention Points:",
    ...report.violations.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Recommendations:",
    ...report.recommendations.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Next Actions:",
    ...report.next_actions.map((item, index) => `${index + 1}. ${item}`)
  ].join("\n");
}

function applyRiskPill(level) {
  ui.riskPill.className = `pill ${level || "neutral"}`;
  ui.riskPill.textContent = level ? `${level} reviewer attention` : "Awaiting run";
}

function updateDashboardStats(data) {
  const completeness = data.validation?.completeness_score ?? 0;
  const duplicates = data.deduplication?.duplicates?.length ?? 0;
  const changes = data.comparison
    ? data.comparison.change_summary.added_count +
      data.comparison.change_summary.removed_count +
      data.comparison.change_summary.modified_count
    : 0;

  ui.completenessStat.textContent = `${completeness}/100`;
  ui.severityStat.textContent = data.classification?.predicted_label || "--";
  ui.duplicatesStat.textContent = String(duplicates);
  ui.changesStat.textContent = String(changes);
  ui.completenessMeterLabel.textContent = `${completeness}%`;
  ui.completenessMeterFill.style.width = `${Math.max(0, Math.min(completeness, 100))}%`;
}

function updateSeverityBars(classification) {
  const map = {};
  for (const score of classification.scores || []) {
    map[score.label.toLowerCase()] = Math.round(score.score * 100);
  }
  for (const key of severityIds) {
    const value = map[key] || 0;
    const bar = document.getElementById(`bar-${key}`);
    const label = document.getElementById(`label-${key}`);
    if (bar) {
      bar.style.width = `${value}%`;
    }
    if (label) {
      label.textContent = `${value}%`;
    }
  }
}

function renderPipeline(data) {
  const report = data.report.report;
  latestAnalysis = data;
  latestReportText = formatReportText(report, data);
  ui.reportTitle.textContent = report.title;
  ui.reportPortal.textContent = `Portal: ${ui.portal.value}`;
  ui.reportDocument.textContent = `Type: ${titleCase(ui.documentType.value)}`;
  ui.reportView.innerHTML = buildReportMarkup(report, data);
  ui.anonymizedView.textContent = data.anonymization.anonymized_text || "No anonymized text returned.";
  renderList(ui.digestView, data.summary.reviewer_digest, "No reviewer digest available.");
  formatValidation(data.validation);
  formatClassification(data.classification);
  formatComparison(data);
  updateDashboardStats(data);
  updateSeverityBars(data.classification);
  applyRiskPill(report.risk_level);
  ui.supportNote.textContent =
    "This is a reviewer support dashboard. Suggested severity, duplicate, and compliance signals should assist human review, not replace it.";
  ui.downloadReport.disabled = false;
}

function downloadReport() {
  if (!latestAnalysis) {
    return;
  }
  exportReportPdf().catch((error) => setStatus(error.message, true));
}

async function exportReportPdf() {
  setStatus("Preparing styled PDF report for download.");
  const response = await fetch("/export-report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      analysis: latestAnalysis,
      portal: ui.portal.value,
      document_type: ui.documentType.value,
      generated_by: "Regulatory Workflow Automation Dashboard"
    })
  });
  if (!response.ok) {
    throw new Error("Could not generate PDF report.");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `regulatory-report-${ui.documentType.value}.pdf`;
  anchor.click();
  URL.revokeObjectURL(url);
  setStatus("PDF report downloaded successfully.");
}

async function runAnalysis() {
  try {
    clearStatus();
    setStatus("Running the full analysis and generating the formatted report.");
    const payload = buildPipelinePayload();
    if (!payload.text) {
      throw new Error("Primary narrative text is required.");
    }
    const data = await postJson("/pipeline/run", payload);
    renderPipeline(data);
    setStatus("Analysis completed. The dashboard and formatted report have been updated.");
  } catch (error) {
    setStatus(error.message, true);
  }
}

ui.runAnalysis.addEventListener("click", runAnalysis);
ui.downloadReport.addEventListener("click", downloadReport);
ui.loadSample.addEventListener("click", loadSample);

loadSample();
