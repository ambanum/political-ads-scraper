
import json
import datetime
import pathlib

import requests

import fb_fetch.fetch


ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent

FORM_DATA = "__user=0&__a=1&__dyn=&__req=1&__be=1&__pc=PHASED%3ADEFAULT&dpr=1&__rev=&__s=&lsd=&jazoest="
FORM_HEADERS = {
    'accept': '*/*',
    'accept-encoding': '',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
    'content-length': str(len(FORM_DATA)+1),
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': 'datr=; fr=; wd=',
    'origin': 'https://www.facebook.com',
    'referer': 'https://www.facebook.com/ads/library/report/?source=archive-landing-page&country=FR',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/74.0.3729.169 Chrome/74.0.3729.169 Safari/537.36',
}
TIME_PRESETS = ['yesterday', 'last_7_days', 'last_30_days', 'last_90_days', 'lifelong']


def fetch_endpoint(endpoint, date, country_code, time_preset=None):
    if endpoint == 'lifetime_data':
        url = "https://www.facebook.com/ads/library/report/async/lifetime_data/?report_ds={}&country={}".format(
            date,
            country_code,
        )
    elif endpoint == 'location_data':
        url = "https://www.facebook.com/ads/library/report/async/location_data/?report_ds={}&country={}&time_preset={}".format(
            date,
            country_code,
            time_preset,
        )
    elif endpoint == 'advertiser_data':
        url = "https://www.facebook.com/ads/library/report/async/advertiser_data/?report_ds={}&country={}&time_preset={}&sort_column=spend&sort_descending=true&q=".format(
            date,
            country_code,
            time_preset,
        )
    elif endpoint == 'download':
        url = "https://www.facebook.com/ads/library/report/v2/download/?report_ds={}&country={}&time_preset={}".format(
            date,
            country_code,
            time_preset,
        )
    else:
        raise ValueError('Unknown endpoint')

    response = None
    nb_retry = 0
    while not response and nb_retry < 3:
        try:
            response = requests.post(
                url,
                headers=FORM_HEADERS,
                data=FORM_DATA
            )
            response.raise_for_status()

        except Exception as exception:
            logging.exception('Request failed')
            if exception.__class__.__name__ == 'KeyboardInterrupt':
                raise
            time.sleep(60)

    if not response:
        assert False

    prefix = 'for (;;);'
    assert response.text[:len(prefix)] == prefix
    json_data = response.text[len(prefix):]
    data = json.loads(json_data)
    return data

def fetch_for_date_country(today, country_code):
    dates = [
        today - datetime.timedelta(delta)
        for delta in range(11)
    ]

    country_data = {
        'lifetime_data': {
            str(date): fetch_endpoint(endpoint='lifetime_data', date=date, country_code=country_code)
            for date in dates
        },
        'location_data': {
            time_preset: {
                str(date): fetch_endpoint(endpoint='location_data', date=date, country_code=country_code, time_preset=time_preset)
                for date in dates
            }
            for time_preset in TIME_PRESETS
        },
        'advertiser_data': {
            time_preset: {
                str(date): fetch_endpoint(endpoint='advertiser_data', date=date, country_code=country_code, time_preset=time_preset)
                for date in dates
            }
            for time_preset in TIME_PRESETS
        },
        'download': {
            time_preset: {
                str(date): fetch_endpoint(endpoint='download', date=date, country_code=country_code, time_preset=time_preset)
                for date in dates
            }
            for time_preset in TIME_PRESETS
        },
    }

    report_dir = ROOT_DIR / 'data' / 'reports' / country_code / str(today)
    report_dir.mkdir()
    with open(report_dir / 'data.json', 'w') as f:
        json.dump(country_data, f)

    for time_preset in TIME_PRESETS:
        url = country_data['download'][time_preset][str(today)]['payload']['uri']
        if not url:
            continue
        filename = url.split('/')[-1].split('?')[0]
        response = requests.get(url)
        response.raise_for_status()
        with open(report_dir / filename, 'wb') as f:
            f.write(response.content)

def fetch_for_date(today):
    for country in fb_fetch.fetch.COUNTRIES:
        country_code=country['code']
        print('Fetching for {} and {}'.format(today, country_code))
        fetch_for_date_country(today=today, country_code=country_code)


# python -c "import datetime; from fb_fetch import reports; reports.init(start_date=datetime.date(2019, 5, 10))"
def init(start_date):
    current_date = start_date
    today = datetime.date.today()
    while current_date <= today:
        fetch_for_date(today=current_date)
        current_date += datetime.timedelta(1)


if __name__ == '__main__':
    today = datetime.date.today()
    fetch_for_date(today=today)
