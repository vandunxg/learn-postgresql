(function () {
  'use strict';

  var keywordSets = {
    sql: 'select from where insert into update delete create alter drop table view index join left right inner outer on and or not null as distinct group by order having limit offset union all returning begin commit rollback grant revoke primary key foreign references values set case when then else end date interval cast char varying boolean'.split(' '),
    javascript: 'const let var function return if else for while new class extends import export async await throw try catch'.split(' '),
    bash: 'if then fi for in do done case esac function'.split(' '),
    yaml: 'true false null'.split(' '),
    generic: 'select from where insert into update delete create alter drop table view index join left right inner outer on and or not null as distinct group by order having limit offset union all returning begin commit rollback grant revoke true false null get post put delete function if then fi set'.split(' ')
  };

  function escapeHtml(value) {
    return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function languageFor(code) {
    var match = (code.className || '').match(/language-([\w-]+)/);
    return match ? match[1].toLowerCase() : '';
  }

  function highlight(code) {
    var language = languageFor(code);
    var keywords = keywordSets[language] || keywordSets.generic;
    var keywordPattern = new RegExp('\\b(' + keywords.join('|') + ')\\b', 'gi');
    var tokenPattern = /(--[^\n]*|#[^\n]*|'(?:''|[^'])*'|"(?:""|[^"])*"|\b\d+(?:\.\d+)?\b|::|<>|!=|<=|>=|:=|[-+*/%=<>])/g;
    var raw = code.textContent;
    var output = '';
    var cursor = 0;
    var match;
    while ((match = tokenPattern.exec(raw))) {
      output += colorize(escapeHtml(raw.slice(cursor, match.index)), keywordPattern);
      var token = escapeHtml(match[0]);
      var kind = match[0].charAt(0) === '-' || match[0].charAt(0) === '#'
        ? 'comment'
        : /^\d/.test(match[0])
          ? 'number'
          : /^[<>=!:+*/%-]/.test(match[0])
            ? 'operator'
            : 'string';
      output += '<span class="token-' + kind + '">' + token + '</span>';
      cursor = match.index + match[0].length;
    }
    output += colorize(escapeHtml(raw.slice(cursor)), keywordPattern);
    if (output.indexOf('<span') === -1) {
      output = '<span class="token-plain">' + output + '</span>';
    }
    code.innerHTML = output;
  }

  function colorize(value, keywordPattern) {
    var functions = /\b(count|sum|avg|min|max|coalesce|nullif|greatest|least|now|extract)\b(?=\s*\()/gi;
    return value
      .replace(functions, '<span class="token-function">$1</span>')
      .replace(keywordPattern, '<span class="token-keyword">$1</span>');
  }

  function initialize() {
    document.querySelectorAll('.listingblock pre code, .literalblock pre, .literalblock pre code').forEach(highlight);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
