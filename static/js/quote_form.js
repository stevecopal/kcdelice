// Formulaire de devis : lignes dynamiques et récapitulatif en direct.
// Les montants affichés ici sont indicatifs ; le serveur recalcule tout.
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-quote-form]");
  if (!form) return;

  const rows = form.querySelector("[data-item-rows]");
  const template = form.querySelector("template[data-item-template]");
  const totalForms = form.querySelector('input[name="items-TOTAL_FORMS"]');
  const addButton = form.querySelector("[data-add-item]");

  const money = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });

  const format = (value) => `${money.format(value)} FCFA`;

  const toNumber = (input) => {
    const value = Number.parseFloat((input && input.value || "").replace(",", "."));
    return Number.isFinite(value) ? value : 0;
  };

  const amount = (name) => {
    const input = form.querySelector(`input[name="${name}"]`);
    return input ? toNumber(input) : 0;
  };

  const isDeleted = (row) => {
    const checkbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
    return Boolean(checkbox && checkbox.checked);
  };

  const update = () => {
    let subtotal = 0;

    rows.querySelectorAll("[data-item-row]").forEach((row) => {
      const target = row.querySelector("[data-line-total]");
      if (isDeleted(row)) {
        if (target) target.textContent = "—";
        return;
      }
      const line = toNumber(row.querySelector("[data-item-quantity]")) *
        toNumber(row.querySelector("[data-item-price]"));
      subtotal += line;
      if (target) target.textContent = format(line);
    });

    const discount = amount("discount");
    const transport = amount("transport_cost");
    const deposit = amount("deposit_amount");
    const total = Math.max(subtotal - discount + transport, 0);

    const summary = (key, value) => {
      const target = form.querySelector(`[data-summary="${key}"]`);
      if (target) target.textContent = format(value);
    };

    summary("subtotal", subtotal);
    summary("discount", discount);
    summary("transport", transport);
    summary("total", total);
    summary("deposit", deposit);
    summary("balance", Math.max(total - deposit, 0));
  };

  const bindRow = (row) => {
    row.querySelectorAll("input").forEach((input) => {
      input.addEventListener("input", update);
      input.addEventListener("change", update);
    });
  };

  addButton?.addEventListener("click", () => {
    if (!template || !rows || !totalForms) return;
    const index = Number.parseInt(totalForms.value, 10) || 0;
    const html = template.innerHTML.replace(/__prefix__/g, String(index));
    const wrapper = document.createElement("tbody");
    wrapper.innerHTML = html.trim();
    const row = wrapper.querySelector("[data-item-row]");
    if (!row) return;
    rows.appendChild(row);
    totalForms.value = String(index + 1);
    bindRow(row);
    const firstInput = row.querySelector("[data-item-title]");
    if (firstInput) firstInput.focus();
    update();
  });

  rows?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-remove-item]");
    if (!button) return;
    const row = button.closest("[data-item-row]");
    if (!row) return;
    const checkbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
    if (checkbox) checkbox.checked = true;
    row.classList.add("hidden");
    update();
  });

  rows?.querySelectorAll("[data-item-row]").forEach(bindRow);

  update();
});
