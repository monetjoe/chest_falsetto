import os
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from utils import *


def get_area_info(area_url):
    response = requests.get(area_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cname = soup.find('span', lang='zh-Hans').text
        tags = soup.find_all('div', class_='pi-data-value',
                             limit=2)[1].text.split(',')

        return {
            'Chinese_name': cname,
            'tags': trim_str_list(tags)
        }

    print(f'Failed to get Chinese name of {area_url.split("/")[-1]}')
    return None


def get_areas(page_url=f"{DOMAIN}/wiki/Area"):
    areas = {}
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        i = 0
        while soup.find('div', id=f'gallery-{2*i+1}'):
            areas_div = soup.find('div', id=f'gallery-{2*i+1}')
            area_divs = areas_div.find_all('div', class_='wikia-gallery-item')
            for area_div in tqdm(area_divs, desc=f'Updating areas {i+1}...'):
                area_a = area_div.find(
                    'div', class_='lightbox-caption').find('a')
                area_name = area_a.text.replace(' ', '_')
                area_url = f'{DOMAIN}/wiki/{area_name}'
                areas[area_name] = get_area_info(area_url)

            i += 1

    else:
        print(f'Failed to request {page_url} : HTTP {response.status_code}')

    return areas


if __name__ == "__main__":
    areas_path = './data/areas.json'
    if FORCE_UPD or ((not FORCE_UPD) and (not os.path.exists(areas_path))):
        create_dir(DATA_DIR)
        area_dict = get_areas()
        with open(areas_path, 'w', encoding='utf-8') as json_file:
            json.dump(area_dict, json_file, ensure_ascii=False)

        print(f'Characters has been updated into {areas_path}.')
