require("../css/main.css");

var d3 = require('d3');
var _ = require('underscore');
var moment = require('moment');

var filter = {};
var url = "/api/summary/";

function makeParams(obj) {
    var str = "";
    for (var key in obj) {
        if (str != "") {
            str += "&";
        }
        str += key + "=" + encodeURIComponent(obj[key]);
    }
    return str;
}

function drawRowBarChart(id, selection, data, colors, clickFn, textFn, titleFn) {
    if (textFn === undefined) {
        textFn = function (d) { return d.key; };
    }

    if (titleFn === undefined) {
        titleFn = function (d) { return d.value; }
    }

    data = _.chain(data)
        .pairs()
        .map(function (d) { return { key: d[0], value: d[1] }})
        .value();

    var width = 300;
    var height = 40 * data.length;
    var margin = {top: 10, left: 10, right: 10, bottom: 30}

    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.ordinal()
        .rangeRoundBands([0, height], .2);

    x.domain([0, d3.max(data, function (d) { return d.value })]).nice();
    y.domain(data.map(function (d) { return d.key }));

    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks(5)
        .tickFormat(d3.format(".2s"))
        .orient("bottom");

    var svg;

    if (d3.select("#" + id).empty()) {
        svg = selection
            .append("svg")
            .attr("id", id)
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g");

        svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + (height + 5) + ")")
            .attr("width", width)
            .attr("height", 20)
            .classed({"x": true, "axis": true});
    } else {
        svg = d3.select("#" + id).select("g")
            .attr("height", height + margin.top + margin.bottom);
    }

    var g = svg.selectAll(".bar")
        .data(data);

    g.select("rect")
        .transition()
        .attr("width", function(d) { return x(d.value); });

    g.select("text").text(textFn);
    g.select("title").text(titleFn);

    var enter = g.enter()
        .append("g")
        .attr("transform", function (d) { 
            return "translate(" + margin.left + ", " + (y(d.key) + margin.top) + ")" 
        })
        .classed("bar", true)
        .on("click", clickFn);

    enter.append("rect")
        .attr("fill", function (d) { return colors(d.key) })
        .attr("width", function(d) { return x(d.value); })
        .attr("height", y.rangeBand());

    enter.append("text")
        .attr("x", 10)
        .attr("y", 20)
        .text(textFn);

    enter.append("title")
        .text(titleFn);

    g.exit().remove();

    svg.select(".x.axis")
        .attr("transform", "translate(" + margin.left + "," + (height + 5) + ")")
        .call(xAxis);
}

function drawColBarChart(id, selection, data, colors, clickFn, textFn, titleFn) {
    var height = 450;

    if (textFn === undefined) {
        textFn = function (d) { return d.key; };
    }

    if (titleFn === undefined) {
        titleFn = function (d) { return d.value; }
    }

    data = _.chain(data)
        .pairs()
        .map(function (d) { return { key: d[0], value: d[1] }})
        .value();

    width = 30 * data.length;

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], .2);

    var y = d3.scale.linear()
        .range([0, height]);

    x.domain(data.map(function (d) { return d.key }));
    y.domain([0, d3.max(data, function (d) { return +d.value })]).nice();

    var svg;

    if (d3.select("#" + id).empty()) {
        svg = selection
            .append("svg")
            .attr("id", id)
            .attr("width", width)
            .attr("height", height)
            .append("g");
    } else {
        svg = d3.select("#" + id).select("g");
    }

    svg.selectAll(".bar").remove();

   var g = svg.selectAll(".bar")
        .data(data);

    g.select("rect")
        .transition()
        .attr("height", function(d) { return y(d.value); });

    g.select("text").text(textFn);
    g.select("title").text(titleFn);

    var enter = g.enter()
        .append("g")
        .attr("transform", function (d) { return "translate(" + x(d.key) + "," + (height - y(+d.value)) + ")" })
        .classed("bar", true)
        .on("click", clickFn);

    enter.append("rect")
        .attr("fill", function (d) { return colors(d.key) })
        .attr("height", function(d) { return y(d.value); })
        .attr("width", x.rangeBand());

    enter.append("text")
        .attr("x", function (d) { return -y(d.value) })
        .attr("y", 15)
        .attr("transform", "rotate(-90)")
        .text(textFn);

    enter.append("title")
        .text(titleFn);
}

function drawAllCharts(error, data) {
    drawRowBarChart("dow-chart",
        d3.select("#dc-call-dow-chart"),
        data.dow,
        d3.scale.category10(),
        function (d) {
            if (filter["dow_received"] == d.key) {
                delete filter["dow_received"];
            } else {
                filter["dow_received"] = d.key;
            }
            d3.json(url + "?" + makeParams(filter), drawAllCharts)
        },
        function (d) {
            return moment().day(+d.key).format("ddd") + " - " + d.value;
        }
    )

    drawRowBarChart("hour-chart",
        d3.select("#dc-call-hour-chart"),
        data.hour,
        d3.scale.category20(),
        function (d) {
            if (filter["hour_received"] == d.key) {
                delete filter["hour_received"];
            } else {
                filter["hour_received"] = d.key;
            }
            d3.json(url + "?" + makeParams(filter), drawAllCharts)
        },
        function (d) {
            return moment().hour(+d.key).format("ha") + " - " + d.value;
        }
    )

    drawRowBarChart("month-chart",
        d3.select("#dc-call-month-chart"),
        data.month,
        d3.scale.category20c(),
        function (d) {
            if (filter["month_received"] == d.key) {
                delete filter["month_received"];
            } else {
                filter["month_received"] = d.key;
            }
            d3.json(url + "?" + makeParams(filter), drawAllCharts)
        },
        function (d) {
            return moment().month(+d.key - 1).date(1).format("MMM") + " - " + d.value;
        }
    )

    drawRowBarChart("source-chart",
        d3.select("#dc-call-source-chart"),
        data.source,
        d3.scale.category20(),
        function (d) {},
        function (d) {
            return d.key + " - " + d.value;
        }
    )

    drawRowBarChart("nature-chart",
        d3.select("#dc-call-nature-chart"),
        data.nature,
        d3.scale.category20(),
        function (d) {},
        function (d) {
            return d.key + " - " + d.value;
        }
    )
}

d3.json(url, drawAllCharts);
