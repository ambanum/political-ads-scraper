import json
import datetime
import os
import logging

import requests

import config

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
european_union_countries = [
    ('AT', 250), # Austria
    ('BE', 250), # Belgium
    ('BG', 250), # Bulgaria
    ('CY', 250), # Cyprus
    ('CZ', 250), # Czechia
    ('DE', 1000), # Germany
    ('DK', 250), # Denmark
    ('EE', 250), # Estonia
    ('ES', 250), # Spain
    ('FI', 250), # Finland
    ('FR', 250), # France
    ('GR', 250), # Greece
    ('HR', 250), # Croatia
    ('HU', 250), # Hungary
    ('IE', 250), # Ireland
    ('IT', 250), # Italy
    ('LT', 250), # Lithuania
    ('LU', 250), # Luxembourg
    ('LV', 250), # Latvia
    ('MT', 250), # Malta
    ('NL', 250), # Netherlands
    ('PL', 250), # Poland
    ('PT', 250), # Portugal
    ('RO', 250), # Romania
    ('SI', 250), # Slovenia
    ('SE', 250), # Sweden
    ('SK', 250), # Slovakia
    ('GB', 250), # United Kingdom
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


def fetch(fb_token, country_code, search_params, limit=250):
    def make_request(after=None):
        params = {
            # 'ad-type': 'POLITICAL_AND_ISSUE_ADS' (default)
            **search_params,
            'fields': ','.join(FIELDS),
            #'search_terms': "''",
            #'search_page_ids': ,
            'ad_reached_countries': "['{}']".format(country_code),
            'limit': limit,
            'access_token': fb_token,
        }
        if after:
            params['after'] = after

        #response = None
        #while not response:
        #    try:
        response = requests.get(
                    "https://graph.facebook.com/v3.3/ads_archive",
                    params=params,
                )
        #    except:
        #        logging.exception()

        assert response.status_code == 200, (response.status_code, response.text)
        json_data = response.json()

        assert set(json_data) <= {'data', 'paging'}, set(json_data)

        ads = json_data['data']
        print('Got {} ads'.format(len(ads)))

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


def write_to_file(fb_token, country_code='FR', limit=250):
    ads = fetch(
        fb_token=fb_token,
        country_code=country_code,
        search_params={'search_terms': "''", 'ad_active_status': 'ALL'},
        limit=limit,
    )

    print('Found {} ads.'.format(len(ads)))
    
    filename_format = ROOT_DIR + '/data/' + country_code + '/facebook-ads-archive_' + country_code + '_{}.json'

    filename_date = filename_format.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    #filename_latest = filename_format.format('latest')

    with open(filename_date, 'w') as outfile:
        json.dump(ads, outfile)

def create_dirs():
    for country_code, _ in european_union_countries:
        os.mkdir('data/' + country_code)

if __name__ == '__main__':
    fb_token = get_fb_token()
    for country_code, limit in european_union_countries:
        print('Fetching ads for {}'.format(country_code))
        write_to_file(
            fb_token=fb_token,
            country_code=country_code,
            limit=limit,
        )
