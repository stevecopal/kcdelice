// Aperçu du devis PDF dans une fenêtre superposée.
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.querySelector("[data-pdf-modal]");
  const trigger = document.querySelector("[data-pdf-preview]");
  if (!modal || !trigger) return;

  const frame = modal.querySelector("[data-pdf-frame]");
  const loading = modal.querySelector("[data-pdf-loading]");
  const closeButton = modal.querySelector("[data-pdf-close]");
  let lastFocus = null;

  const close = () => {
    modal.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    if (frame) frame.src = "about:blank";
    if (lastFocus) lastFocus.focus();
  };

  const open = () => {
    lastFocus = document.activeElement;
    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    if (loading) loading.classList.remove("hidden");
    if (frame) {
      frame.onload = () => {
        if (loading) loading.classList.add("hidden");
      };
      frame.src = trigger.dataset.pdfUrl;
    }
    if (closeButton) closeButton.focus();
  };

  trigger.addEventListener("click", open);
  if (closeButton) closeButton.addEventListener("click", close);

  modal.addEventListener("click", (event) => {
    if (event.target === modal) close();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.classList.contains("hidden")) close();
  });
});
