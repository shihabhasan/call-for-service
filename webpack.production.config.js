var config = require("./webpack.config");
var webpack = require("webpack");

config.plugins.push(
  new webpack.optimize.UglifyJsPlugin({
    compress: {
      warnings: false,
      drop_console: true
    }
  })
);

config.watch = false;

module.exports = config;
