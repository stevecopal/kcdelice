// Validation visuelle du mot de passe : robustesse et correspondance.
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-password-form]");
  if (!form) return;

  const newPassword = form.querySelector("input[name='new_password1']");
  const confirmation = form.querySelector("input[name='new_password2']");
  const bar = form.querySelector("[data-password-strength-bar]");
  const text = form.querySelector("[data-password-strength-text]");
  const rules = form.querySelector("[data-password-rules]");
  const match = form.querySelector("[data-password-match]");
  const mismatch = form.querySelector("[data-password-mismatch]");
  if (!newPassword || !bar) return;

  const username = (form.dataset.username || "").toLowerCase();
  const email = (form.dataset.email || "").toLowerCase();
  const emailLocal = email.split("@")[0];

  const labels = {
    0: "—",
    1: "Faible",
    2: "Moyen",
    3: "Bon",
    4: "Excellent",
  };

  const setRule = (name, ok, active) => {
    const item = rules ? rules.querySelector(`[data-rule="${name}"]`) : null;
    if (!item) return;
    const dot = item.querySelector("span");
    item.classList.toggle("text-noir", ok);
    item.classList.toggle("text-noir/60", !ok);
    if (dot) {
      dot.classList.toggle("border-vert", ok);
      dot.classList.toggle("bg-vert", ok);
      dot.classList.toggle("border-noir/20", !ok);
      dot.innerHTML = ok
        ? '<svg class="h-2.5 w-2.5 text-blanc" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>'
        : "";
    }
    item.dataset.active = active ? "1" : "";
  };

  const evaluate = () => {
    const value = newPassword.value;
    const lower = value.toLowerCase();

    const checks = {
      length: value.length >= 8,
      variety: /[a-zA-Z]/.test(value) && /[0-9\W_]/.test(value),
      "not-numeric": value.length > 0 && /[^0-9]/.test(value),
      personal:
        value.length > 0 &&
        (!username || (!lower.includes(username) && !username.includes(lower))) &&
        (!emailLocal || !lower.includes(emailLocal)),
    };

    Object.entries(checks).forEach(([name, ok]) => setRule(name, ok, value.length > 0));

    const score = value.length === 0 ? 0 : Object.values(checks).filter(Boolean).length;
    text.textContent = labels[score];

    const segments = bar.querySelectorAll("span");
    segments.forEach((segment, index) => {
      segment.className = "h-1.5 flex-1 rounded-full transition-colors";
      if (index >= score) {
        segment.classList.add("bg-noir/10");
      } else if (score >= 3) {
        segment.classList.add("bg-vert");
      } else {
        segment.classList.add("bg-noir/40");
      }
    });

    const confirmValue = confirmation ? confirmation.value : "";
    if (match && mismatch) {
      const filled = confirmValue.length > 0;
      const equal = filled && confirmValue === value;
      match.classList.toggle("hidden", !equal);
      match.classList.toggle("flex", equal);
      mismatch.classList.toggle("hidden", !filled || equal);
      mismatch.classList.toggle("flex", filled && !equal);
      if (confirmation) {
        confirmation.setAttribute("aria-invalid", filled && !equal ? "true" : "false");
      }
    }
  };

  newPassword.addEventListener("input", evaluate);
  if (confirmation) confirmation.addEventListener("input", evaluate);

  form.querySelectorAll("[data-password-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const input = button.parentElement.querySelector("input");
      if (!input) return;
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      button.setAttribute("aria-pressed", String(show));
      button.setAttribute(
        "aria-label",
        show ? "Masquer le mot de passe" : "Afficher le mot de passe"
      );
    });
  });

  evaluate();
});
