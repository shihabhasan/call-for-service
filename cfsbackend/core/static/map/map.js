"use strict";

var url = "/api/map_info/";
var charts = {};
var outFormats = {
    "month": "%b %y",
    "week": "%m/%d/%y",
    "day": "%a %m/%d",
    "hour": "%m/%d %H:%M"
};

var map = new Page({
    el: $('body').get(),
    template: "#map-template",
    data: {
        showing: 'call_volume',
        mapDrawn: false
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


function ensureMapIsDrawn() {
    var deferred = Q.defer();

    function isMapDrawn() {

        if (map.get('mapDrawn')) {
            deferred.resolve();
        } else {
            setTimeout(isMapDrawn, 30);
        }
    }

    isMapDrawn();

    return deferred.promise;
}


map.observe('data', function (newData) {
    d3.selectAll(".nvtooltip").remove();
    var svg = d3.select("#map g");
    if (svg.size() === 0) {
        buildMap();
    }

    ensureMapIsDrawn().then(function () {
        updateMap(newData)
    });
});

map.observe('showing', function () {
    d3.selectAll(".nvtooltip").remove();
    var svg = d3.select("#map g");
    if (svg.size() === 0) {
        return;
    }

    ensureMapIsDrawn().then(function () {
        updateMap(map.get('data'));
    });
});

map.on('showing', function (event, state) {
    map.set('showing', state);
    return false;
})

// ========================================================================
// Functions
// ========================================================================

function cleanupData(data) {
    return data;
}

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}

function buildMap() {
    var width = d3.select("#map-container").node().clientWidth;
    var height = width * 1.3

    var projection = d3.geo.conicConformal()
        .scale(1)
        .translate([0, 0])
        .rotate([80, 0]);

    var path = d3.geo.path()
        .projection(projection);

    var svg = d3.select("#map")
        .attr("width", width)
        .attr("height", height)
        .append("g");

    d3.json("/static/map/beats.json", function (json) {
        json.features = _(json.features).reject(function (d) {
            return d.properties.LAWDIST === "DSO"
        });

        // Compute the bounds of a feature of interest, then derive scale & translate.
        var b = path.bounds(json),
            s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
            t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

        // Update the projection to use computed scale & translate.
        projection
            .scale(s)
            .translate(t);

        svg.selectAll("path")
            .data(json.features)
            .enter()
            .append("path")
            .attr("d", path)
            .style("fill", "white")
            .style("stroke", "black")
            .style("stroke-width", 1)
            .attr("class", function (d) {
                return "beat beat-" + d.properties.LAWBEAT;
            })
            .attr("data-beat", function (d) {
                return d.properties.LAWBEAT
            })
            .attr("data-dist", function (d) {
                return d.properties.LAWDIST
            });

        map.set('mapDrawn', true);
    });
}

function updateMap(data) {
    if (data === undefined) {
        return;
    }

    var svg = d3.select("#map g")
        , tooltip = nv.models.tooltip()
        , blankColor = "#EEE"
        ;

    svg.selectAll(".beat").style("fill", blankColor);


    function updateLegend(legendData) {
        var legend = d3.select('#legend');
        legend.selectAll("ul").remove();
        var list = legend.append('ul').classed('inline-list', true);
        var keys = list.selectAll('li.key').data(legendData);
        keys.enter()
            .append('li')
            .classed('key', true)
            .style('border-left-width', '30px')
            .style('border-left-style', 'solid')
            .style('padding', '0 10px')
            .style('border-left-color', function (d) {
                return d[0]
            })
            .text(function (d) {
                return d[1];
            });
    }

    function setupTooltip(tooltipData) {
        svg.selectAll(".beat")
            .on('mouseover', function (d, i) {
                tooltip.data(tooltipData(d, i)).hidden(false);
            })
            .on('mouseout', function (d, i) {
                tooltip.data(tooltipData(d, i)).hidden(true);
            })
            .on('mousemove', function () {
                tooltip();
            })
    }

    function update(data, key, seriesName, numColors, colorScheme, fmt) {
        var colors = colorScheme[numColors]
            , minValue = _(data).chain().pluck(key).min().value()
            , maxValue = _(data).chain().pluck(key).max().value()
            , scale = d3.scale.linear().domain([minValue, maxValue]).nice().range([0, numColors])
            ;

        _(data).each(function (d) {
            var n = Math.min(numColors - 1, Math.floor(scale(d[key])));
            d3.selectAll(".beat-" + d.name)
                .style("fill", colors[n]);
        });

        var beats = _.reduce(data, function (memo, d) {
            memo[d.name] = d[key];
            return memo
        }, {});

        var tooltipData = function (d, i) {
            var n = Math.floor(scale(beats[d.properties.LAWBEAT]));
            var series = {'key': seriesName};
            if (_.isUndefined(beats[d.properties.LAWBEAT])) {
                series.value = "No data";
                series.color = blankColor;
            } else {
                series.value = fmt(beats[d.properties.LAWBEAT]);
                series.color = colors[n];
            }
            return {
                key: "Beat",
                value: "Beat " + d.properties.LAWBEAT,
                series: series,
                data: d,
                index: i,
                e: d3.event
            }
        }

        setupTooltip(tooltipData);

        var legendData = _.range(numColors);
        legendData = _.map(legendData, function (n) {
            return [
                colors[n],
                fmt(scale.invert(n)) + "-" + fmt(scale.invert(n + 1))
            ];
        });

        updateLegend(legendData);
    }

    if (map.get('showing') === 'call_volume') {
        update(data.call_volume, 'volume', "Call Volume", 5, colorbrewer.OrRd, d3.format(",.g"));
    } else {
        update(data.officer_response_time, 'mean', "Officer Response Time", 6, colorbrewer.PuRd, durationFormat);
    }
}




