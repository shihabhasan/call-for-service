var configs = require("./webpack.config");
var webpack = require("webpack");

configs.forEach(function (config) {
    config.plugins.push(
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings: false
            }
        })
    );
});

module.exports = configs;
