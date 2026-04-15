import { renderStageTwoFields } from "./helpers.js";

export function TestLicenseStageTwo(workflow, data, errors) {
  return renderStageTwoFields(workflow.stageTwoFields, data, errors);
}
