var path = require("path");
var webpack = require("webpack");
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
    babel: {
        presets: ["es2015"]
    }
};