(function () {
  'use strict';

  function initialize() {
    document.querySelectorAll('.listingblock, .literalblock').forEach(function (block) {
      var pre = block.querySelector('pre');
      var code = block.querySelector('pre code');
      if (!pre || !code || block.querySelector('.code-toolbar')) return;

      var toolbar = document.createElement('div');
      toolbar.className = 'code-toolbar';
      toolbar.setAttribute('data-reader-ignore', '');
      var language = document.createElement('span');
      var languageMatch = (code.className || '').match(/language-([\w-]+)/);
      language.textContent = languageMatch ? languageMatch[1] : 'Code';
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'copy-code-button';
      button.textContent = 'Copy';
      button.setAttribute('aria-label', 'Copy code');
      toolbar.appendChild(language);
      toolbar.appendChild(button);
      pre.parentNode.insertBefore(toolbar, pre);

      button.addEventListener('click', function () {
        var value = code.textContent;
        var copy = navigator.clipboard && navigator.clipboard.writeText
          ? navigator.clipboard.writeText(value)
          : Promise.reject(new Error('Clipboard API unavailable'));
        copy.then(function () {
          button.textContent = 'Copied';
          window.setTimeout(function () { button.textContent = 'Copy'; }, 1400);
        }).catch(function () {
          button.textContent = 'Copy unavailable';
          window.setTimeout(function () { button.textContent = 'Copy'; }, 1600);
        });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
