import { toggleFilter } from "./core";

import d3 from "d3";
import nv from "nvd3";
import colorbrewer from "colorbrewer";
import Q from "q";
import L from "leaflet";
import _ from "underscore";

export var Heatmap = function(options) {
  // Expected data:
  // [{day: 0, hour: 0, value: x1}, {day: 0, hour: 1, value: x2}...
  // ...{day: 6, hour: 23, value: x168}]
  var self = this;
  var dashboard = options.dashboard;
  var colors = options.colors || colorbrewer.OrRd[7];
  var getValue = options.value || function(d) {
    return d.value;
  };
  var margin = {
    top: 0,
    right: 30,
    bottom: 0,
    left: 0
  };
  var fmt = options.fmt || function(x) {
    return x;
  };
  var measureName = options.measureName || "";

  var days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    times = ["12a", "1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a",
      "11a", "12p", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p",
      "9p", "10p", "11p", "12a"
    ];

  this.el = options.el;
  this.ratio = options.ratio || 2.5;

  this.drawn = false;

  this.ensureDrawn = function() {
    var deferred = Q.defer();

    function isDrawn() {
      if (self.drawn) {
        deferred.resolve();
      } else {
        setTimeout(isDrawn, 30);
      }
    }

    isDrawn();

    return deferred.promise;
  };

  this.getBounds = function() {
    var parent = d3.select(this.el).select("h3"),
      width = Math.min(parent.node().offsetWidth, parent.node().clientWidth) - margin.left - margin.right,
      height = (width / this.ratio) - margin.top - margin.bottom;

    return {
      width: width,
      height: height
    };
  };

  this.getGridSize = function() {
    var bounds = this.getBounds(),
      width = bounds.width,
      gridSize = Math.floor(width / this.ratio / 10);
    return gridSize;
  };

  this.getSVG = function() {
    var container = d3.select(this.el),
      svg = container.select("svg").select("g");

    return svg;
  };

  this.resize = function() {
    var bounds = self.getBounds(),
      svg = d3.select(this.el).select("svg");

    svg.attr("width", bounds.width)
      .attr("height", bounds.height);
  };

  this.drawLabels = function() {
    var gridSize = this.getGridSize(),
      svg = this.getSVG();

    svg.selectAll(".dayLabel")
      .remove()
      .data(days)
      .enter()
      .append("text")
      .text(
        function(d) {
          return d;
        })
      .attr("x", gridSize)
      .attr(
        "y",
        function(d, i) {
          return (i + 1) * gridSize;
        })
      .style("text-anchor", "end")
      .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
      .attr("class", "dayLabel axis");

    svg.selectAll(".timeLabel")
      .remove()
      .data(times)
      .enter()
      .append("text")
      .text(
        function(d) {
          return d;
        })
      .attr(
        "x",
        function(d, i) {
          return (i + 1) * gridSize;
        })
      .attr("y", gridSize * 1)
      .style("text-anchor", "middle")
      .attr("transform", "translate(-4,-8)")
      .attr("class", "timeLabel axis");
  };

  this.create = function() {
    var bounds = this.getBounds(),
      container = d3.select(this.el),
      width = bounds.width,
      height = bounds.height,
      gridSize = Math.floor(width / this.ratio / 10);

    this.origGridSize = gridSize;

    container
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", "0 0 " + width + " " + height)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    this.drawLabels();

    d3.select(window).on("resize", function() {
      self.resize();
    });

    this.drawn = true;
  };

  this.update = function(data) {
    self.ensureDrawn().then(function() {
      self._update(data);
    });
  };

  this._update = function(data) {
    var container = d3.select(this.el),
      bounds = self.getBounds(),
      width = bounds.width,
      height = bounds.height,
      gridSize = Math.floor(width / this.ratio / 10),
      svg = container.select("svg").select("g"),
      tooltip = nv.models.tooltip();

    if (_.isEmpty(data)) {
      var noDataText = svg.selectAll(".nv-noData").data(["No Data Available"]);

      noDataText.enter().append("text")
        .attr("class", "nvd3 nv-noData")
        .attr("dy", "-.7em")
        .style("text-anchor", "middle");

      noDataText
        .attr("x", width / 2)
        .attr("y", height / 2)
        .text(function(d) {
          return d;
        });

      return;
    } else {
      svg.selectAll(".nv-noData").remove();
    }

    var values = _.map(data, getValue);
    var scale = d3.scale.quantile().domain(values).range(colors);

    var hours = svg.selectAll(".hour").data(data);

    hours.enter()
      .append("rect")
      .attr(
        "x",
        function(d) {
          return (d.hour + 1) * gridSize;
        })
      .attr(
        "y",
        function(d) {
          return margin.top + (d.day + 1) * gridSize;
        })
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("class", "hour bordered")
      .attr("width", gridSize)
      .attr("height", gridSize);

    hours.exit().remove();
    hours.style("fill", "#F6F6F6");
    hours.transition().duration(1000).style("fill", function(d) {
      return scale(d.value);
    });

    var tooltipData = function(d, i) {
      return {
        key: "Call Volume",
        value: "Call Volume",
        series: [{
          key: "Avg",
          value: fmt(getValue(d)),
          color: scale(getValue(d))
        }],
        data: d,
        index: i,
        e: d3.event
      };
    };

    hours.on("mouseover", function (d, i) {
      var hideTooltip = _.isUndefined(getValue(d));
      if (hideTooltip) {
        tooltip.hidden(true);
      } else {
        tooltip.data(tooltipData(d, i)).hidden(false);
      }
    }).on("mouseout", function () {
      tooltip.hidden(true);
    }).on("mousemove", function () {
      tooltip.position({top: d3.event.pageY, left: d3.event.pageX})();
    });

    svg.selectAll(".legend").remove();

    var legend = svg.selectAll(".legend").data(
        [0].concat(scale.quantiles()),
        function(d) {
          return d;
        }).enter().append("g").attr("class", "legend")
      .attr("transform", "translate(" + self.origGridSize + ", 0)");

    legend.append("rect")
      .attr(
        "x",
        function(d, i) {
          return self.origGridSize * i * 4;
        })
      .attr("y", 0)
      .attr("width", self.origGridSize)
      .attr("height", self.origGridSize / 2)
      .style(
        "fill",
        function(d, i) {
          return colors[i];
        });

    var textX = function(d, i) {
      return self.origGridSize * (i * 4 + 1) + 8;
    };

    var text = legend.append("text")
      .attr("x", textX)
      .attr("y", 0);

    // text.append("tspan").attr("class", "axis").text(
    //     function (d, i) {
    //       return ordinalize(Math.floor((i / buckets) * 100)) + " percentile";
    //     }).attr("x", textX).attr("dy", self.origGridSize / 3);

    text.append("tspan").attr("class", "axis").text(
      function(d, i) {
        var q = scale.quantiles();
        if (q[i]) {
          return [fmt(d), "-", fmt(q[i]), measureName].join(" ");
        } else {
          return fmt(d) + "+ " + measureName;
        }
        // return "≥ " + fmt(d);
      }).attr("x", textX).attr("dy", self.origGridSize / 3);
  };

  dashboard.on("complete", function() {
    self.create();
  });
};


