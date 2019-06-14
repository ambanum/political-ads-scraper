
import datetime

import requests

from google_fetch import config


def write_to_file():
    file_path = config.DATA_DIR / 'google/google-political-ads-transparency-bundle_{}.zip'.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    response = requests.get('https://storage.googleapis.com/transparencyreport/google-political-ads-transparency-bundle.zip')
    response.raise_for_status()
    with open(file_path, 'wb') as f:
        f.write(response.content)


if __name__ == '__main__':
    write_to_file()
