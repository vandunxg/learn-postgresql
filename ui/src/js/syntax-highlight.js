(function () {
  'use strict';

  var keywordSets = {
    sql: 'select from where insert into update delete merge create alter drop truncate table view index join left right full inner outer cross lateral on using and or not null is in exists as distinct group by order having limit offset union all except intersect returning begin start commit rollback savepoint grant revoke primary key foreign references values set reset case when then else end with recursive over partition window filter conflict do nothing generated always identity cascade restrict replace explain analyze vacuum copy do language function procedure trigger extension database schema role user date time timestamp interval cast char character varying text integer bigint numeric decimal real double precision boolean json jsonb array enum true false current_user current_role'.split(' '),
    javascript: 'const let var function return if else for while new class extends import export async await throw try catch'.split(' '),
    bash: 'if then fi for in do done case esac function sudo apt apt-get yum dnf systemctl psql pg_ctl createdb dropdb'.split(' '),
    yaml: 'true false null'.split(' '),
    generic: 'select from where insert into update delete create alter drop table view index join left right inner outer on and or not null as distinct group by order having limit offset union all returning begin commit rollback grant revoke true false null get post put delete function if then fi set'.split(' ')
  };
  var functionSets = {
    sql: 'count sum avg min max coalesce nullif greatest least now extract date_part lower upper substring concat'.split(' '),
    generic: 'count sum avg min max coalesce nullif greatest least now extract'.split(' ')
  };

  var tokenPattern = /(--[^\n]*|#[^\n]*|\/\*[\s\S]*?\*\/|'(?:''|[^'])*'|"(?:""|[^"])*"|\b\d+(?:\.\d+)?\b|::|<>|!=|<=|>=|:=|[-+*/%=<>])/g;
  var wordPattern = /[A-Za-z_][\w$]*/g;
  var promptPattern = /^\s*(?:[\w.-]+(?:=>|->|=#|-#)|(?:[\w.-]+@[\w.-]+(?::[^$]*)?)?[$#%])\s?/;

  function escapeHtml(value) {
    return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function languageFor(code) {
    var match = (code.className || '').match(/language-([\w-]+)/);
    return match ? match[1].toLowerCase() : '';
  }

  function keywordLookup(language) {
    var keywords = keywordSets[language] || keywordSets.generic;
    var lookup = Object.create(null);
    keywords.forEach(function (keyword) { lookup[keyword.toLowerCase()] = true; });
    return lookup;
  }

  function functionLookup(language) {
    var functions = functionSets[language] || functionSets.generic;
    var lookup = Object.create(null);
    functions.forEach(function (name) { lookup[name.toLowerCase()] = true; });
    return lookup;
  }

  function span(kind, value) {
    var className = kind === 'function' ? 'token-function' : 'token-' + kind;
    return '<span class="' + className + '">' + escapeHtml(value) + '</span>';
  }

  function tokenize(value, language) {
    var keywords = keywordLookup(language);
    var functions = functionLookup(language);
    var output = '';
    var cursor = 0;
    var match;

    tokenPattern.lastIndex = 0;
    while ((match = tokenPattern.exec(value))) {
      output += tokenizeWords(value.slice(cursor, match.index), keywords, functions);
      var token = match[0];
      var kind = token.charAt(0) === '-' || token.charAt(0) === '#' || token.indexOf('/*') === 0
        ? 'comment'
        : token.charAt(0) === "'" || token.charAt(0) === '"'
          ? 'string'
          : /^\d/.test(token)
            ? 'number'
            : 'operator';
      output += span(kind, token);
      cursor = match.index + token.length;
    }
    output += tokenizeWords(value.slice(cursor), keywords, functions);
    return output || '<span class="token-plain"></span>';
  }

  function tokenizeWords(value, keywords, functions) {
    var output = '';
    var cursor = 0;
    var match;
    wordPattern.lastIndex = 0;
    while ((match = wordPattern.exec(value))) {
      output += escapeHtml(value.slice(cursor, match.index));
      var word = match[0];
      var after = value.slice(match.index + word.length);
      if (/^\s*\(/.test(after) && (functions[word.toLowerCase()] || keywords[word.toLowerCase()])) {
        output += span('function', word);
      } else if (keywords[word.toLowerCase()]) {
        output += span('keyword', word);
      } else {
        output += escapeHtml(word);
      }
      cursor = match.index + word.length;
    }
    return output + escapeHtml(value.slice(cursor));
  }

  function highlightConsole(raw) {
    return raw.split('\n').map(function (line) {
      var prompt = line.match(promptPattern);
      if (!prompt) return escapeHtml(line);
      var promptText = prompt[0];
      var command = line.slice(promptText.length);
      var language = /[$#%]\s?$/.test(promptText) ? 'bash' : 'sql';
      return span('prompt', promptText) + tokenize(command, language);
    }).join('\n');
  }

  function highlight(code) {
    var language = languageFor(code);
    var raw = code.textContent;
    var output;
    if (language === 'output' || language === 'text' || !language) {
      output = '<span class="token-plain">' + escapeHtml(raw) + '</span>';
    } else if (language === 'console') {
      output = highlightConsole(raw);
    } else {
      output = tokenize(raw, language);
    }
    code.innerHTML = output;
    var block = code.closest('.listingblock, .literalblock');
    if (block) {
      block.classList.add('code-language-' + (language || 'text'));
      if (language === 'output') block.classList.add('code-output');
      if (language === 'console') block.classList.add('code-console');
    }
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
