import "leaflet/dist/leaflet.css";
import "prunecluster/dist/LeafletStyleSheet.css";

import {
    Page,
    buildURL,
    monitorChart
} from "./core";

import Q from "q";
import L from "leaflet";
import d3 from "d3";
import $ from "jquery";
import _ from "underscore-contrib";
import proj4 from "proj4";

import "leaflet-easybutton";

L.Icon.Default.imagePath = '/static/img/leaflet/';

var Cluster = require(
    "exports?PruneClusterForLeaflet&PruneCluster!prunecluster/dist/PruneCluster.js");
var PruneClusterForLeaflet = Cluster.PruneClusterForLeaflet;
var PruneCluster = Cluster.PruneCluster;

var utm = "+proj=utm +zone=32";
var ncStatePlane = "+proj=lcc +lat_1=36.16666666666666 +lat_2=34.33333333333334 +lat_0=33.75 +lon_0=-79 +x_0=609601.2192024384 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs"
var wgs84 = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs";

var url = "/api/call_map/";

var dashboard = new Page({
    el: $("#dashboard").get(),
    template: require("../templates/call_map.html"),
    data: {
        loading: true,
        initialload: true,
        data: {}
    },
    filterUpdated: function (filter) {
        d3.json(buildURL(url, filter), _.bind(function (error, newData) {
            if (error) throw error;
            this.set("loading", false);
            this.set("initialload", false);
            this.set("data", cleanData(newData));
        }, this));
    }
});

function cleanData(data) {
    var locations = data.locations.map(function (datum) {
        var loc = proj4(ncStatePlane, wgs84, [datum[0], datum[1]]);
        return {
            lat: loc[1],
            lng: loc[0],
            address: _([datum[2], datum[3]]).reject(_.isNull).join(" "),
            street_num: datum[2],
            street_name: datum[3],
            business: datum[4]
        }
    });

    data.locations = locations;

    data.top_locations = getTopAddresses(locations, 20);
    console.log(data.top_locations);

    return data;
}

function getTopAddresses (locations, count) {
    locations = _(locations).reject(function (d) {
        return _.isNull(d.street_name) || d.street_name === "";
    });

    var data = d3.nest()
        .key(function (d) { return d.address; })
        .rollup(function (v) {
            return {
                count: v.length,
                business: _.chain(v)
                    .map(function (d) { return d.business })
                    .compact()
                    .unique()
                    .value()
                    .join(", ")
            }
        })
        .entries(locations)
        .sort(function (a, b) { return b.values.count - a.values.count })
        .slice(0, count);

    console.log(data);

    return data.map(function (d) {
        return {
            address: d.key,
            business: d.values.business,
            total: d.values.count
        }
    });
}

var DurhamClusterMap = function (options) {
    var self = this;
    var dashboard = options.dashboard;

    this.el = options.el || "#map";
    this.container = options.container || "#map-container";
    this.ratio = options.ratio || 0.77;

    this.geojson = null;
    this.drawn = false;

    this.pruneCluster = new PruneClusterForLeaflet();

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
            "map", {
                center: [36.0, -78.9],
                zoom: 11,
                maxBounds: bounds,
                minZoom: 11,
                maxZoom: 18,
                scrollWheelZoom: false
            });

        map.addLayer(this.pruneCluster);

        var centerBtn = L.easyButton('fa-crosshairs', function (btn, map) {
            map.fitBounds(bounds);
        });

        centerBtn.addTo(map);

        function resize() {
            var container = d3.select(self.container).node(),
                width = container.clientWidth,
                height = width / self.ratio;

            d3.select(self.el)
                .style("width", width + "px")
                .style("height", height + "px");

            map.invalidateSize();
        }

        d3.select(window).on("resize.map", function () {
            resize();
        });

        L.tileLayer(
            "//stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}.png", {
                attribution: "Map tiles by <a href=\"http://stamen.com\">Stamen Design</a>, under <a href=\"http://creativecommons.org/licenses/by/3.0\">CC BY 3.0</a>. Data by <a href=\"http://openstreetmap.org\">OpenStreetMap</a>, under <a href=\"http://www.openstreetmap.org/copyright\">ODbL</a>.",
                maxZoom: 18
            }).addTo(map);

        function onEachFeature(feature, layer) {
            layer.on({});
        }

        d3.json(
            "/static/beats.json",
            function (json) {
                json.features = _(json.features).reject(
                    function (d) {
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

    this._update = function (data) {
        this.pruneCluster.RemoveMarkers();

        var datum;

        var markers = data.map(function (datum) {
            var marker = new PruneCluster.Marker(datum.lat, datum.lng);

            if (datum.business) {
                marker.data.popup = `${datum.address} (${datum.business})`
            } else {
                marker.data.popup = datum.address;
            }

            return marker;
        });

        this.pruneCluster.RegisterMarkers(markers);
        this.pruneCluster.ProcessView();
    };

    this.update = function (newData) {
        self.ensureDrawn().then(function () {
            self._update(newData);
        });
    };

    dashboard.on("complete", function () {
        self.create();
    });
};

var map = new DurhamClusterMap({
    el: "#map",
    dashboard: dashboard,
    ratio: 0.9
});

monitorChart(dashboard, "data.locations", map.update)