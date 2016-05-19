var path = require("path");
var webpack = require("webpack");
var BundleTracker = require("webpack-bundle-tracker");
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var CleanWebpackPlugin = require('clean-webpack-plugin');


module.exports = {
    context: path.join(__dirname, "assets"),
    entry: {
        call_volume: "./js/call_volume",
        response_time: "./js/response_time",
        officer_allocation: "./js/officer_allocation",
        landing_page: "./js/landing_page",
        call_list: "./js/call_list",
        call_map: "./js/call_map",
    },
    output: {
        path: path.join(__dirname, "assets", "bundles"),
        filename: "[name]-[hash].js"
    },
    resolve: {
        extensions: ["", ".js"],
        alias: {
            // This prevents bootstrap-daterangepicker from using its own jQuery.
            "jquery": path.join(__dirname, "node_modules/jquery/dist/jquery")
        }
    },
    plugins: [
        new CleanWebpackPlugin(['assets/bundles'], {
            verbose: true,
            dry: false
        }),
        new BundleTracker({
            filename: "./webpack-stats.json"
        }),
        new webpack.ProvidePlugin({
            $: "jquery",
            "window.jQuery": "jquery",
            "jQuery": "jquery",
            "L": "leaflet"
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
        noParse: [
            /proj4\.js/
        ],
        loaders: [{
            test: /.js$/,
            exclude: /node_modules/,
            loaders: ["babel?compact=false"]
        }, {
            test: /\.html$/,
            loader: "raw"
        }, {
            test: /\.css$/,
            loader: ExtractTextPlugin.extract("style", "css")
        }, {
            test: /\.scss$/,
            loader: ExtractTextPlugin.extract("style", "css!sass")
        }, {
            test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
            loader: "url?limit=10000&mimetype=application/font-woff"
        }, {
            test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
            loader: "file"
        }, {
            test: /\.(png|jpg|jpeg)$/,
            loader: "file"
        }]
    },

    babel: {
        presets: ["es2015"]
    }
};
