const path = require('path');

module.exports = {
  entry: path.resolve(__dirname, 'ui/index.js'),
  output: {
    path: path.resolve(__dirname, 'static'),
    filename: 'main.js'
  },
  devtool: 'source-map',
  module: {
    rules: [{
      test: /.js/,
      exclude: /node_modules/,
      use: {
          loader: "babel-loader"
      }
    }]
  }
}
