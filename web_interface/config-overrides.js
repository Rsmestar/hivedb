module.exports = function override(config, env) {
  // إضافة قاعدة لتجاهل أخطاء source-map في بعض الحزم
  config.module.rules.push({
    test: /\.js$/,
    enforce: 'pre',
    use: ['source-map-loader'],
    exclude: [
      /node_modules\/@mui\/material\/node_modules\/react-is/,
      /node_modules\/@mui\/utils\/node_modules\/react-is/,
      /node_modules\/@emotion\/cache\/node_modules\/stylis/,
      /node_modules\/react-is/,
      /node_modules\/stylis/
    ],
  });

  // تجاهل أخطاء webpack
  config.ignoreWarnings = [/Failed to parse source map/];
  
  return config;
};
