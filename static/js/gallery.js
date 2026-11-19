document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("gallery-overlay");
  const dataEl = document.getElementById("gallery-data");
  if (!overlay || !dataEl) return;

  const entries = JSON.parse(dataEl.textContent || "[]");
  const byId = new Map(entries.map((entry) => [entry.id, entry]));
  const imageEl = document.getElementById("gallery-image");
  const titleEl = document.getElementById("gallery-title");
  const counterEl = document.getElementById("gallery-counter");
  const closeBtn = document.getElementById("gallery-close");
  const prevBtn = document.getElementById("gallery-prev");
  const nextBtn = document.getElementById("gallery-next");

  let activeId = null;
  let index = 0;
  let touchStartX = null;

  function currentEntry() {
    return byId.get(activeId);
  }

  function render() {
    const entry = currentEntry();
    if (!entry || !entry.images.length) return;
    const src = entry.images[index];
    imageEl.src = src;
    imageEl.alt = entry.title;
    titleEl.textContent = entry.title;
    counterEl.textContent = `${index + 1} / ${entry.images.length}`;
  }

  function open(id) {
    const entry = byId.get(id);
    if (!entry || !entry.images.length) return;
    activeId = id;
    index = 0;
    render();
    overlay.classList.remove("hidden");
    overlay.classList.add("flex");
    document.body.style.overflow = "hidden";
    if (closeBtn) closeBtn.focus();
  }

  function close() {
    overlay.classList.add("hidden");
    overlay.classList.remove("flex");
    document.body.style.overflow = "";
    activeId = null;
    imageEl.src = "";
  }

  function step(delta) {
    const entry = currentEntry();
    if (!entry || !entry.images.length) return;
    index = (index + delta + entry.images.length) % entry.images.length;
    render();
  }

  document.querySelectorAll("[data-gallery-id]").forEach((button) => {
    button.addEventListener("click", () => open(button.dataset.galleryId));
  });

  if (closeBtn) closeBtn.addEventListener("click", close);
  if (prevBtn) prevBtn.addEventListener("click", () => step(-1));
  if (nextBtn) nextBtn.addEventListener("click", () => step(1));

  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) close();
  });

  document.addEventListener("keydown", (event) => {
    if (overlay.classList.contains("hidden")) return;
    if (event.key === "Escape") close();
    if (event.key === "ArrowLeft") step(-1);
    if (event.key === "ArrowRight") step(1);
  });

  overlay.addEventListener(
    "touchstart",
    (event) => {
      touchStartX = event.changedTouches[0].screenX;
    },
    { passive: true }
  );

  overlay.addEventListener(
    "touchend",
    (event) => {
      if (touchStartX === null) return;
      const delta = event.changedTouches[0].screenX - touchStartX;
      touchStartX = null;
      if (Math.abs(delta) < 50) return;
      step(delta > 0 ? -1 : 1);
    },
    { passive: true }
  );
});
