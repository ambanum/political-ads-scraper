import json
import datetime
import os

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


def fetch(country_code, search_params):
    def make_request(after=None):
        params = {
            # 'ad-type': 'POLITICAL_AND_ISSUE_ADS' (default)
            **search_params,
            'fields': ','.join(FIELDS),
            #'search_terms': "''",
            #'search_page_ids': ,
            'ad_reached_countries': "['{}']".format(country_code),
            'limit': 5000,
            'access_token': creds.FB_TOKEN,
        }
        if after:
            params['after'] = after

        response = requests.get(
            "https://graph.facebook.com/v3.3/ads_archive",
            params=params,
        )

        assert response.status_code == 200, (response.status_code, response.text)
        json_data = response.json()

        assert set(json_data) <= {'data', 'paging'}, set(json_data)

        ads = json_data['data']

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
    ads = fetch(country_code=country_code, search_params={'search_terms': "''"})
    
    filename_format = ROOT_DIR + '/data/ads-archive_' + country_code + '_{}.json'

    filename_date = filename_format.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    filename_latest = filename_format.format('latest')

    with open(filename_date, 'w') as outfile:
        json.dump(ads, outfile)

    with open(filename_latest, 'w') as outfile:
        json.dump(ads, outfile)


if __name__ == '__main__':
    write_to_file()
