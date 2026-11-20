/* Application installable de l'espace d'administration. */
(function () {
  "use strict";

  var standalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  var currentPrompt = function () {
    return window.__pwaInstallPrompt || null;
  };

  /* --- Service worker (tout le site, pour que /connexion/ soit installable) */
  var registration = null;
  var registerServiceWorker = function () {
    if (!("serviceWorker" in navigator)) return Promise.reject();
    if (!registration) {
      registration = navigator.serviceWorker.register("/espace/service-worker.js", {
        scope: "/",
      });
      registration.catch(function () {});
    }
    return registration;
  };
  registerServiceWorker().catch(function () {
    /* Le mode hors ligne est un bonus : l'administration reste utilisable. */
  });

  /* --- Écran de lancement ------------------------------------------------ */
  var splash = document.querySelector("[data-pwa-splash]");
  if (splash) {
    if (!standalone) {
      splash.remove();
    } else {
      var startedAt = Date.now();
      var hide = function () {
        var remaining = Math.max(0, 950 - (Date.now() - startedAt));
        window.setTimeout(function () {
          splash.classList.add("is-hidden");
          window.setTimeout(function () {
            splash.remove();
          }, 500);
        }, remaining);
      };
      if (document.readyState === "complete") {
        hide();
      } else {
        window.addEventListener("load", hide);
      }
    }
  }

  /* --- Invite d'installation -------------------------------------------- */
  var installWrapper = document.querySelector("[data-pwa-install]");
  if (!installWrapper) return;

  var installButton = installWrapper.querySelector("button");
  var helpPanel = document.querySelector("[data-pwa-help]");
  var pendingClick = false;

  var setVisible = function (element, visible) {
    if (!element) return;
    element.classList.toggle("hidden", !visible);
  };

  var showHelp = function (show) {
    if (!helpPanel) return;
    setVisible(helpPanel, show);
    if (installButton) installButton.setAttribute("aria-expanded", show ? "true" : "false");
  };

  /* Le bouton reste visible même sans invite native (ngrok, navigateur sans
     support) : un clic lance l'installation ou explique comment faire. */
  setVisible(installWrapper, !standalone);

  var launchPrompt = function (event) {
    installButton.disabled = true;
    /* Certains navigateurs n'aboutissent jamais la promesse : on ne laisse pas
       le bouton bloqué pour autant. */
    window.setTimeout(function () {
      installButton.disabled = false;
    }, 2500);
    event.prompt();
    return event.userChoice
      .catch(function () {})
      .then(function (choice) {
        installButton.disabled = false;
        if (choice && choice.outcome === "accepted") setVisible(installWrapper, false);
      });
  };

  /* L'événement est capturé très tôt par le partial du <head> : on installe
     immédiatement s'il arrive après un clic resté en attente. */
  document.addEventListener("pwa:installprompt", function () {
    var event = currentPrompt();
    if (!event) return;
    showHelp(false);
    setVisible(installWrapper, true);
    if (pendingClick) {
      pendingClick = false;
      launchPrompt(event);
    }
  });

  if (installButton) {
    installButton.addEventListener("click", function () {
      var event = currentPrompt();
      if (event) {
        launchPrompt(event);
        return;
      }

      /* Invite pas encore émise : on laisse au navigateur le temps de rendre le
         service worker actif, puis on installe dès qu'elle apparaît. */
      pendingClick = true;
      installButton.disabled = true;
      var deadline = Date.now() + 6000;
      var poll = function () {
        var ready = currentPrompt();
        if (ready) {
          pendingClick = false;
          installButton.disabled = false;
          launchPrompt(ready);
          return;
        }
        if (Date.now() < deadline) {
          window.setTimeout(poll, 200);
          return;
        }
        pendingClick = false;
        installButton.disabled = false;
        showHelp(true);
      };
      registerServiceWorker()
        .catch(function () {})
        .then(function () {
          poll();
        });
    });
  }

  var retryButton = document.querySelector("[data-pwa-retry]");
  if (retryButton) {
    retryButton.addEventListener("click", function () {
      window.location.reload();
    });
  }

  window.addEventListener("appinstalled", function () {
    pendingClick = false;
    showHelp(false);
    setVisible(installWrapper, false);
  });
})();
