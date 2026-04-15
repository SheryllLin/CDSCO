import { routes, workflowRouteSet } from "./config/workflows.js";
import { Dashboard } from "./components/Dashboard.js";
import { LoginPage } from "./components/LoginPage.js";
import { WorkflowWizard } from "./components/WorkflowWizard.js";
import { createStore } from "./state/store.js";

const appRoot = document.getElementById("app");
const store = createStore();

const WORKFLOW_ANALYSIS_CONFIG = {
  formulation: { documentType: "application", checklistType: "formulation_rd", portal: "SUGAM" },
  dual_noc: { documentType: "application", checklistType: "dual_use_noc", portal: "SUGAM" },
  babe_clinical: { documentType: "application", checklistType: "babe_clinical", portal: "SUGAM" },
  cosmetics: { documentType: "application", checklistType: "cosmetics_registration", portal: "SUGAM" },
  test_license: { documentType: "application", checklistType: "test_license", portal: "SUGAM" },
  cdtl: { documentType: "application", checklistType: "cdtl_registration", portal: "MD Online" }
};

function renderApp() {
  const pathname = window.location.pathname;
  const isAuthenticated = store.isAuthenticated();

  if (!isAuthenticated && pathname !== "/") {
    navigate("/", { replace: true });
    return;
  }

  if (isAuthenticated && pathname === "/") {
    navigate("/dashboard", { replace: true });
    return;
  }

  if (pathname === "/") {
    appRoot.innerHTML = LoginPage();
    attachLoginPage();
    return;
  }

  if (pathname === "/dashboard") {
    appRoot.innerHTML = Dashboard(routes);
    attachDashboard();
    return;
  }

  if (workflowRouteSet.has(pathname)) {
    const workflow = routes.find((item) => item.path === pathname);
    appRoot.innerHTML = WorkflowWizard(workflow, store.getWorkflowState(workflow.key));
    attachWorkflow(workflow);
    return;
  }

  navigate(isAuthenticated ? "/dashboard" : "/", { replace: true });
}

function navigate(path, { replace = false } = {}) {
  if (window.location.pathname === path) {
    renderApp();
    return;
  }
  const action = replace ? "replaceState" : "pushState";
  window.history[action]({}, "", path);
  renderApp();
}

function attachLoginPage() {
  const form = document.getElementById("login-form");
  const errorBox = document.getElementById("login-error");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const email = String(formData.get("email") || "").trim();
    const password = String(formData.get("password") || "").trim();
    const errors = [];

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.push("Enter a valid email address.");
    }
    if (!password || password.length < 6) {
      errors.push("Password must be at least 6 characters long.");
    }

    if (errors.length) {
      errorBox.textContent = errors.join(" ");
      errorBox.classList.remove("hidden");
      return;
    }

    store.login({ email });
    navigate("/dashboard");
  });
}

function attachDashboard() {
  const logoutButton = document.getElementById("logout-button");
  const resetAllButton = document.getElementById("reset-all-button");
  const cards = Array.from(document.querySelectorAll("[data-route]"));

  logoutButton?.addEventListener("click", () => {
    store.logout();
    navigate("/", { replace: true });
  });

  resetAllButton?.addEventListener("click", () => {
    store.resetAllWorkflows();
    renderApp();
  });

  for (const card of cards) {
    card.addEventListener("click", () => {
      navigate(card.dataset.route);
    });
  }
}

