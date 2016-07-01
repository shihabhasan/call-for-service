import "leaflet/dist/leaflet.css";
import "prunecluster/LeafletStyleSheet.css";

import {
    Page,
    buildURL,
    monitorChart
} from "./core";

import Q from "q";
import L from "leaflet";
import d3 from "d3";
import _ from "underscore-contrib";

import "leaflet-easybutton";

L.Icon.Default.imagePath = '/static/img/leaflet/';

var Cluster = require(
    "exports?PruneClusterForLeaflet&PruneCluster!prunecluster/dist/PruneCluster.js");
var PruneClusterForLeaflet = Cluster.PruneClusterForLeaflet;
var PruneCluster = Cluster.PruneCluster;

var url = "/api/call_map/";

var dashboard = new Page({
    el: document.getElementById("dashboard"),
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
        var loc = [datum[0], datum[1]];
        return {
            lat: loc[0],
            lng: loc[1],
            address: datum[2],
            business: datum[3],
            nature: datum[4]
        }
    });

    data.locations = locations;

    return data;
}

function getTopAddresses(locations, count) {
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

    return data.map(function (d) {
        return {
            address: d.key,
            business: d.values.business,
            total: d.values.count
        }
    });
}

var ClusterMap = function (options) {
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

    function resetTopLocations(map) {
        var bounds = map.getBounds();
        var locations = dashboard.get('data.locations');
        if (locations) {
            locations = locations.filter(function (d) {
                return bounds.contains(new L.LatLng(d.lat, d.lng))
            });
            dashboard.set('data.top_locations', getTopAddresses(locations, 20));
        }
    }

    this.create = function () {
        var northEast = L.latLng.apply(null, siteConfig.geo_ne_bound),
            southWest = L.latLng.apply(null, siteConfig.geo_sw_bound),
            bounds = L.latLngBounds(southWest, northEast);

        var map = L.map(
            "map", {
                center: siteConfig.geo_center,
                zoom: siteConfig.geo_default_zoom,
                maxBounds: bounds,
                minZoom: Math.min(siteConfig.geo_default_zoom, 11),
                maxZoom: Math.max(siteConfig.geo_default_zoom, 18),
                scrollWheelZoom: true
            });
        this.map = map;

        map.addLayer(this.pruneCluster);

        var centerBtn = L.easyButton('fa-crosshairs', function (btn, map) {
            map.fitBounds(bounds);
        });

        centerBtn.addTo(map);

        map.on('moveend', function () { resetTopLocations(map) });


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

            if (datum.nature) {
                marker.data.popup += `<br/>${datum.nature}`;
            }

            return marker;
        });

        this.pruneCluster.RegisterMarkers(markers);
        this.pruneCluster.ProcessView();

        resetTopLocations(this.map);
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

var map = new ClusterMap({
    el: "#map",
    dashboard: dashboard,
    ratio: 0.9
});

monitorChart(dashboard, "data.locations", map.update)