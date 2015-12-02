var HorizontalBarChart = function (options) {
    var self = this;

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
                    .x(function (d) { return d.name })
                    .y(function (d) { return d.volume })
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

    this.create();
};