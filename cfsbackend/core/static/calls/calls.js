"use strict";

var url = "/api/calls/";

var outFormats = {
    "month": "%b %y",
    "week": "%m/%d/%y",
    "day": "%a %m/%d",
    "hour": "%m/%d %H:%M"
};

var timeFormatter = d3.time.format("%a %Y-%m-%d %H:%M");
var timeParser = d3.time.format("%Y-%m-%dT%H:%M:%S");

var calls = new Page({
    el: document.getElementById("calls"),
    template: "#calls-template",
    data: {
        timeFormat: function (t) {
            if (t) {
                var time = timeParser.parse(t);
                return timeFormatter(time);
            } else {
                return "-";
            }
        },
        d: function (x) {
            return x ? x : "-";
        },
        perPage: 20,
        page: 1,
        data: {
            data: {}
        }
    },
    filterUpdated: function (filter) {
        var page = this.get('page');
        var perPage = this.get('perPage');
        var offset = (page - 1) * perPage;
        var limit = perPage;
        var paginatingFilter = _.clone(filter);
        if (paginatingFilter) {
            paginatingFilter.limit = limit;
            paginatingFilter.offset = offset;
            this.set('loading', true);
            d3.json(buildURL(paginatingFilter), _.bind(function (error, newData) {
                if (error) throw error;
                this.set('loading', false);
                this.set('initialload', false)
                this.set('data', newData);
            }, this));
        }
    }
});

calls.observe('page', function (newPage) {
    var filter = calls.findComponent('Filter');
    filter.fire('filterUpdated');
});

// ========================================================================
// Functions
// ========================================================================

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}

