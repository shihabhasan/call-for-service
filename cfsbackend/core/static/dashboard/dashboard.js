"use strict";

var url = "/api/overview/";
var charts = {};
var outFormats = {
    "month": "%b %y",
    "week": "%m/%d/%y",
    "day": "%a %m/%d",
    "hour": "%m/%d %H:%M"
};

var dashboard = new Ractive({
    el: document.getElementById("dashboard"),
    template: "#dashboard-template",
    components: {'Filter': Filter},
    data: {
        'capitalize': function (string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
        },
        loading: true,
        data: {
            'volume_over_time': {
                'period_size': 'day',
                'results': []
            },
            'day_hour_heatmap': [],
            'volume_by_source': {}
        }
    },
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]']
});

dashboard.on('Filter.filterUpdated', function (filter) {
    d3.json(buildURL(filter), function (error, newData) {
        if (error) throw error;
        dashboard.set('loading', false);
        newData = cleanupData(newData);
        dashboard.set('data', newData);
    });
});

function cleanupData(data) {
    var natureCols = 30;
    var volumeByNature = _(data.volume_by_nature).sortBy('volume').reverse();

    volumeByNature = _.first(volumeByNature, natureCols - 1).concat(
        _.chain(volumeByNature)
            .rest(natureCols - 1)
            .reduce(function (total, cur) {
                return {name: "ALL OTHER", volume: total.volume + cur.volume}
            }, {name: "ALL OTHER", volume: 0})
            .value()
    );

    data.volume_by_nature = volumeByNature;

    var volumeByDate = _.chain(data.volume_by_date)
        .sortBy('date')
        .map(function (d) {
            return [
                {date: d.date, volume: d.volume, type: "Daily Volume"},
                {date: d.date, volume: d.average, type: "30-Day Moving Average"}
            ]
        })
        .flatten()
        .value();

    data.volume_by_date = volumeByDate;

    _(data.volume_by_source).each(function (d) {
        d.source = d.self_initiated ? "Self Initiated" : "Citizen Initiated";
    });

    return data;
}

dashboard.observe('data.day_hour_heatmap', function (newData) {
    if (!dashboard.get('loading')) {
        charts.dayHourHeatmap = buildDayHourHeatmap(newData);
    }
});

function monitorChart(keypath, chartName, buildFn) {
    dashboard.observe(keypath, function (newData) {
        if (!dashboard.get('loading')) {
            if (!charts[chartName]) {
                charts[chartName] = buildFn(newData);
            } else {
                charts[chartName].data = newData;
                charts[chartName].draw(200);
            }
        }
    })
}

monitorChart('data.volume_by_date', 'volumeByDate', buildVolumeByDateChart);
monitorChart('data.volume_by_source', 'volumeBySource', buildVolumeBySourceChart);
monitorChart('data.volume_by_beat', 'volumeByBeat', buildVolumeByBeatChart);
monitorChart('data.volume_by_nature', 'volumeByNature', buildVolumeByNatureChart);
monitorChart('data.volume_by_close_code', 'volumeByCloseCode', buildVolumeByCloseCodeChart);


// ========================================================================
// Functions
// ========================================================================

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}

function buildVolumeByDateChart(data) {
    var parentWidth = d3.select("#volume-over-time").node().clientWidth;

    var margin = {top: 40, right: 50, bottom: 70, left: 50},
        width = parentWidth,
        height = parentWidth * 0.3;

    var svg = dimple.newSvg("#volume-over-time", width, height);

    var myChart = new dimple.chart(svg, data);
    myChart.setMargins(margin.left, margin.top, margin.right, margin.bottom);

    var x = myChart.addTimeAxis("x", "date", "%Y-%m-%dT%H:%M:%S", outFormats["week"]);
    x.title = "Date";
    var y1 = myChart.addMeasureAxis("y", "volume");
    y1.title = "Call Volume";
    y1.ticks = 5;

    var s1 = myChart.addSeries("type", dimple.plot.line);
    var ttDate = d3.time.format(outFormats["day"]);
    s1.getTooltipText = function (e) {
        console.log(e);
        return ["Date: " + ttDate(e.cx),
                "Volume: " + e.cy];
    }

    myChart.addLegend(width - margin.right - 100, 0, 100, 40, "right");
    myChart.draw();

    return myChart;
}

function buildVolumeBySourceChart(data) {
    var parentWidth = d3.select("#volume-by-source").node().clientWidth;

    var margin = {top: 50, right: 10, bottom: 80, left: 20},
        width = parentWidth,
        height = parentWidth * 0.5;

    var svg = dimple.newSvg("#volume-by-source", width, height);

    var myChart = new dimple.chart(svg, data);
    myChart.setMargins(margin.left, margin.top, margin.right, margin.bottom);

    var x = myChart.addTimeAxis("x", "date", "%Y-%m-%dT%H:%M:%S", outFormats["week"]);
    x.title = "Date";
    var y = myChart.addPctAxis("y", "volume");
    y.hidden = true;
    var area = myChart.addSeries("source", dimple.plot.area);
    area.interpolation = 'cardinal';
    var ttDate = d3.time.format(outFormats["day"]);
    var pct = d3.format("%p");
    area.getTooltipText = function (e) {
        return ["Date: " + ttDate(e.cx),
                "Self Initiated: " + pct(e.cy),
                "Citizen Initiated: " + pct(1 - e.cy)];
    }
    myChart.addLegend(width - margin.right - 100, 0, 100, 40, "right");
    myChart.draw();

    return myChart;
}

