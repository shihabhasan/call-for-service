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
        d3.json(buildURL(url, filter), _.bind(function (error, newData) {
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

    var f = cloneFilter(dashboard);
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

function cleanupData(data) {
    var indate = d3.time.format("%H:%M:%S");
    
    var temp_allocation_data = [{
            key: "Citizen-Initiated Call",
            values: [],
        }, {
            key: "Officer-Initiated Call",
            values: [],
        }, {
            key: "Out of Service",
            values: [],
        }, {
            key: "Directed Patrol",
            values: [],
        }, {
            key: "Patrol",
            values: [],
        }];

    _.sortBy(_.keys(data.allocation_over_time)).forEach(function (k) {
        var oos = d3.round(data.allocation_over_time[k]['OUT OF SERVICE'].avg_volume, 2),
            dp = data.allocation_over_time[k]['IN CALL - DIRECTED PATROL'].avg_volume,
            oic = data.allocation_over_time[k]['IN CALL - SELF INITIATED'].avg_volume,
            cic = data.allocation_over_time[k]['IN CALL - CITIZEN INITIATED'].avg_volume,
            pat = data.allocation_over_time[k]['PATROL'].avg_volume,
            time = indate.parse(k);

        temp_allocation_data[0].values.push({
            'x': time,
            'y': cic,
        });
        temp_allocation_data[1].values.push({
            'x': time,
            'y': oic,
        });
        temp_allocation_data[2].values.push({
            'x': time,
            'y': oos,
        });
        temp_allocation_data[3].values.push({
            'x': time,
            'y': dp,
        });
        temp_allocation_data[4].values.push({
            'x': time,
            'y': pat,
        });
    });

    data.allocation_over_time = temp_allocation_data;

    data.on_duty_by_beat = [
        {
            key: "On Duty By Beat",
            values: _.chain(data.on_duty_by_beat)
                .filter(
                    function (d) {
                        return d.beat;
                    })
                .sortBy(
                    function (d) {
                        return d.on_duty;
                    })
                .value()
        }
    ];

    data.on_duty_by_district = [
        {
            key: "On Duty By District",
            values: _.chain(data.on_duty_by_district)
                .filter(
                    function (d) {
                        return d.district;
                    })
                .sortBy(
                    function (d) {
                        return d.on_duty;
                    })
                .value()
        }
    ];
    console.log(data.on_duty_by_beat);
    console.log(data.on_duty_by_district);

    return data;
}

monitorChart(dashboard, 'data.allocation_over_time', buildAllocationOverTimeChart);
monitorChart(dashboard, 'data.on_duty_by_beat', buildOnDutyByBeatChart);
monitorChart(dashboard, 'data.on_duty_by_district', buildOnDutyByDistrictChart);

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
            .axisLabel("Average Officers Allocated")
            .tickFormat(d3.format(",.2r"));

        // Keep NaNs from showing up in the tooltip header
        // This was supposed to have been fixed, but
        // apparently, it wasn't
        //
        // https://github.com/novus/nvd3/issues/1081
        chart.interactiveLayer.tooltip
            .headerFormatter(function (d) { return d; });

        svg.datum(data).call(chart);
        nv.utils.windowResize(chart.update);
        return chart;
    });
}

function buildOnDutyByBeatChart(data) {
    var parentWidth = d3.select("#on-duty-by-beat").node().clientWidth;
    var width = parentWidth;
    var height = width * 1.5;

    var svg = d3.select("#on-duty-by-beat svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.multiBarHorizontalChart()
            .x(
                function (d) {
                    return d.beat;
                })
            .y(
                function (d) {
                    return d.on_duty;
                })
            .duration(250)
            .showControls(false)
            .showLegend(false);

        chart.yAxis.tickFormat(d3.format(",d"));

        svg.datum(data).call(chart);

        svg.selectAll('.nv-bar').style('cursor', 'pointer');
        chart.multibar.dispatch.on(
            'elementClick', function (e) {
                toggleFilter(dashboard, "call_unit__beat", e.data.beat_id);
            });
        
        nv.utils.windowResize(chart.update);

        return chart;
    });
}

function buildOnDutyByDistrictChart(data) {
    var parentWidth = d3.select("#on-duty-by-district").node().clientWidth;
    var width = parentWidth;
    var height = width * 1.5;

    var svg = d3.select("#on-duty-by-district svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(function () {
        var chart = nv.models.multiBarHorizontalChart()
            .x(
                function (d) {
                    return d.district;
                })
            .y(
                function (d) {
                    return d.on_duty;
                })
            .duration(250)
            .showControls(false)
            .showLegend(false);

        chart.yAxis.tickFormat(d3.format(",d"));

        svg.datum(data).call(chart);

        svg.selectAll('.nv-bar').style('cursor', 'pointer');
        chart.multibar.dispatch.on(
            'elementClick', function (e) {
                toggleFilter(dashboard, "call_unit__district", e.data.district_id);
            });
        
        nv.utils.windowResize(chart.update);

        return chart;
    });
}
