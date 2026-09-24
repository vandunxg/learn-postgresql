(function () {
  'use strict';

  function slugify(value) {
    return value.toLowerCase().trim().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
  }

  function initialize() {
    var article = document.querySelector('[data-article]');
    var toc = document.querySelector('[data-toc-list]');
    if (!article || !toc) return;

    var headings = Array.prototype.slice.call(article.querySelectorAll('h2, h3, h4, h5, h6'));
    var usedIds = {};
    headings.forEach(function (heading) {
      var id = heading.id || slugify(heading.textContent) || 'section';
      var baseId = id;
      var count = 1;
      while (usedIds[id] || (document.getElementById(id) && document.getElementById(id) !== heading)) {
        id = baseId + '-' + count;
        count += 1;
      }
      heading.id = id;
      usedIds[id] = true;

      var link = document.createElement('a');
      link.href = '#' + id;
      link.textContent = heading.textContent;
      link.dataset.level = heading.tagName.slice(1);
      link.dataset.tocId = id;
      toc.appendChild(link);
    });
    if (!headings.length) {
      toc.parentElement.hidden = true;
      return;
    }

    var links = Array.prototype.slice.call(toc.querySelectorAll('a'));
    function setActive(id) {
      links.forEach(function (link) {
        var active = link.dataset.tocId === id;
        link.classList.toggle('is-active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }

    function updateFromScroll() {
      var active = headings[0];
      headings.forEach(function (heading) {
        if (heading.getBoundingClientRect().top <= 120) active = heading;
      });
      if (active) setActive(active.id);
    }

    window.addEventListener('scroll', updateFromScroll, { passive: true });
    updateFromScroll();

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        var visible = entries.filter(function (entry) { return entry.isIntersecting; });
        if (visible.length) {
          visible.sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
          setActive(visible[visible.length - 1].target.id);
        }
      }, { rootMargin: '-96px 0px -62% 0px', threshold: [0, .1, .5] });
      headings.forEach(function (heading) { observer.observe(heading); });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
