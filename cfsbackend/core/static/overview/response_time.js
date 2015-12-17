"use strict";

var url = "/api/response_time/";

var dashboard = new Page({
    el: $('#dashboard').get(),
    template: "#dashboard-template",
    data: {
        'capitalize': function (string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
        },
        data: {}
    },
    filterUpdated: function (filter) {
        d3.json(buildURL(url, filter), _.bind(function (error, newData) {
            if (error) throw error;
            this.set('loading', false);
            this.set('initialload', false);
            newData = cleanupData(newData);
            this.set('data', newData);
        }, this));
    }
});

function cleanupData(data) {
    data.map_data = _.reduce(
        data.officer_response_time_by_beat, function (memo, d) {
            memo[d.name] = d.mean;
            return memo
        }, {});

    data.officer_response_time_by_priority =
        _.chain(data.officer_response_time_by_priority)
            .filter(function (d) {
                return d.name;
            })
            .sortBy(function (d) {
                return d.name == "P" ? "0" : d.name;
            })
            .value();
    data.officer_response_time_by_priority =
        [{key: "Officer Response Time", values: data.officer_response_time_by_priority}];
    data.officer_response_time_by_source =
        [{
            key: "Officer Response Time",
            values: _.sortBy(data.officer_response_time_by_source, function (d) { return d.name; })
        }];

    return data;
}

var responseTimeMap = new DurhamMap({
    el: "#map",
    dashboard: dashboard,
    colorScheme: colorbrewer.Oranges,
    format: durationFormat,
    dataDescr: "Officer Response Time"
});

var ortBySourceChart = new DiscreteBarChart({
    dashboard: dashboard,
    el: '#ort-by-source',
    filter: 'call_source',
    fmt: durationFormat,
    rotateLabels: true,
    x: function (d) { return d.name },
    y: function (d) { return Math.round(d.mean) },
    colors: ["#f16913"]
});

var ortByPriorityChart = new DiscreteBarChart({
    dashboard: dashboard,
    el: '#ort-by-priority',
    filter: 'priority',
    fmt: durationFormat,
    x: function (d) { return d.name },
    y: function (d) { return Math.round(d.mean) },
    colors: ["#f16913"]
});

monitorChart(dashboard, 'data.officer_response_time', buildORTChart);
monitorChart(dashboard, 'data.officer_response_time_by_source', ortBySourceChart.update);
monitorChart(dashboard, 'data.officer_response_time_by_priority', ortByPriorityChart.update);
monitorChart(dashboard, 'data.map_data', responseTimeMap.update);

// ========================================================================
// Functions
// ========================================================================


function getORTChartBounds() {
    var parent = d3.select("#ort"),
        parentWidth = parent.node().clientWidth,
        ratio = 5 / 1,
        width = parentWidth,
        height = width / ratio;

    return {width: width, height: height};
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
        , colors = ['#fd8d3c', '#f16913', '#d94801', '#8c2d04']
        ;

    var svg = d3.select("#ort").select("svg");
    var g;

    if (svg.size() === 0) {
        g = d3.select("#ort")
            .append("svg")
            .classed("nvd3-svg", true)
            .attr("width", bounds.width)
            .attr("height", bounds.height)
            .attr("viewBox", "0 0 " + bounds.width + " " + bounds.height)
            .append("g")
            .classed({"nvd3": true, "nv-boxPlotWithAxes": true})
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    } else {
        g = svg.select("g");
    }

    if (_.isEmpty(data)) {
        g.selectAll("g.nv-boxplot").remove();

        var noDataText = g.selectAll('.nv-noData').data(["No Data Available."]);

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

        g
            .on('mouseover', null)
            .on('mouseout', null)
            .on('mousemove', null);

        return;
    } else {
        g.selectAll('.nv-noData').remove();
    }

    var domainMax = Math.max(3600, Math.min(data.max, data.quartiles[2] + 3 * data.iqr));

    var xScale = d3.scale.linear()
        .domain([0, domainMax])
        .range([0, width]);

    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .tickFormat(durationFormat);

    // NOTE: This should not have to be done, but without it, the chart does
    // not update. TODO investigate.
    g.selectAll("g.nv-boxplot").remove();

    var boxplot = g.selectAll("g.nv-boxplot").data([data]);

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
            return xScale(Math.max(0, d.quartiles[0] - d.iqr * 1.5))
        })
        .attr("x2", function (d) {
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

    g
        .on('mouseover', function (d, i) {
            tooltip.data(tooltipData(d, i)).hidden(false);
        })
        .on('mouseout', function (d, i) {
            tooltip.data(tooltipData(d, i)).hidden(true);
        })
        .on('mousemove', function () {
            tooltip();
        })

    function resize() {
        var bounds = getORTChartBounds();

        svg.attr("width", bounds.width)
            .attr("height", bounds.height);

        boxplot.selectAll("g.nv-x.nv-axis").call(xAxis);
    }

    d3.select(window).on('resize.ort', resize);
}
