import os
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from utils import *


def get_boss_Chinese_name(boss_url):
    response = requests.get(boss_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find_all('span', lang='zh-Hans')[-1].text

    print(f'Failed to get Chinese name of {boss_url.split("/")[-1]}')
    return None


def get_bosses(page_url=f"{DOMAIN}/wiki/Weekly_Boss"):
    weeklybosses = {}
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        bosses_tab = soup.find('table', class_='tdc1')
        boss_trs = bosses_tab.find_all(name='tr')
        for boss_tr in tqdm(boss_trs, desc='Updating weekly booses...'):
            boss_td = boss_tr.find('td')
            if not boss_td:
                continue

            boss_a = boss_td.find('span', class_='card-caption').find('a')
            boss_name = boss_a.text
            boss_url = f"{DOMAIN}{boss_a.get('href')}"
            boss_tags = boss_td.find_all('a', recursive=False)
            tags = []
            for boss_tag in boss_tags:
                tags.append(boss_tag.get('title'))

            weeklybosses[boss_name] = {
                'Chinese_name': get_boss_Chinese_name(boss_url),
                'tags': tags
            }

    else:
        print(f'\nFailed to request {page_url} : HTTP {response.status_code}')

    return weeklybosses


if __name__ == "__main__":
    points_path = './data/bosses.json'
    if FORCE_UPD or ((not FORCE_UPD) and (not os.path.exists(points_path))):
        create_dir(DATA_DIR)
        area_dict = get_bosses()
        with open(points_path, 'w', encoding='utf-8') as json_file:
            json.dump(area_dict, json_file, ensure_ascii=False)

        print(f'Weekly bosses have been updated into {points_path}.')
