(function () {
  'use strict';

  var root = document.documentElement;
  var storageKey = 'learn-postgresql:theme';

  function preferredTheme() {
    var saved = null;
    try {
      saved = localStorage.getItem(storageKey);
    } catch (_) {}
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }

  function setTheme(theme, persist) {
    root.dataset.theme = theme;
    if (persist) {
      try { localStorage.setItem(storageKey, theme); } catch (_) {}
    }

    var button = document.querySelector('[data-theme-button]');
    if (!button) return;
    var dark = theme === 'dark';
    button.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
    button.setAttribute('title', dark ? 'Light mode' : 'Dark mode');
    var icon = button.querySelector('[aria-hidden="true"]');
    if (icon) icon.textContent = dark ? '\u2600' : '\u263e';
  }

  setTheme(preferredTheme(), false);

  function initialize() {
    var button = document.querySelector('[data-theme-button]');
    if (!button) return;
    button.addEventListener('click', function () {
      setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', true);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
