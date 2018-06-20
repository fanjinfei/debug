var webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
//const ExtractTextWebpackPlugin = require('extract-text-webpack-plugin');
//const OptimizeCssAssetsWebpackPlugin = require('optimize-css-assets-webpack-plugin');

module.exports = {
//    context: __dirname + '/',
    entry: {
        app: './myApp.js',
//        vendor: ['./angular.min.js', './angular-route.min.js'],
    },
    output: {
        path: __dirname + '/js',
        filename: '[name].bundle.js'
    },
/*    optimization: {
        runtimeChunk: true,
        splitChunks: {
            chunks: "initial",
            cacheGroups: {
                default: false,
                vendors: false,
            },
        },
    },*/
  	module: {
    	rules: [
/*			{
				test: /\.js$/,
				exclude: /node_modules/,
				loader: ['ng-annotate-loader', 'babel-loader']
			},
			{
				test: /\.(scss)$/,
				use: ExtractTextWebpackPlugin.extract({
					use: [
							{
								loader: "css-loader",
								options: {
									minimize: true
								}
							},
							{
								loader: "sass-loader"
							}
					]
				})
			},
			// for fixing of loading bootstrap icon files
			{
				test: /\.(png|jpg|jpeg|gif|svg|woff|woff2)$/,
				loader: 'url-loader?limit=10000',
				options: {
					name: './fonts/[name].[ext]'
				}
			},
			{
				test: /\.(eot|ttf)$/,
				loader: 'file-loader',
				options: {
					name: './fonts/[name].[ext]'
				}
			},*/
			{ test: /\.html$/, loader: 'html-loader' }
		]
	},

    plugins: [ 
/*           new HtmlWebpackPlugin({
               filename: 'main.html',
               template: __dirname + '/main.html',
               inject: false,
           }),*/
//		new ExtractTextWebpackPlugin('styles/styles.css'),
//		new OptimizeCssAssetsWebpackPlugin()
    ]
};
