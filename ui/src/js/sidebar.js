(function () {
  'use strict';

  function initialize() {
    var sidebar = document.querySelector('[data-sidebar]');
    var menuButton = document.querySelector('[data-menu-button]');
    var scrim = document.querySelector('[data-sidebar-scrim]');
    if (!sidebar || !menuButton) return;

    var scrollKey = 'learn-postgresql:sidebar-scroll';
    try {
      var savedScroll = Number(localStorage.getItem(scrollKey));
      if (savedScroll) sidebar.scrollTop = savedScroll;
    } catch (_) {}

    var current = sidebar.querySelector('.is-current-page');
    while (current) {
      var parent = current.parentElement && current.parentElement.closest('.nav-item');
      if (!parent) break;
      parent.classList.add('is-active-section');
      current = parent;
    }

    function setOpen(open) {
      sidebar.classList.toggle('is-open', open);
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'Close documentation navigation' : 'Open documentation navigation');
      if (scrim) {
        scrim.hidden = !open;
        scrim.classList.toggle('is-visible', open);
      }
      document.body.classList.toggle('sidebar-open', open);
    }

    menuButton.addEventListener('click', function () {
      setOpen(!sidebar.classList.contains('is-open'));
    });
    if (scrim) scrim.addEventListener('click', function () { setOpen(false); });
    sidebar.addEventListener('click', function (event) {
      if (event.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && sidebar.classList.contains('is-open')) {
        setOpen(false);
        menuButton.focus();
      }
    });
    sidebar.addEventListener('scroll', function () {
      try { localStorage.setItem(scrollKey, String(sidebar.scrollTop)); } catch (_) {}
    }, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
