const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..', '..');
const uiRoot = path.join(root, 'ui');

const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), 'utf8');

test('Antora UI source contains the reusable template structure', () => {
  const requiredFiles = [
    'ui/ui.yml',
    'ui/build-ui.sh',
    'ui/src/layouts/default.hbs',
    'ui/src/partials/header.hbs',
    'ui/src/partials/sidebar.hbs',
    'ui/src/partials/article.hbs',
    'ui/src/partials/toc.hbs',
    'ui/src/partials/pagination.hbs',
    'ui/src/partials/reader-tools.hbs',
    'ui/src/css/tokens.css',
    'ui/src/js/theme.js',
    'ui/src/js/sidebar.js',
    'ui/src/js/toc.js',
    'ui/src/js/syntax-highlight.js',
    'ui/src/js/copy-code.js',
    'ui/src/js/reading-progress.js',
  ];

  for (const relativePath of requiredFiles) {
    assert.equal(fs.existsSync(path.join(root, relativePath)), true, relativePath);
  }

  assert.equal(fs.existsSync(path.join(uiRoot, 'tests', 'ui-contract.test.js')), true);
});

test('default layout uses Antora page data and production partials', () => {
  const template = read('ui/src/layouts/default.hbs');

  for (const token of [
    '{{site.title}}',
    '{{page.url}}',
    '{{> header}}',
    '{{> sidebar}}',
    '{{> article}}',
    '{{> toc}}',
    '{{> reader-tools}}',
  ]) {
    assert.match(template, new RegExp(token.replace(/[{}]/g, '\\$&')));
  }

  assert.doesNotMatch(template, /Transactions|MVCC|ACID|Chapter 7/);
  assert.match(read('ui/src/partials/article.hbs'), /{{> pagination}}/);
});

test('reader state keeps theme only and has no highlight feature', () => {
  const productionUi = [
    read('ui/src/layouts/default.hbs'),
    read('ui/src/partials/header.hbs'),
    read('ui/src/partials/reader-tools.hbs'),
    read('ui/src/css/tokens.css'),
    read('ui/src/css/layout.css'),
    read('ui/src/css/reader.css'),
  ].join('\n');

  assert.match(read('ui/src/js/theme.js'), /learn-postgresql:theme/);
  assert.doesNotMatch(productionUi, /data-highlight-button|\/js\/highlight\.js|learn-postgresql:highlights:|user-highlight|highlight-status/);
});

