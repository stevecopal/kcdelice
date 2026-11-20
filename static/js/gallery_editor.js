// Galerie d'une réalisation : ajout, aperçu local et retrait d'images.
document.addEventListener("DOMContentLoaded", () => {
  const items = document.querySelector("[data-gallery-items]");
  const template = document.querySelector("[data-gallery-template]");
  const addButton = document.querySelector("[data-gallery-add]");
  const totalForms = document.querySelector("input[name='images-TOTAL_FORMS']");
  const emptyNotice = document.querySelector("[data-gallery-empty]");
  if (!items) return;

  const cards = () => Array.from(items.querySelectorAll("[data-gallery-item]"));

  const refreshEmptyNotice = () => {
    if (!emptyNotice) return;
    emptyNotice.classList.toggle("hidden", cards().length > 0);
  };

  const setRemoved = (card, removed) => {
    const checkbox = card.querySelector("input[type='checkbox'][name$='-DELETE']");
    if (checkbox) checkbox.checked = removed;
    card.classList.toggle("gallery-item-removed", removed);

    const badge = card.querySelector("[data-gallery-removed-badge]");
    if (badge) badge.classList.toggle("hidden", !removed);

    const remove = card.querySelector("[data-gallery-remove]");
    if (remove) {
      remove.classList.toggle("text-vert", removed);
      remove.classList.toggle("text-noir/40", !removed);
      remove.setAttribute("aria-pressed", String(removed));
      remove.title = removed ? "Rétablir cette image" : "Retirer cette image";
    }
  };

  const bind = (card) => {
    const input = card.querySelector("input[type='file']");
    const label = card.querySelector("label");

    if (input && label && !label.htmlFor) label.htmlFor = input.id;

    if (input) {
      input.addEventListener("change", () => {
        const file = input.files && input.files[0];
        const preview = card.querySelector("[data-gallery-preview]");
        const placeholder = card.querySelector("[data-gallery-placeholder]");
        const filename = card.querySelector("[data-gallery-filename]");

        if (!file) return;

        if (preview) {
          if (preview.dataset.objectUrl) URL.revokeObjectURL(preview.dataset.objectUrl);
          const url = URL.createObjectURL(file);
          preview.dataset.objectUrl = url;
          preview.src = url;
          preview.classList.remove("hidden");
        }
        if (placeholder) placeholder.classList.add("hidden");
        if (filename) filename.textContent = file.name;
        setRemoved(card, false);
      });
    }

    const remove = card.querySelector("[data-gallery-remove]");
    if (remove) {
      remove.addEventListener("click", () => {
        const checkbox = card.querySelector("input[type='checkbox'][name$='-DELETE']");
        setRemoved(card, !(checkbox && checkbox.checked));
      });
    }
  };

  cards().forEach(bind);

  if (addButton && template && totalForms) {
    addButton.addEventListener("click", () => {
      const index = Number.parseInt(totalForms.value, 10) || 0;
      const wrapper = document.createElement("div");
      wrapper.innerHTML = template.innerHTML.replace(/__prefix__/g, String(index)).trim();

      const card = wrapper.firstElementChild;
      if (!card) return;

      items.appendChild(card);
      totalForms.value = String(index + 1);
      bind(card);
      refreshEmptyNotice();

      const input = card.querySelector("input[type='file']");
      if (input) input.click();
    });
  }

  refreshEmptyNotice();
});
