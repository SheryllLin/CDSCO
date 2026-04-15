function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function fieldError(errors, key) {
  return errors[key] ? `<span class="error-text">${escapeHtml(errors[key])}</span>` : "";
}

export function renderStageTwoFields(fields, data, errors) {
  return fields
    .map((field) => {
      if (field.type === "select") {
        const options = (field.options || [])
          .map(
            (option) =>
              `<option value="${escapeHtml(option)}" ${String(data[field.name] || "") === option ? "selected" : ""}>${escapeHtml(option || "Select")}</option>`
          )
          .join("");

        return `
          <div class="field">
            <label for="${field.name}">${field.label}</label>
            <select id="${field.name}" name="${field.name}">
              ${options}
            </select>
            ${fieldError(errors, field.name)}
          </div>
        `;
      }

      if (field.type === "checkbox") {
        const checked = String(data[field.name] || "").toLowerCase() === "true";
        return `
          <div class="checkbox-row">
            <input id="${field.name}" name="${field.name}" type="checkbox" value="True" ${checked ? "checked" : ""} />
            <label for="${field.name}">${field.label}</label>
          </div>
        `;
      }

      if (field.type === "textarea") {
        return `
          <div class="field">
            <label for="${field.name}">${field.label}</label>
            <textarea id="${field.name}" name="${field.name}" placeholder="${escapeHtml(field.placeholder || "")}">${escapeHtml(data[field.name] || "")}</textarea>
            ${fieldError(errors, field.name)}
          </div>
        `;
      }

      return `
        <div class="field">
          <label for="${field.name}">${field.label}</label>
          <input id="${field.name}" name="${field.name}" type="${field.type || "text"}" value="${escapeHtml(data[field.name] || "")}" placeholder="${escapeHtml(field.placeholder || "")}" />
          ${fieldError(errors, field.name)}
        </div>
      `;
    })
    .join("");
}
