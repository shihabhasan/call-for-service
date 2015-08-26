var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
    context: __dirname,
    entry: {
        app: './cfsbackend/assets/js/main.js',
    },
    output: {
        path: require('path').resolve('./cfsbackend/assets/bundles/'),
        filename: '[name]-[hash].js'
    },

    module: {
        loaders: [
            {
                test: /\.css$/,
                loader: ExtractTextPlugin.extract("style-loader", "css-loader")
            }
        ]
    },

    plugins: [
        new BundleTracker({filename: './cfsbackend/webpack-stats.json'}),
        new ExtractTextPlugin("[name]-[hash].css")
    ]
}