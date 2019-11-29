"""
ssh -NT -L 27018:localhost:27017 cloud@desinfo.quaidorsay.fr

This script has been ran for a first batch during May 2019, and during a second one during Novembre 2019. Media were saved
only for the 2nd batch. (because CDN urls of the media expire in a few months)
"""


import time
import logging
import getpass

from pymongo import MongoClient
import requests

from facebook_fetch import config
from facebook_fetch import fetch
from facebook_fetch import snapshot
from facebook_fetch.fb_login import login


def process_batch(user, app_id, password, totp):

    media_dir = config.DATA_DIR / 'facebook/media'

    client = MongoClient(config.MONGODB_URL)
    ads_collection = client.facebook_ads.ads_2019_11

    ads_collection.create_index('ad_id')

    user_access_token, browser = login.connect_and_get_user_token(user=user, app_id=app_id, password=password, totp=totp)

    ads_to_process = ads_collection.find({"snapshot" : {"$exists" : False}})

    for ad in ads_to_process:
        ad_id = fetch.get_ad_id(ad)
        print(ad_id)

        try:
            snapshot_data = snapshot.get_snapshot_data(
                user_access_token=user_access_token,
                browser=browser,
                ad_id=ad_id,
            )

            url_list = [
                image_data['resized_image_url']
                for image_data in snapshot_data['media']['images']
            ]+[
                image_data['video_sd_url']
                for image_data in snapshot_data['media']['videos']
            ]

            for url in url_list:
                media_filename = url.split('/')[-1].split('?')[0] # not very secure
                filepath = media_dir / media_filename

                if not filepath.is_file():
                    response = requests.get(url)   
                    response.raise_for_status()

                    with filepath.open('wb') as file:
                        file.write(response.content)

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

        except Exception:
            logging.exception('Something happened')
            time.sleep(5)
            #user_access_token, browser = login.connect_and_get_user_token(...)


#while True:
#    try:
#        process_batch()

#    except Exception:
#        logging.exception('Something happened')
#        time.sleep(5)

if __name__ == '__main__':
    try:
        user = config.FB_USER
    except AttributeError:
        user = input('Facebook account email: ')

    try:
        app_id = config.APP_ID
    except AttributeError:
        app_id = input('App ID: ')

    try:
        password = config.FB_PASSWORD
    except AttributeError:
        password = getpass.getpass('Password (hidden): ')

    try:
        totp = config.TOTP_SECRET
    except AttributeError:
        totp = getpass.getpass('TOTP secret (hidden): ')

    process_batch(user=user, app_id=app_id, password=password, totp=totp)
