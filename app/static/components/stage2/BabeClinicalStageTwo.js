import { renderStageTwoFields } from "./helpers.js";

export function BabeClinicalStageTwo(workflow, data, errors) {
  return renderStageTwoFields(workflow.stageTwoFields, data, errors);
}
