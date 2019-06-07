
import re
import pathlib
import datetime
import json
import time

import requests


ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/74.0.3729.169 Chrome/74.0.3729.169 Safari/537.36'


class Headers():
    max_count = 34

    def __init__(self):
        self._count = None
        self._headers = None

    def _renew_headers(self):
        def get_root_page():
            response_root = requests.request(
                'GET',
                'https://ads.twitter.com/transparency/i/political_advertisers'
            )
            response_root.raise_for_status()

            csrf_token = re.search(
                r'ct0=([a-z0-9]+)',
                response_root.headers['set-cookie']
            ).groups()[0]

            script_url = re.search(
                r'<script src="(https://ton\.twimg\.com/ads-manager/js/transparency-app\.[a-z0-9]+\.js)"></script>',
                response_root.text
            ).groups()[0]

            return csrf_token, script_url

        csrf_token, script_url = get_root_page()

        def get_bearer_token(script_url):
            response_script = requests.request(
                'GET',
                script_url
            )
            response_script.raise_for_status()

            bearer_token = re.search(
                r'"([A-Za-z0-9%]{40,200})"',
                response_script.text
            ).groups()[0]
            assert bearer_token == 'AAAAAAAAAAAAAAAAAAAAAOLv4AAAAAAAQubRLkVexZO02uKUva6eI9ZHmMY%3D3jfkYEj27hoTzTlXvxRiMg0wSb285GH9h2WfCvEeOh53QyxA5j', bearer_token

            return bearer_token

        bearer_token = get_bearer_token(script_url)

        headers = {
            'authorization': 'Bearer {}'.format(bearer_token),
            'Origin': 'https://ads.twitter.com',
            'Referer': 'https://ads.twitter.com/transparency/i/political_advertisers',
            'User-Agent': USER_AGENT,
            'x-csrf-token': csrf_token,
        }

        def get_guest_token(headers):
            response_activate = requests.request(
                'POST',
                'https://api.twitter.com/1.1/guest/activate.json',
                headers=headers,
            )
            response_activate.raise_for_status()

            guest_token = response_activate.json()['guest_token']
            headers['x-guest-token'] = guest_token

        get_guest_token(headers)

        self._headers = headers
        self._count = 0

    @property
    def headers(self):
        if self._count is None or self._count > self.max_count:
            self._renew_headers()
        self._count += 1
        return self._headers


class Api():
    def __init__(self):
        self.headers = Headers()

    def request(self, method, url):
        response = None
        nb_retry = 0
        while ((not response) and (nb_retry < 5)):
            response = requests.request(
                method,
                url,
                headers=self.headers.headers,
                timeout=60,
            )
            if response.status_code != 200:
                print(response.status_code, url, response.text)
            nb_retry += 1
        return response


