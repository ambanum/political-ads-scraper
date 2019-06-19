require('dotenv').config();
const express = require('express');
const { getDatabase } = require('./database');
const crypto = require('crypto');

const router = express.Router();
const DEFAULT_NB_ADDS = 20;
const CLASSIFICATION_TYPES = {
  NOTHING_SUSPECT: 'Nothing suspect',
  CANT_SAY: "Can't say",
  SURVEY: 'Contains a survey',
  NOT_RELATED_TO_POLITICS_OR_ISSUES_OF_NATIONAL_IMPORTANCE:
    'Not related to politics or issues of national importance',
  PROMOTES_A_CANDIDATE: 'Promotes a candidate, list or political party',
  INTRODUCES_OF_A_NEW_CONTROVERSIAL_ELEMENT:
    'Introduces of a new controversial element',
};

const paramsToClassificationType = {
    survey: CLASSIFICATION_TYPES.SURVEY,
    'promotes-candidates': CLASSIFICATION_TYPES.PROMOTES_A_CANDIDATE,
    'new-controversial-element': CLASSIFICATION_TYPES.INTRODUCES_OF_A_NEW_CONTROVERSIAL_ELEMENT,
    'nothing-suspect': CLASSIFICATION_TYPES.NOTHING_SUSPECT,
    'cant-say': CLASSIFICATION_TYPES.CANT_SAY,
    'not-related-to-politics': CLASSIFICATION_TYPES.NOT_RELATED_TO_POLITICS_OR_ISSUES_OF_NATIONAL_IMPORTANCE,
}

router.get('/annotations/:type?', async function (req, res, next) {
    try {
        const type = req.params.type;
        const skip = parseInt(req.query.skip) || 0;
        const limit = parseInt(req.query.limit) || 100;
        const isReview = !!req.query.isReview || false;
        const annotationsCount = await getDatabase().collection('annotations').count();
        const annotationsCollection = await getDatabase().collection('annotations');
        const query = [
            {
                $lookup:
                {
                    from: "ads",
                    localField: "adId",
                    foreignField: "ad_id",
                    as: 'ad'
                }
            },
            { $unwind: '$ad' },
        ];

        if (type && paramsToClassificationType[type]) {
            query.push({
                $match: { 'payload.value': paramsToClassificationType[type]}
            });
        }


        if (isReview) {
            query.unshift({ $match: { 'isReview': { '$eq': true } }});
        } else {
            query.unshift({ $match: { 'isReview': { '$ne': true } }});
        }

        query.push({ $skip: skip });
        query.push({ $limit: limit });

        const results = await annotationsCollection.aggregate(query).toArray();

        res.json({
            results,
            pagination: {
                total: annotationsCount,
                skip,
                limit
            }
        });
    } catch (e) {
        return next(e);
    }
});

router.get('/counts', async function (req, res, next) {
    try {
        const nbAds = parseInt(req.query.nb_ads) || DEFAULT_NB_ADDS;

        const adsCount = await getDatabase().collection('ads').count();
        const annotationsCount = await getDatabase().collection('annotations').count();

        res.json({
            adsCount,
            annotationsCount,
        });
    } catch (e) {
        return next(e);
    }
});

router.get('/random', async function(req, res, next) {
    try {
        const nbAds = parseInt(req.query.nb_ads) || DEFAULT_NB_ADDS;

        adsTable = getDatabase().collection('ads');
        const cursor = await adsTable.aggregate([{ '$sample': { size: nbAds } }]);
        const randomAds = await cursor.toArray();

        res.json(randomAds);
    } catch(e) {
        return next(e);
    }
});

async function annotate(req, res, next) {
    try {
        // Front-end data
        const adId = req.params['adId'];
        const payload = req.body;

        // Back-end data
        const timestamp = new Date().toISOString();
        const contributorIP = crypto.createHmac('sha512', process.env.SALT).update(req.ip).digest("hex");
        const userAgent = crypto.createHmac('sha512', process.env.SALT).update(req.headers['user-agent']).digest("hex");

        annotationTable = getDatabase().collection('annotations');
        await annotationTable.insertOne({
            adId,
            payload,
            timestamp,
            contributorIP,
            userAgent,
        });

        res.status(201).json({
            id: adId
        });
    } catch (e) {
        return next(e);
    }
}



//deprecatde route
router.post('/ads/:adId/annotation', annotate);

// Sample request:
// curl -X POST http://localhost:3003/ads/1254/annotation --header "Content-Type: application/json" --data '{"value": "hello"}'
router.post('/political-ads/:adId/annotation', annotate);


module.exports = router;
