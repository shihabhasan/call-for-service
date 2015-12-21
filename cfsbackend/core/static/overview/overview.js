"use strict";

var callVolumeURL = "/api/call_volume/";
var outFormats = {
    "month": "%b %Y",
    "week": "%m/%d/%y",
    "day": "%a %m/%d",
    "hour": "%m/%d %H:%M"
};

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

    data.volume_by_nature_group = _.chain(data.volume_by_nature_group)
        .filter(function (d) { return d.name; })
        .sortBy(function (d) { return d.name; })
        .value();
    data.volume_by_nature_group = [{key: "Call Volume", values: data.volume_by_nature_group}];

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

    var sources = ["Officer", "Citizen"];

    data.volume_by_source = _.chain(data.volume_by_source).map(function (d) {
        return {
            id: d.id,
            volume: d.volume,
            name: sources[d.id]
        }
    }).sortBy(function (d) {
        return d.id;
    }).value();

    data.volume_by_source = [{key: "Volume by Source", values: data.volume_by_source}];

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
    fmt: d3.format(",d"),
    x: function (d) { return d.name },
    y: function (d) { return d.volume }
});

var volumeByShiftChart = new HorizontalBarChart({
    el: "#volume-by-shift",
    filter: "shift",
    ratio: 2.5,
    dashboard: dashboard,
    fmt: d3.format(",d"),
    x: function (d) { return d.name },
    y: function (d) { return d.volume }
});

var volumeByNatureGroupChart = new DiscreteBarChart({
    el: '#volume-by-nature',
    dashboard: dashboard,
    filter: 'nature__nature_group',
    ratio: 2,
    rotateLabels: true,
    fmt: d3.format(",d"),
    x: function (d) { return d.name },
    y: function (d) { return d.volume }
});

var volumeBySourceChart = new HorizontalBarChart({
    el: "#volume-by-source",
    filter: "initiated_by",
    ratio: 2.5,
    dashboard: dashboard,
    fmt: d3.format(",d"),
    x: function (d) { return d.name },
    y: function (d) { return d.volume }
});

var volumeMap = new DurhamMap({
    el: "#map",
    dashboard: dashboard,
    colorScheme: colorbrewer.Blues,
    format: function (val, style) {
        return d3.format(",.2f")(val).replace(/\.0+$/, "");
    },
    dataDescr: "Call Volume"
});

function buildVolumeByDateChart(data) {
    var container = d3.select("#volume-by-date");
    var parentWidth = container.node().clientWidth;
    var width = parentWidth;
    var height = width / 2.5;

    var svg = d3.select("#volume-by-date svg");
    svg.attr("width", width)
        .attr("height", height)
        .style("height", height + "px")
        .style("width", width + "px");

    var resize = function (chart) {
        width = container.node().clientWidth;
        height = Math.ceil(width / 2.5);

        container.select("svg")
            .attr("width", width)
            .attr("height", height)
            .style("height", height + "px")
            .style("width", width + 'px');

        chart.height(height).width(width);

        chart.update();
    };

    nv.addGraph(
        function () {
            var chart = nv.models.lineChart()
                .options(
                    {
                        height: height,
                        width: width,
                        margin: {"right": 60},
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
            nv.utils.windowResize(function () {
                resize(chart);
            });
            return chart;
        });
}


monitorChart(dashboard, 'data.volume_by_nature_group', volumeByNatureGroupChart.update);
monitorChart(dashboard, 'data.volume_by_date', buildVolumeByDateChart);
monitorChart(dashboard, 'data.volume_by_source', volumeBySourceChart.update);
monitorChart(dashboard, 'data.volume_by_dow', volumeByDOWChart.update);
monitorChart(dashboard, 'data.volume_by_shift', volumeByShiftChart.update);
monitorChart(dashboard, 'data.map_data', volumeMap.update);