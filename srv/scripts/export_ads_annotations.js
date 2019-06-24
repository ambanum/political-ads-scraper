const MongoClient = require('mongodb').MongoClient;
const stringify = require('csv-stringify')
const fs = require('fs');

const MONGODB_URL = 'mongodb://localhost:27017';
const MONGODB_DB_NAME = 'facebook_ads';

const client = new MongoClient(MONGODB_URL, { useNewUrlParser: true });

const DELIMITER = ';';
const COLUMNS = ['facebook_ad_id', 'crowdsourcing_annotation', 'reviewed_annotation'];

const exportToCSV = (annotations, reviews) => {
	return new Promise((resolve, reject) => {
		const data = []

		const stringifier = stringify({
			delimiter: DELIMITER,
			header: true,
			columns: COLUMNS
		});

		stringifier.on('readable', () => {
			let row;
			while(row = stringifier.read()){
				data.push(row)
			}
		});

		stringifier.on('error', (err) => {
			reject(err.message);
		});

		annotations.forEach(annotation => {
			const review = reviews.find(r => r.adId === annotation.adId);
			stringifier.write([ annotation.adId, annotation.payload.value, review ? review.payload.value : '' ]);
		});

		stringifier.on('finish', async () => {
			await fs.writeFileSync('ads_annotations.csv', data.join(''));
			resolve();
		})

		stringifier.end();
	});
}

const getResult = async () => {
	try {
		await client.connect();
		const db = client.db(MONGODB_DB_NAME);
		const annotationsCollection = await db.collection('annotations');

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
			{ $project: {"adId" : true, contributorIP: true, "payload": { "value": true }}},
		];

		console.log('total number of annotations', await annotationsCollection.count());

		const annotations = await annotationsCollection.aggregate([{ $match: { 'isReview': { '$ne': true } }}, ...query]).toArray();
		const reviews = await annotationsCollection.aggregate([{ $match: { 'isReview': { '$eq': true } }}, ...query]).toArray();

		console.log('found', annotations.length, 'annotations');
		console.log('found', reviews.length, 'reviews');

		await exportToCSV(annotations, reviews);
		await client.close();
	} catch(e) {
		console.log(e);
	}
};

getResult();
