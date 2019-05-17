require('dotenv').config();
const fs = require('fs');
const express = require('express');
const { connectDatabase } = require('./database');
const crypto = require('crypto');

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
    return Math.floor(Math.random() * (high - low) + low);
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

// Sample request:
// curl -X POST http://localhost:3003/ads/1254/annotation\?payload\=hello
router.post('/ads/:adId/annotation', async function(req, res, next) {
    try {
        // Front-end data
        const adId = req.params['adId'];
        const payload = req.body;

        // Back-end data
        const timestamp = new Date().toISOString();
        const contributorIP = crypto.createHmac('sha512', process.env.SALT).update(req.ip).digest("hex");
        const userAgent = crypto.createHmac('sha512', process.env.SALT).update(req.headers['user-agent']).digest("hex");

        const db = await connectDatabase();

        await db.collection('annotations').insertOne({
            adId,
            payload,
            timestamp,
            contributorIP,
            userAgent,
        });

        res.status(201).json({
            id: adId
        });
    } catch(e) {
        return next(e);
    }
});


module.exports = router;
