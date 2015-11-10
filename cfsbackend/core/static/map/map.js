"use strict";

var url = "/api/map_info/";
var charts = {};
var outFormats = {
    "month": "%b %y",
    "week": "%m/%d/%y",
    "day": "%a %m/%d",
    "hour": "%m/%d %H:%M"
};

var geojson, control;

var dashboard = new Page(
    {
        el: $('body').get(),
        template: "#map-template",
        data: {
            showing: 'call_volume',
            mapDrawn: false
        },
        filterUpdated: function (filter) {
            d3.json(
                buildURL(filter), _.bind(
                    function (error, newData) {
                        if (error) throw error;
                        this.set('loading', false);
                        this.set('initialload', false);
                        newData = cleanupData(newData);
                        this.set('data', newData);
                    }, this));
        }
    });

dashboard.observe(
    'data', function (newData) {
        if (newData === undefined) {
            return;
        }

        var call_volume = _.reduce(
            newData.call_volume, function (memo, d) {
                memo[d.name] = d.volume;
                return memo
            }, {});

        var officer_response_time = _.reduce(
            newData.officer_response_time, function (memo, d) {
                memo[d.name] = d.mean;
                return memo
            }, {});

        dashboard.set('beats', {
            call_volume: call_volume,
            officer_response_time: officer_response_time
        });

        ensureMapIsDrawn().then(
            function () {
                updateMap(newData)
            });
    });

dashboard.observe(
    'showing', function (val) {
        ensureMapIsDrawn().then(
            function () {
                updateMap(dashboard.get('data'));
            });
    });

dashboard.on(
    'showing', function (event, state) {
        dashboard.set('showing', state);
        return false;
    });

dashboard.on('complete', drawMap);

function drawMap() {
    var width = d3.select("#map-container").node().clientWidth,
        height = width * 1.15;

    d3.select("#map")
        .style('width', width + 'px')
        .style('height', height + 'px');

    var northEast = L.latLng(36.13898378070337, -78.75068664550781),
        southWest = L.latLng(35.860952532806905, -79.04937744140625),
        bounds = L.latLngBounds(southWest, northEast);

    var map = L.map('map', {
        center: [36.0, -78.9],
        zoom: 12,
        maxBounds: bounds,
        minZoom: 11,
        maxZoom: 18
    });


    L.tileLayer(
        'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}',
        {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
            maxZoom: 18,
            id: 'dpdcfs.cigtj42c107u5tpkn9bxnh6mo',
            accessToken: 'pk.eyJ1IjoiZHBkY2ZzIiwiYSI6ImNpZ3RqNDNoNzA3dTl0cGtudnd6dTVjYmYifQ.PVmca7xR3BwLEfN4HWgVvQ'
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
            this._div.innerHTML = '<h4>Beat ' + props.LAWBEAT + '</h4>' +
                "<div>Call Volume " +
                fmt(dashboard.get('beats').call_volume[props.LAWBEAT], 'call_volume') +
                "<br />Officer Response Time " +
                fmt(
                    dashboard.get('beats').officer_response_time[props.LAWBEAT],
                    'officer_response_time') +
                "</div>";
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
                fillOpacity: 0.6
            });

        if (!L.Browser.ie && !L.Browser.opera) {
            layer.bringToFront();
        }

        info.update();
    }

    function onEachFeature(feature, layer) {
        layer.on(
            {
                mouseover: highlightFeature,
                mouseout: resetHighlight
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
            dashboard.set('mapDrawn', true);
        });
}

function updateMap(data) {
    if (data.count === 0) {
        // handle no data
    }

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
        var colors = colorScheme[numColors + 1].slice(1)
            , minValue = _(data).chain().pluck(key).min().value()
            , maxValue = _(data).chain().pluck(key).max().value()
            , scale = d3.scale.linear()
            .domain([minValue, maxValue])
            .nice()
            .range([0, numColors])
            ;


        var beats = _.reduce(
            data, function (memo, d) {
                memo[d.name] = d[key];
                return memo
            }, {});

        var legendData = _.range(numColors);
        legendData = _.map(
            legendData, function (n) {
                return [
                    colors[n],
                    fmt(scale.invert(n)) + "-" + fmt(scale.invert(n + 1))
                ];
            });

        updateLegend(legendData);

        var styleFn = function (d) {
            var n = Math.min(
                numColors - 1, Math.floor(scale(beats[d.properties.LAWBEAT])));
            return {
                fillColor: colors[n],
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.8
            }
        };

        geojson.setStyle(styleFn);
    }

    if (dashboard.get('showing') === 'call_volume') {
        update(data.call_volume, 'volume', 5, colorbrewer.Reds);
    } else {
        update(data.officer_response_time, 'mean', 6, colorbrewer.Blues);
    }
}


//// ========================================================================
//// Functions
//// ========================================================================

function cleanupData(data) {
    return data;
}

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
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
    if (style === undefined) {
        style = dashboard.get('showing');
    }
    if (style === 'call_volume') {
        return d3.format(",.2f")(val).replace(/\.0+$/, "");
    } else if (style === 'officer_response_time') {
        return durationFormat(val);
    } else {
        return val;
    }
}