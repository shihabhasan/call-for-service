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

var calls = new Ractive({
    el: document.getElementById("calls"),
    template: "#calls-template",
    components: {'Filter': Filter},
    data: {
        loading: true,
        timeFormat: function (t) {
            if (t) {
                var time = timeParser.parse(t);
                return timeFormatter(time);
            } else {
                return "-";
            }
        },
        d: function (x) { return x ? x : "-"; },
        perPage: 20,
        page: 1,
        data: {
            data: {}
        }
    },
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]']
});

calls.on('Filter.filterUpdated', loadNewData);

calls.observe('page', function (newPage) {
    var filter = calls.findComponent('Filter');
    filter.fire('filterUpdated');
});

function loadNewData(filter) {
    var page = calls.get('page');
    var perPage = calls.get('perPage');
    var offset = (page - 1) * perPage;
    var limit = perPage;
    var paginatingFilter = _.clone(filter);
    if (paginatingFilter) {
        paginatingFilter.limit = limit;
        paginatingFilter.offset = offset;
        d3.json(buildURL(paginatingFilter), function (error, newData) {
            if (error) throw error;
            calls.set('loading', false);
            calls.set('data', newData);
        });
    }
}

// ========================================================================
// Functions
// ========================================================================

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}