test('TOC has a scroll-position fallback for the active section', () => {
  const toc = read('ui/src/js/toc.js');

  assert.match(toc, /function updateFromScroll\(\)/);
  assert.match(toc, /window\.addEventListener\('scroll', updateFromScroll/);
});

test('nested AsciiDoc contents lists have dedicated readable formatting', () => {
  const article = read('ui/src/css/article.css');

  assert.match(article, /\.article \.sect1 > \.sectionbody > \.ulist > ul/);
  assert.match(article, /list-style:\s*none/);
});

test('SQL highlighting styles functions and operators', () => {
  const highlighter = read('ui/src/js/syntax-highlight.js');
  const code = read('ui/src/css/code.css');
  const copyCode = read('ui/src/js/copy-code.js');

  assert.match(highlighter, /count|sum|coalesce/);
  assert.match(highlighter, /token-function/);
  assert.match(highlighter, /'operator'/);
  assert.match(code, /\.token-function/);
  assert.match(code, /\.token-operator/);
  assert.match(code, /\.token-prompt/);
  assert.match(code, /\.code-output/);
  assert.match(copyCode, /output: 'Output'/);
});

test('copy toolbar omits its language label when the block already has a title', () => {
  const source = read('ui/src/js/copy-code.js');
  const titleChildren = [];
  const title = {
    className: 'title',
    setAttribute() {},
    appendChild(child) { titleChildren.push(child); },
  };
  let insertedToolbar;
  const pre = { parentNode: { insertBefore(node) { insertedToolbar = node; } } };
  const code = { className: 'language-output', textContent: 'INSERT 0 1' };
  const block = {
    querySelector(selector) {
      if (selector === 'pre') return pre;
      if (selector === 'pre code') return code;
      if (selector === '.code-toolbar') return null;
      if (selector === '.title') return title;
      return null;
    },
  };
  const context = {
    document: {
      readyState: 'complete',
      querySelectorAll() { return [block]; },
      createElement() {
        return {
          className: '',
          setAttribute() {},
          appendChild() {},
          addEventListener() {},
          textContent: '',
        };
      },
    },
  };

  vm.runInNewContext(source, context);

  assert.match(title.className, /code-toolbar/);
  assert.equal(titleChildren.length, 1);
  assert.equal(titleChildren[0].className, 'copy-code-button');
  assert.equal(insertedToolbar, undefined);
});

test('titled code headers keep the title left and copy button right', () => {
  const code = read('ui/src/css/code.css');

  assert.match(code, /\.code-toolbar\.has-block-title\s*\{\s*justify-content:\s*space-between;/);
  assert.doesNotMatch(code, /\.code-toolbar\.has-block-title\s*\{\s*justify-content:\s*flex-end;/);
});

test('quote styling does not apply a second frame to its inner blockquote', () => {
  const article = read('ui/src/css/article.css');

  assert.match(article, /\.article \.quoteblock \{/);
  assert.doesNotMatch(article, /\.article blockquote,\s*\.article \.quoteblock/);
});

test('unknown source languages receive generic syntax highlighting', () => {
  const highlighter = read('ui/src/js/syntax-highlight.js');

  assert.match(highlighter, /generic/);
  assert.match(highlighter, /keywordSets\[language\] \|\| keywordSets\.generic/);
  assert.match(highlighter, /token-plain/);
});

test('syntax highlighter decorates SQL, console, and output blocks at runtime', () => {
  const nodes = [
    { className: 'language-sql', textContent: 'SELECT count(*) FROM users;', innerHTML: '', closest: () => null },
    { className: 'language-console', textContent: 'forumdb=> SELECT 1;', innerHTML: '', closest: () => null },
    { className: 'language-output', textContent: 'SELECT 1;\n(1 row)', innerHTML: '', closest: () => null },
  ];
  const context = {
    document: {
      readyState: 'complete',
      querySelectorAll(selector) {
        assert.match(selector, /\.literalblock pre/);
        return nodes;
      },
    },
  };

  vm.runInNewContext(read('ui/src/js/syntax-highlight.js'), context);

  assert.match(nodes[0].innerHTML, /token-keyword/);
  assert.match(nodes[1].innerHTML, /token-prompt/);
  assert.match(nodes[1].innerHTML, /token-keyword/);
  assert.match(nodes[2].innerHTML, /token-plain/);
  assert.doesNotMatch(nodes[2].innerHTML, /token-keyword/);
});

test('Antora build creates the component version index alias', () => {
  const builder = read('scripts/build-antora.sh');

  assert.match(builder, /rm -rf "\$ROOT\/build\/site"/);
  assert.match(builder, /npx --yes antora@3\.2\.0/);
  assert.match(builder, /learn-postgresql\/main/);
  assert.match(builder, /front-matter\.html/);
  assert.match(builder, /index\.html/);
});

test('front matter does not turn cover or contents entries into page headings', () => {
  const frontMatter = read('content/modules/ROOT/pages/front-matter.adoc');

  assert.doesNotMatch(frontMatter, /^== (Learn PostgreSQL|Ấn bản thứ hai|Chương (14|15|16|17|18|19):|Các sách khác|Mục lục tra cứu)/m);
  assert.match(frontMatter, /^\* Chương 14: Logging và auditing —/m);
  assert.match(frontMatter, /^\* Chương 19: Các công cụ và extension hữu ích —/m);
});

test('playbook consumes the local UI bundle', () => {
  const playbook = read('playbook/antora-playbook.yml');

  assert.match(playbook, /ui:\n\s+bundle:\n\s+url: .*ui-bundle\.zip/);
  assert.doesNotMatch(playbook, /gitlab\.com\/antora\/antora-ui-default/);
});
