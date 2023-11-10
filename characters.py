import os
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from utils import *

FORCE_UPD = True
DOMAIN = 'https://genshin-impact.fandom.com'


def get_Chinese_char_name(char_url):
    response = requests.get(f'{DOMAIN}{char_url}')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find('span', lang='zh-Hans').text

    print(f'Failed to get Chinese name of {char_url.split("/")[-1]}')
    return ''


def get_characters(page_url="https://genshin-impact.fandom.com/wiki/Character/List"):
    characters = {}
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        char_tab = soup.find('tbody')
        char_trs = char_tab.find_all('tr')
        for char_tr in tqdm(char_trs[1:], desc='Updating characters...'):
            char_tds = char_tr.find_all('td')
            if char_tds[5].find('a') == None:
                continue

            url = char_tds[0].find('a').get('href')
            name = url.split('/')[-1]
            element = char_tds[3].find('a').get('href').split('/')[-1]
            region = char_tds[5].find('a').get('href').split('/')[-1]
            gender = char_tds[6].find('a').get('href').split(
                ':')[-1].replace('_Characters', '')

            characters[name] = {
                'Chinese_name': get_Chinese_char_name(url),
                'tags': [element, region, gender]
            }

    else:
        print(f'Failed to request {page_url} : HTTP {response.status_code}')

    return characters


if __name__ == "__main__":
    if FORCE_UPD or ((not FORCE_UPD) and (not os.path.exists(CHARACTER_PATH))):
        create_dir(DATA_DIR)
        char_dict = get_characters()
        with open(CHARACTER_PATH, 'w', encoding='utf-8') as json_file:
            json.dump(char_dict, json_file, ensure_ascii=False)

        print(f'Characters has been updated into {CHARACTER_PATH}.')
