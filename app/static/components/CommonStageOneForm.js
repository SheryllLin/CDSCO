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

function inputField({ name, label, value = "", type = "text", placeholder = "", errors = {} }) {
  return `
    <div class="field">
      <label for="${name}">${label}</label>
      <input id="${name}" name="${name}" type="${type}" value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder)}" />
      ${fieldError(errors, name)}
    </div>
  `;
}

function selectField({ name, label, value = "", options = [], errors = {} }) {
  const optionMarkup = options
    .map((option) => `<option value="${escapeHtml(option)}" ${option === value ? "selected" : ""}>${escapeHtml(option || "Select")}</option>`)
    .join("");

  return `
    <div class="field">
      <label for="${name}">${label}</label>
      <select id="${name}" name="${name}">
        ${optionMarkup}
      </select>
      ${fieldError(errors, name)}
    </div>
  `;
}

function fileField({ name, label, errors = {}, fileName = "", accept = "" }) {
  return `
    <div class="field">
      <label class="upload-label" for="${name}">${label}</label>
      <input id="${name}" name="${name}" type="file" ${accept ? `accept="${accept}"` : ""} />
      <span class="upload-note">File uploads are mocked for this workflow demo.</span>
      ${fileName ? `<span class="file-pill">${escapeHtml(fileName)}</span>` : ""}
      ${fieldError(errors, name)}
    </div>
  `;
}

