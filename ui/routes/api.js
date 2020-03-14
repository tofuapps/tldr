var express = require('express');
var router = express.Router();

var path = require('path');
const spawn = require("child_process").spawn;

router.get('/newsfeed/get', function(req, res, next) {
  //res.render('index', { title: 'Express' });
  //res.render('app');
  const pythonProcess = spawn('pipenv', ['run', 'python3', path.join(global.appRoot, '../main.py'), '--curate']);
  pythonProcess.stdout.on('data', (data) => {
    // Do something with the data returned from python script
    //console.log('got data??? ' + data.toString());
    //res.status(400).json({ success: true, message: 'Success.', newsfeed: data.toString() });
    res.write(data);
  });
  pythonProcess.stdout.on('end', () => {
    console.log('done')
    res.end();
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(data.toString());
  });
});

router.get('/newsfeed/get_article_summary', function(req, res, next) {
  //res.render('index', { title: 'Express' });
  //res.render('app');
  const pythonProcess = spawn('pipenv', ['run', 'python3', path.join(global.appRoot, '../main.py'),
    '-t', req.query.title, '-l', req.query.link, '--summarize']);
  pythonProcess.stdout.on('data', (data) => {
    res.write(data);
  });
  pythonProcess.stdout.on('end', () => {
    console.log('done')
    res.end();
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(data.toString());
  });
});

module.exports = router;