function attachWorkflow(workflow) {
  const logoutButton = document.getElementById("logout-button");
  const homeButton = document.getElementById("dashboard-button");
  const backButton = document.getElementById("stage-back-button");
  const resetDemoButton = document.getElementById("reset-demo-button");
  const downloadReportButton = document.getElementById("download-report-button");
  const form = document.getElementById("workflow-form");
  const stageOneContainer = document.getElementById("stage-one-fields");
  const stageTwoContainer = document.getElementById("stage-two-fields");

  logoutButton?.addEventListener("click", () => {
    store.logout();
    navigate("/", { replace: true });
  });

  homeButton?.addEventListener("click", () => {
    navigate("/dashboard");
  });

  resetDemoButton?.addEventListener("click", () => {
    store.resetWorkflowState(workflow.key);
    renderApp();
  });

  backButton?.addEventListener("click", () => {
    store.updateWorkflowState(workflow.key, { step: 1, errors: {} });
    renderApp();
  });

  downloadReportButton?.addEventListener("click", () => {
    downloadWorkflowReport(workflow).catch(() => {
      const workflowState = store.getWorkflowState(workflow.key);
      store.updateWorkflowState(workflow.key, {
        submissionError: "The PDF report could not be downloaded right now. Please try again."
      });
      if (workflowState.submitted) {
        renderApp();
      }
    });
  });

  stageOneContainer?.addEventListener("change", handleStageOneFileChange(workflow));
  stageOneContainer?.addEventListener("input", clearErrorOnInput(workflow));
  stageTwoContainer?.addEventListener("input", clearErrorOnInput(workflow));
  stageTwoContainer?.addEventListener("change", clearErrorOnInput(workflow));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const workflowState = store.getWorkflowState(workflow.key);
    const formData = new FormData(form);

    if (workflowState.step === 1) {
      const nextStageOne = extractStageOneData(formData, workflowState.stageOne);
      const errors = validateStageOne(nextStageOne);
      store.updateWorkflowState(workflow.key, { stageOne: nextStageOne, errors });

      if (Object.keys(errors).length) {
        renderApp();
        return;
      }

      store.updateWorkflowState(workflow.key, { step: 2, errors: {} });
      renderApp();
      return;
    }

    const nextStageTwo = extractStageTwoData(formData, workflow.stageTwoFields, workflowState.stageTwo);
    const errors = validateStageTwo(nextStageTwo, workflow.stageTwoFields);
    store.updateWorkflowState(workflow.key, { stageTwo: nextStageTwo, errors });

    if (Object.keys(errors).length) {
      renderApp();
      return;
    }

    store.updateWorkflowState(workflow.key, {
      submitting: true,
      submissionError: "",
      analysis: null
    });
    renderApp();

    const submittedAt = new Date().toISOString();

    try {
      const analysis = await submitWorkflowForAnalysis(workflow, {
        ...workflowState,
        stageTwo: nextStageTwo,
        submittedAt
      });

      store.updateWorkflowState(workflow.key, {
        errors: {},
        submitted: true,
        submittedAt,
        submitting: false,
        submissionError: "",
        analysis
      });
    } catch (error) {
      store.updateWorkflowState(workflow.key, {
        submitted: false,
        submittedAt: null,
        submitting: false,
        submissionError: error instanceof Error ? error.message : "The submission analysis failed.",
        analysis: null
      });
    }

    renderApp();
  });
}

async function submitWorkflowForAnalysis(workflow, workflowState) {
  const payload = buildPipelineRequest(workflow, workflowState);
  const response = await fetch("/pipeline/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("The submission was saved, but the analysis service could not complete the report.");
  }

  return response.json();
}

