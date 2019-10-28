
import datetime

import requests

from snapchat_fetch import config


def write_to_file():
    file_path = config.DATA_DIR / 'snapchat' / str(config.current_year) / 'snapchat-political-ads_{}_fetched-{}.zip'.format(config.current_year, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    response = requests.get('https://storage.googleapis.com/ad-manager-political-ads-dump/political/{}/PoliticalAds.zip'.format(config.current_year))
    response.raise_for_status()
    with open(file_path, 'wb') as f:
        f.write(response.content)


if __name__ == '__main__':
    write_to_file()
