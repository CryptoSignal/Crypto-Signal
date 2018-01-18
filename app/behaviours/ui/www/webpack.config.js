const path = require('path');

module.exports = {
  entry: './react/Router.js',

  output: {
     path: path.resolve(__dirname, 'static'),
     //path: 'C:\\Users\\Jesse\\Documents\\Python\\TradingBot\\www',//  '/C/Users/Jesse/Documents/Python/TradingBot/www',
     filename: 'index.js'
  },

  devServer: {
     inline: true,
     port: 12944,
     contentBase: "./static",
     hot: true
  },

  module: {
     loaders: [
        {
           test: /\.jsx?$/,
           exclude: /node_modules/,
           loader: 'babel-loader',

           query: {
              presets: ['es2015', 'react']
           }
        }
     ]
  }
}