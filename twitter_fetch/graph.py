
import datetime
import json

from twitter_fetch import config


def read_ad_ids():
    ad_ids_by_date = {}

    for filename in sorted(list((config.DATA_DIR / 'twitter').iterdir())):
        fetch_datetime = datetime.datetime.strptime(
            filename.stem,
            'twitter-ads_EU_%Y-%m-%d_%H-%M-%S',
        )

        with open(filename, 'r') as f:
            ads = json.load(f)

        tweet_ids = set([
            tweet['basic_data']['tweetId']
            for adv_tweets in ads['advertisers_tweets'].values()
            for tweet in adv_tweets
        ])

        ad_ids_by_date[fetch_datetime.strftime("%Y-%m-%d")] = tweet_ids

    return ad_ids_by_date


def compute_graph(ad_ids_by_date):
    past_ads = set()
    time_series = {}
    for date in ad_ids_by_date.keys():
        visible_ads = ad_ids_by_date[date]
        removed_ads = past_ads - visible_ads

        time_series[str(date)] = {
            'nb_visible': len(visible_ads),
            'nb_removed': len(removed_ads),
            'nb_total': len(visible_ads) + len(removed_ads),
        }

        past_ads |= visible_ads
    
    return time_series

def write_graph():
    ad_ids_by_date = read_ad_ids()
    time_series = compute_graph(ad_ids_by_date)
    with open(config.DATA_DIR / 'twitter/graph_nb_ads_twitter.json', 'w') as f:
        json.dump(time_series, f)


if __name__ == '__main__':
    write_graph()