export var DiscreteBarChart = function(options) {
  var self = this;
  var dashboard = options.dashboard;
  var fmt = options.fmt || function(x) {
    return x;
  };
  var rotateLabels = options.rotateLabels || false;
  var getX = options.x;
  var getY = options.y;
  var width, height;
  var colors = options.colors || ["#2171b5"];
  var container = d3.select(options.el);

  this.el = options.el;
  this.filter = options.filter;
  this.ratio = options.ratio || 1.25;

  this.create = function() {
    var container = d3.select(this.el);
    width = container.node().clientWidth;
    height = width / self.ratio;

    container
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .style("height", height + "px")
      .style("width", width + "px");
  };

  this.update = function(data) {
    var svg = d3.select(self.el).select("svg");
    nv.addGraph(function() {
      var chart = nv.models.discreteBarChart()
        .x(getX)
        .y(getY)
        .height(height)
        .width(width)
        .margin({
          "bottom": 150,
          "right": 80
        })
        .color(colors);

      chart.yAxis.tickFormat(fmt);

      svg.datum(data).call(chart);

      svg.selectAll(".nv-bar").style("cursor", "pointer");

      chart.discretebar.dispatch.on("elementClick", function(e) {
        if (e.data.id) {
          toggleFilter(dashboard, self.filter, e.data.id);
        }
      });

      if (rotateLabels) {
        // Have to call this both during creation and after updating the chart
        // when the window is resized.
        var doRotateLabels = function() {
          var xTicks = d3.select(self.el + " .nv-x.nv-axis > g").selectAll("g");

          xTicks.selectAll("text")
            .style("text-anchor", "start")
            .attr("dx", "0.25em")
            .attr("dy", "0.75em")
            .attr("transform", "rotate(45 0,0)");
        };

        doRotateLabels();
      }

      nv.utils.windowResize(function() {
        self.resize(chart);
        if (rotateLabels) {
          doRotateLabels();
        }
      });

      return chart;
    });
  };

  this.resize = function(chart) {
    width = container.node().clientWidth;
    height = Math.ceil(width / self.ratio);

    container.select("svg")
      .attr("width", width)
      .attr("height", height)
      .style("height", height + "px")
      .style("width", width + "px");

    chart.height(height).width(width);

    chart.update();
  };

  this.create();
};

