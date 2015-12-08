"use strict";

var callVolumeURL = "/api/call_volume/";
var outFormats = {
    "month": "%b %Y",
    "week": "%m/%d/%y",
    "day": "%a %m/%d",
    "hour": "%m/%d %H:%M"
};
var geojson;


var dashboard = new Page(
    {
        el: $('#dashboard').get(),
        template: "#dashboard-template",
        data: {
            mapDrawn: false,
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
            d3.json(
                buildURL(callVolumeURL, filter), _.bind(
                    function (error, newData) {
                        if (error) throw error;
                        this.set('loading', false);
                        this.set('initialload', false);
                        newData = cleanupData(newData);
                        this.set('data', newData);
                    }, this));
        }
    });

dashboard.on(
    'filterByDate', function (event, span) {
        var pastSunday = moment().day("Sunday").startOf("day");

        var f = cloneFilter(dashboard);
        if (span === "7days") {
            f['time_received__gte'] = pastSunday.clone().subtract(7, 'days').format("YYYY-MM-DD");
            f['time_received__lte'] = pastSunday.clone().subtract(1, 'days').format("YYYY-MM-DD");
        } else if (span === "28days") {
            f['time_received__gte'] = pastSunday.clone().subtract(28, 'days').format("YYYY-MM-DD");
            f['time_received__lte'] = pastSunday.clone().subtract(1, 'days').format("YYYY-MM-DD");
        } else if (span == "ytd") {
            f['time_received__gte'] = moment().clone().startOf("year").format("YYYY-MM-DD");
            delete f['time_received__lte'];
        }

        updateHash(buildQueryParams(f));
        return false;
    });


function cleanupData(data) {
    var indate = d3.time.format("%Y-%m-%dT%H:%M:%S");

    var natureCols = 30;
    var volumeByNature = _(data.volume_by_nature).sortBy('volume').reverse();

    var allOther = _.chain(volumeByNature)
        .rest(natureCols)
        .reduce(
            function (total, cur) {
                return {name: "ALL OTHER", volume: total.volume + cur.volume}
            }, {name: "ALL OTHER", volume: 0})
        .value();

    volumeByNature = _.first(volumeByNature, natureCols).concat(
        allOther.volume > 0 ? [allOther] : []);

    data.volume_by_nature = [{key: "Call Volume", values: volumeByNature}];

    data.volume_by_date = [
        {
            key: "Call Volume",
            values: _.map(
                data.volume_by_date, function (obj) {
                    obj = _.chain(obj)
                        .selectKeys(["date", "volume"])
                        .renameKeys({"date": "x", "volume": "y"})
                        .value();
                    obj.x = indate.parse(obj.x);
                    return obj;
                })
        }
    ];

    var sources = ["Self", "Citizen"];

    data.volume_by_source = _.map(data.volume_by_source, function (d) {
        return {
            id: d.id,
            volume: d.volume,
            name: sources[d.id]
        }
    });

    data.map_data = _.reduce(
        data.volume_by_beat, function (memo, d) {
            memo[d.name] = d.volume;
            return memo
        }, {});

    data.volume_by_beat = [
        {
            key: "Volume By Beat",
            values: _.chain(data.volume_by_beat)
                .filter(
                    function (d) {
                        return d.name;
                    })
                .sortBy(
                    function (d) {
                        return d.volume;
                    })
                .value()
        }
    ];

    var dow = ['Mon', 'Tue', "Wed", 'Thu', "Fri", 'Sat', 'Sun'];
    data.volume_by_dow = [
        {
            key: "Volume By Day of Week",
            values: _.chain(data.volume_by_dow)
                .map(function (d) {
                    return {
                        id: d.id,
                        volume: d.volume,
                        name: dow[d.id]
                    }
                })
                .sortBy(
                    function (d) {
                        return d.id;
                    })
                .value()
        }
    ]

    var shifts = ['Shift 1', 'Shift 2'];
    data.volume_by_shift = [
        {
            key: "Volume By Shift",
            values: _.chain(data.volume_by_shift)
                .map(function (d) {
                    return {
                        id: d.id,
                        volume: d.volume,
                        name: shifts[d.id]
                    }
                })
                .sortBy(
                    function (d) {
                        return d.id;
                    })
                .value()
        }
    ]

    return data;
}


// ========================================================================
// Functions
// ========================================================================

var volumeByDOWChart = new HorizontalBarChart({
    el: "#volume-by-dow",
    filter: "dow_received",
    ratio: 1.5,
    dashboard: dashboard,
    x: function (d) { return d.name },
    y: function (d) { return d.volume }
});

var volumeByShiftChart = new HorizontalBarChart({
    el: "#volume-by-shift",
    filter: "shift",
    ratio: 2.5,
    dashboard: dashboard,
    x: function (d) { return d.name },
    y: function (d) { return d.volume }
});

var volumeByNatureChart = new DiscreteBarChart({
    el: '#volume-by-nature',
    filter: 'nature',
    ratio: 2,
    rotateLabels: true,
    x: function (d) { return d.name },
    y: function (d) { return d.volume }
})

var volumeMap = new DurhamMap({
    el: "#map",
    dashboard: dashboard,
    colorScheme: colorbrewer.Reds,
    format: function (val, style) {
        return d3.format(",.2f")(val).replace(/\.0+$/, "");
    },
    dataDescr: "Call Volume"
});

function buildVolumeByDateChart(data) {
    var parentWidth = d3.select("#volume-by-nature").node().clientWidth;
    var width = parentWidth;
    var height = width / 2.5;

    var svg = d3.select("#volume-by-date svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(
        function () {
            var chart = nv.models.lineChart()
                .options(
                    {
                        margin: {"right": 50},
                        transitionDuration: 300,
                        useInteractiveGuideline: true,
                        forceY: [0],
                        showLegend: false
                    });

            chart.xAxis
                .tickFormat(
                    function (d) {
                        return d3.time.format(outFormats[dashboard.get('data.precision')])(
                            new Date(d));
                        //return d3.time.format('%x')(new Date(d));
                    });

            chart.yAxis
                .axisLabel("Volume")
                .tickFormat(d3.format(",d"));

            svg.datum(data).call(chart);
            nv.utils.windowResize(chart.update);
            return chart;
        });
}


function buildVolumeBySourceChart(data) {
    var parentWidth = d3.select("#volume-by-source").node().clientWidth;
    var width = parentWidth,
        height = width / 1.5;

    var svg = d3.select("#volume-by-source svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(
        function () {
            var chart = nv.models.pieChart()
                .x(function (d) { return d.name })
                .y(function (d) { return d.volume }); // allow custom CSS for this one svg
            chart.pie.labelsOutside(true).donut(true);

            svg.datum(data).call(chart);

            svg.selectAll('.nv-slice').style('cursor', 'pointer');

            chart.pie.dispatch.on(
                'elementClick', function (e) {
                    if (e.data.id || e.data.id === 0) {
                        toggleFilter(dashboard, "initiated_by", e.data.id);
                    }
                });

            nv.utils.windowResize(chart.update);

            return chart;
        });
}


monitorChart(dashboard, 'data.volume_by_nature', volumeByNatureChart.update);
monitorChart(dashboard, 'data.volume_by_date', buildVolumeByDateChart);
monitorChart(dashboard, 'data.volume_by_source', buildVolumeBySourceChart);
monitorChart(dashboard, 'data.volume_by_dow', volumeByDOWChart.update);
monitorChart(dashboard, 'data.volume_by_shift', volumeByShiftChart.update);
monitorChart(dashboard, 'data.map_data', volumeMap.update);