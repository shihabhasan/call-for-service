"use strict";

var url = "/api/map_info/";
var charts = {};
var outFormats = {
    "month": "%b %y",
    "week": "%m/%d/%y",
    "day": "%a %m/%d",
    "hour": "%m/%d %H:%M"
};

var dashboard = new Page({
    el: $('body').get(),
    template: "#map-template",
    data: {
        showing: 'call_volume',
        mapDrawn: false
    },
    filterUpdated: function (filter) {
        //d3.json(buildURL(filter), _.bind(function (error, newData) {
        //    if (error) throw error;
            this.set('loading', false);
            this.set('initialload', false);
        //    newData = cleanupData(newData);
        //    this.set('data', newData);
        //}, this));
    }
});

dashboard.on('complete', function () {
    var width = d3.select("#map-container").node().clientWidth
        , height = width * 1.15
        ;

    d3.select("#map")
        .style('width', width + 'px')
        .style('height', height + 'px');

    var map = L.map('map').setView([36.0, -78.9], 12);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18,
        id: 'dpdcfs.cigtj42c107u5tpkn9bxnh6mo',
        accessToken: 'pk.eyJ1IjoiZHBkY2ZzIiwiYSI6ImNpZ3RqNDNoNzA3dTl0cGtudnd6dTVjYmYifQ.PVmca7xR3BwLEfN4HWgVvQ'
    }).addTo(map);

    d3.json("/static/map/beats.json", function (json) {
        json.features = _(json.features).reject(function (d) {
            return d.properties.LAWDIST === "DSO"
        });

        var myStyle = {
            "color": "#ff7800",
            "weight": 2,
            "opacity": 0.25
        };

        L.geoJson(json, {style: myStyle}).addTo(map);
    });
});


//
//
//function ensureMapIsDrawn() {
//    var deferred = Q.defer();
//
//    function isMapDrawn() {
//
//        if (map.get('mapDrawn')) {
//            deferred.resolve();
//        } else {
//            setTimeout(isMapDrawn, 30);
//        }
//    }
//
//    isMapDrawn();
//
//    return deferred.promise;
//}
//
//
//map.observe('data', function (newData) {
//    d3.selectAll(".nvtooltip").remove();
//    var svg = d3.select("#map g");
//    if (svg.size() === 0) {
//        buildMap();
//    }
//
//    ensureMapIsDrawn().then(function () {
//        updateMap(newData)
//    });
//});
//
//map.observe('showing', function () {
//    d3.selectAll(".nvtooltip").remove();
//    var svg = d3.select("#map g");
//    if (svg.size() === 0) {
//        return;
//    }
//
//    ensureMapIsDrawn().then(function () {
//        updateMap(map.get('data'));
//    });
//});
//
//map.on('showing', function (event, state) {
//    map.set('showing', state);
//    return false;
//})
//
//// ========================================================================
//// Functions
//// ========================================================================

function cleanupData(data) {
    return data;
}

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}

