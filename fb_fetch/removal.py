
import json
import sys

from fb_fetch import fetch


def compare_ad_lists(ads_old, ads_new):

    print('Comparing {} old ads and {} new ads.'.format(len(ads_old), len(ads_new)))
    print()

    for field in fetch.FIELDS:
        print('{} ads have the field "{}" on a total of {}'.format(
            sum([field in ad for ad in ads_new]),
            field,
            len(ads_new)
        ))
    print()


    # Index

    def to_dict(ads):
        ads_by_id = {}
        for ad in ads:
            ad_id = fetch.get_ad_id(ad)
            assert ad_id not in ads_by_id, ad
            ads_by_id[ad_id] = ad
        return ads_by_id

    ads_old_by_id = to_dict(ads_old)
    ads_new_by_id = to_dict(ads_new)


    # Find removed ads

    old_ids = set(ads_old_by_id.keys())
    new_ids = set(ads_new_by_id.keys())

    new_only_ids = new_ids - old_ids
    old_only_ids = old_ids - new_ids
    both_ids = old_ids & new_ids

    assert len(new_only_ids) + len(both_ids) == len(new_ids)
    assert len(old_only_ids) + len(both_ids) == len(old_ids)

    print('{} ads have been added.'.format(len(new_only_ids)))
    print('{} ads have been removed.'.format(len(old_only_ids)))
    print()
    print('='*80)

    for removed_ad_id in old_only_ids:
        removed_ad = ads_old_by_id[removed_ad_id]
        print('-'*80)
        print(removed_ad_id)
        print(removed_ad['ad_creative_body'])

    print()
    print('='*80)
    print()

    # Find removed fields

    for ad_id in both_ids:
        old_ad = ads_old_by_id[ad_id]
        new_ad = ads_new_by_id[ad_id]

        removed_fields = set(old_ad)-set(new_ad)
        if removed_fields:
            print('Ad {} had this fields removed: {}'.format(
                ad_id,
                removed_fields,
            ))


def main(filename_old, filename_new):

    with open(filename_old, 'r') as f:
        ads_old = json.load(f)
    with open(filename_new, 'r') as f:
        ads_new = json.load(f)

    compare_ad_lists(ads_old=ads_old, ads_new=ads_new)


if __name__ == '__main__':

    # Load ads
    if len(sys.argv) != 3:
        print("""
Usage:
> python fb_fetch/removal/py data/FR/facebook-ads-archive_FR_2019-05-16_20-37-43.json data/FR/facebook-ads-archive_FR_2019-05-20_14-03-03.json
""")
        exit()

    main(filename_old=sys.argv[1], filename_new=sys.argv[2])