export function CommonStageOneForm(data, errors) {
  return `
    <div id="stage-one-fields">
      <section class="section-block">
        <div class="section-heading">
          <span class="section-kicker">Applicant Details</span>
          <h3>Applicant profile and credentials</h3>
          <p>Capture the account, identity, and contact information required for the filing.</p>
        </div>
        <div class="field-grid grid-two">
          ${selectField({
            name: "applicant_type",
            label: "Applicant Type",
            value: data.applicant_type,
            options: ["", "Individual", "Organization", "Authorized Agent", "Laboratory"],
            errors
          })}
          ${inputField({
            name: "username",
            label: "Username (Email)",
            value: data.username,
            type: "email",
            placeholder: "name@example.com",
            errors
          })}
        </div>
        <div class="field-grid grid-two">
          ${inputField({ name: "password", label: "Password", value: data.password, type: "password", placeholder: "Enter password", errors })}
          ${inputField({
            name: "confirm_password",
            label: "Confirm Password",
            value: data.confirm_password,
            type: "password",
            placeholder: "Re-enter password",
            errors
          })}
        </div>
        <div class="field-grid grid-three">
          ${inputField({ name: "first_name", label: "First Name", value: data.first_name, placeholder: "First name", errors })}
          ${inputField({ name: "middle_name", label: "Middle Name", value: data.middle_name, placeholder: "Middle name", errors })}
          ${inputField({ name: "last_name", label: "Last Name", value: data.last_name, placeholder: "Last name", errors })}
        </div>
        <div class="field-grid grid-three">
          ${inputField({ name: "mobile_number", label: "Mobile Number", value: data.mobile_number, placeholder: "9876543210", errors })}
          ${selectField({
            name: "gender",
            label: "Gender",
            value: data.gender,
            options: ["", "Male", "Female", "Other"],
            errors
          })}
          ${inputField({ name: "nationality", label: "Nationality", value: data.nationality, placeholder: "Nationality", errors })}
        </div>
        <div class="field-grid grid-three">
          ${selectField({
            name: "id_proof_type",
            label: "ID Proof Type",
            value: data.id_proof_type,
            options: ["", "Aadhaar", "Passport", "PAN", "Driving Licence", "Voter ID"],
            errors
          })}
          ${inputField({ name: "id_proof_number", label: "ID Proof Number", value: data.id_proof_number, placeholder: "Document number", errors })}
          ${inputField({ name: "designation", label: "Designation", value: data.designation, placeholder: "Designation", errors })}
        </div>
        <div class="field-grid grid-two">
          ${fileField({ name: "id_proof_upload", label: "ID Proof Upload", errors, fileName: data.id_proof_upload })}
          ${fileField({ name: "undertaking_upload", label: "Undertaking Upload (PDF)", errors, fileName: data.undertaking_upload, accept: ".pdf" })}
        </div>
        <div class="field-grid grid-two">
          ${inputField({
            name: "alternate_email",
            label: "Alternate Email",
            value: data.alternate_email,
            type: "email",
            placeholder: "alternate@example.com",
            errors
          })}
        </div>
      </section>

      <section class="section-block">
        <div class="section-heading">
          <span class="section-kicker">Registered Address</span>
          <h3>Organization and address information</h3>
          <p>Enter the registered office details exactly as recorded in organizational documents.</p>
        </div>
        <div class="field-grid grid-two">
          ${inputField({ name: "organization_name", label: "Organization Name", value: data.organization_name, placeholder: "Organization name", errors })}
          ${selectField({
            name: "organization_type",
            label: "Organization Type",
            value: data.organization_type,
            options: ["", "Company", "Partnership", "Proprietorship", "Government", "Laboratory", "Trust"],
            errors
          })}
        </div>
        <div class="field-grid grid-two">
          ${inputField({ name: "cin_number", label: "CIN Number", value: data.cin_number, placeholder: "CIN number", errors })}
          ${inputField({
            name: "dsr_registration_number",
            label: "DSR Registration Number",
            value: data.dsr_registration_number,
            placeholder: "DSR registration number",
            errors
          })}
        </div>
        <div class="field-grid grid-two">
          ${inputField({ name: "address_line_1", label: "Address Line 1", value: data.address_line_1, placeholder: "Address line 1", errors })}
          ${inputField({ name: "address_line_2", label: "Address Line 2", value: data.address_line_2, placeholder: "Address line 2", errors })}
        </div>
        <div class="field-grid grid-three">
          ${inputField({ name: "country", label: "Country", value: data.country, placeholder: "Country", errors })}
          ${inputField({ name: "state", label: "State", value: data.state, placeholder: "State", errors })}
          ${inputField({ name: "district", label: "District", value: data.district, placeholder: "District", errors })}
        </div>
        <div class="field-grid grid-three">
          ${inputField({ name: "city", label: "City", value: data.city, placeholder: "City", errors })}
          ${inputField({ name: "pincode", label: "Pincode", value: data.pincode, placeholder: "Pincode", errors })}
          ${inputField({ name: "contact_number", label: "Contact Number", value: data.contact_number, placeholder: "Contact number", errors })}
        </div>
        <div class="field-grid grid-two">
          ${inputField({ name: "fax_number", label: "Fax Number", value: data.fax_number, placeholder: "Fax number", errors })}
          ${fileField({ name: "address_proof_upload", label: "Address Proof Upload", errors, fileName: data.address_proof_upload })}
        </div>
      </section>

      <section class="section-block">
        <div class="section-heading">
          <span class="section-kicker">Other Details</span>
          <h3>Alerts, CAPTCHA, and declarations</h3>
          <p>Complete the declaration items before continuing to the workflow-specific stage.</p>
        </div>
        <div class="checkbox-grid">
          <div class="checkbox-row">
            <input id="sms_alert" name="sms_alert" type="checkbox" ${data.sms_alert ? "checked" : ""} />
            <label for="sms_alert">Enable SMS alert notifications</label>
          </div>
          <div class="field">
            <label>CAPTCHA</label>
            <div class="captcha-box">CDSCO</div>
            <input id="captcha" name="captcha" type="text" value="${escapeHtml(data.captcha)}" placeholder="Enter CAPTCHA text" />
            ${fieldError(errors, "captcha")}
          </div>
          <div class="checkbox-row">
            <input id="terms_accepted" name="terms_accepted" type="checkbox" ${data.terms_accepted ? "checked" : ""} />
            <label for="terms_accepted">I agree to the terms and conditions of the portal</label>
          </div>
          ${fieldError(errors, "terms_accepted")}
        </div>
      </section>
    </div>
  `;
}
