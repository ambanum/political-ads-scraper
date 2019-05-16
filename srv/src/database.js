const MongoClient = require('mongodb').MongoClient;

const MONGODB_URL = 'mongodb://localhost:27017';
const MONGODB_DB_NAME = 'facebook_ads';

const client = new MongoClient(MONGODB_URL);

async function connectDatabase() {
    await client.connect();
    const db = client.db(MONGODB_DB_NAME);
    return db;
}

module.exports = {
    connectDatabase,
};
