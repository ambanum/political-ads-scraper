
import pathlib
import datetime
import json

from facebook_fetch import fetch, config


def build_graph():
    timeseries = {}
    for country in fetch.COUNTRIES:
        country_code = country['code']

        api_timeseries = {}
        for filename in sorted(list((config.DATA_DIR / 'facebook/API' / country_code).iterdir())):
            fetch_datetime = datetime.datetime.strptime(
                filename.stem,
                'facebook-ads-archive_{}_%Y-%m-%d_%H-%M-%S'.format(
                    country_code),
            )

            with open(filename, 'r') as f:
                ads = json.load(f)

            api_timeseries[fetch_datetime.strftime("%Y-%m-%d")] = len(ads)

        reports_timeseries = {}
        for dir_path in sorted(list((config.DATA_DIR / 'facebook/reports' / country_code).iterdir())):
            date_str = dir_path.name
            date = datetime.date(*map(int, date_str.split('-')))
            yesterday = date - datetime.timedelta(1)

            with open(dir_path / 'data.json', 'r') as f:
                data = json.load(f)

            nb_ads = data['lifetime_data'][str(
                yesterday)]['payload']['totalAds']

            reports_timeseries[date_str] = nb_ads

        timeseries[country_code] = {
            'API': api_timeseries,
            'report': reports_timeseries,
        }

    with open(config.DATA_DIR / 'facebook/graph_nb_ads_facebook.json', 'w') as f:
        json.dump(timeseries, f)


if __name__ == '__main__':
    build_graph()
