import json

from fb_fetch import fetch


# Load ads

with open('../data/FR/facebook-ads-archive_FR_2019-05-16_20-37-43.json', 'r') as f:
    data_old = json.load(f)
with open('../data/FR/facebook-ads-archive_FR_2019-05-20_14-03-03.json', 'r') as f:
    data_new = json.load(f)

print('Comparing {} old ads and {} new ads.'.format(len(data_old), len(data_new)))

for field in fetch.FIELDS:
    print('{} ads have the field "{}" on a total of {}'.format(
        sum([field in ad for ad in data_new]),
        field,
        len(data_new)
    ))


# Index

def to_dict(ads):
    ads_by_id = {}
    for ad in ads:
        ad_id = fetch.get_ad_id(ad)
        assert ad_id not in ads_by_id, ad
        ads_by_id[ad_id] = ad
    return ads_by_id

data_old_by_id = to_dict(data_old)
data_new_by_id = to_dict(data_new)


# Find removed ads

old_ids = set(data_old_by_id.keys())
new_ids = set(data_new_by_id.keys())

new_only_ids = new_ids - old_ids
old_only_ids = old_ids - new_ids
both_ids = old_ids & new_ids

assert len(new_only_ids) + len(both_ids) == len(new_ids)
assert len(old_only_ids) + len(both_ids) == len(old_ids)

print('{} ads have been removed.'.format(len(old_only_ids)))

for removed_ad_id in old_only_ids:
    removed_ad = data_old_by_id[removed_ad_id]
    print()
    print(removed_ad_id)
    print(removed_ad['ad_creative_body'])


# Find removed fields

for ad_id in both_ids:
    old_ad = data_old_by_id[ad_id]
    new_ad = data_new_by_id[ad_id]

    removed_fields = set(old_ad)-set(new_ad)
    if removed_fields:
        print('Ad {} had this fields removed: {}'.format(
            ad_id,
            removed_fields,
        ))
