const DISMISS_DELAY = 5000;
const FADE_DELAY = 300;

function dismiss(toast) {
  toast.classList.add("opacity-0", "translate-x-4", "transition", "duration-300");
  window.setTimeout(() => toast.remove(), FADE_DELAY);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-toast]").forEach((toast) => {
    const timer = window.setTimeout(() => dismiss(toast), DISMISS_DELAY);
    const closeButton = toast.querySelector("[data-toast-close]");
    if (closeButton) {
      closeButton.addEventListener("click", () => {
        window.clearTimeout(timer);
        dismiss(toast);
      });
    }
  });
});
