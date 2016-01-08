var path = require("path");
var webpack = require("webpack");
var BundleTracker = require("webpack-bundle-tracker");
var ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
  context: path.join(__dirname, "assets"),
  entry: {
    call_volume: "./js/call_volume",
    response_time: "./js/response_time",
    officer_allocation: "./js/officer_allocation",
    landing_page: "./js/landing_page"
  },
  output: {
    path: path.join(__dirname, "assets", "bundles"),
    filename: "[name]-[hash].js"
  },
  resolve: {
    extensions: ["", ".js"]
  },
  plugins: [
    new BundleTracker({
      filename: "./webpack-stats.json"
    }),
    new webpack.ProvidePlugin({
      $: "jquery",
      "window.jQuery": "jquery",
      "jQuery": "jquery"
    }),
    new ExtractTextPlugin("[name]-[hash].css"),
    new webpack.optimize.CommonsChunkPlugin({
      // (the commons chunk name)
      name: "commons",
      filename: "commons-[hash].js"

      // (Modules must be shared between 3 entries)
      // minChunks: 3
    })
  ],
  module: {
    loaders: [{
      test: /.js$/,
      exclude: /node_modules/,
      loaders: ["babel-loader"]
    }, {
      test: /\.html$/,
      loader: "html![name].[ext]"
    }, {
      test: /\.css$/,
      loader: ExtractTextPlugin.extract("style-loader", "css-loader")
    }, {
      test: /\.scss$/,
      loader: ExtractTextPlugin.extract("style-loader", "css-loader!sass-loader")
    }, {
      test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
      loader: "url-loader?limit=10000&mimetype=application/font-woff"
    }, {
      test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
      loader: "file-loader"
    }, {
      test: /\.(png|jpg|jpeg)$/,
      loader: "file-loader"
    }]
  },

  babel: {
    presets: ["es2015"]
  }
};
