"""
ssh -NT -L 27018:localhost:27017 cloud@desinfo.quaidorsay.fr
"""


import time

from pymongo import MongoClient

from fb_fetch import config
from fb_fetch import fetch
from fb_fetch import snapshot
from fb_fetch.fb_login import login


client = MongoClient(config.MONGODB_URL)
ads_collection = client.facebook_ads.ads

#ads_collection.create_index('ad_id')


user_access_token, browser = login.connect_and_get_user_token()

ads_to_process = ads_collection.find({ "snapshot" : { "$exists" : False } })

for ad in ads_to_process:
    ad_id = fetch.get_ad_id(ad)
    print(ad_id)

    snapshot_data = snapshot.get_snapshot_data(
        user_access_token=user_access_token,
        browser=browser,
        ad_id=ad_id,
    )

    ads_collection.update_one(
        {'_id': ad['_id'] },
        {
            '$set': {
                'ad_id': ad_id,
                'snapshot': snapshot_data,
            },
        },
    )
    
    time.sleep(4)
