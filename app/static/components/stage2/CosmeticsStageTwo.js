import { renderStageTwoFields } from "./helpers.js";

export function CosmeticsStageTwo(workflow, data, errors) {
  return renderStageTwoFields(workflow.stageTwoFields, data, errors);
}
