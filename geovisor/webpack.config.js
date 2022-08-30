const HtmlWebPackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyPlugin = require("copy-webpack-plugin");
const webpack = require('webpack');

module.exports = {

    mode: 'development',
    output : {
        clean: true,
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
            }
        ]
    },
    plugins: [
        new HtmlWebPackPlugin({
             template: './src/index.html',
             filename: './index.html',
             inject: 'body'
        }), 

        new MiniCssExtractPlugin({
            filename: 'style.css',
            ignoreOrder: true,
        }),
        new CopyPlugin({
            patterns: [
              { from: "./src/assets/", to: "assets/" },
            ],
          }),
        new webpack.DefinePlugin({
          "urlEndPoint": JSON.stringify("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJodHRwOi8vbG9jYWxob3N0OjQwMDAvIn0.huu6JnASNpb3f05t4IXSoCDaw21CDco7P6aK07JLDEw")
        }),
    ]

}