module.exports = function override(config) {
  // Add resolve.extensionAlias configuration
  config.resolve = {
    ...config.resolve,
    extensionAlias: {
      ...config.resolve?.extensionAlias,
      '.js': ['.js', '.jsx', '.ts', '.tsx']
    }
  };
  
  return config;
};