import "../styles/officer_allocation.scss";

import {
  Page,
  Filter,
  buildURL,
  monitorChart,
  cloneFilter,
  updateHash,
  buildQueryParams,
} from "core";

import $ from "jquery";
import _ from "underscore-contrib";
import d3 from "d3";
import moment from "moment";
import nv from "nvd3";

var url = "/api/officer_allocation/";

var OfficerAllocationFilter = Filter.extend({
  template: require("../templates/officer_allocation_filter.html")
});

var dashboard = new Page({
  components: {
    "Filter": OfficerAllocationFilter
  },
  el: document.getElementById("dashboard"),
  template: require("../templates/officer_allocation.html"),
  data: {
    data: {
      "allocation_over_time": []
    }
  },
  filterUpdated: function(filter) {
    d3.json(buildURL(url, filter), _.bind(function(error, newData) {
      if (error) throw error;
      this.set("loading", false);
      this.set("initialload", false);
      newData = cleanupData(newData);
      this.set("data", newData);
    }, this));
  }
});

dashboard.on("filterByDate", function(event, span) {
  var pastSunday = moment().day("Sunday").startOf("day");

  var f = cloneFilter(dashboard);
  if (span === "7days") {
    f["time__gte"] = pastSunday.clone().subtract(7, "days").format("YYYY-MM-DD");
    f["time__lte"] = pastSunday.clone().format("YYYY-MM-DD");
  } else if (span === "28days") {
    f["time__gte"] = pastSunday.clone().subtract(28, "days").format("YYYY-MM-DD");
    f["time__lte"] = pastSunday.clone().format("YYYY-MM-DD");
  } else if (span == "ytd") {
    f["time__gte"] = moment().clone().startOf("year").format("YYYY-MM-DD");
    delete f["time__lte"];
  }

  updateHash(buildQueryParams(f));
  return false;
});

function cleanupData(data) {
  var indate = d3.time.format("%H:%M:%S");

  var temp_allocation_data = [{
    key: "Citizen-Initiated Call",
    values: []
  }, {
    key: "Officer-Initiated Call",
    values: []
  }, {
    key: "Directed Patrol",
    values: []
  }, {
    key: "Out of Service",
    values: []
  }, {
    key: "Patrol",
    values: []
  }];

  _.sortBy(_.keys(data.allocation_over_time)).forEach(function(k) {
    var oos = d3.round(data.allocation_over_time[k]["OUT OF SERVICE"].avg_volume, 2),
      dp = data.allocation_over_time[k]["IN CALL - DIRECTED PATROL"].avg_volume,
      oic = data.allocation_over_time[k]["IN CALL - SELF INITIATED"].avg_volume,
      cic = data.allocation_over_time[k]["IN CALL - CITIZEN INITIATED"].avg_volume,
      pat = data.allocation_over_time[k]["PATROL"].avg_volume,
      time = indate.parse(k);

    temp_allocation_data[0].values.push({
      "x": time,
      "y": cic
    });
    temp_allocation_data[1].values.push({
      "x": time,
      "y": oic
    });
    temp_allocation_data[2].values.push({
      "x": time,
      "y": oos
    });
    temp_allocation_data[3].values.push({
      "x": time,
      "y": dp
    });
    temp_allocation_data[4].values.push({
      "x": time,
      "y": pat
    });
  });

  data.allocation_over_time = temp_allocation_data;

  data.on_duty_by_beat = [{
    key: "Average On Duty",
    values: _.chain(data.on_duty_by_beat)
      .filter(
        function(d) {
          return d.beat;
        })
      .sortBy(
        function(d) {
          return d.beat;
        })
      .value()
  }];

  data.on_duty_by_district = [{
    key: "Average On Duty",
    values: _.chain(data.on_duty_by_district)
      .filter(
        function(d) {
          return d.district;
        })
      .sortBy(
        function(d) {
          return d.district;
        })
      .value()
  }];

  return data;
}

monitorChart(dashboard, "data.allocation_over_time", buildAllocationOverTimeChart);

function buildAllocationOverTimeChart(data) {
  var containerID = '#allocation-over-time';
  var container = d3.select(containerID);
  var parentWidth = container.node().clientWidth;
  var width = parentWidth;
  var height = width / 2;

  var svg = d3.select(containerID + " svg");
  svg.attr("width", width)
    .attr("height", height)
    .style("height", height + "px")
    .style("width", width + "px");

  var resize = function(chart) {
    width = container.node().clientWidth;
    height = width / 2;

    container.select("svg")
      .attr("width", width)
      .attr("height", height)
      .style("height", height + "px")
      .style("width", width + "px");

    chart.height(height).width(width);

    chart.update();
  };

  nv.addGraph(function() {
    var chart = nv.models.stackedAreaChart()
      .options({
        height: height,
        width: width,
        margin: {
          "right": 50
        },
        transitionDuration: 300,
        useInteractiveGuideline: true,
        forceY: [0],
        // Remove the "Stream" option
        controlOptions: ['Stacked', 'Expanded'],
      });

    // Disable legend clicking
    chart.legend.options({
        updateState: false,
    });


    chart.xAxis
      .axisLabel("Time")
      .tickFormat(function(d) {
        return d3.time.format("%X")(new Date(d));
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
      .headerFormatter(function(d) {
        return d;
      });

    svg.datum(data).call(chart);
    nv.utils.windowResize(function() {
      resize(chart);
    });

    return chart;
  });
}

function removeStreamControl(chartID) {
    // Remove the "stream" option from the chart
    var streamControl = $('#allocation-over-time .nv-controlsWrap > .nv-legend > g > .nv-series:nth-child(2)');
    var expandedControl = $('#allocation-over-time .nv-controlsWrap > .nv-legend > g > .nv-series:nth-child(3)');

    expandedControl.attr('transform', streamControl.attr('transform'));
    streamControl.remove();
}
