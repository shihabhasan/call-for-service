"use strict";

var url = "/api/map_info/";

var geojson;

var dashboard = new Page(
    {
        el: $('#dashboard').get(),
        template: "#map-template",
        data: {
            showing: 'call_volume',
            mapDrawn: false
        },
        filterUpdated: function (filter) {
            d3.json(
                buildURL(url, filter), _.bind(
                    function (error, newData) {
                        if (error) throw error;
                        this.set('loading', false);
                        this.set('initialload', false);
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

        dashboard.set(
            'beats', {
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
            pTop = bounds.top,
            pBottom = window.innerHeight,
            height = Math.max(10, pBottom - pTop - 100);

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
            var call_volume = dashboard.get('beats').call_volume[props.LAWBEAT],
                officer_response_time = dashboard.get('beats').officer_response_time[props.LAWBEAT],
                text;

            if (call_volume === undefined) {
                text = "No data.";
            } else {
                text = "Call Volume " +
                    fmt(dashboard.get('beats').call_volume[props.LAWBEAT], 'call_volume') +
                    "<br />Officer Response Time " +
                    fmt(
                        dashboard.get('beats').officer_response_time[props.LAWBEAT],
                        'officer_response_time');
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

            resize();
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
        var minValue = _(data).chain().pluck(key).min().value(),
            maxValue = _(data).chain().pluck(key).max().value(),
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

        var beats = _.reduce(
            data, function (memo, d) {
                memo[d.name] = d[key];
                return memo
            }, {});

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

