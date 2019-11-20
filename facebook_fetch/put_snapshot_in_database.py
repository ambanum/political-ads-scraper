"""
ssh -NT -L 27018:localhost:27017 cloud@desinfo.quaidorsay.fr
"""


import time
import logging

from pymongo import MongoClient

from facebook_fetch import config
from facebook_fetch import fetch
from facebook_fetch import snapshot
from facebook_fetch.fb_login import login


def process_batch():

    client = MongoClient(config.MONGODB_URL)
    ads_collection = client.facebook_ads.ads

    # ads_collection.create_index('ad_id')

    user_access_token, browser = login.connect_and_get_user_token()

    ads_to_process = ads_collection.find({"snapshot": {"$exists": False}})

    for ad in ads_to_process:
        ad_id = fetch.get_ad_id(ad)
        print(ad_id)

        try:
            snapshot_data = snapshot.get_snapshot_data(
                user_access_token=user_access_token,
                browser=browser,
                ad_id=ad_id,
            )

            ads_collection.update_one(
                {'_id': ad['_id']},
                {
                    '$set': {
                        'ad_id': ad_id,
                        'snapshot': snapshot_data,
                    },
                },
            )

            time.sleep(4)

        except Exception:
            logging.exception('Something happened')
            time.sleep(5)
            #user_access_token, browser = login.connect_and_get_user_token()


process_batch()
# while True:
#    try:
#        process_batch()

#    except Exception:
#        logging.exception('Something happened')
#        time.sleep(5)
