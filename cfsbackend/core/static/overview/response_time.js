"use strict";

var url = "/api/response_time/";
var charts = {};

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

function cloneFilter() {
    return _.clone(dashboard.findComponent('Filter').get('filter'));
}

function toggleFilter(key, value) {
    var f = cloneFilter();
    if (f[key] == value) {
        delete f[key];
    } else {
        f[key] = value;
    }
    updateHash(buildQueryParams(f));
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

monitorChart('data.officer_response_time', buildORTChart);
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

        svg.selectAll('.nv-bar').style('cursor', 'pointer');

        chart.discretebar.dispatch.on('elementClick', function (e) {
            if (e.data.id) {
                toggleFilter("call_source", e.data.id);
            }
        });

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

        svg.selectAll('.nv-bar').style('cursor', 'pointer');

        chart.discretebar.dispatch.on('elementClick', function (e) {
            if (e.data.id) {
                toggleFilter("beat", e.data.id);
            }
        });

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

        chart.yAxis.tickFormat(durationFormat);

        svg.datum([{key: "Officer Response Time", values: data}]).call(chart);

        svg.selectAll('.nv-bar').style('cursor', 'pointer');

        chart.discretebar.dispatch.on('elementClick', function (e) {
            if (e.data.id) {
                toggleFilter("priority", e.data.id);
            }
        });

        nv.utils.windowResize(function () {
            chart.update();
        });

        return chart;
    })
}

function getORTChartBounds() {
    var parent = d3.select("#ort"),
        parentWidth = parent.node().clientWidth,
        ratio = 5 / 1,
        width = parentWidth,
        height = width / ratio;

    return {width: width, height: height};
}

function resizeORTChart() {
    var bounds = getORTChartBounds(),
        svg = d3.select("#ort").select("svg");

    svg.attr("width", bounds.width)
       .attr("height", bounds.height);
}

