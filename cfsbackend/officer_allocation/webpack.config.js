var path = require("path");
var webpack = require("webpack");
var BundleTracker = require("webpack-bundle-tracker");
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {
    context: path.join(__dirname, "assets"),
    entry: {
        officer_allocation: "./js/officer_allocation"
    },
    output: {
        path: path.join(__dirname, "assets", "bundles"),
        filename: "[name]-[hash].js"
    },
    resolve: {
        extensions: ["", ".js"],
        fallback: [
            path.join(__dirname, "..", "core", "assets", "js")
        ]
    },
    plugins: [
        new CleanWebpackPlugin(['assets/bundles'], {
            verbose: true,
            dry: false
        }),
        new webpack.ProvidePlugin({
            $: "jquery",
            "window.jQuery": "jquery",
            "jQuery": "jquery"
        }),
        new ExtractTextPlugin("[name]-[hash].css")
    ],
    module: {
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