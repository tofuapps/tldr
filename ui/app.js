var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
var apiRouter = require('./routes/api');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
global.appRoot = __dirname;
global.config = require('./config.js'); // config.js

app.use('/', indexRouter);
app.use('/users', usersRouter);
const { createProxyMiddleware } = require('http-proxy-middleware');
//app.use('/api', apiRouter);
app.use('/api/v1.0/', createProxyMiddleware({
  target: global.config.apiEndpoint, // target host
  changeOrigin: true, // needed for virtual hosted sites
  ws: true, // proxy websockets
  pathRewrite: {
    '^/api/v1.0': '' // remove base path
  }
  //, router: {
  //  // when request.headers.host == 'dev.localhost:3000',
  //  // override target 'http://www.example.org' to 'http://localhost:8000'
  //  'dev.localhost:3000': 'http://localhost:8000'
  //}
}));

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
