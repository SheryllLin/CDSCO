import { renderStageTwoFields } from "./helpers.js";

export function FormulationStageTwo(workflow, data, errors) {
  return renderStageTwoFields(workflow.stageTwoFields, data, errors);
}
