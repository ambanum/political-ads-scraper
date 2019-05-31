import json
import datetime
import os
import pathlib
import logging
import re
import time

import requests

from fb_fetch import config

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
FIELDS = [
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
    {'code': 'US', 'page_size': 2000}, # United States of America
]


def get_fb_token():
    response = requests.get(
        config.FB_TOKEN_SERVICE_URL,
        params={
            'shared_secret': config.FB_TOKEN_SERVICE_SECRET,
        },
    )
    response.raise_for_status()
    return response.text.strip()

AD_ID_REGEX = re.compile(r'^https://www\.facebook\.com/ads/archive/render_ad/\?id=(\d+)&access_token=[a-zA-Z0-9]+$')
def get_ad_id(ad):
    return AD_ID_REGEX.match(ad['ad_snapshot_url']).groups()[0]

def fetch(fb_token, country_code, page_size=250):
    def make_request(after=None):
        ADS_API_URL = "https://graph.facebook.com/v3.3/ads_archive"

        params = {
            'ad_active_status': 'ALL',
            # 'ad-type': 'POLITICAL_AND_ISSUE_ADS' (default)
            'fields': ','.join(FIELDS),
            'search_terms': "''",
            #'search_page_ids': ,
            'ad_reached_countries': "['{}']".format(country_code),
            'limit': page_size,
            'access_token': fb_token,
        }
        if after:
            params['after'] = after

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
        print('{} Got {} ads'.format(datetime.datetime.now(), len(ads)))

        if 'paging' in json_data:
            paging = json_data['paging']
            assert set(paging) <= {'cursors', 'next', 'previous'}, paging
            assert set(paging['cursors']) <= {'after', 'before'}, paging
            after = json_data['paging']['cursors'].get('after')
        else:
            after = None

        return ads, after

    ads, after = make_request()
    while(after):
        ads_batch, after = make_request(after=after)
        ads += ads_batch

    return ads


def write_to_file(country_code='FR', page_size=250):
    ads = None
    nb_retry = 0
    while not ads and nb_retry < 3:
        try:
            nb_retry += 1

            fb_token = get_fb_token()

            ads = fetch(
                fb_token=fb_token,
                country_code=country_code,
                page_size=page_size,
            )

            print('Found {} ads.'.format(len(ads)))
        except Exception as exception:
            print('{} Fetch failed'.format(datetime.datetime.now()))
            logging.exception('Fetch failed')
            if exception.__class__.__name__ == 'KeyboardInterrupt':
                raise

    if not ads:
        print('Could not fetch ads for country {}'.format(country_code))
        return

    filename_format = ROOT_DIR + '/data/' + country_code + '/facebook-ads-archive_' + country_code + '_{}.json'

    filename_date = filename_format.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    #filename_latest = filename_format.format('latest')

    with open(filename_date, 'w') as outfile:
        json.dump(ads, outfile)


# python -c "from fb_fetch import fetch; fetch.create_dirs()"
def create_dirs():
    pathlib.Path('data/reports').mkdir(exist_ok=True)
    for country in COUNTRIES:
        pathlib.Path('data/' + country['code']).mkdir(exist_ok=True)
        pathlib.Path('data/reports/' + country['code']).mkdir(exist_ok=True)


if __name__ == '__main__':
    for country in COUNTRIES:
        print('Fetching ads for {}'.format(country['code']))
        write_to_file(
            country_code=country['code'],
            page_size=country['page_size'],
        )