export var HorizontalBarChart = function(options) {
  var self = this;
  var dashboard = options.dashboard;
  var fmt = options.fmt || function(x) {
    return x;
  };
  var getX = options.x;
  var getY = options.y;
  var colors = options.colors || ["#2171b5"];
  var container, width, height;

  this.el = options.el;
  this.filter = options.filter;
  this.ratio = options.ratio || 0.5;

  this.create = function() {
    container = d3.select(this.el);
    width = container.node().clientWidth;
    height = Math.ceil(width / self.ratio);

    container
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .style("height", height + "px")
      .style("width", width + "px");
  };

  this.update = function(data) {
    var svg = d3.select(self.el).select("svg");
    nv.addGraph(
      function() {
        var chart = nv.models.multiBarHorizontalChart()
          .x(getX)
          .y(getY)
          .height(height)
          .width(width)
          .margin({
            left: 60,
            right: 60,
            bottom: 40
          })
          .duration(0)
          .showControls(false)
          .showLegend(false)
          .barColor(colors);

        chart.yAxis.tickFormat(fmt);

        svg.datum(data).call(chart);

        // More click filtering
        svg.selectAll(".nv-bar").style("cursor", "pointer");
        chart.multibar.dispatch.on(
          "elementClick",
          function(e) {
            toggleFilter(dashboard, self.filter, e.data.id);
          });

        nv.utils.windowResize(function() {
          self.resize(chart);
        });

        return chart;
      });
  };

  this.resize = function(chart) {
    width = container.node().clientWidth;
    height = Math.ceil(width / self.ratio);

    container.select("svg")
      .attr("width", width)
      .attr("height", height)
      .style("height", height + "px")
      .style("width", width + "px");

    chart.height(height).width(width);

    chart.update();
  };

  dashboard.on("complete", function() {
    self.create();
  });
};

