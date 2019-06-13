import json

from bs4 import BeautifulSoup


def get_snapshot_data(user_access_token, browser, ad_id):
    response_data_1 = None
    response_data_2 = None

    try:
        snapshot_url = 'https://www.facebook.com/ads/archive/render_ad/?id={ad_id}&access_token={access_token}'.format(
            ad_id=ad_id,
            access_token=user_access_token,
        )
        response_1 = browser.open(snapshot_url)
        response_data_1 = response_1.read()
        soup_1 = BeautifulSoup(response_data_1, 'html.parser')

        scripts_1 = soup_1.findAll('script')
        assert len(scripts_1) == 11, len(scripts_1)

        link_to_real_page = scripts_1[6].text

        page_hash = link_to_real_page[link_to_real_page.index('&__fns&hash='):]
        page_hash = page_hash[:page_hash.index('"')]

        response_2 = browser.open(snapshot_url + page_hash)
        response_data_2 = response_2.read()
        soup_2 = BeautifulSoup(response_data_2, 'html.parser')

        scripts_2 = soup_2.findAll('script')

        assert len(scripts_2) == 10, len(scripts_2)
        script = scripts_2[6].text

        prefix = 'new (require("ServerJS"))().handle('
        suffix = ');'
        assert script[:len(prefix)] == prefix
        assert script[-len(suffix):] == suffix
        json_data = script[len(prefix):-len(suffix)]
        data = json.loads(json_data)

        react_components = []
        for require_item in data['require']:
            if require_item[0] == 'ReactRenderer' and require_item[2][0] == 'PoliticalAdArchiveDemoAd.react':
                react_components.append(require_item[3])
        assert len(react_components) == 1
        react_component_list = react_components[0]
        assert len(react_component_list) == 1
        react_component = react_component_list[0]
        original_snapshot_data = react_component['props']['adCard']['snapshot']

        return {
            'snapshot_raw_data': {
                'markup': data['markup'],
                'require': data['require'],
            },
            'react_component': react_component,
            'media': {
                'images': original_snapshot_data['images'],
                'videos': original_snapshot_data['videos'],
            },
            'page_profile_picture_url': original_snapshot_data['page_profile_picture_url']
        }

    except Exception:
        with open('debug.json', 'w') as f:
            json.dump({
                'response_data_1': response_data_1.decode('utf-8') if response_data_1 else None,
                'response_data_2': response_data_2.decode('utf-8') if response_data_2 else None,
            }, f)
        raise