function buildORTChart(data) {
    var margin = {top: 0, left: 15, right: 15, bottom: 40}
        , bounds = getORTChartBounds()
        , width = bounds.width - margin.left - margin.right
        , height = bounds.height - margin.top - margin.bottom
        , boxtop = margin.top + 10
        , boxbottom = height - 10
        , tickHeight = (boxbottom - boxtop) * 0.7
        , tickTop = height / 2 - tickHeight / 2
        , center = boxtop + (boxbottom - boxtop) / 2
        , tooltip = nv.models.tooltip()
        , colors = ['#fcae91', '#fb6a4a', '#de2d26', '#a50f15']
        ;

    var svg = d3.select("#ort").select("svg");

    if (svg.size() === 0) {
        svg = d3.select("#ort")
            .append("svg")
            .classed("nvd3-svg", true)
            .attr("width", bounds.width)
            .attr("height", bounds.height)
            .attr("viewBox", "0 0 " + bounds.width + " " + bounds.height)
            .append("g")
            .classed({"nvd3": true, "nv-boxPlotWithAxes": true})
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    } else {
        svg = svg.select("g");
    }

    if (_.isEmpty(data)) {
        svg.selectAll("g.nv-boxplot").remove();

        var noDataText = svg.selectAll('.nv-noData').data(["No Data Available."]);

        noDataText.enter().append('text')
            .attr('class', 'nvd3 nv-noData')
            .attr('dy', '-.7em')
            .style('text-anchor', 'middle');

        noDataText
            .attr('x', margin.left + width / 2)
            .attr('y', margin.top + height / 2)
            .text(function (d) {
                return d
            });

        svg
            .on('mouseover', null)
            .on('mouseout', null)
            .on('mousemove', null);

        return;
    } else {
        svg.selectAll('.nv-noData').remove();
    }

    var domainMax = Math.min(data.max, data.quartiles[2] + 3 * data.iqr);

    var xScale = d3.scale.linear()
        .domain([0, domainMax])
        .range([0, width]);

    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .tickFormat(durationFormat);

    // NOTE: This should not have to be done, but without it, the chart does
    // not update. TODO investigate.
    svg.selectAll("g.nv-boxplot").remove();

    var boxplot = svg.selectAll("g.nv-boxplot").data([data]);

    boxplot.exit().remove();

    var boxplotEnter = boxplot.enter()
        .append("g")
        .classed("nv-boxplot", true);

    boxplotEnter.append("line")
        .attr("y1", center)
        .attr("y2", center)
        .classed({"nv-boxplot-whisker": true, "whisker-left": true});

    boxplotEnter.append("line")
        .attr("y1", tickTop)
        .attr("y2", tickTop + tickHeight)
        .classed({"nv-boxplot-tick": true, "tick-left": true});

    boxplotEnter.append("line")
        .attr("y1", center)
        .attr("y2", center)
        .classed({"nv-boxplot-whisker": true, "whisker-right": true});

    boxplotEnter.append("line")
        .attr("y1", tickTop)
        .attr("y2", tickTop + tickHeight)
        .classed({"nv-boxplot-tick": true, "tick-right": true});

    boxplotEnter.append("rect")
        .attr("y", boxtop)
        .attr("height", boxbottom - boxtop)
        .classed({"nv-boxplot-box": true, "box-left": true});

    boxplotEnter.append("rect")
        .attr("y", boxtop)
        .attr("height", boxbottom - boxtop)
        .classed({"nv-boxplot-box": true, "box-right": true});

    boxplotEnter.append("line")
        .attr("y1", boxtop)
        .attr("y2", boxbottom)
        .classed({"nv-boxplot-median": true});

    boxplotEnter.append("g")
        .classed({"nv-x": true, "nv-axis": true})
        .attr("transform", "translate(0, " + (height) + ")");

    boxplot.selectAll("g.nv-x.nv-axis").call(xAxis);

    boxplot.selectAll("line.whisker-left")
        .attr("x1", function (d) {
            console.log("hi");
            console.log(d);
            console.log(xScale(Math.max(0, d.quartiles[0] - d.iqr * 1.5)))
            return xScale(Math.max(0, d.quartiles[0] - d.iqr * 1.5))
        })
        .attr("x2", function (d) {
            console.log("hi");
            console.log(d);
            console.log(d.quartiles[0])
            return xScale(d.quartiles[0])
        })
        .style({"stroke": colors[0], "stroke-width": 3});

    boxplot.selectAll("line.tick-left")
        .attr("x1", function (d) {
            return xScale(Math.max(0, d.quartiles[0] - d.iqr * 1.5))
        })
        .attr("x2", function (d) {
            return xScale(Math.max(0, d.quartiles[0] - d.iqr * 1.5))
        })
        .style({"stroke": colors[0], "stroke-width": 3});

    boxplot.selectAll("line.whisker-right")
        .attr("x1", function (d) {
            return xScale(d.quartiles[2])
        })
        .attr("x2", function (d) {
            return xScale(Math.min(domainMax, d.quartiles[2] + d.iqr * 1.5))
        })
        .style({"stroke": colors[3], "stroke-width": 3});

    boxplot.selectAll("line.tick-right")
        .attr("x1", function (d) {
            return xScale(Math.min(domainMax, d.quartiles[2] + d.iqr * 1.5))
        })
        .attr("x2", function (d) {
            return xScale(Math.min(domainMax, d.quartiles[2] + d.iqr * 1.5))
        })
        .style({"stroke": colors[3], "stroke-width": 3});

    boxplot.selectAll("rect.box-left")
        .attr("x", function (d) {
            return xScale(d.quartiles[0])
        })
        .attr("width", function (d) {
            return xScale(d.quartiles[1] - d.quartiles[0])
        })
        .style({"stroke": colors[1], "fill": colors[1]});

    boxplot.selectAll("rect.box-right")
        .attr("x", function (d) {
            return xScale(d.quartiles[1])
        })
        .attr("width", function (d) {
            return xScale(d.quartiles[2] - d.quartiles[1])
        })
        .style({"stroke": colors[2], "fill": colors[2]});

    boxplot.selectAll("line.nv-boxplot-median")
        .attr("x1", function (d) {
            return xScale(d.quartiles[1])
        })
        .attr("x2", function (d) {
            return xScale(d.quartiles[1])
        })
        .style({"stroke-width": 3})

    var tooltipData = function (d, i) {
        return {
            key: "Officer Response Time",
            value: "Officer Response Time",
            series: [
                {
                    key: '25%',
                    value: durationFormat(data.quartiles[0]),
                    color: colors[0]
                },
                {
                    key: '50%',
                    value: durationFormat(data.quartiles[1]),
                    color: colors[1]
                },
                {
                    key: '75%',
                    value: durationFormat(data.quartiles[2]),
                    color: colors[2]
                },
                {key: 'Max', value: durationFormat(data.max), color: colors[3]}
            ],
            data: d,
            index: i,
            e: d3.event
        }
    }

    svg
        .on('mouseover', function (d, i) {
            tooltip.data(tooltipData(d, i)).hidden(false);
        })
        .on('mouseout', function (d, i) {
            tooltip.data(tooltipData(d, i)).hidden(true);
        })
        .on('mousemove', function () {
            tooltip();
        })

}

d3.select(window).on('resize', function () {
    resizeORTChart();
})