"use strict";

var url = "/api/overview/";
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
        d3.json(buildURL(filter), _.bind(function (error, newData) {
            if (error) throw error;
            this.set('loading', false);
            this.set('initialload', false);
            newData = cleanupData(newData);
            this.set('data', newData);
        }, this));
    }
});

dashboard.on('filterByDate', function (event, span) {
    var pastSunday = moment().day("Sunday").startOf("day");

    var f = cloneFilter();
    if (span === "7days") {
        f['time_received__gte'] = pastSunday.clone().subtract(7, 'days').format("YYYY-MM-DD");
        f['time_received__lte'] = pastSunday.clone().format("YYYY-MM-DD");
    } else if (span === "28days") {
        f['time_received__gte'] = pastSunday.clone().subtract(28, 'days').format("YYYY-MM-DD");
        f['time_received__lte'] = pastSunday.clone().format("YYYY-MM-DD");
    } else if (span == "ytd") {
        f['time_received__gte'] = moment().clone().startOf("year").format("YYYY-MM-DD");
        delete f['time_received__lte'];
    }

    updateHash(buildQueryParams(f));
    return false;
});

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


function cleanupData(data) {
    var indate = d3.time.format("%Y-%m-%dT%H:%M:%S");

    var natureCols = 30;
    var volumeByNature = _(data.volume_by_nature).sortBy('volume').reverse();

    var allOther = _.chain(volumeByNature)
        .rest(natureCols)
        .reduce(function (total, cur) {
            return {name: "ALL OTHER", volume: total.volume + cur.volume}
        }, {name: "ALL OTHER", volume: 0})
        .value();

    volumeByNature = _.first(volumeByNature, natureCols).concat(
        allOther.volume > 0 ? [allOther] : []);

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
        .filter(function (d) {
            return d.self_initiated;
        })
        .reduce(function (obj, d) {
            obj[d.date] = d.volume;
            return obj;
        }, {})
        .value();

    var ci = _.chain(volBySrc)
        .filter(function (d) {
            return !d.self_initiated;
        })
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
                .sortBy(function (d) {
                    return d[0]
                })
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
                .sortBy(function (d) {
                    return d[0]
                })
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
            // If we don't remove the tooltips before updating
            // the chart, they'll stick around
            d3.selectAll(".nvtooltip").remove();

            fn(newData);
        }
    })
}

monitorChart('data.officer_response_time_by_source', buildORTBySourceChart);

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

