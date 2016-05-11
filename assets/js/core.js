import "../dashboard/toolkit-light.css";
import "font-awesome/css/font-awesome.css";
import "bootstrap-daterangepicker/daterangepicker.css";
import "../styles/core.scss";

import "./polyfills";
import "../dashboard/toolkit";
import "bootstrap-daterangepicker";

import Ractive from "ractive";
import _ from "underscore";
import $ from "jquery";

import moment from "moment";
import d3 from "d3";

Ractive.DEBUG = /unminified/.test(function() { /*unminified*/ });

var helpers = Ractive.defaults.data;

helpers.formatCount = function (number, singular, plural) {
  if (!plural) {
    plural = singular + "s";
  }
  if (number) {
    var retval = d3.format(",d")(number) + " ";
    retval += (number === 1) ? singular : plural;
    return retval;
  }
}

var NavBar = Ractive.extend({
  template: require("../templates/navbar.html")
});

var ChartHeader = Ractive.extend({
  template: require("../templates/chart_header.html"),
  isolated: true,
  data: {
    hidden: true
  },
  oninit: function() {
    this.on("toggleExplanation", function() {
      this.set("hidden", !this.get("hidden"));
    });
  }
});

var FilterButton = Ractive.extend({
  template: require("../templates/filter_button.html"),
  computed: {
    fieldType: function() {
      return this.get("getFieldType")(this.get("field")).type;
    }
  },
  oninit: function() {
    this.on("addfilter", function(event, key, value) {
      var filter = this.get("filter");

      filter = _.clone(filter);
      filter[key] = value;

      updateHash(buildQueryParams(filter));
    });

    this.on("removefilter", function(event, key) {
      updateHash(buildQueryParams(_.omit(this.get("filter"), key)));
    });
  },
  oncomplete: function() {
    var field = this.get("field");
    var self = this;

    if (this.get("fieldType") === "daterange") {
      var $button = $("#button_" + field);
      var value = this.get("filterValue")(field, this.get("filter"));
      var pastSunday = getLastSunday();

      // todo set up ranges
      var ranges = {
        "Last 7 Days": [
          pastSunday.clone().subtract(7, "days").format("YYYY-MM-DD"),
          pastSunday.clone().subtract(1, "days").format("YYYY-MM-DD")
        ],
        "Last 28 Days": [
          pastSunday.clone().subtract(28, "days").format("YYYY-MM-DD"),
          pastSunday.clone().subtract(1, "days").format("YYYY-MM-DD")
        ],
        "Year to Date": [
          moment().clone().startOf("year").format("YYYY-MM-DD"),
          moment()
        ]
      };

      var options = {
        locale: {
          format: "YYYY-MM-DD",
          cancelLabel: "Clear"
        },
        ranges: ranges,
        cancelClass: "btn-danger"
      };
      if (value) {
        options.startDate = value.gte;
        options.endDate = value.lte;
      }

      $button.daterangepicker(options);

      $button.on("apply.daterangepicker", function(event, picker) {
        var filter = self.get("filter");

        filter = _.clone(filter);

        var dates = {
          gte: picker.startDate.format("YYYY-MM-DD"),
          lte: picker.endDate.format("YYYY-MM-DD")
        };

        filter[field] = dates;
        updateHash(buildQueryParams(filter));
      });

      $button.on("cancel.daterangepicker", function() {
        var filter = self.get("filter");
        filter = _.clone(filter);
        filter = _.omit(filter, field);
        updateHash(buildQueryParams(filter));
      });
    }
  }
});

export var Filter = Ractive.extend({
  components: {
    "filter-button": FilterButton
  },
  template: require("../templates/filter.html"),
  data: function() {
    return {
      filter: {},
      displayName: displayName,
      getFieldType: function(fieldName) {
        var field = findField(fieldName);
        if (field.rel !== undefined) {
          return {
            type: "select",
            options: filterForm.refs[field.rel]
          };
        } else if (field.type === "select") {
          return {
            type: field.type,
            options: field.options
          };
        } else {
          return {
            type: field.type
          };
        }
      },
      buttonClass: function(field, filter) {
        if (filterValue(field, filter)) {
          return "btn-success";
        } else {
          return "btn-primary";
        }
      },
      filterValue: filterValue,
      displayValue: displayValue
    };
  },
  computed: {
    filterHash: function() {
      return "#!" + buildQueryParams(this.get("filter"));
    },
    fields: function() {
      return filterForm.fields;
    }
  },
  oninit: function() {
    var component = this;

    function updateFilter() {
      var newFilter = {};
      if (window.location.hash) {
        newFilter = parseQueryParams(window.location.hash.slice(1));
      }

      // Time field for the call volume and response time pages
      if (!newFilter['time_received']) {
        newFilter['time_received'] = {
          "gte": getLastSunday().subtract(28, "days").format("YYYY-MM-DD"),
          "lte": getLastSunday().subtract(1, "days").format("YYYY-MM-DD"),
        }
      }
      // Time field for the officer allocation page
      if (!newFilter['time']) {
        newFilter['time'] = {
          "gte": getLastSunday().subtract(28, "days").format("YYYY-MM-DD"),
          "lte": getLastSunday().subtract(1, "days").format("YYYY-MM-DD"),
        }
      }

      component.set("filter", newFilter);
    }

    updateFilter();
    $(window).on("hashchange", updateFilter);
  },
  oncomplete: function() {
    this.observe("filter", function(filter) {
      this.fire("filterUpdated", filter);
    });
  }
});

