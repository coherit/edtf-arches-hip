// Hello.
//
// This is JSHint, a tool that helps to detect errors and potential
// problems in your JavaScript code.
//
// To start, simply enter some JavaScript anywhere on this page. Your
// report will appear on the right side.
//
// Additionally, you can toggle specific options in the Configure
// menu.

(function (exports) {
function uncertainOrApproximateParts(str) {
  var grouped, 
      affected, 
      results = [],
    	affectedGroups; 

  // Make a string where every ? or ~ marker applies to a group in parentheses
  grouped = str
    .replace(/(^|-)([0-9u\-]+)([?~])/g, '$1($2)$3')
    .replace(/~\?/g, '?~'); // Processing marks in ?, ~ order

  // Replace each part with T$index, to end up with, e.g.:
  // (T0-T1)?-T2 or (T0)?~-(T1-T2)~
  for (var i = 0; i < str.match(/[0-9u]+/g).length; i++) {
    grouped = grouped.replace(/(^|[^T])([0-9u]+)/, '$1T' + i);
    results[i] = {uncertain: false, approximate: false};
  }

  // This will give the indices of the sections affected by the leftmost
  // instance of the provided token.
  affectedGroups = function (token) {
    var tmpstr;
    tmpstr = grouped.slice(0, grouped.indexOf(')' + token) + 1);
    tmpstr = tmpstr.replace(/\((.*)\)/, '$1');
    return tmpstr.replace(/[^0-9]/g, '').split(/\B/);
  };

  // These two might be written better with recursion
  if (str.indexOf('?') >= 0) {
    for (var i = 0; i < str.match(/\?/g).length; i++) {
      affected = affectedGroups('?');
      for (var j = 0; j < affected.length; j++) {
        results[affected[j]].uncertain = true;
      }
      grouped = grouped.replace('?', '');
    }
  }

  if (str.indexOf('~') >= 0) {
    for (var i = 0; i < str.match(/~/g).length; i++) {
      affected = affectedGroups('~');
      for (var j = 0; j < affected.length; j++) {
        results[affected[j]].approximate = true;
      }
      grouped = grouped.replace('~', '');
    }
  }

  return results;
}

function validateSingleDate(dateString) {
  var verdict, 
      sepMarks = dateString.split(/([?~]*)$/),
      dateParts = sepMarks[0].split(/(?!^)-/),
      possiblyUnclearYear = /^-?[0-9]{0,2}(?:[0-9]{2}|[0-9]u|uu)$/,
      knownYear = /^-?(?:[0-9]{1,4}|y[0-9]{5,})$/,
      possiblyUnclear = /^(?:[0-9]{2}|uu)$/,
      year,
      month,
      day,
      time; // TODO

  switch (dateParts.length) {
  case 1:
    // Valid if this is only a year (possibly unclear).
    year = dateParts[0];
    verdict = possiblyUnclearYear.test(year) || knownYear.test(year);
    break;

  case 2:
    // Valid if this is a year (definitely known) and a month (possibly unclear)
    year = dateParts[0];
    month = dateParts[1];
    verdict = knownYear.test(year) && possiblyUnclear.test(month);
    if (/[0-9]/.test(month)) {
      verdict = verdict && (month >= 1 && month <= 12 || month >= 21 && month <= 24);
    }
    break;

  case 3:
    // Valid is this is a year (definitely known) and one of the following:
    // 1. Known month & possibly unclear day
    // 2. Unclear month & unclear day
    year = dateParts[0];
    month = dateParts[1];
    day = dateParts[2].split('T')[0];

    verdict = knownYear.test(year) && (
      (/^[0-9]{2}$/.test(month) && possiblyUnclear.test(day)) ||
      (/^uu$/.test(month) && /^uu$/.test(day))
    );

    if (/[0-9]/.test(month)) {
      verdict = (month >= 1 && month <= 12) && verdict;
    }
    if (/[0-9]/.test(day)) {
      verdict = (day >= 1 && day <= 31) && verdict;
    }
    break;

  default:
    verdict = false;
  }
  return !!verdict;
}

var validateEDTF = function (str) {
  var verdict, 
      intervals = str.split('/');
  
  switch (intervals.length) {
  case 1:
    verdict = validateSingleDate(intervals[0]);
    break;

  case 2:
    verdict = intervals[0].length && intervals[1].length &&
      ((validateSingleDate(intervals[0]) || /^unknown$/.test(intervals[0])) &&
       (validateSingleDate(intervals[1]) || /^(?:open|unknown)$/.test(intervals[1])));
    break;

  default:
    verdict = false;
  }

  return !!verdict;
};

exports.validateEDTF = validateEDTF;
var EDTFDate = function (data) {

  this.year = data.year ? '' + data.year : null;
  this.month = data.year ? zeroPadded(data.month) : null;
  this.day = data.year ? zeroPadded(data.day) : null;
  this.uncertain = !!data.uncertain;
  this.approximate = !!data.approximate;
  this.open = !!data.open;
  this.unknown = !!data.unknown;

  return this;
};

EDTFDate.prototype = {
  asEDTFString: function () {
    var s = '';

    if (this.open) return 'open';
    if (this.unknown) return 'unknown';

    s += this.year;
    if (this.month) s += '-' + this.month;
    if (this.day) s += '-' + this.day;
    if (this.uncertain) s += '?';
    if (this.approximate) s += '~';

    return s;
  },

  toString: function () {
    return this.asEDTFString();
  },

  toNativeDate: function () {
    var date = new Date(0);

    // js Date type can't represent these cases
    if (this.unknown || this.open) {
      return null;
    }
    if (this.year < -271820 || this.year > 275759) {
      return null;
    }
    if (this.year.indexOf('uu') >= 0) {
      return null;
    }

    date.setFullYear(this.year);

    switch (this.month) {

    // If month is not set or is 'uu', pretend it's January 1.
    case null:
    case 'uu':
      date.setMonth(0);
      date.setDate(1);
      break;

    // Assuming northern hemisphere for seasons.
    case 21:
      date.setMonth(2);
      date.setDate(22);
      break;
    case 22:
      date.setMonth(5);
      date.setDate(22);
      break;
    case 23:
      date.setMonth(8);
      date.setDate(22);
      break;
    case 24:
      date.setMonth(11);
      date.setDate(22);
      break;

    // Month is set; if day is not set or is 'uu', pretend it's the first.
    default:
      date.setMonth(parseInt(this.month, 10) - 1);
      if (this.day === null || this.day === 'uu') {
        date.setDate(1);
      } else {
        date.setDate(parseInt(this.day, 10));
      }
      break;
    }

    return date;
  }
};

function edtfObjFromString(string) {
  var tokens, 
      edtfObj = {};

  if (string === 'unknown') {
    return new EDTFDate({unknown: true});
  }
  if (string === 'open') {
    return new EDTFDate({open: true});
  }

  tokens = string
    .replace(/(?!^)-/g, ' ')
    .replace(/[?~]/g, ' $1')
    .split(' ');

  if (tokens.indexOf('?') >= 0) {
    edtfObj.uncertain = !!tokens.splice(tokens.indexOf('?'), 1)[0];
  }
  if (tokens.indexOf('~') >= 0) {
    edtfObj.approximate = !!tokens.splice(tokens.indexOf('~'), 1)[0];
  }

  edtfObj.year = tokens.splice(0, 1)[0];
  edtfObj.month = tokens.splice(0, 1)[0];
  edtfObj.day = tokens.splice(0, 1)[0];

  return new EDTFDate(edtfObj);
}
})(typeof(exports) === 'undefined' ? this.edtf = {} : exports);
