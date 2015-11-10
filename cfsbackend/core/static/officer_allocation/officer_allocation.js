"use strict";

var url = "/api/officer_allocation/";

var dashboard = new Page({
    el: $('body').get(),
    template: "#dashboard-template",
    data: {
        data: {
            'allocation_over_time': []
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
        f['time__gte'] = pastSunday.clone().subtract(7, 'days').format("YYYY-MM-DD");
        f['time__lte'] = pastSunday.clone().format("YYYY-MM-DD");
    } else if (span === "28days") {
        f['time__gte'] = pastSunday.clone().subtract(28, 'days').format("YYYY-MM-DD");
        f['time__lte'] = pastSunday.clone().format("YYYY-MM-DD");
    } else if (span == "ytd") {
        f['time__gte'] = moment().clone().startOf("year").format("YYYY-MM-DD");
        delete f['time__lte'];
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
    var indate = d3.time.format("%H:%M:%S");
    data.allocation_over_time = _.sortBy(data.allocation_over_time, 'time_hour_minute');
    data.allocation_over_time = [
        {
            key: "Out of Service",
            values: _.where(data.allocation_over_time, { activity: "OUT OF SERVICE" })
                .map(function(obj) {
                    obj = _.chain(obj)
                        .selectKeys(["time_hour_minute", "avg_volume"])
                        .renameKeys({"time_hour_minute": "x", "avg_volume": "y"})
                        .value();
                    obj.x = indate.parse(obj.x);
                    return obj;
                })
        },
        {
            key: "In Call",
            values: _.where(data.allocation_over_time, { activity: "IN CALL" })
                .map(function(obj) {
                    obj = _.chain(obj)
                        .selectKeys(["time_hour_minute", "avg_volume"])
                        .renameKeys({"time_hour_minute": "x", "avg_volume": "y"})
                        .value();
                    obj.x = indate.parse(obj.x);
                    return obj;
                })
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

monitorChart('data.allocation_over_time', buildAllocationOverTimeChart);

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}

function buildAllocationOverTimeChart(data) {
    var parentWidth = d3.select("#allocation-over-time").node().clientWidth;
    var width = parentWidth;
    var height = width / 2;

    var svg = d3.select("#allocation-over-time svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.stackedAreaChart()
            .options({
                margin: {"right": 50},
                transitionDuration: 300,
                useInteractiveGuideline: true,
                forceY: [0]
            });

        chart.xAxis
            .axisLabel("Time")
            .tickFormat(function (d) {
                return d3.time.format('%X')(new Date(d));
            });

        chart.yAxis
            .axisLabel("Officers Allocated")
            .tickFormat(d3.format(",d"));

        svg.datum(data).call(chart);
        nv.utils.windowResize(chart.update);
        return chart;
    });
}
