(function () {
  'use strict';

  function initialize() {
    document.querySelectorAll('.listingblock, .literalblock').forEach(function (block) {
      var pre = block.querySelector('pre');
      var code = block.querySelector('pre code');
      if (!pre || !code || block.querySelector('.code-toolbar')) return;

      var toolbar = document.createElement('div');
      var hasTitle = !!block.querySelector('.title');
      toolbar.className = 'code-toolbar' + (hasTitle ? ' has-block-title' : '');
      toolbar.setAttribute('data-reader-ignore', '');
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'copy-code-button';
      button.textContent = 'Copy';
      button.setAttribute('aria-label', 'Copy code');
      if (!hasTitle) {
        var language = document.createElement('span');
        var languageMatch = (code.className || '').match(/language-([\w-]+)/);
        var languageName = languageMatch ? languageMatch[1].toLowerCase() : 'code';
        var labels = {
          sql: 'SQL',
          bash: 'Bash',
          sh: 'Shell',
          console: 'Terminal',
          output: 'Output',
          text: 'Text'
        };
        language.textContent = labels[languageName] || languageName;
        toolbar.appendChild(language);
      }
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
