document.addEventListener("DOMContentLoaded", () => {
  // --- Menu latéral (mobile) ---------------------------------------------
  const sidebar = document.getElementById("admin-sidebar");
  const backdrop = document.getElementById("admin-backdrop");
  const toggles = document.querySelectorAll("[data-admin-sidebar-toggle]");

  const setMenuOpen = (open) => {
    if (!sidebar) return;
    sidebar.classList.toggle("hidden", !open);
    if (backdrop) backdrop.classList.toggle("hidden", !open);
    toggles.forEach((toggle) => toggle.setAttribute("aria-expanded", String(open)));
    document.body.classList.toggle("overflow-hidden", open);
    if (open) {
      const firstLink = sidebar.querySelector("a");
      if (firstLink) firstLink.focus();
    }
  };

  toggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
      setMenuOpen(sidebar ? sidebar.classList.contains("hidden") : false);
    });
  });

  if (backdrop) {
    backdrop.addEventListener("click", () => setMenuOpen(false));
  }

  if (sidebar) {
    sidebar.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        if (window.innerWidth < 1024) setMenuOpen(false);
      });
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMenuOpen(false);
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth >= 1024) document.body.classList.remove("overflow-hidden");
  });

  // --- Prévisualisation des images ----------------------------------------
  document.querySelectorAll("input[type='file'][data-preview]").forEach((input) => {
    const target = document.getElementById(input.dataset.preview);
    if (!target) return;
    const empty = document.getElementById(input.dataset.preview + "-empty");
    const originalSrc = target.getAttribute("src") || "";
    let objectUrl = null;

    const showImage = (src) => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
        objectUrl = null;
      }
      target.src = src;
      target.classList.remove("hidden");
      if (empty) empty.classList.add("hidden");
    };

    const showPlaceholder = () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
        objectUrl = null;
      }
      target.classList.add("hidden");
      if (empty) empty.classList.remove("hidden");
    };

    input.addEventListener("change", () => {
      const file = input.files && input.files[0];
      if (file) {
        objectUrl = URL.createObjectURL(file);
        showImage(objectUrl);
      } else if (originalSrc) {
        showImage(originalSrc);
      } else {
        showPlaceholder();
      }
    });
  });

  // --- Anti double-soumission ---------------------------------------------
  document.querySelectorAll("form[data-single-submit]").forEach((form) => {
    form.addEventListener("submit", () => {
      if (form.dataset.submitted === "true") return;
      form.dataset.submitted = "true";
      const button = form.querySelector("button[type='submit']");
      if (button) {
        button.disabled = true;
        button.setAttribute("aria-disabled", "true");
      }
    });
  });
});
