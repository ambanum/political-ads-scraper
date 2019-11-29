"""
After scraping the ads from FB ads library, this script imports them to mongodb.

A first import for French ads was made during May 2019, a second 2019 during Novembre 2019.
"""


import json
import os

from pymongo import MongoClient

from facebook_fetch import config


with open(config.DATA_DIR / 'facebook/API/FR/facebook-ads-archive_FR_2019-11-27_23-21-50.json') as f:
    ads = json.load(f)

print('Loaded {} ads'.format(len(ads)))

client = MongoClient('localhost', 27017)
ads_table = client.facebook_ads.ads_2019_11
ads_table.drop()
ads_table.insert_many(ads)

#list(ads_table.aggregate([{ '$sample': { 'size': 1 } }]))
