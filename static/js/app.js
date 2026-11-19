document.addEventListener("DOMContentLoaded", () => {
  // --- Menu mobile (ouverture animée) ------------------------------------
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navMenu = document.querySelector("[data-nav-menu]");

  const setNavOpen = (open) => {
    if (!navToggle || !navMenu) return;
    navToggle.setAttribute("aria-expanded", String(open));
    navToggle.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
    navMenu.classList.toggle("grid-rows-[1fr]", open);
    navMenu.classList.toggle("grid-rows-[0fr]", !open);

    // Hamburger → croix
    const bars = navToggle.querySelectorAll("[data-nav-bar]");
    if (bars.length === 3) {
      bars[0].style.transform = open ? "translateY(7px) rotate(45deg)" : "";
      bars[1].style.opacity = open ? "0" : "";
      bars[2].style.transform = open ? "translateY(-7px) rotate(-45deg)" : "";
    }
  };

  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      setNavOpen(navToggle.getAttribute("aria-expanded") !== "true");
    });

    navMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => setNavOpen(false));
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") setNavOpen(false);
    });
  }

  // --- Description longue : lire plus / réduire ---------------------------
  document.querySelectorAll("[data-readmore]").forEach((container) => {
    const text = container.querySelector("[data-readmore-text]");
    const button = container.querySelector("[data-readmore-toggle]");
    const moreLabel = container.dataset.moreLabel || "Lire plus";
    const lessLabel = container.dataset.lessLabel || "Réduire";
    if (!text || !button) return;

    // Le bouton n'apparaît que si le texte dépasse réellement le nombre de lignes.
    text.classList.remove("line-clamp-3");
    const fullHeight = text.clientHeight;
    text.classList.add("line-clamp-3");
    if (fullHeight <= text.clientHeight + 1) {
      text.classList.remove("line-clamp-3");
      return;
    }

    button.classList.remove("hidden");
    button.addEventListener("click", () => {
      const expanded = text.classList.toggle("line-clamp-3") === false;
      button.textContent = expanded ? lessLabel : moreLabel;
      button.setAttribute("aria-expanded", String(expanded));
    });
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

// --- Demande de devis → WhatsApp -------------------------------------------
// Le formulaire ne fait aucun aller-retour serveur : il compose un message
// lisible et ouvre WhatsApp avec la demande déjà rédigée.
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-quote-form]");
  if (!form) return;

  const error = form.querySelector("[data-quote-error]");

  const showError = (message) => {
    if (!error) return;
    error.textContent = message;
    error.hidden = false;
  };

  form.querySelectorAll("input, textarea").forEach((field) => {
    field.addEventListener("input", () => {
      if (error) error.hidden = true;
    });
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const number = (form.dataset.waNumber || "").replace(/\D/g, "");
    if (!number) {
      showError("Le numéro WhatsApp de l'administrateur n'est pas configuré.");
      return;
    }

    const data = new FormData(form);
    const value = (key) => String(data.get(key) || "").trim();

    const name = value("name");
    const phone = value("phone");
    const eventName = value("event");
    const place = value("place");
    const description = value("description");
    const company = form.dataset.company || "KCDélices";

    const lines = [
      `Bonjour ${company}, je m'appelle ${name}.`,
      `Je souhaite un devis pour : ${eventName}.`,
      `Lieu de l'événement : ${place}.`,
      `Téléphone : ${phone}.`,
    ];
    if (description) {
      lines.push("", `Mon projet : ${description}`);
    }

    window.open(
      `https://wa.me/${number}?text=${encodeURIComponent(lines.join("\n"))}`,
      "_blank",
      "noopener"
    );
  });
});