def fetch():
    api = Api()

    def get_advertisers():
        response_advertisers = api.request(
            'GET',
            'https://ads.twitter.com/transparency/political_advertisers.json?user_list_type=POLITICAL_EU',
        )
        response_advertisers.raise_for_status()

        advertiser_screen_names = [
            adv['screenName']
            for adv in response_advertisers.json()['users']
        ]

        response_lookup = api.request(
            'GET',
            'https://api.twitter.com/1.1/users/lookup.json?include_entities=true&include_ext_highlighted_label=true&screen_name={}'.format(
                '%2C'.join(advertiser_screen_names)
            ),
        )
        response_lookup.raise_for_status()

        advertisers_data = response_lookup.json()
        assert len(advertisers_data) == len(advertiser_screen_names)

        return advertisers_data

    advertisers_data = get_advertisers()

    def get_advertiser_tweets(adv):
        adv_screen_name = adv['screen_name']
        adv_id = adv['id_str']
        print('Fetching data for {}'.format(adv_screen_name))

        response_advertiser_metadata = api.request(
            'GET',
            'https://ads.twitter.com/transparency/user_metadata.json?screen_name={}'.format(adv_screen_name),
        )
        response_advertiser_metadata.raise_for_status()

        adv_metadata = response_advertiser_metadata.json()
        assert adv_metadata == {'isPolitical': True, 'isIssue': False, 'isSuspended': False}

        tweets = []
        cursor = '0'
        while cursor:
            response_timeline = api.request(
                'GET',
                'https://ads.twitter.com/transparency/tweets_timeline.json?user_id={}&cursor={}'.format(
                    adv_id,
                    cursor,
                ),
            )
            response_timeline.raise_for_status()
            timeline_batch = response_timeline.json()
            tweets_basic_data = timeline_batch['tweets']

            tweet_ids = [
                tweet['tweetId']
                for tweet in tweets_basic_data
            ]
            data_by_id = {
                tweet['tweetId']: {
                    'basic_data': tweet
                }
                for tweet in tweets_basic_data
            }
            response_tweets = api.request(
                'GET',
                'https://api.twitter.com/1.1/statuses/lookup.json?cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_ext_highlighted_label=true&include_reply_count=1&tweet_mode=extended&trim_user=0&include_ext_media_color=1&id={}'.format(
                    '%2C'.join(tweet_ids)
                ),
            )
            response_tweets.raise_for_status()
            tweets_additional_data = response_tweets.json()
            for tweet_additional_data in tweets_additional_data:
                data_by_id[tweet_additional_data['id_str']]['additional_data'] = tweet_additional_data

            for tweet_id in tweet_ids:
                print(tweet_id)
                if 'additional_data' in data_by_id[tweet_id]:

                    response_tweet_metadata = api.request(
                        'GET',
                        'https://ads.twitter.com/transparency/line_item_metadata.json?tweet_id={}&user_id={}'.format(
                            tweet_id,
                            adv_id,
                        ),
                    )
                    response_tweet_metadata.raise_for_status()
                    tweet_metadata = response_tweet_metadata.json()

                    response_tweet_perf = api.request(
                        'GET',
                        'https://ads.twitter.com/transparency/tweet_performance.json?tweet_id={}&user_id={}'.format(
                            tweet_id,
                            adv_id,
                        ),
                    )
                    response_tweet_perf.raise_for_status()
                    tweet_perf = response_tweet_perf.json()

                    campaigns_data = []
                    for campaign in tweet_metadata['metadata']:
                        account_id = campaign['account_id']
                        line_item_id = campaign['line_item_id']


                        response_campaign_targeting_criteria = api.request(
                            'GET',
                            'https://ads.twitter.com/transparency/data/line_item_delivered_targeting_criteria.json?account_id={}&line_item_id={}'.format(
                                account_id,
                                line_item_id,
                            ),
                        )
                        response_campaign_targeting_criteria.raise_for_status()
                        line_item_delivered_targeting_criteria = response_campaign_targeting_criteria.json()


                        response_campaign_targeted_audience = api.request(
                            'GET',
                            'https://ads.twitter.com/transparency/data/line_item_targeted_audience.json?account_id={}&line_item_id={}'.format(
                                account_id,
                                line_item_id,
                            ),
                        )
                        if response_campaign_targeted_audience.status_code != 200:
                            line_item_targeted_audience = None
                        else:
                            line_item_targeted_audience = response_campaign_targeted_audience.json()

                        campaigns_data.append({
                            'line_item_delivered_targeting_criteria': line_item_delivered_targeting_criteria,
                            'line_item_targeted_audience': line_item_targeted_audience,
                        })

                        #time.sleep(2)
                else:
                    tweet_metadata = None
                    tweet_perf = None
                    campaigns_data = None

                tweets.append({
                    'basic_data': data_by_id[tweet_id]['basic_data'],
                    'additional_data': data_by_id[tweet_id].get('additional_data'),
                    'metadata': tweet_metadata,
                    'performance': tweet_perf,
                    'campaigns': campaigns_data,
                })

            cursor = timeline_batch.get('cursor')

        return tweets


    advertisers_tweets = {
        adv['id_str']: get_advertiser_tweets(adv=adv)
        for adv in advertisers_data
    }

    return {
        'advertisers_data': advertisers_data,
        'advertisers_tweets': advertisers_tweets,
    }


def write_to_file():
    data = fetch()

    filename = ROOT_DIR / 'data/twitter/twitter-ads_EU_{}.json'.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)


if __name__ == '__main__':
    write_to_file()
