const express = require('express');
const logger = require('morgan');
const cors = require('cors');

const router = require('./router');

const app = express();
app.enable('trust proxy');
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors());

app.use('/', router);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
    const err = new Error('Not Found');
    err.status = 404;
    next(err);
});

// error handler
app.use(function(err, req, res, next) {
    console.log(err);

    // render the error page
    res.status(err.status || 500);
    res.send(err);
});

module.exports = app;
