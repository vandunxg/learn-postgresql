'use strict';

module.exports = function () {
  var args = Array.prototype.slice.call(arguments);
  var options = args.pop();
  if (args.length === 2) return args[0] || args[1];
  return args.some(Boolean);
};
