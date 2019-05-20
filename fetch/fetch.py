import json
import datetime
import os
import logging

import requests

import creds

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
european_union_country_codes = [
    'AT', # Austria
    'BE', # Belgium
    'BG', # Bulgaria
    'CY', # Cyprus
    'CZ', # Czechia
    'DE', # Germany
    'DK', # Denmark
    'EE', # Estonia
    'ES', # Spain
    'FI', # Finland
    'FR', # France
    'GR', # Greece
    'HR', # Croatia
    'HU', # Hungary
    'IE', # Ireland
    'IT', # Italy
    'LT', # Lithuania
    'LU', # Luxembourg
    'LV', # Latvia
    'MT', # Malta
    'NL', # Netherlands
    'PL', # Poland
    'PT', # Portugal
    'RO', # Romania
    'SI', # Slovenia
    'SE', # Sweden
    'SK', # Slovakia
    'GB', # United Kingdom
]


def fetch(country_code, search_params):
    def make_request(after=None):
        params = {
            # 'ad-type': 'POLITICAL_AND_ISSUE_ADS' (default)
            **search_params,
            'fields': ','.join(FIELDS),
            #'search_terms': "''",
            #'search_page_ids': ,
            'ad_reached_countries': "['{}']".format(country_code),
            'limit': 250,
            'access_token': creds.FB_TOKEN,
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


def write_to_file(country_code='FR'):
    ads = fetch(
        country_code=country_code,
        search_params={'search_terms': "''", 'ad_active_status': 'ALL'},
    )

    print('Found {} ads.'.format(len(ads)))
    
    filename_format = ROOT_DIR + '/data/ads-archive_' + country_code + '_{}.json'

    filename_date = filename_format.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    filename_latest = filename_format.format('latest')

    with open(filename_date, 'w') as outfile:
        json.dump(ads, outfile)

    with open(filename_latest, 'w') as outfile:
        json.dump(ads, outfile)


if __name__ == '__main__':
    for country_code in european_union_country_codes:
        print('Fetching ads for {}'.format(country_code))
        write_to_file(country_code=country_code)
