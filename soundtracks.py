import os
import time
import json
import random
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from utils import *


def get_song_info(song_url):
    time.sleep(random.uniform(0.1, 1.0))
    try:
        response = requests.get(song_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tags = []
            cname = soup.find('span', lang='zh-Hans')
            if cname:
                cname = cname.text
            else:
                cname = ''

            play_h3 = soup.find(
                name='h3',
                class_='pi-data-label',
                string='Played In'
            )
            if play_h3:
                tags.append(play_h3.find_next('div').text)

            album_h3 = soup.find(
                name='h3',
                class_='pi-data-label',
                string='Album'
            )
            if album_h3:
                tags.append(album_h3.find_next('div').text)

            feature_h3 = soup.find(
                name='h3',
                class_='pi-data-label',
                string='Featured in'
            )
            if feature_h3:
                tags.append(feature_h3.find_next('div').text)

            return {
                'Chinese_name': cname,
                'tags': trim_str_list(tags)
            }

        print(f'Failed to get Chinese name of {song_url.split("/")[-1]}')

    except requests.RequestException as e:
        print(f'Error making request of {song_url.split("/")[-1]} : {e}')

    return None


def get_songs(page_url=f"{DOMAIN}/wiki/Category:Soundtrack"):
    time.sleep(random.uniform(0.1, 1.0))
    soundtracks = {}
    try:
        response = requests.get(page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            songs_div = soup.find('div', class_='category-page__members')
            song_as = songs_div.find_all(
                name='a',
                class_='category-page__member-link'
            )
            for song_a in tqdm(song_as, desc='Updating soundtracks...'):
                song_name = song_a.get('title').strip()
                song_url = f"{DOMAIN}{song_a.get('href')}"
                soundtracks[song_name] = get_song_info(song_url)

            nextpage = soup.find('a', class_='category-page__pagination-next')
            if nextpage:
                nextpage_url = nextpage.get('href')
                soundtracks = merge_dicts(soundtracks, get_songs(nextpage_url))

        else:
            print(
                f'Failed to request {page_url} : HTTP {response.status_code}'
            )

    except requests.RequestException as e:
        print(f'Error making request of {page_url.split("/")[-1]} : {e}')

    return soundtracks


if __name__ == "__main__":
    soundtrack_path = './data/soundtracks.json'
    if FORCE_UPD or ((not FORCE_UPD) and (not os.path.exists(soundtrack_path))):
        create_dir(DATA_DIR)
        soundtrack_dict = get_songs()
        with open(soundtrack_path, 'w', encoding='utf-8') as json_file:
            json.dump(soundtrack_dict, json_file, ensure_ascii=False)

        print(f'Soundtracks have been updated into {soundtrack_path}.')
