const MongoClient = require('mongodb').MongoClient;

const MONGODB_URL = 'mongodb://localhost:27017';
const MONGODB_DB_NAME = 'facebook_ads';

const client = new MongoClient(MONGODB_URL, { useNewUrlParser: true });
let db = undefined;

async function connectDatabase() {
    await client.connect();
    db = client.db(MONGODB_DB_NAME);
}

function getDatabase() {
    return db;
}

connectDatabase();

module.exports = {
    getDatabase,
};
