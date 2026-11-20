// Filtres de listes (devis, réalisations, services) sans rechargement de page.
// Le serveur ne renvoie que le bloc de résultats quand la requête vient d'ici.
document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll("[data-ajax-filter]");
  if (!forms.length) return;

  const delay = (fn, wait) => {
    let timer = null;
    return (...args) => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => fn(...args), wait);
    };
  };

  forms.forEach((form) => {
    const results = document.querySelector("[data-filter-results]");
    if (!results) return;

    let request = null;
    const submitButton = form.querySelector("button[type='submit']");

    const load = async () => {
      const url = new URL(form.getAttribute("action") || window.location.pathname, window.location.origin);
      const data = new FormData(form);
      url.search = "";
      data.forEach((value, key) => {
        if (String(value).trim() !== "") url.searchParams.set(key, value);
      });

      if (request) request.abort();
      request = new AbortController();
      results.setAttribute("aria-busy", "true");
      results.classList.add("opacity-50", "transition-opacity");
      if (submitButton) submitButton.disabled = true;

      try {
        const response = await fetch(url, {
          headers: { "X-Requested-With": "XMLHttpRequest" },
          signal: request.signal,
        });
        if (!response.ok) throw new Error(String(response.status));
        results.innerHTML = await response.text();
        window.history.replaceState({}, "", url.toString());
      } catch (error) {
        if (error.name === "AbortError") return;
        window.location.assign(url.toString());
      } finally {
        results.removeAttribute("aria-busy");
        results.classList.remove("opacity-50");
        if (submitButton) submitButton.disabled = false;
      }
    };

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      load();
    });

    form.querySelectorAll("input[type='search'], input[type='text']").forEach((input) => {
      input.addEventListener("input", delay(load, 350));
    });

    form.querySelectorAll("select").forEach((select) => {
      select.addEventListener("change", load);
    });
  });
});
