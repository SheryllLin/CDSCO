import { renderStageTwoFields } from "./helpers.js";

export function CdtlStageTwo(workflow, data, errors) {
  return renderStageTwoFields(workflow.stageTwoFields, data, errors);
}