async function downloadWorkflowReport(workflow) {
  const workflowState = store.getWorkflowState(workflow.key);
  if (!workflowState.analysis) {
    throw new Error("No analysis is available for download.");
  }

  const config = getWorkflowAnalysisConfig(workflow.key);
  const response = await fetch("/export-report", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      analysis: workflowState.analysis,
      portal: config.portal,
      document_type: config.documentType,
      generated_by: workflowState.stageOne.username || "CDSCO Portal User"
    })
  });

  if (!response.ok) {
    throw new Error("Unable to export the analysis report.");
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${workflow.key}_analysis_report.pdf`;
  document.body.append(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

function getWorkflowAnalysisConfig(workflowKey) {
  return WORKFLOW_ANALYSIS_CONFIG[workflowKey] || {
    documentType: "application",
    checklistType: "clinical_application",
    portal: "SUGAM"
  };
}

function buildPipelineRequest(workflow, workflowState) {
  const config = getWorkflowAnalysisConfig(workflow.key);
  const formData = normalizeFormData({
    ...workflowState.stageOne,
    ...workflowState.stageTwo
  });

  return {
    text: buildSubmissionNarrative(workflow, workflowState),
    form_data: formData,
    pseudonymize: String(formData.anonymization_required || "").toLowerCase() === "true",
    document_type: config.documentType,
    checklist_type: config.checklistType,
    source_type: "typed",
    metadata: {
      portal: config.portal,
      submission_id: formData.application_id || formData.username || workflow.key,
      workflow_type: workflow.title,
      applicant_name:
        formData.applicant_name ||
        [formData.first_name, formData.middle_name, formData.last_name].filter(Boolean).join(" ") ||
        formData.organization_name ||
        workflow.title
    }
  };
}

function normalizeFormData(values) {
  return Object.fromEntries(
    Object.entries(values)
      .filter(([, value]) => value !== null && value !== undefined)
      .map(([key, value]) => [key, typeof value === "boolean" ? String(value) : String(value)])
  );
}

function buildSubmissionNarrative(workflow, workflowState) {
  const stageOneKeys = [
    "organization_name",
    "organization_type",
    "designation",
    "city",
    "state",
    "country",
    "applicant_type"
  ];
  const stageTwoKeys = workflow.stageTwoFields.map((field) => field.name);
  const sections = [
    `${workflow.title} application submission for portal review.`,
    "Applicant profile:",
    ...stageOneKeys
      .filter((key) => workflowState.stageOne[key])
      .map((key) => `${humanizeFieldName(key)}: ${formatNarrativeValue(workflowState.stageOne[key])}`),
    "Stage 2 submission details:",
    ...stageTwoKeys
      .filter((key) => workflowState.stageTwo[key] !== null && workflowState.stageTwo[key] !== undefined && workflowState.stageTwo[key] !== "")
      .map((key) => `${humanizeFieldName(key)}: ${formatNarrativeValue(workflowState.stageTwo[key])}`),
    workflowState.submittedAt ? `Submission timestamp: ${workflowState.submittedAt}` : ""
  ];

  return sections.filter(Boolean).join("\n");
}

function humanizeFieldName(name) {
  return String(name)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNarrativeValue(value) {
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  if (value === null || value === undefined || value === "") {
    return "Not provided";
  }
  return String(value);
}

function clearErrorOnInput(workflow) {
  return (event) => {
    const workflowState = store.getWorkflowState(workflow.key);
    const fieldName = event.target.name;
    if (!fieldName || !workflowState.errors[fieldName]) {
      return;
    }
    const nextErrors = { ...workflowState.errors };
    delete nextErrors[fieldName];
    store.updateWorkflowState(workflow.key, { errors: nextErrors });
  };
}

function handleStageOneFileChange(workflow) {
  return (event) => {
    const { target } = event;
    if (target.type !== "file" || !target.name) {
      return;
    }
    const workflowState = store.getWorkflowState(workflow.key);
    const fileName = target.files?.[0]?.name || "";
    store.updateWorkflowState(workflow.key, {
      stageOne: {
        ...workflowState.stageOne,
        [target.name]: fileName
      }
    });
  };
}

function extractStageOneData(formData, previousData) {
  const data = { ...previousData };
  for (const [key, value] of formData.entries()) {
    if (key.endsWith("_upload")) {
      continue;
    }
    data[key] = typeof value === "string" ? value.trim() : value;
  }

  const checkboxNames = ["sms_alert", "terms_accepted"];
  for (const name of checkboxNames) {
    data[name] = formData.get(name) === "on";
  }
  return data;
}

function extractStageTwoData(formData, fields, previousData) {
  const data = { ...previousData };
  for (const field of fields) {
    if (field.type === "checkbox") {
      data[field.name] = formData.get(field.name) === "True" ? "True" : "False";
      continue;
    }
    const value = formData.get(field.name);
    data[field.name] = typeof value === "string" ? value.trim() : "";
  }
  return data;
}

function validateStageOne(data) {
  const errors = {};
  const requiredFields = [
    "applicant_type",
    "username",
    "password",
    "confirm_password",
    "first_name",
    "last_name",
    "mobile_number",
    "gender",
    "nationality",
    "id_proof_type",
    "id_proof_number",
    "designation",
    "organization_name",
    "organization_type",
    "address_line_1",
    "country",
    "state",
    "district",
    "city",
    "pincode",
    "contact_number",
    "captcha"
  ];

  for (const field of requiredFields) {
    if (!data[field]) {
      errors[field] = "This field is required.";
    }
  }

  if (data.username && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.username)) {
    errors.username = "Enter a valid email address.";
  }
  if (data.alternate_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.alternate_email)) {
    errors.alternate_email = "Enter a valid alternate email.";
  }
  if (data.password && data.password.length < 6) {
    errors.password = "Password must be at least 6 characters long.";
  }
  if (data.password !== data.confirm_password) {
    errors.confirm_password = "Passwords do not match.";
  }
  if (data.mobile_number && !/^\d{10,15}$/.test(data.mobile_number.replace(/\D/g, ""))) {
    errors.mobile_number = "Enter a valid mobile number.";
  }
  if (data.pincode && !/^\d{5,10}$/.test(data.pincode)) {
    errors.pincode = "Enter a valid pincode.";
  }
  if (String(data.captcha || "").trim().toUpperCase() !== "CDSCO") {
    errors.captcha = "Enter the displayed CAPTCHA text.";
  }
  if (!data.id_proof_upload) {
    errors.id_proof_upload = "Upload the ID proof file.";
  }
  if (!data.undertaking_upload) {
    errors.undertaking_upload = "Upload the undertaking PDF.";
  }
  if (!data.address_proof_upload) {
    errors.address_proof_upload = "Upload the address proof.";
  }
  if (!data.terms_accepted) {
    errors.terms_accepted = "You must accept the terms and conditions.";
  }
  return errors;
}

function validateStageTwo(data, fields) {
  const errors = {};
  for (const field of fields) {
    if (field.required !== false && !data[field.name]) {
      errors[field.name] = "This field is required.";
    }
  }
  return errors;
}

window.addEventListener("popstate", renderApp);
renderApp();