var LoadingIndicator = Ractive.extend({
  template: require("../templates/loading.html"),
  isolated: true
});

export var Page = Ractive.extend({
  components: {
    "Filter": Filter,
    "NavBar": NavBar,
    "chart-header": ChartHeader,
    "LoadingIndicator": LoadingIndicator
  },
  data: {
    filterHash: "",
    queryParams: "",
    initialload: true,
    loading: true
  },
  oninit: function() {
    this.on("Filter.filterUpdated", _.bind(function(filter) {
      this.set("loading", true);
      this.set("filterHash", this.findComponent("Filter").get("filterHash"));
      this.set("queryParams", buildQueryParams(this.findComponent("Filter").get("filter")));
      this.filterUpdated(filter);
    }, this));
  }
});


// ========================================================================
// Functions
// ========================================================================

function getLastSunday() {
  return moment().day("Sunday").startOf("day");
}

function findField(fieldName) {
  return _(filterForm.fields).find(function(field) {
    return field.name == fieldName;
  });
}

function humanize(property) {
  return property.replace(/_/g, " ")
    .replace(/(\w+)/g, function(match) {
      return match.charAt(0).toUpperCase() + match.slice(1);
    });
}

function displayName(fieldName) {
  if (fieldName === undefined) {
    return;
  }
  return findField(fieldName).label || humanize(fieldName);
}

function arrayToObj(arr) {
  // Given an array of two-element arrays, turn it into an object.
  var obj = {};
  arr.forEach(function(x) {
    obj[x[0]] = x[1];
  });

  return obj;
}

function displayValue(fieldName, value) {
  if (fieldName === undefined) {
    return;
  }
  var field = findField(fieldName);
  var dValue;
  var choiceMap;

  if (field.rel) {
    choiceMap = arrayToObj(filterForm.refs[field.rel]);
    dValue = choiceMap[value];
  } else if (field.options) {
    choiceMap = arrayToObj(field.options);
    dValue = choiceMap[value];
  }

  if (field.type === "daterange" && typeof value == "object" && value["gte"] && value["lte"]) {
    dValue = value["gte"] + " to " + value["lte"];
  }

  if (!dValue) {
    dValue = value;
  }

  return dValue;
}

function filterValue(fieldName, filter) {
  return filter[fieldName];
}

export function buildQueryParams(obj, prefix) {
  if (typeof prefix === "undefined") {
    prefix = "";
  } else {
    prefix = prefix + "__";
  }
  var str = "";
  for (var key in obj) {
    if (str != "") {
      str += "&";
    }
    if (_.isObject(obj[key])) {
      str += buildQueryParams(obj[key], key);
    } else {
      str += prefix + key + "=" + encodeURIComponent(obj[key]);
    }
  }
  return str;
}

function nest(segments, value) {
  var retval = {};
  if (segments.length == 1) {
    retval[segments[0]] = value;
  } else {
    retval[segments[0]] = nest(segments.slice(1), value);
  }
  return retval;
}

function parseQueryParams(str) {
  var comparators = ["lte", "gte"];

  if (typeof str != "string") return {};
  if (str.charAt(0) === "!") {
    str = str.slice(1);
  }

  if (str.length == 0) return {};

  var s = str.split("&");
  var s_length = s.length;
  var bit,
    query = {},
    first,
    second,
    segments;
  for (var i = 0; i < s_length; i++) {
    bit = s[i].split("=");
    first = decodeURIComponent(bit[0]);
    if (first.length == 0) continue;
    second = decodeURIComponent(bit[1]);

    segments = first.split("__");

    if (segments.length > 1) {
      var lastSegment = segments[segments.length - 1];
      if (comparators.indexOf(lastSegment) != -1) {
        segments = [segments.slice(0, -1).join("__"), segments[segments.length - 1]];
      } else {
        segments = [segments.join("__")];
      }
    }

    if (segments.length == 1) {
      if (typeof query[first] == "undefined") {
        query[first] = second;
      } else if (query[first] instanceof Array) {
        query[first].push(second);
      } else {
        query[first] = [query[first], second];
      }
    } else {
      query = $.extend(true, {}, query, nest(segments, second));
    }
  }
  return query;
}

export function updateHash(newHash) {
  var scr = document.body.scrollTop;
  window.location.hash = "!" + newHash;
  document.body.scrollTop = scr;
}

export function monitorChart(ractive, keypath, fn) {
  ractive.observe(keypath, function(newData) {
    if (!ractive.get("loading")) {
      // If we don't remove the tooltips before updating
      // the chart, they'll stick around
      d3.selectAll(".nvtooltip").remove();

      fn(newData);
    }
  });
}

export function cloneFilter(ractive) {
  return _.clone(ractive.findComponent("Filter").get("filter"));
}

export function toggleFilter(ractive, key, value) {
  var f = cloneFilter(ractive);
  if (f[key] == value) {
    delete f[key];
  } else {
    f[key] = value;
  }
  updateHash(buildQueryParams(f));
}

export function buildURL(url, filter) {
  return url + "?" + buildQueryParams(filter);
}