//function buildMap() {
//    var width = d3.select("#map-container").node().clientWidth;
//    var height = width * 1.3;
//
//    var projection = d3.geo.conicConformal()
//        .scale(1)
//        .translate([0, 0])
//        .rotate([80, 0]);
//
//    var path = d3.geo.path()
//        .projection(projection);
//
//    var svg = d3.select("#map")
//        .attr("width", width)
//        .attr("height", height)
//        .append("g");
//
//    d3.json("/static/map/beats.json", function (json) {
//        json.features = _(json.features).reject(function (d) {
//            return d.properties.LAWDIST === "DSO"
//        });
//
//        // Compute the bounds of a feature of interest, then derive scale & translate.
//        var b = path.bounds(json),
//            s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
//            t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];
//
//        // Update the projection to use computed scale & translate.
//        projection
//            .scale(s)
//            .translate(t);
//
//        svg.selectAll("path")
//            .data(json.features)
//            .enter()
//            .append("path")
//            .attr("d", path)
//            .style("fill", "white")
//            .style("stroke", "black")
//            .style("stroke-width", 1)
//            .attr("class", function (d) {
//                return "beat beat-" + d.properties.LAWBEAT;
//            })
//            .attr("data-beat", function (d) {
//                return d.properties.LAWBEAT
//            })
//            .attr("data-dist", function (d) {
//                return d.properties.LAWDIST
//            });
//
//        map.set('mapDrawn', true);
//    });
//}
//
//function updateMap(data) {
//    if (data === undefined) {
//        return;
//    }
//
//    var svg = d3.select("#map")
//        , g = svg.select("g")
//        , tooltip = nv.models.tooltip()
//        , blankColor = "#EEE"
//        ;
//
//    g.selectAll(".beat").style("fill", blankColor);
//
//    if (data.count === 0) {
//        var noDataText = g.selectAll('.nv-noData').data(["No Data Available."]);
//        g.selectAll('path').style('opacity', 0.2);
//
//        var width = svg.node().clientWidth;
//        var height = svg.node().clientHeight;
//
//        noDataText.enter()
//            .append('text')
//            .attr('class', 'nvd3 nv-noData')
//            .attr('dy', '-.7em')
//            .style('text-anchor', 'middle');
//
//        noDataText
//            .attr('x', width / 2 )
//            .attr('y', 100 )
//            .text(function (d) {
//                console.log(d);
//                return d;
//            });
//
//        g
//            .on('mouseover', null)
//            .on('mouseout', null)
//            .on('mousemove', null);
//
//        return;
//    } else {
//        g.selectAll('.nv-noData').remove();
//        g.selectAll('path').style('opacity', 1);
//    }
//
//    function updateLegend(legendData) {
//        var legend = d3.select('#legend');
//        legend.selectAll("ul").remove();
//        var list = legend.append('ul').classed('inline-list', true);
//        var keys = list.selectAll('li.key').data(legendData);
//        keys.enter()
//            .append('li')
//            .classed('key', true)
//            .style('border-left-width', '30px')
//            .style('border-left-style', 'solid')
//            .style('padding', '0 10px')
//            .style('border-left-color', function (d) {
//                return d[0]
//            })
//            .text(function (d) {
//                return d[1];
//            });
//    }
//
//    function setupTooltip(tooltipData) {
//        g.selectAll(".beat")
//            .on('mouseover', function (d, i) {
//                tooltip.data(tooltipData(d, i)).hidden(false);
//            })
//            .on('mouseout', function (d, i) {
//                tooltip.data(tooltipData(d, i)).hidden(true);
//            })
//            .on('mousemove', function () {
//                tooltip();
//            })
//    }
//
//    function update(data, key, seriesName, numColors, colorScheme, fmt) {
//        var colors = colorScheme[numColors]
//            , minValue = _(data).chain().pluck(key).min().value()
//            , maxValue = _(data).chain().pluck(key).max().value()
//            , scale = d3.scale.linear().domain([minValue, maxValue]).nice().range([0, numColors])
//            ;
//
//        _(data).each(function (d) {
//            var n = Math.min(numColors - 1, Math.floor(scale(d[key])));
//            d3.selectAll(".beat-" + d.name)
//                .style("fill", colors[n]);
//        });
//
//        var beats = _.reduce(data, function (memo, d) {
//            memo[d.name] = d[key];
//            return memo
//        }, {});
//
//        var tooltipData = function (d, i) {
//            var n = Math.floor(scale(beats[d.properties.LAWBEAT]));
//            var series = {'key': seriesName};
//            if (_.isUndefined(beats[d.properties.LAWBEAT])) {
//                series.value = "No data";
//                series.color = blankColor;
//            } else {
//                series.value = fmt(beats[d.properties.LAWBEAT]);
//                series.color = colors[n];
//            }
//            return {
//                key: "Beat",
//                value: "Beat " + d.properties.LAWBEAT,
//                series: series,
//                data: d,
//                index: i,
//                e: d3.event
//            }
//        }
//
//        setupTooltip(tooltipData);
//
//        var legendData = _.range(numColors);
//        legendData = _.map(legendData, function (n) {
//            return [
//                colors[n],
//                fmt(scale.invert(n)) + "-" + fmt(scale.invert(n + 1))
//            ];
//        });
//
//        updateLegend(legendData);
//    }
//
//    if (map.get('showing') === 'call_volume') {
//        update(data.call_volume, 'volume', "Call Volume", 5, colorbrewer.OrRd, d3.format(",.g"));
//    } else {
//        update(data.officer_response_time, 'mean', "Officer Response Time", 6, colorbrewer.PuRd, durationFormat);
//    }
//}
//
//
//
//
