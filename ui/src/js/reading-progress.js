(function () {
  'use strict';

  function initialize() {
    var line = document.querySelector('[data-reading-progress-line]');
    var fab = document.querySelector('[data-reader-fab]');
    var tooltip = document.querySelector('[data-reader-tooltip]');
    if (!line || !fab || !tooltip) return;

    var scheduled = false;
    function update() {
      scheduled = false;
      var max = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
      var percent = max ? Math.round(Math.min(100, Math.max(0, (window.scrollY / max) * 100))) : 0;
      line.style.width = percent + '%';
      fab.style.setProperty('--reader-progress', (percent * 3.6) + 'deg');
      tooltip.textContent = 'Read ' + percent + '% - Back to top';
      fab.setAttribute('aria-label', 'Reading progress ' + percent + ' percent, back to top');
      fab.setAttribute('title', 'Reading progress ' + percent + '% - Back to top');
    }
    function schedule() {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(update);
    }

    fab.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    update();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
