require('dotenv').config();
const express = require('express');
const { connectDatabase } = require('./database');
const crypto = require('crypto');

const router = express.Router();
const DEFAULT_NB_ADDS = 20;


router.get('/random', async function(req, res, next) {
    try {
        const nbAds = parseInt(req.query.nb_ads) || DEFAULT_NB_ADDS;

        const db = await connectDatabase();

        const cursor = await db.collection('ads').aggregate([{ '$sample': { size: nbAds } }]);
        const randomAds = await cursor.toArray();

        res.json(randomAds);
    } catch(e) {
        return next(e);
    }
});


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
