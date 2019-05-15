const fs = require('fs');
const express = require('express');


const router = express.Router();
const FILE_NAME = __dirname + '/../../data/ads-archive_FR_latest.json';

router.get('/ads', async function(req, res, next) {
  try {
    var jsonData = fs.readFileSync(FILE_NAME, 'utf8');

    res.send(jsonData);
  } catch(e) {
    return next(e);
  }
});

module.exports = router;
