import json
import datetime
import os
import pathlib
import logging
import re
import time

import requests

from facebook_fetch import config

FIELDS = [
    'id',
    'ad_creation_time',
    'ad_creative_body',
    'ad_creative_link_caption',
    'ad_creative_link_description',
    'ad_creative_link_title',
    'ad_delivery_start_time',
    'ad_delivery_stop_time',
    'ad_snapshot_url',
    'currency',
    'demographic_distribution',
    'funding_entity',
    'impressions',
    'page_id',
    'page_name',
    'potential_reach',
    'publisher_platforms',
    'region_distribution',
    'spend',
]
COUNTRIES = [
    {'code': 'AT', 'page_size': 250}, # Austria
    {'code': 'BE', 'page_size': 250}, # Belgium
    {'code': 'BG', 'page_size': 250}, # Bulgaria
    {'code': 'CY', 'page_size': 250}, # Cyprus
    {'code': 'CZ', 'page_size': 250}, # Czechia
    {'code': 'DE', 'page_size': 1000}, # Germany
    {'code': 'DK', 'page_size': 250}, # Denmark
    {'code': 'EE', 'page_size': 250}, # Estonia
    {'code': 'ES', 'page_size': 250}, # Spain
    {'code': 'FI', 'page_size': 250}, # Finland
    {'code': 'FR', 'page_size': 250}, # France
    {'code': 'GR', 'page_size': 250}, # Greece
    {'code': 'HR', 'page_size': 250}, # Croatia
    {'code': 'HU', 'page_size': 250}, # Hungary
    {'code': 'IE', 'page_size': 250}, # Ireland
    {'code': 'IT', 'page_size': 250}, # Italy
    {'code': 'LT', 'page_size': 250}, # Lithuania
    {'code': 'LU', 'page_size': 250}, # Luxembourg
    {'code': 'LV', 'page_size': 250}, # Latvia
    {'code': 'MT', 'page_size': 250}, # Malta
    {'code': 'NL', 'page_size': 250}, # Netherlands
    {'code': 'PL', 'page_size': 250}, # Poland
    {'code': 'PT', 'page_size': 250}, # Portugal
    {'code': 'RO', 'page_size': 250}, # Romania
    {'code': 'SI', 'page_size': 250}, # Slovenia
    {'code': 'SE', 'page_size': 250}, # Sweden
    {'code': 'SK', 'page_size': 250}, # Slovakia
    {'code': 'GB', 'page_size': 250}, # United Kingdom
#    {'code': 'US', 'page_size': 2000}, # United States of America
]

class FacebookToken():
    _delay = datetime.timedelta(0, 30*60) # 30 minutes

    def __init__(self):
        self._timestamp = None
        self._token = None

    def _renew_token(self):
        new_timestamp = datetime.datetime.now()
        response = requests.get(
            config.FB_TOKEN_SERVICE_URL,
            params={
                'shared_secret': config.FB_TOKEN_SERVICE_SECRET,
            },
        )
        response.raise_for_status()

        self._timestamp = new_timestamp
        self._token = response.text.strip()

    @property
    def token(self):
        if not self._timestamp or (datetime.datetime.now() - self._timestamp > self._delay):
            self._renew_token()
        return self._token


AD_ID_REGEX = re.compile(r'^https://www\.facebook\.com/ads/archive/render_ad/\?id=(\d+)&access_token=[a-zA-Z0-9]+$')
def get_ad_id(ad):
    return AD_ID_REGEX.match(ad['ad_snapshot_url']).groups()[0]

