'use strict';

var path = require('path').posix;

module.exports = function (to, from, context) {
  if (!to) return '#';
  if (to.charAt(0) !== '/') return to;
  if (!context) {
    context = from;
    from = context.data.root.page.url;
  }
  if (!from) return (context.data.root.site.path || '') + to;

  var hash = '';
  var hashIndex = to.indexOf('#');
  if (hashIndex >= 0) {
    hash = to.slice(hashIndex);
    to = to.slice(0, hashIndex);
  }
  if (to === from) return hash || (isDirectory(to) ? './' : path.basename(to));

  var relative = path.relative(path.dirname(from + '.'), to);
  return relative
    ? (isDirectory(to) ? relative + '/' : relative) + hash
    : (isDirectory(to) ? './' : '../' + path.basename(to)) + hash;
};

function isDirectory (value) {
  return value.charAt(value.length - 1) === '/';
}
