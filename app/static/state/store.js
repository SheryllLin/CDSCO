import { routeMap, routes } from "../config/workflows.js";

const SESSION_KEY = "cdsco_portal_session";
const WORKFLOW_KEY = "cdsco_portal_workflows";

const defaultStageOne = {
  applicant_type: "Organization",
  username: "review.officer@cdsco.gov.in",
  password: "cdsco123",
  confirm_password: "cdsco123",
  first_name: "Aarav",
  middle_name: "K",
  last_name: "Sharma",
  mobile_number: "9876543210",
  gender: "Male",
  nationality: "Indian",
  id_proof_type: "Aadhaar",
  id_proof_number: "456712341234",
  id_proof_upload: "aadhaar_demo.pdf",
  undertaking_upload: "undertaking_demo.pdf",
  designation: "Regulatory Affairs Manager",
  alternate_email: "backup.regulatory@cdsco.gov.in",
  organization_name: "Zenova Life Sciences Pvt Ltd",
  organization_type: "Company",
  cin_number: "U24230MH2021PTC123456",
  dsr_registration_number: "DSR-2024-1108",
  address_line_1: "Plot No. 18, Knowledge Park",
  address_line_2: "Phase II Industrial Estate",
  country: "India",
  state: "Maharashtra",
  district: "Pune",
  city: "Pune",
  pincode: "411045",
  contact_number: "02041234567",
  fax_number: "02041234568",
  address_proof_upload: "registered_office_proof.pdf",
  sms_alert: true,
  captcha: "CDSCO",
  terms_accepted: true
};

function parseJson(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function createStore() {
  const session = parseJson(SESSION_KEY, null);
  const workflows = parseJson(WORKFLOW_KEY, {});

  function buildWorkflowDefaults() {
    return Object.fromEntries(
      routes.map((route) => [
        route.key,
        {
          step: 1,
          stageOne: { ...defaultStageOne },
          stageTwo: { ...(route.demoStageTwo || {}) },
          errors: {},
          submitted: false,
          submittedAt: null,
          submitting: false,
          submissionError: "",
          analysis: null
        }
      ])
    );
  }

  function persistWorkflows(nextWorkflows) {
    window.localStorage.setItem(WORKFLOW_KEY, JSON.stringify(nextWorkflows));
  }

  return {
    isAuthenticated() {
      return Boolean(parseJson(SESSION_KEY, session)?.email);
    },
    login(payload) {
      window.localStorage.setItem(SESSION_KEY, JSON.stringify(payload));
    },
    logout() {
      window.localStorage.removeItem(SESSION_KEY);
    },
    getWorkflowState(key) {
      const saved = parseJson(WORKFLOW_KEY, workflows)[key] || {};
      const workflowDefaults = buildWorkflowDefaults()[key] || {
        step: 1,
        stageOne: { ...defaultStageOne },
        stageTwo: {}
      };
      const route = routeMap[key];
      return {
        step: saved.step || workflowDefaults.step || 1,
        stageOne: {
          ...workflowDefaults.stageOne,
          ...(saved.stageOne || {}),
          username: saved.stageOne?.username || parseJson(SESSION_KEY, session)?.email || workflowDefaults.stageOne.username
        },
        stageTwo: { ...(route?.demoStageTwo || {}), ...(saved.stageTwo || {}) },
        errors: saved.errors || {},
        submitted: Boolean(saved.submitted),
        submittedAt: saved.submittedAt || null,
        submitting: Boolean(saved.submitting),
        submissionError: saved.submissionError || "",
        analysis: saved.analysis || null
      };
    },
    updateWorkflowState(key, patch) {
      const currentWorkflows = parseJson(WORKFLOW_KEY, workflows);
      const current = this.getWorkflowState(key);
      const next = {
        ...current,
        ...patch,
        stageOne: patch.stageOne ? { ...current.stageOne, ...patch.stageOne } : current.stageOne,
        stageTwo: patch.stageTwo ? { ...current.stageTwo, ...patch.stageTwo } : current.stageTwo
      };
      const merged = { ...currentWorkflows, [key]: next };
      persistWorkflows(merged);
    },
    resetWorkflowState(key) {
      const currentWorkflows = parseJson(WORKFLOW_KEY, workflows);
      const workflowDefaults = buildWorkflowDefaults()[key];
      const next = {
        ...workflowDefaults,
        stageOne: {
          ...workflowDefaults.stageOne,
          username: parseJson(SESSION_KEY, session)?.email || workflowDefaults.stageOne.username
        }
      };
      persistWorkflows({ ...currentWorkflows, [key]: next });
    },
    resetAllWorkflows() {
      const defaults = buildWorkflowDefaults();
      const email = parseJson(SESSION_KEY, session)?.email;
      for (const key of Object.keys(defaults)) {
        defaults[key].stageOne.username = email || defaults[key].stageOne.username;
      }
      persistWorkflows(defaults);
    }
  };
}