export var DurhamMap = function(options) {
  var self = this;
  var dashboard = options.dashboard;
  var fmt = options.format;

  this.el = options.el || "#map";
  this.container = options.container || "#map-container";
  this.ratio = options.ratio || 0.77;
  this.colorScheme = options.colorScheme || colorbrewer.Reds;
  this.dataDescr = options.dataDescr;

  this.geojson = null;
  this.drawn = false;

  this.ensureDrawn = function() {
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

  this.create = function() {
    var northEast = L.latLng(36.13898378070337, -78.75068664550781),
      southWest = L.latLng(35.860952532806905, -79.04937744140625),
      bounds = L.latLngBounds(southWest, northEast);

    var map = L.map(
      "map", {
        center: [36.0, -78.9],
        zoom: (d3.select(self.container).node().clientWidth <= 660) ? 11 : 12,
        maxBounds: bounds,
        minZoom: 11,
        maxZoom: 16,
        scrollWheelZoom: false
      });

    function resize() {
      var container = d3.select(self.container).node(),
        width = container.clientWidth,
        height = width / self.ratio;

      d3.select(self.el)
        .style("width", width + "px")
        .style("height", height + "px");

      map.invalidateSize();
    }

    d3.select(window).on("resize.map", function() {
      resize();
    });

    L.tileLayer(
      "//stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}.png", {
        attribution: "Map tiles by <a href=\"http://stamen.com\">Stamen Design</a>, under <a href=\"http://creativecommons.org/licenses/by/3.0\">CC BY 3.0</a>. Data by <a href=\"http://openstreetmap.org\">OpenStreetMap</a>, under <a href=\"http://www.openstreetmap.org/copyright\">ODbL</a>.",
        maxZoom: 18
      }).addTo(map);

    var info = L.control();

    info.onAdd = function() {
      self._div = L.DomUtil.create("div", "mapinfo");
      self._div.innerHTML = "<div>Hover over a beat</div>";
      return self._div;
    };

    // method that we will use to update the control based on feature
    // properties passed
    info.update = function(props) {
      if (props) {
        var displayData = dashboard.get("data.map_data")[props.LAWBEAT],
          text;

        if (displayData === undefined) {
          text = "No data.";
        } else {
          text = self.dataDescr + " " +
            fmt(displayData);
        }

        self._div.innerHTML = "<h4>Beat " + props.LAWBEAT + "</h4>" +
          "<div>" + text + "</div>";
      } else {
        self._div.innerHTML = "<div>Hover over a beat</div>";
      }
    };

    info.addTo(map);

    function highlightFeature(e) {
      var layer = e.target;

      layer.setStyle({
        dashArray: "",
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

      layer.setStyle({
        weight: 2,
        dashArray: "3",
        fillOpacity: 0.8
      });

      if (!L.Browser.ie && !L.Browser.opera) {
        layer.bringToFront();
      }

      info.update();
    }

    function toggleBeat(e) {
      var layer = e.target;
      toggleFilter(dashboard, "beat",
        dashboard.get("data.beat_ids")[layer.feature.properties.LAWBEAT]);
    }

    function onEachFeature(feature, layer) {
      layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: toggleBeat
      });
    }

    d3.json(
      "/static/beats.json",
      function(json) {
        json.features = _(json.features).reject(
          function(d) {
            return d.properties.LAWDIST === "DSO";
          });

        var myStyle = {
          color: "white",
          dashArray: "3",
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
  };

  this._update = function(data) {
    var numColors = 5;

    function updateLegend(legendData) {
      if (!legendData) {
        return;
      }

      var legend = d3.select("#legend");
      legend.selectAll("ul").remove();
      var list = legend.append("ul").classed("list-inline", true);
      var keys = list.selectAll("li.key").data(legendData);
      keys.enter()
        .append("li")
        .classed("key", true)
        .style("border-left-width", "30px")
        .style("border-left-style", "solid")
        .style("padding", "0 10px")
        .style(
          "border-left-color",
          function(d) {
            return d[0];
          })
        .text(
          function(d) {
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
      _.range(numColors),
      function(n) {
        var start = Math.ceil(scale.invert(n)),
          end = Math.floor(scale.invert(n + 1)),
          text;

        if (start >= end) {
          text = fmt(start);
        } else {
          text = fmt(start) + "-" + fmt(end);
        }

        return [
          colors[n],
          text
        ];
      });

    updateLegend(legendData);

    var styleFn = function(d) {
      var n = Math.min(
        numColors - 1, Math.floor(scale(data[d.properties.LAWBEAT])));
      return {
        fillColor: colors[n] || "gray",
        weight: 2,
        opacity: 1,
        color: "white",
        dashArray: "3",
        fillOpacity: 0.8
      };
    };

    self.geojson.setStyle(styleFn);
  };

  this.update = function(newData) {
    self.ensureDrawn().then(function() {
      self._update(newData);
    });
  };

  dashboard.on("complete", function() {
    self.create();
  });
};
