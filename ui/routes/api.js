const { createProxyMiddleware } = require('http-proxy-middleware');

// api server is now separate, so we just create a proxy here
module.exports = createProxyMiddleware({
  target: global.config.apiEndpoint, // target host
  changeOrigin: true, // needed for virtual hosted sites
  ws: true, // proxy websockets
  pathRewrite: {
    '^/api/v1.0': '' // remove base path
  }
});
