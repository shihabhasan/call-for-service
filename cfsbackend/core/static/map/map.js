"use strict";

var url = "/api/response_time/";
var charts = {};
var outFormats = {
    "month": "%b %y",
    "week": "%m/%d/%y",
    "day": "%a %m/%d",
    "hour": "%m/%d %H:%M"
};

var dashboard = new Page({
    el: $('body').get(),
    template: "#map-template",
    data: {
        data: {
            'volume_over_time': {
                'period_size': 'day',
                'results': []
            },
            'day_hour_heatmap': [],
            'volume_by_source': {}
        }
    },
    filterUpdated: function (filter) {
        this.set('loading', false);
        this.set('initialload', false);
        //d3.json(buildURL(filter), _.bind(function (error, newData) {
        //    if (error) throw error;
        //    this.set('loading', false);
        //    this.set('initialload', false);
        //    //newData = cleanupData(newData);
        //    //this.set('data', newData);
        //}, this));
    }
});

// ========================================================================
// Functions
// ========================================================================

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}

var width = 800;
var height = 800;

var projection = d3.geo.conicConformal()
.scale(1)
    .translate([0, 0]);

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("#map")
    .attr("width", 800)
    .attr("height", 800)
    .append("g");

d3.json("/static/map/beats3.json", function (json) {
    // Compute the bounds of a feature of interest, then derive scale & translate.
    var b = path.bounds(json),
        s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
        t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

    // Update the projection to use computed scale & translate.
    projection
        .scale(s)
        .translate(t);

    svg.selectAll("path")
        .data(json.features)
        .enter()
        .append("path")
        .attr("d", path)
        .style("fill", "blue")
        .style("stroke", "black")
        .style("stroke-width", 2)
});
