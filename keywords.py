import json
from utils import *


def region_keywords():
    regions = list(Teyvat.keys())[:5]
    region_keys = {}
    for region in regions:
        region_keys[region] = Teyvat[region]['tags']
        region_keys[region].append(Teyvat[region]['Chinese_name'])

    return region_keys


def load_subarea_tags(baseline=region_keywords(), jsoname='subareas'):
    keywords = baseline
    with open(f'./data/{jsoname}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        items = dict(data).keys()
        for item in tqdm(items, desc=f'Extracting {jsoname} regions...'):
            region = find_cross(
                data[item]['tags'],
                keywords
            )

            if region != '':
                keywords[region].append(item)
                keywords[region] += data[item]['Chinese_name'].split('/')

            else:
                print(f'{jsoname} [{item}] has no region.')

    return keywords


def save_keywords(keywords_dict, keywords_path='./data/keywords.json', force_upd=True):
    if force_upd or ((not force_upd) and (not os.path.exists(keywords_path))):
        with open(keywords_path, 'w', encoding='utf-8') as json_file:
            json.dump(keywords_dict, json_file, ensure_ascii=False, indent=4)

        print(f'Kewords have been updated into {keywords_path}.')


if __name__ == "__main__":
    jsonames = [
        'areas',
        'bosses',
        'characters',
        'points',
        # 'soundtracks'
    ]

    benchmark = load_subarea_tags()

    for jsoname in jsonames:
        benchmark = load_subarea_tags(baseline=benchmark, jsoname=jsoname)

    for key in benchmark.keys():
        benchmark[key] = trim_str_list(benchmark[key])

    save_keywords(benchmark)
