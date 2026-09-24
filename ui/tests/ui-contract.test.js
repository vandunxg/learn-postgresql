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

  assert.match(highlighter, /count|sum|coalesce/);
  assert.match(highlighter, /token-function/);
  assert.match(highlighter, /'operator'/);
  assert.match(code, /\.token-function/);
  assert.match(code, /\.token-operator/);
});

test('unknown source languages receive generic syntax highlighting', () => {
  const highlighter = read('ui/src/js/syntax-highlight.js');

  assert.match(highlighter, /generic/);
  assert.match(highlighter, /keywordSets\[language\] \|\| keywordSets\.generic/);
  assert.match(highlighter, /token-plain/);
});

test('syntax highlighter decorates source and literal blocks at runtime', () => {
  const nodes = [
    { className: 'language-text', textContent: 'EXPLAIN SELECT 1;', innerHTML: '' },
    { className: '', textContent: 'plain output', innerHTML: '' },
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
  assert.match(nodes[1].innerHTML, /token-plain/);
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
  assert.match(frontMatter, /^\* Chương 14: Logging và Auditing/m);
  assert.match(frontMatter, /^\* Chương 19: Các công cụ và extension hữu ích/m);
});

test('playbook consumes the local UI bundle', () => {
  const playbook = read('playbook/antora-playbook.yml');

  assert.match(playbook, /ui:\n\s+bundle:\n\s+url: .*ui-bundle\.zip/);
  assert.doesNotMatch(playbook, /gitlab\.com\/antora\/antora-ui-default/);
});
