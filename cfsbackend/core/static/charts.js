var HorizontalBarChart = function (options) {
    this.el = options.el;
    this.filter = options.filter;
    this.ratio = options.ratio || 2;

    this.create = _.bind(function () {
        var container = d3.select(this.el);
        var width = container.node().clientWidth;
        var height = width * this.ratio;

        var svg = container
            .append("svg")
            .attr("width", width)
            .attr("height", height);
    }, this);

    this.update = _.bind(function (data) {
        var svg = d3.select(this.el).select("svg");
        nv.addGraph(
            function () {
                var chart = nv.models.multiBarHorizontalChart()
                    .x(function (d) { return d.name })
                    .y(function (d) { return d.volume })
                    .duration(250)
                    .showControls(false)
                    .showLegend(false);

                chart.yAxis.tickFormat(d3.format(",d"));

                svg.datum(data).call(chart);

                // More click filtering
                svg.selectAll('.nv-bar').style('cursor', 'pointer');
                chart.multibar.dispatch.on(
                    'elementClick', function (e) {
                        toggleFilter(dashboard, this.filter, e.data.id);
                    });

                nv.utils.windowResize(chart.update);

                return chart;
            });
    }, this);

    this.create();
};