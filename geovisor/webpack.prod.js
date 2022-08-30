const HtmlWebPackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizer = require('css-minimizer-webpack-plugin');
const Terser = require ('terser-webpack-plugin');
const webpack = require('webpack');
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {

    mode: 'production',
    output : {
        clean: true,
        filename: 'main.[fullhash].js',
    },
    module: {
        rules: [
            {
                test: /\.html$/,
                loader: 'html-loader',
                options: {
                    sources: false,
                },
            },
            {
                test: /\.css$/i,
                exclude: /styles.css$/,
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /styles.css$/,
                use: [ MiniCssExtractPlugin.loader, 'css-loader']
            },
            {
                test: /\.(png|jpe?g|gif)$/,
                loader: 'file-loader',
                options: {
                    outputPath: './assets/img/',
                },
            },
        ]
    },

    optimization: {
        minimize: true,
        minimizer: [
            new CssMinimizer(),
            new Terser(),
        ]
    },

    plugins: [
        new HtmlWebPackPlugin({
             template: './src/index.html',
             filename: './index.html',
             inject: 'body'
        }), 

        new MiniCssExtractPlugin({
            filename: 'style.[fullhash].css',
            ignoreOrder: true,
        }),
        new webpack.DefinePlugin({
            "urlEndPoint": JSON.stringify("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJodHRwOi8vZmFvYmFja2VuZC5zb3V0aGNlbnRyYWx1cy5henVyZWNvbnRhaW5lci5pbzo0MDAwLyJ9")
        }),
        new CopyPlugin({
            patterns: [
              { from: "./src/assets/img/favicon.png", to: "./assets/img" },
            ],
        }),
    ]

}