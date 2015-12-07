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

    data.volume_by_nature = volumeByNature;

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
    ratio: 1.5
});

var volumeByShiftChart = new HorizontalBarChart({
    el: "#volume-by-shift",
    filter: "shift",
    ratio: 2.5
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


function buildVolumeByNatureChart(data) {
    var parentWidth = d3.select("#volume-by-nature").node().clientWidth;
    var width = parentWidth;
    var height = width / 2;

    var svg = d3.select("#volume-by-nature svg");
    svg.attr("width", width).attr("height", height);

    nv.addGraph(
        function () {
            var chart = nv.models.discreteBarChart()
                .x(
                    function (d) {
                        return d.name
                    })
                .y(
                    function (d) {
                        return d.volume
                    })
                .margin({"bottom": 200, "right": 50});

            svg.datum([{key: "Call Volume", values: data}]).call(chart);

            svg.selectAll('.nv-bar').style('cursor', 'pointer');

            chart.discretebar.dispatch.on(
                'elementClick', function (e) {
                    if (e.data.id) {
                        toggleFilter(dashboard, "nature", e.data.id);
                    }
                });

            // Have to call this both during creation and after updating the chart
            // when the window is resized.
            var rotateLabels = function () {
                var xTicks = d3.select('#volume-by-nature .nv-x.nv-axis > g').selectAll('g');

                xTicks.selectAll('text')
                    .style("text-anchor", "start")
                    .attr("dx", "0.25em")
                    .attr("dy", "0.75em")
                    .attr("transform", "rotate(45 0,0)");
            };

            rotateLabels();

            nv.utils.windowResize(
                function () {
                    chart.update();
                    rotateLabels();

                });

            return chart;
        })
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

function getDayHourHeatmapBounds() {
    var parent = d3.select("#day-hour-heatmap"),
        parentWidth = parent.node().clientWidth,
        ratio = 2.5 / 1,
        width = parentWidth,
        height = width / ratio;

    return {width: width, height: height};
}

function resizeDayHourHeatmap() {
    var bounds = getDayHourHeatmapBounds(),
        svg = d3.select("#day-hour-heatmap").select("svg");

    svg.attr("width", bounds.width)
        .attr("height", bounds.height);
}

function buildDayHourHeatmap(data) {
    var margin = {top: 0, right: 0, bottom: 100, left: 0},
        bounds = getDayHourHeatmapBounds(),
        width = bounds.width - margin.left - margin.right,
        height = bounds.height - margin.top - margin.bottom,
        gridSize = Math.floor(width / 25),
        legendElementWidth = gridSize * 2,
        buckets = 9,
        colors = colorbrewer.OrRd[9],
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
        times = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p",
            "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];

    data.forEach(
        function (d) {
            d.day = +d.dow_received;
            d.hour = +d.hour_received;
            d.value = +d.volume;
        });

    if (data.length > 0 && data.length < 24 * 7) {
        for (var i = 0; i < 7; i++) {
            for (var j = 0; j < 24; j++) {
                if (!_.find(
                        data, function (d) {
                            return d.day === i && d.hour === j;
                        })) {
                    data.push({day: i, hour: j, value: 0});
                }
            }
        }
    }

    data = _.sortBy(
        data, function (d) {
            return d.day * 24 + d.hour;
        });

    var colorScale = d3.scale.quantile().domain(
        [0, buckets - 1, d3.max(
            data, function (d) {
                return d.value;
            })]).range(colors);

    var svg = d3.select("#day-hour-heatmap").select("svg");

    if (svg.size() === 0) {
        svg = d3.select("#day-hour-heatmap")
            .append("svg")
            .attr("width", bounds.width)
            .attr("height", bounds.height)
            .attr("viewBox", "0 0 " + bounds.width + " " + bounds.height)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    } else {
        svg = svg.select("g");
    }

    if (_.isEmpty(data)) {
        var noDataText = svg.selectAll('.nv-noData').data(["No Data Available"]);

        noDataText.enter().append('text')
            .attr('class', 'nvd3 nv-noData')
            .attr('dy', '-.7em')
            .style('text-anchor', 'middle');

        noDataText
            .attr('x', margin.left + width / 2)
            .attr('y', margin.top + height / 2)
            .text(
                function (d) {
                    return d
                });

        return;
    } else {
        svg.selectAll('.nv-noData').remove();
    }

    var dayLabels = svg.selectAll(".dayLabel")
        .data(days)
        .enter()
        .append("text")
        .text(
            function (d) {
                return d;
            })
        .attr("x", gridSize)
        .attr(
            "y", function (d, i) {
                return (i + 1) * gridSize;
            })
        .style("text-anchor", "end")
        .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
        .attr(
            "class", function (d, i) {
                return i >= 0 && i <= 4 ? "dayLabel mono axis axis-workweek" : "dayLabel mono axis";
            });

    var timeLabels = svg.selectAll(".timeLabel")
        .data(times)
        .enter()
        .append("text")
        .text(
            function (d) {
                return d;
            })
        .attr(
            "x", function (d, i) {
                return (i + 1) * gridSize;
            })
        .attr("y", gridSize)
        .style("text-anchor", "middle")
        .attr("transform", "translate(" + gridSize / 2 + ", -8)")
        .attr(
            "class", function (d, i) {
                return i >= 7 && i <= 16 ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis";
            });

    var heatMap = svg.selectAll(".hour").data(data);

    heatMap.enter()
        .append("rect")
        .attr(
            "x", function (d) {
                return (d.hour + 1) * gridSize;
            })
        .attr(
            "y", function (d) {
                return (d.day + 1) * gridSize;
            })
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("class", "hour bordered")
        .attr("width", gridSize)
        .attr("height", gridSize);

    heatMap.exit().remove();

    heatMap.style("fill", colors[0]);

    heatMap.transition().duration(1000).style(
        "fill", function (d) {
            return colorScale(d.value);
        });

    heatMap.select("title").remove();

    heatMap.append("title").text(
        function (d) {
            return Math.round(d.value);
        });

    svg.selectAll(".legend").remove();

    var legend = svg.selectAll(".legend").data(
        [0].concat(colorScale.quantiles()), function (d) {
            return d;
        }).enter().append("g").attr("class", "legend")
        .attr("transform", "translate(" + gridSize + ", 0)");

    legend.append("rect")
        .attr(
            "x", function (d, i) {
                return legendElementWidth * i;
            })
        .attr("y", gridSize * 9)
        .attr("width", legendElementWidth)
        .attr("height", gridSize / 2)
        .style(
            "fill", function (d, i) {
                return colors[i];
            });

    legend.append("text").attr("class", "mono").text(
        function (d) {
            return "≥ " + Math.round(d);
        }).attr(
        "x", function (d, i) {
            return legendElementWidth * i;
        }).attr("y", gridSize * 10);
}

function drawMap() {
    var northEast = L.latLng(36.13898378070337, -78.75068664550781),
        southWest = L.latLng(35.860952532806905, -79.04937744140625),
        bounds = L.latLngBounds(southWest, northEast);

    var map = L.map(
        'map', {
            center: [36.0, -78.9],
            zoom: 12,
            maxBounds: bounds,
            minZoom: 11,
            maxZoom: 16
        });

    function resize() {
        var container = d3.select("#map-container").node(),
            width = container.clientWidth,
            bounds = container.getBoundingClientRect(),
            height = width * 1.3;
            //pTop = bounds.top,
            //pBottom = window.innerHeight,
            //height = Math.max(10, pBottom - pTop - 100);

        d3.select("#map")
            .style('width', width + 'px')
            .style('height', height + 'px');

        map.invalidateSize();
    }

    d3.select(window).on("resize.map", function () {
        resize();
    });

    L.tileLayer(
        'http://tile.stamen.com/toner-lite/{z}/{x}/{y}.png',
        {
            attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
            maxZoom: 18
        }).addTo(map);

    var info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'mapinfo');
        this.update();
        return this._div;
    };

    // method that we will use to update the control based on feature
    // properties passed
    info.update = function (props) {
        if (props) {
            var call_volume = dashboard.get('data.map_data')[props.LAWBEAT],
                text;

            if (call_volume === undefined) {
                text = "No data.";
            } else {
                text = "Call Volume " +
                    fmt(call_volume, 'call_volume');
            }

            this._div.innerHTML = '<h4>Beat ' + props.LAWBEAT + '</h4>' +
                "<div>" + text + "</div>";
        } else {
            this._div.innerHTML = "<div>Hover over a beat</div>";
        }
    };

    info.addTo(map);

    function highlightFeature(e) {
        var layer = e.target;

        layer.setStyle(
            {
                dashArray: '',
                fillOpacity: 0.5,
                weight: 3
            });

        if (!L.Browser.ie && !L.Browser.opera) {
            layer.bringToFront();
        }

        info.update(layer.feature.properties);
    }

    function resetHighlight(e) {
        var layer = e.target;

        layer.setStyle(
            {
                weight: 2,
                dashArray: '3',
                fillOpacity: 0.8
            });

        if (!L.Browser.ie && !L.Browser.opera) {
            layer.bringToFront();
        }

        info.update();
    }

    function toggleBeat(e) {
        var layer = e.target;
        toggleFilter(dashboard, 'beat', dashboard.get('data.beat_ids')[layer.feature.properties.LAWBEAT]);
    }

    function onEachFeature(feature, layer) {
        layer.on(
            {
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: toggleBeat
            });
    }

    d3.json(
        "/static/map/beats.json", function (json) {
            json.features = _(json.features).reject(
                function (d) {
                    return d.properties.LAWDIST === "DSO"
                });

            var myStyle = {
                color: "white",
                dashArray: '3',
                fillColor: "#AAAAAA",
                opacity: 1,
                fillOpacity: 0.6,
                weight: 2
            };

            geojson = L.geoJson(
                json, {
                    style: myStyle,
                    onEachFeature: onEachFeature
                }).addTo(map);

            resize();
            dashboard.set('mapDrawn', true);
        });
}

function updateMap(data) {
    function updateLegend(legendData) {
        var legend = d3.select('#legend');
        legend.selectAll("ul").remove();
        var list = legend.append('ul').classed('list-inline', true);
        var keys = list.selectAll('li.key').data(legendData);
        keys.enter()
            .append('li')
            .classed('key', true)
            .style('border-left-width', '30px')
            .style('border-left-style', 'solid')
            .style('padding', '0 10px')
            .style(
                'border-left-color', function (d) {
                    return d[0]
                })
            .text(
                function (d) {
                    return d[1];
                });
    }

    function update(data, key, numColors, colorScheme) {
        var minValue = _(data).chain().values().min().value(),
            maxValue = _(data).chain().values().max().value(),
            colors;

        numColors = Math.min(numColors, maxValue - minValue + 1);

        if (numColors < 3) {
            colors = colorScheme[3].slice(3 - numColors);
        } else {
            colors = colorScheme[numColors + 1].slice(1);
        }

        var scale = d3.scale.linear()
            .domain([minValue, maxValue])
            .nice()
            .range([0, numColors]);

        var legendData = _.map(
            _.range(numColors), function (n) {
                var start = Math.ceil(scale.invert(n)),
                    end = Math.floor(scale.invert(n + 1)),
                    text;

                if (start >= end) {
                    text = fmt(start);
                } else {
                    text = fmt(start) + "-" + fmt(end)
                }

                return [
                    colors[n],
                    text
                ];
            });

        updateLegend(legendData);

        var styleFn = function (d) {
            var n = Math.min(
                numColors - 1, Math.floor(scale(data[d.properties.LAWBEAT])));
            return {
                fillColor: colors[n] || "gray",
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.8
            }
        };

        geojson.setStyle(styleFn);
    }

    update(data, 'volume', 5, colorbrewer.Reds);
}

function ensureMapIsDrawn() {
    var deferred = Q.defer();

    function isMapDrawn() {
        if (dashboard.get('mapDrawn')) {
            deferred.resolve();
        } else {
            setTimeout(isMapDrawn, 30);
        }
    }

    isMapDrawn();

    return deferred.promise;
}

function fmt(val, style) {
    return d3.format(",.2f")(val).replace(/\.0+$/, "");
}



d3.select(window).on('resize', function () {
    resizeDayHourHeatmap();
});

dashboard.on('complete', drawMap);

dashboard.observe('data.map_data', function (newData) {
    ensureMapIsDrawn().then(function () {
        updateMap(newData);
    })
})

monitorChart(dashboard, 'data.day_hour_heatmap', buildDayHourHeatmap);
monitorChart(dashboard, 'data.volume_by_nature', buildVolumeByNatureChart);
monitorChart(dashboard, 'data.volume_by_date', buildVolumeByDateChart);
monitorChart(dashboard, 'data.volume_by_source', buildVolumeBySourceChart);
monitorChart(dashboard, 'data.volume_by_dow', volumeByDOWChart.update);
monitorChart(dashboard, 'data.volume_by_shift', volumeByShiftChart.update);