def try_fetch_country(country_code, page_size, token):
    FIRST_REQUEST_POINTER = "first request"
    NO_MORE_LEFT_POINTER = "no more left"

    def make_request(token_value, pointer):
        ADS_API_URL = "https://graph.facebook.com/v3.3/ads_archive"

        params = {
            'ad_active_status': 'ALL',
            # 'ad-type': 'POLITICAL_AND_ISSUE_ADS' (default)
            'fields': ','.join(FIELDS),
            'search_terms': "''",
            #'search_page_ids': ,
            'ad_reached_countries': "['{}']".format(country_code),
            'limit': page_size,
            'access_token': token_value,
        }
        if pointer != FIRST_REQUEST_POINTER:
            params['after'] = pointer

        response = None
        nb_retry = 0
        while not response and nb_retry < 3:
            try:
                nb_retry += 1

                response = requests.get(
                    ADS_API_URL,
                    params=params,
                    timeout=60,
                )

                assert response.status_code == 200, (response.status_code, response.text)

            except Exception as exception:
                logging.exception('Request failed')
                if exception.__class__.__name__ == 'KeyboardInterrupt':
                    raise
                time.sleep(60)

        assert response

        json_data = response.json()

        assert set(json_data) <= {'data', 'paging'}, set(json_data)

        ads = json_data['data']

        if country_code == 'US':
            # We don't keep US ads (there are way too many)
            ads = [
                get_ad_id(ad)
                for ad in ads
            ]

        if 'paging' in json_data:
            paging = json_data['paging']
            assert set(paging) <= {'cursors', 'next', 'previous'}, paging
            assert set(paging['cursors']) <= {'after', 'before'}, paging
            pointer = json_data['paging']['cursors'].get('after')
        else:
            pointer = NO_MORE_LEFT_POINTER

        return ads, pointer

    pointer_list = [FIRST_REQUEST_POINTER]
    ads_batches = []

    def write_ads_to_file(country_code, index_file, ads_batches):
        file_path = config.DATA_DIR / 'facebook/API' / country_code / 'facebook-ads-archive_{}_{}_part-{}.json'.format(
            country_code,
            datetime.datetime.now().strftime("%Y-%m-%d"),
            index_file,
        )  # "%Y-%m-%d_%H-%M-%S"
        flattened_ads = [
            ad
            for ads_batch in ads_batches
            for ad in ads_batch
        ]

        with open(file_path, 'w') as outfile:
            json.dump(flattened_ads, outfile)

    index_file = 0
    while(pointer_list[-1] != NO_MORE_LEFT_POINTER):
        pointer = pointer_list[-1]
        print('Beginning batch', len(pointer_list), 'with pointer', pointer)
        ads_batch, new_pointer = make_request(token_value=token.token, pointer=pointer)
        print('Found', len(ads_batch), 'ads.')
        pointer_list.append(new_pointer)
        ads_batches.append(ads_batch)

        if len(ads_batches) >= 100:
            write_ads_to_file(
                country_code=country_code,
                index_file=index_file,
                ads_batches=ads_batches,
            )

            index_file += 1
            ads_batches = []

    write_ads_to_file(
        country_code=country_code,
        index_file=index_file,
        ads_batches=ads_batches,
    )


def fetch_country(country_code, page_size, token):
    success = False
    nb_retry = 0
    while not success and nb_retry < 5:
        try:
            nb_retry += 1

            try_fetch_country(
                country_code=country_code,
                page_size=page_size,
                token=token,
            )

            success = True

        except Exception as exception:
            print('{} Fetch failed'.format(datetime.datetime.now()))
            logging.exception('Fetch failed')
            if exception.__class__.__name__ == 'KeyboardInterrupt':
                raise

    if not success:
        print('Could not fetch ads for country {}'.format(country_code))



# python -c "from facebook_fetch import fetch; fetch.create_dirs()"
def create_dirs():
    (config.DATA_DIR / 'google').mkdir(exist_ok=True)
    (config.DATA_DIR / 'facebook').mkdir(exist_ok=True)
    (config.DATA_DIR / 'facebook/reports').mkdir(exist_ok=True)
    (config.DATA_DIR / 'facebook/API').mkdir(exist_ok=True)
    (config.DATA_DIR / 'twitter').mkdir(exist_ok=True)
    for country in COUNTRIES:
        (config.DATA_DIR / 'facebook/API' / country['code']).mkdir(exist_ok=True)
        (config.DATA_DIR / 'facebook/reports' / country['code']).mkdir(exist_ok=True)


if __name__ == '__main__':
    token = FacebookToken()

    for country in COUNTRIES:
        print('Fetching ads for country {}', country)
        fetch_country(
            country_code=country['code'],
            page_size=country['page_size'],
            token=token,
        )
