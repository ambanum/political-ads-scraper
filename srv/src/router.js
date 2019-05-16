const fs = require('fs');
const express = require('express');


const router = express.Router();
const FILE_NAME = __dirname + '/../../data/ads-archive_FR_latest.json';

router.get('/random', async function(req, res, next) {
    try {
        var jsonData = fs.readFileSync(FILE_NAME, 'utf8');
        const ads = JSON.parse(jsonData);

        const nbAds = req.query.nb_ads || 20;

        randomAds = randomSelect(ads, nbAds);

        res.json(randomAds);
    } catch(e) {
        return next(e);
    }
});


function randomInt(low, high) {
    return Math.floor(Math.random() * (high - low) + low)
}


function randomSelect(array, n) {
    let i = 0,
        j = 0,
        temp;

    while (i < n) {
        j = randomInt(i, array.length);

        temp = array[i];
        array[i] = array[j];
        array[j] = temp;

        i += 1;
    }

    return array.slice(0, n);
}


module.exports = router;
