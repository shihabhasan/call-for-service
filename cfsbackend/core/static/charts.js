var DiscreteBarChart = function (options) {
    var self = this;
    var dashboard = options.dashboard;
    var fmt = options.fmt || function (x) { return x; };
    var rotateLabels = options.rotateLabels || false;
    var getX = options.x;
    var getY = options.y;

    this.el = options.el;
    this.filter = options.filter;
    this.ratio = options.ratio || 1.25;


    this.create = function () {
        var container = d3.select(this.el);
        var width = container.node().clientWidth;
        var height = width / self.ratio;

        var svg = container
            .append("svg")
            .attr("width", width)
            .attr("height", height);
    };

    this.update = function (data) {
        var svg = d3.select(self.el).select("svg");
        nv.addGraph(function () {
            var chart = nv.models.discreteBarChart()
                .x(getX)
                .y(getY)
                .margin({"bottom": 150, "right": 50});

            chart.yAxis.tickFormat(fmt);

            svg.datum(data).call(chart);

            svg.selectAll('.nv-bar').style('cursor', 'pointer');

            chart.discretebar.dispatch.on('elementClick', function (e) {
                if (e.data.id) {
                    toggleFilter(dashboard, self.filter, e.data.id);
                }
            });

            if (rotateLabels) {
                // Have to call this both during creation and after updating the chart
                // when the window is resized.
                var doRotateLabels = function () {
                    var xTicks = d3.select(self.el + ' .nv-x.nv-axis > g').selectAll('g');

                    xTicks.selectAll('text')
                        .style("text-anchor", "start")
                        .attr("dx", "0.25em")
                        .attr("dy", "0.75em")
                        .attr("transform", "rotate(45 0,0)");
                };

                doRotateLabels();
            }

            nv.utils.windowResize(function () {
                chart.update();
                if (rotateLabels) {
                    doRotateLabels();
                }
            });

            return chart;
        })
    }

    this.create();
}

var HorizontalBarChart = function (options) {
    var self = this;
    var dashboard = options.dashboard;
    var getX = options.x;
    var getY = options.y;

    this.el = options.el;
    this.filter = options.filter;
    this.ratio = options.ratio || 0.5;

    this.create = function () {
        var container = d3.select(this.el);
        var width = container.node().clientWidth;
        var height = width / self.ratio;

        var svg = container
            .append("svg")
            .attr("width", width)
            .attr("height", height);
    };

    this.update = function (data) {
        var svg = d3.select(self.el).select("svg");
        nv.addGraph(
            function () {
                var chart = nv.models.multiBarHorizontalChart()
                    .x(getX)
                    .y(getY)
                    .duration(250)
                    .showControls(false)
                    .showLegend(false)
                    .barColor(d3.scale.category20().range());


                chart.yAxis.tickFormat(d3.format(",d"));

                svg.datum(data).call(chart);

                // More click filtering
                svg.selectAll('.nv-bar').style('cursor', 'pointer');
                chart.multibar.dispatch.on(
                    'elementClick', function (e) {
                        toggleFilter(dashboard, self.filter, e.data.id);
                    });

                nv.utils.windowResize(chart.update);

                return chart;
            });
    };

    dashboard.on('complete', function () {
        self.create();
    });
};

var DurhamMap = function (options) {
    var self = this;
    var dashboard = options.dashboard;
    var fmt = options.format;

    this.el = options.el;
    this.ratio = options.ratio || 0.77;
    this.colorScheme = options.colorScheme || colorbrewer.Reds;

    this.geojson = null;
    this.drawn = false;

    this.ensureDrawn = function () {
        var deferred = Q.defer();

        function isMapDrawn() {
            if (self.drawn) {
                deferred.resolve();
            } else {
                setTimeout(isMapDrawn, 30);
            }
        }

        isMapDrawn();

        return deferred.promise;
    };

    this.create = function () {
        var northEast = L.latLng(36.13898378070337, -78.75068664550781),
            southWest = L.latLng(35.860952532806905, -79.04937744140625),
            bounds = L.latLngBounds(southWest, northEast);

        var map = L.map(
            'map', {
                center: [36.0, -78.9],
                zoom: 12,
                maxBounds: bounds,
                minZoom: 11,
                maxZoom: 16,
                scrollWheelZoom: false
            });

        function resize() {
            var container = d3.select("#map-container").node(),
                width = container.clientWidth,
                bounds = container.getBoundingClientRect(),
                height = width / self.ratio;

            d3.select(self.el)
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
            self._div = L.DomUtil.create('div', 'mapinfo');
            self.update();
            return self._div;
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

                self._div.innerHTML = '<h4>Beat ' + props.LAWBEAT + '</h4>' +
                    "<div>" + text + "</div>";
            } else {
                self._div.innerHTML = "<div>Hover over a beat</div>";
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
            toggleFilter(dashboard, 'beat',
                dashboard.get('data.beat_ids')[layer.feature.properties.LAWBEAT]);
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

                self.geojson = L.geoJson(
                    json, {
                        style: myStyle,
                        onEachFeature: onEachFeature
                    }).addTo(map);


                resize();
                self.drawn = true;
            });
    }

    this._update = function (data) {
        var numColors = 5;

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

        var minValue = _(data).chain().values().min().value(),
            maxValue = _(data).chain().values().max().value(),
            colors;

        numColors = Math.min(numColors, maxValue - minValue + 1);

        if (numColors < 3) {
            colors = this.colorScheme[3].slice(3 - numColors);
        } else {
            colors = this.colorScheme[numColors + 1].slice(1);
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

        self.geojson.setStyle(styleFn);
    }

    this.update = function (newData) {
        self.ensureDrawn().then(function () {
            self._update(newData);
        })
    };

    dashboard.on('complete', function () {
        self.create();
    });
}