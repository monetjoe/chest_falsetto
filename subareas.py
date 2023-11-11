import os
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from utils import *


def get_subarea_info(subarea_url):
    response = requests.get(subarea_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cname = soup.find('span', lang='zh-Hans').text
        tags = soup.find_all('div', class_='pi-data-value',
                             limit=2)[1].text.split(',')

        return {
            'Chinese_name': cname,
            'tags': trim_str_list(tags)
        }

    print(f'\nFailed to get Chinese name of {subarea_url.split("/")[-1]}')
    return None


def get_subareas(page_url=f"{DOMAIN}/wiki/Category:Subareas"):
    subareas = {}
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        subareas_div = soup.find('div', class_='category-page__members')
        subarea_as = subareas_div.find_all(
            'a', class_='category-page__member-link')
        for subarea_a in tqdm(subarea_as, desc='Updating subareas...'):
            subarea_name = subarea_a.get('title').split('/')[0]
            subarea_url = f"{DOMAIN}/wiki/{quote(subarea_name)}"
            subareas[subarea_name.replace(
                '"', '')] = get_subarea_info(subarea_url)

    else:
        print(f'Failed to request {page_url} : HTTP {response.status_code}')

    return subareas


if __name__ == "__main__":
    subareas_path = './data/subareas.json'
    if FORCE_UPD or ((not FORCE_UPD) and (not os.path.exists(subareas_path))):
        create_dir(DATA_DIR)
        area_dict = get_subareas()
        with open(subareas_path, 'w', encoding='utf-8') as json_file:
            json.dump(area_dict, json_file, ensure_ascii=False)

        print(f'Subareas have been updated into {subareas_path}.')
