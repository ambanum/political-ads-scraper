"""
To run on server:

sudo apt install python3-pip
pip3 install pew
pew new political-ads-scraper
pip install pymongo
"""


import json

from pymongo import MongoClient

from facebook_fetch import config


with open(config.DATA_DIR / 'facebook/API/FR/facebook-ads-archive_FR_latest.json') as f:
    ads = json.load(f)

print('Loaded {} ads'.format(len(ads)))

client = MongoClient('localhost', 27017)
ads_table = client.facebook_ads.ads
ads_table.drop()
ads_table.insert_many(ads)

#list(ads_table.aggregate([{ '$sample': { 'size': 1 } }]))
