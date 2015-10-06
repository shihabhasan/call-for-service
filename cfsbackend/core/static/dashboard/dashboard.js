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

function toggleFilter(key, value) {
    var f = _.clone(dashboard.findComponent('Filter').get('filter'));
    if (f[key] == value) {
        delete f[key];
    } else {
        f[key] = value;
    }
    window.location.hash = buildQueryParams(f);
}


function cleanupData(data) {
    var indate = d3.time.format("%Y-%m-%dT%H:%M:%S");

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

    data.volume_by_date = [
        {
            key: "Call Volume",
            values: _.map(data.volume_by_date, function (obj) {
                obj = _.chain(obj)
                    .selectKeys(["date", "volume"])
                    .renameKeys({"date": "x", "volume": "y"})
                    .value();
                obj.x = indate.parse(obj.x);
                return obj;
            })
        },
        {
            key: "30-Day Average",
            values: _.map(data.volume_by_date, function (obj) {
                obj = _.chain(obj)
                    .selectKeys(["date", "average"])
                    .renameKeys({"date": "x", "average": "y"})
                    .value();
                obj.x = indate.parse(obj.x);
                return obj;
            })
        }
    ];

    var volBySrc = data.volume_by_source;

    var si = _.chain(volBySrc)
        .filter(function (d) { return d.self_initiated; })
        .reduce(function (obj, d) {
            obj[d.date] = d.volume;
            return obj;
        }, {})
        .value();

    var ci = _.chain(volBySrc)
        .filter(function (d) { return !d.self_initiated; })
        .reduce(function (obj, d) {
            obj[d.date] = d.volume;
            return obj;
        }, {})
        .value();

    _.difference(_.keys(ci), _.keys(si)).forEach(function (k) {
        si[k] = 0;
    });
    _.difference(_.keys(si), _.keys(ci)).forEach(function (k) {
        ci[k] = 0;
    });


    data.volume_by_source = [
        {
            key: "Self Initiated",
            values: _.chain(si)
                .pairs()
                .sortBy(function (d) { return d[0]} )
                .map(function (d) {
                    return {
                        x: indate.parse(d[0]),
                        y: d[1]
                    }
                })
                .value()
        },
        {
            key: "Citizen Initiated",
            values: _.chain(ci)
                .pairs()
                .sortBy(function (d) { return d[0]} )
                .map(function (d) {
                    return {
                        x: indate.parse(d[0]),
                        y: d[1]
                    }
                })
                .value()
        }
    ];



    data.volume_by_beat = [
        {
            key: "Volume By Beat",
            values: _.chain(data.volume_by_beat)
                .filter(function (d) {
                    return d.name;
                })
                .sortBy(function (d) {
                    return d.volume;
                })
                .value()
        }
    ];

    return data;
}

function monitorChart(keypath, fn) {
    dashboard.observe(keypath, function (newData) {
        if (!dashboard.get('loading')) {
            fn(newData);
        }
    })
}

monitorChart('data.day_hour_heatmap', buildDayHourHeatmap);
monitorChart('data.volume_by_nature', buildVolumeByNatureChart);
monitorChart('data.volume_by_date', buildVolumeByDateChart);
monitorChart('data.volume_by_source', buildVolumeBySourceChart);
monitorChart('data.volume_by_beat', buildVolumeByBeatChart);

// ========================================================================
// Functions
// ========================================================================

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}


function buildVolumeByDateChart(data) {
    var parentWidth = d3.select("#volume-by-nature").node().clientWidth;
    var width = parentWidth;
    var height = width / 2.5;

    var svg = d3.select("#volume-by-date svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.lineChart()
            .options({
                margin: {"right": 50},
                transitionDuration: 300,
                useInteractiveGuideline: true,
                forceY: [0]
            });

        chart.xAxis
            .axisLabel("Date")
            .tickFormat(function (d) {
                return d3.time.format('%x')(new Date(d));
            });

        chart.yAxis
            .axisLabel("Volume")
            .tickFormat(d3.format(",d"));

        svg.datum(data).call(chart);
        nv.utils.windowResize(chart.update);
        return chart;
    });
}


function buildVolumeByNatureChart(data) {
    var parentWidth = d3.select("#volume-by-nature").node().clientWidth;
    var width = parentWidth;
    var height = width / 2;

    var svg = d3.select("#volume-by-nature svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.discreteBarChart()
            .x(function (d) {
                return d.name
            })
            .y(function (d) {
                return d.volume
            })
            .margin({"bottom": 200, "right": 50})

        svg.datum([{key: "Call Volume", values: data}]).call(chart);

        chart.discretebar.dispatch.on('elementClick', function (e) {
            toggleFilter("nature", e.data.id);
        });

        // Have to call this both during creation and after updating the chart
        // when the window is resized.
        var rotateLabels = function() {
            var xTicks = d3.select('#volume-by-nature .nv-x.nv-axis > g').selectAll('g');

            xTicks.selectAll('text')
                .style("text-anchor", "start")
                .attr("dx", "0.25em")
                .attr("dy", "0.75em")
                .attr("transform", "rotate(45 0,0)" );
        };

        rotateLabels();

        nv.utils.windowResize(function () {
            chart.update();
            rotateLabels();

        });

        return chart;
    })
}


function buildVolumeBySourceChart(data) {
    var parentWidth = d3.select("#volume-by-source").node().clientWidth;
    var width = parentWidth,
        height = width / 2;

    var svg = d3.select("#volume-by-source svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.stackedAreaChart()
            .useInteractiveGuideline(true)
            .duration(300)
            .margin({"right": 50});

        chart.xAxis.tickFormat(function (d) {
            return d3.time.format('%x')(new Date(d))
        });
        chart.yAxis.tickFormat(d3.format(',.1f%'));
        chart.style('expand');

        svg.datum(data).call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
}


function buildVolumeByBeatChart(data) {
    var parentWidth = d3.select("#volume-by-beat").node().clientWidth;

    var width = parentWidth,
        height = width * 2;

    var svg = d3.select("#volume-by-beat svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.multiBarHorizontalChart()
            .x(function (d) {
                return d.name
            })
            .y(function (d) {
                return d.volume
            }).showValues(true)
            .duration(250)
            .showControls(false)
            .showLegend(false);

        svg.datum(data).call(chart);

        chart.multibar.dispatch.on('elementClick', function (e) {
            toggleFilter("beat", e.data.id);
        });

        nv.utils.windowResize(chart.update);

        return chart;
    });
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

