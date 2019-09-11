'use strict'
const { VueLoaderPlugin } = require('vue-loader')
module.exports = {
//  mode: 'development',
  mode: 'production',
  entry: [
    './src/app.js'
  ],
  module: {
    rules: [
      {
        test: /\.vue$/,
        use: 'vue-loader'
      },
      {
        test: /\.css$/,
        use: [
          'vue-style-loader',
          'css-loader'
        ]
     },
    {
      test: /\.styl(us)?$/,
      use: [
        'vue-style-loader',
        'css-loader',
        'stylus-loader'
      ]
    },
    {
      test: /\.js$/,
      use: 'babel-loader'
    }       
     
   ]
  },
  resolve: {
    alias: {
      'vue$': 'vue/dist/vue.esm.js' // 'vue/dist/vue.common.js' for webpack 1
    }
  },
  
  plugins: [
    new VueLoaderPlugin()
  ]
}
