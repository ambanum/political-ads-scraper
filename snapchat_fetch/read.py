
import datetime
import pathlib
import zipfile
import tempfile
import re

import requests
import pandas as pd

from snapchat_fetch import config


def read_bundle(bundle_path):
    fetch_datetime = datetime.datetime.strptime(
        bundle_path.stem,
        'snapchat-political-ads_2019_fetched-%Y-%m-%d_%H-%M-%S',
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_dir = pathlib.Path(tmpdirname)

        with zipfile.ZipFile(bundle_path, "r") as zip_ref:
            zip_ref.extractall(tmpdirname)

            assert set([
                element.name
                for element in tmp_dir.iterdir()
            ]) == {'readme.txt', 'PoliticalAds.csv'}


            bundle_data = {}

            with open(tmp_dir / 'readme.txt', 'r') as f:
                bundle_data['readme.txt'] = f.read()

            bundle_data['PoliticalAds.csv'] = pd.read_csv(
                tmp_dir / 'PoliticalAds.csv',
                dtype=str,
                keep_default_na=False,
                na_values={},
            )

    return fetch_datetime, bundle_data


# /path/to/venv/python -c "import snapchat_fetch.read; snapchat_fetch.read.download_media()"
def download_media():
    last_archive = sorted(list((config.DATA_DIR / 'snapchat' / '2019').iterdir()))[-1]

    _, bundle_data = read_bundle(last_archive)

    df = bundle_data['PoliticalAds.csv']
    urls = list(df['CreativeUrl']) 

    media_data = []
    for url_list in urls:
        for url in url_list.split(';'):
            groups = re.search(
                r'^https://www\.snap\.com/political-ads/asset/([a-z0-9]+)\?mediaType=([A-Za-z0-9]+)$',
                url
            ).groups()
            media_data.append(groups)

    media_dir = config.DATA_DIR / 'snapchat' / 'media'

    for asset_id, media_type in media_data:
        filepath = media_dir / '{}.{}'.format(asset_id, media_type)

        if not filepath.is_file():
            url = 'https://storage.googleapis.com/ad-manager-political-ads-dump-shadow/{}.{}'.format(asset_id, media_type)
            response = requests.get(url)   
            response.raise_for_status()

            with filepath.open('wb') as file:
                file.write(response.content)
