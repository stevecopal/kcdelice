const DISMISS_DELAY = 6000;
const FADE_DELAY = 220;

function dismiss(toast) {
  if (toast.dataset.leaving === "true") return;
  toast.dataset.leaving = "true";
  toast.classList.add("toast-out");
  window.setTimeout(() => toast.remove(), FADE_DELAY);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-toast]").forEach((toast) => {
    let timer = window.setTimeout(() => dismiss(toast), DISMISS_DELAY);
    const progress = toast.querySelector(".toast-progress");

    // Le survol met en pause le compte à rebours et la barre de progression.
    toast.addEventListener("mouseenter", () => {
      window.clearTimeout(timer);
      if (progress) progress.style.animationPlayState = "paused";
    });

    toast.addEventListener("mouseleave", () => {
      if (progress) progress.style.animationPlayState = "running";
      timer = window.setTimeout(() => dismiss(toast), DISMISS_DELAY);
    });

    const closeButton = toast.querySelector("[data-toast-close]");
    if (closeButton) {
      closeButton.addEventListener("click", () => {
        window.clearTimeout(timer);
        dismiss(toast);
      });
    }
  });
});
