document.addEventListener("DOMContentLoaded", () => {
  // Menu mobile
  const toggle = document.querySelector("[data-nav-toggle]");
  const menu = document.querySelector("[data-nav-menu]");
  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const isHidden = menu.classList.toggle("hidden");
      menu.classList.toggle("flex");
      toggle.setAttribute("aria-expanded", String(!isHidden));
      toggle.setAttribute("aria-label", isHidden
        ? "Ouvrir le menu"
        : "Fermer le menu");
    });
  }

  // Fermeture au clic sur un lien
  document.querySelectorAll("[data-nav-menu] a").forEach((link) => {
    link.addEventListener("click", () => {
      const menu = document.querySelector("[data-nav-menu]");
      if (menu) {
        menu.classList.add("hidden");
        menu.classList.remove("flex");
        const toggle = document.querySelector("[data-nav-toggle]");
        if (toggle) {
          toggle.setAttribute("aria-expanded", "false");
          toggle.setAttribute("aria-label", "Ouvrir le menu");
        }
      }
    });
  });

  // Fermeture avec Échap
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const menu = document.querySelector("[data-nav-menu]");
      const toggle = document.querySelector("[data-nav-toggle]");
      if (menu) {
        menu.classList.add("hidden");
        menu.classList.remove("flex");
      }
      if (toggle) {
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Ouvrir le menu");
      }
    }
  });

  // Gallery
  const overlay = document.getElementById("gallery-overlay");
  const dataEl = document.getElementById("gallery-data");
  if (overlay && dataEl) {
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

    function currentEntry() { return byId.get(activeId); }

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

    closeBtn.addEventListener("click", close);
    prevBtn.addEventListener("click", () => step(-1));
    nextBtn.addEventListener("click", () => step(1));

    // Navigation clavier
    overlay.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
    });

    // Gestes tactiles
    overlay.addEventListener("touchstart", (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    overlay.addEventListener("touchmove", (e) => {
      e.preventDefault();
    }, { passive: false });
    overlay.addEventListener("touchend", (e) => {
      if (touchStartX === null) return;
      const touchEndX = e.changedTouches[0].screenX;
      const diff = touchStartX - touchEndX;
      if (Math.abs(diff) > 50) {
        step(diff > 0 ? 1 : -1);
      }
      touchStartX = null;
    }, { passive: true });
  }
});