function buildVolumeByBeatChart(data) {
    var parentWidth = d3.select("#volume-by-beat").node().clientWidth;

    var margin = {top: 20, right: 20, bottom: 20, left: 50},
        width = parentWidth,
        height = parentWidth * 1.1;

    var svg = dimple.newSvg("#volume-by-beat", width, height);

    var myChart = new dimple.chart(svg, data);
    myChart.setMargins(margin.left, margin.top, margin.right, margin.bottom);

    var x = myChart.addMeasureAxis("x", "volume");
    x.title = null;
    var y = myChart.addCategoryAxis("y", "name");
    y.addOrderRule("volume", true);
    y.title = null;
    myChart.addSeries(null, dimple.plot.bar);
    myChart.draw();

    return myChart;
}

function buildVolumeByNatureChart(data) {
    var parentWidth = d3.select("#volume-by-nature").node().clientWidth;

    var margin = {top: 20, right: 50, bottom: 200, left: 50},
        width = parentWidth,
        height = parentWidth * 0.5;

    var svg = dimple.newSvg("#volume-by-nature", width, height);

    var myChart = new dimple.chart(svg, data);
    myChart.setMargins(margin.left, margin.top, margin.right, margin.bottom);

    var x = myChart.addCategoryAxis("x", "name");
    x.title = null;
    var y = myChart.addMeasureAxis("y", "volume");
    y.ticks = 5;
    y.title = null;
    var s = myChart.addSeries(null, dimple.plot.bar);
    myChart.draw();
    return myChart;
}

function buildVolumeByCloseCodeChart(data) {
    var parentWidth = d3.select("#volume-by-close-code").node().clientWidth;

    var margin = {top: 20, right: 50, bottom: 200, left: 50},
        width = parentWidth,
        height = parentWidth * 0.5;

    var svg = dimple.newSvg("#volume-by-close-code", width, height);

    var myChart = new dimple.chart(svg, data);
    myChart.setMargins(margin.left, margin.top, margin.right, margin.bottom);

    var x = myChart.addCategoryAxis("x", "name");
    x.title = null;
    var y = myChart.addMeasureAxis("y", "volume");
    y.ticks = 5;
    y.title = null;
    myChart.addSeries(null, dimple.plot.bar);
    myChart.draw();
    return myChart;
}

function buildDayHourHeatmap(data) {
    var parentWidth = d3.select("#day-hour-heatmap").node().clientWidth;

    var margin = {top: 50, right: 0, bottom: 100, left: 30},
        width = parentWidth - margin.left - margin.right,
        height = 430 - margin.top - margin.bottom,
        gridSize = Math.floor(width / 24),
        legendElementWidth = gridSize * 2,
        buckets = 9,
        colors = colorbrewer.OrRd[9],
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
        times = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];

    data.forEach(function (d) {
        d.day = +d.dow_received;
        d.hour = +d.hour_received;
        d.value = +d.volume;
    });

    if (data.length < 24 * 7) {
        for (var i = 0; i < 7; i++) {
            for (var j = 0; j < 24; j++) {
                if (!_.find(data, function (d) {
                        return d.day === i && d.hour === j;
                    })) {
                    data.push({day: i, hour: j, value: 0});
                }
            }
        }
    }

    data = _.sortBy(data, function (d) {
        return d.day * 24 + d.hour;
    });

    var colorScale = d3.scale.quantile().domain([0, buckets - 1, d3.max(data, function (d) {
        return d.value;
    })]).range(colors);

    var svg = d3.select("#day-hour-heatmap").select("svg");

    if (svg.size() === 0) {
        svg = d3.select("#day-hour-heatmap").append("svg").attr("width", width + margin.left + margin.right).attr("height", height + margin.top + margin.bottom).append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    } else {
        svg = svg.select("g");
    }

    var dayLabels = svg.selectAll(".dayLabel").data(days).enter().append("text").text(function (d) {
        return d;
    }).attr("x", 0).attr("y", function (d, i) {
        return i * gridSize;
    }).style("text-anchor", "end").attr("transform", "translate(-6," + gridSize / 1.5 + ")").attr("class", function (d, i) {
        return i >= 0 && i <= 4 ? "dayLabel mono axis axis-workweek" : "dayLabel mono axis";
    });

    var timeLabels = svg.selectAll(".timeLabel").data(times).enter().append("text").text(function (d) {
        return d;
    }).attr("x", function (d, i) {
        return i * gridSize;
    }).attr("y", 0).style("text-anchor", "middle").attr("transform", "translate(" + gridSize / 2 + ", -6)").attr("class", function (d, i) {
        return i >= 7 && i <= 16 ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis";
    });

    var heatMap = svg.selectAll(".hour").data(data);

    heatMap.enter().append("rect").attr("x", function (d) {
        return d.hour * gridSize;
    }).attr("y", function (d) {
        return d.day * gridSize;
    }).attr("rx", 4).attr("ry", 4).attr("class", "hour bordered").attr("width", gridSize).attr("height", gridSize);

    heatMap.exit().remove();

    heatMap.style("fill", colors[0]);

    heatMap.transition().duration(1000).style("fill", function (d) {
        return colorScale(d.value);
    });

    heatMap.select("title").remove();

    heatMap.append("title").text(function (d) {
        return d.value;
    });

    svg.selectAll(".legend").remove();

    var legend = svg.selectAll(".legend").data([0].concat(colorScale.quantiles()), function (d) {
        return d;
    }).enter().append("g").attr("class", "legend");

    legend.append("rect").attr("x", function (d, i) {
        return legendElementWidth * i;
    }).attr("y", height).attr("width", legendElementWidth).attr("height", gridSize / 2).style("fill", function (d, i) {
        return colors[i];
    });

    legend.append("text").attr("class", "mono").text(function (d) {
        return "≥ " + Math.round(d);
    }).attr("x", function (d, i) {
        return legendElementWidth * i;
    }).attr("y", height + gridSize);
}

