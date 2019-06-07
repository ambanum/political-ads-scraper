
import pathlib
import datetime
import json

from fb_fetch import fetch


ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent


def build_graph():
    timeseries = {}
    for country in fetch.COUNTRIES:
        country_code = country['code']
        print(country_code)

        api_timeseries = {}
        for filename in sorted(list((ROOT_DIR / 'data' / country_code).iterdir())):
            fetch_datetime = datetime.datetime.strptime(
                filename.stem,
                'facebook-ads-archive_{}_%Y-%m-%d_%H-%M-%S'.format(country_code),
            )

            with open(filename, 'r') as f:
                ads = json.load(f)

            api_timeseries[fetch_datetime.strftime("%Y-%m-%d")] = len(ads)

        reports_timeseries = {}
        for dir_path in sorted(list((ROOT_DIR / 'data/reports' / country_code).iterdir())):
            date_str = dir_path.name
            date = datetime.date(*map(int, date_str.split('-')))
            yesterday = date - datetime.timedelta(1)

            with open(dir_path / 'data.json', 'r') as f:
                data = json.load(f)

            nb_ads = data['lifetime_data'][str(yesterday)]['payload']['totalAds']

            reports_timeseries[date_str] = nb_ads

        timeseries[country_code] = {
            'API': api_timeseries,
            'report': reports_timeseries,
        }

    with open(ROOT_DIR / 'data/graph_nb_ads.json', 'w') as f:
        json.dump(timeseries, f)

if __name__ == '__main__':
    build_graph()
