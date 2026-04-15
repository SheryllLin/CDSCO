import { renderStageTwoFields } from "./helpers.js";

export function DualUseNocStageTwo(workflow, data, errors) {
  return renderStageTwoFields(workflow.stageTwoFields, data, errors);
}
