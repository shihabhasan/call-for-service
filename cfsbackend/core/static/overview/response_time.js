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
    template: "#dashboard-template",
    data: {
        'capitalize': function (string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
        },
        data: {}
    },
    filterUpdated: function (filter) {
        d3.json(buildURL(filter), _.bind(function (error, newData) {
            if (error) throw error;
            this.set('loading', false);
            this.set('initialload', false);
            newData = cleanupData(newData);
            this.set('data', newData);
        }, this));
    }
});

function cleanupData(data) {
    console.log(data.officer_response_time_by_beat);
    data.officer_response_time_by_beat =
        _.chain(data.officer_response_time_by_beat)
        .filter(function (d) {
            return d.name;
        })
        .sortBy(function (d) {
            return d.name;
        })
        .value();

    data.officer_response_time_by_priority =
        _.chain(data.officer_response_time_by_priority)
        .filter(function (d) {
            return d.name;
        })
        .sortBy(function (d) {
            return d.name == "P" ? "0" : d.name;
        })
        .value();

    return data;
}

function monitorChart(keypath, fn) {
    dashboard.observe(keypath, function (newData) {
        if (!dashboard.get('loading')) {
            // If we don't remove the tooltips before updating
            // the chart, they'll stick around
            d3.selectAll(".nvtooltip").remove();

            fn(newData);
        }
    })
}

//monitorChart('data.officer_response_time', buildORTChart);
monitorChart('data.officer_response_time_by_source', buildORTBySourceChart);
monitorChart('data.officer_response_time_by_beat', buildORTByBeatChart);
monitorChart('data.officer_response_time_by_priority', buildORTByPriorityChart);

// ========================================================================
// Functions
// ========================================================================

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}


function buildORTBySourceChart(data) {
    var parentWidth = d3.select("#ort-by-source").node().clientWidth;
    var width = parentWidth;
    var height = width * 0.8;

    var svg = d3.select("#ort-by-source svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.discreteBarChart()
            .x(function (d) {
                return d.name
            })
            .y(function (d) {
                return Math.round(d.mean);
            })
            .margin({"bottom": 150, "right": 50});

        chart.yAxis.tickFormat(function (secs) {
            return d3.format("d")(Math.round(secs / 60)) + ":" +
                d3.format("02d")(Math.round(secs % 60));
        });

        svg.datum([{key: "Officer Response Time", values: data}]).call(chart);

        //svg.selectAll('.nv-bar').style('cursor', 'pointer');
        //
        //chart.discretebar.dispatch.on('elementClick', function (e) {
        //    if (e.data.id) {
        //        toggleFilter("nature", e.data.id);
        //    }
        //});

        // Have to call this both during creation and after updating the chart
        // when the window is resized.
        var rotateLabels = function () {
            var xTicks = d3.select('#ort-by-source .nv-x.nv-axis > g').selectAll('g');

            xTicks.selectAll('text')
                .style("text-anchor", "start")
                .attr("dx", "0.25em")
                .attr("dy", "0.75em")
                .attr("transform", "rotate(45 0,0)");
        };

        rotateLabels();

        nv.utils.windowResize(function () {
            chart.update();
            rotateLabels();
        });

        return chart;
    })
}

function buildORTByBeatChart(data) {
    var parentWidth = d3.select("#ort-by-beat").node().clientWidth;
    var width = parentWidth;
    var height = width * 0.8;

    var svg = d3.select("#ort-by-beat svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.discreteBarChart()
            .x(function (d) {
                return d.name
            })
            .y(function (d) {
                return Math.round(d.mean);
            })
            .margin({"bottom": 150, "right": 50});

        chart.yAxis.tickFormat(function (secs) {
            return d3.format("d")(Math.round(secs / 60)) + ":" +
                d3.format("02d")(Math.round(secs % 60));
        });

        svg.datum([{key: "Officer Response Time", values: data}]).call(chart);


        // Have to call this both during creation and after updating the chart
        // when the window is resized.
        var rotateLabels = function () {
            var xTicks = d3.select('#ort-by-beat .nv-x.nv-axis > g').selectAll('g');

            xTicks.selectAll('text')
                .style("text-anchor", "start")
                .attr("dx", "0.25em")
                .attr("dy", "0.75em")
                .attr("transform", "rotate(45 0,0)");
        };

        rotateLabels();

        nv.utils.windowResize(function () {
            chart.update();
            rotateLabels();
        });

        return chart;
    })
}


function buildORTByPriorityChart(data) {
    var parentWidth = d3.select("#ort-by-priority").node().clientWidth;
    var width = parentWidth;
    var height = width * 1.2;

    var svg = d3.select("#ort-by-priority svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.discreteBarChart()
            .x(function (d) {
                return d.name
            })
            .y(function (d) {
                return Math.round(d.mean);
            })
            ;

        chart.yAxis.tickFormat(function (secs) {
            return d3.format("d")(Math.round(secs / 60)) + ":" +
                d3.format("02d")(Math.round(secs % 60));
        });

        svg.datum([{key: "Officer Response Time", values: data}]).call(chart);

        nv.utils.windowResize(function () {
            chart.update();
        });

        return chart;
    })
}