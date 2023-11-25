from utils import *


def get_song_info(song_url):
    try:
        response = requests.get(song_url, proxies=PROXY())
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cname_tds = soup.find_all('small', string='(Simplified)')
            tags, cname = [], []
            if len(cname_tds) > 0:
                for cname_td in cname_tds:
                    cname.append(
                        cname_td.find_next(name='span', lang='zh-Hans').text
                    )

            loc_h3 = soup.find(
                name='h3',
                class_='pi-data-label',
                string='Played In'
            )
            if loc_h3:
                tags += loc_h3.find_next(
                    name='div',
                    class_='pi-data-value'
                ).text.split(',')

            album_h3 = soup.find(
                name='h3',
                class_='pi-data-label',
                string='Album'
            )
            if album_h3:
                tags.append(
                    album_h3.find_next(
                        name='div',
                        class_='pi-data-value'
                    ).text.replace(' (Album)', '')
                )

            feature_h3 = soup.find(
                name='h3',
                class_='pi-data-label',
                string='Featured in'
            )
            if feature_h3:
                tags.append(
                    feature_h3.find_next(
                        name='div',
                        class_='pi-data-value'
                    ).text
                )

            return {
                'Chinese_name': '/'.join(cname),
                'tags': trim_str_list(tags, rm_bracket=False)
            }

        print(f'Failed to get Chinese name of {song_url.split("/")[-1]}')

    except requests.RequestException as e:
        print(f'Error making request of {song_url.split("/")[-1]} : {e}')

    return None


def get_songs(page_url=f"{DOMAIN}/wiki/Category:Soundtrack"):
    soundtracks = {}
    try:
        response = requests.get(page_url, proxies=PROXY())
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            songs_div = soup.find('div', class_='category-page__members')
            song_as = songs_div.find_all(
                name='a',
                class_='category-page__member-link'
            )
            for song_a in tqdm(song_as, desc='Updating soundtracks...'):
                song_name = song_a.get('title').strip()
                if ' - Instrumental' in song_name or '(Album)' in song_name:
                    continue

                song_url = f"{DOMAIN}{song_a.get('href')}"
                song_key = song_name.replace(' (Soundtrack)', '')
                song_info = get_song_info(song_url)
                while not song_info:
                    print(f'Failed to get [{song_name}] info, retrying...')
                    rand_sleep(1, 2)
                    song_info = get_song_info(song_url)

                soundtracks[song_key] = song_info

                # Special items
                if song_key == 'La vaguelette':
                    soundtracks[song_key]['tags'].append('Fontaine')
                elif song_key == 'Novatio Novena':
                    soundtracks[song_key]['tags'].append('Inazuma')

            nextpage = soup.find('a', class_='category-page__pagination-next')
            if nextpage:
                nextpage_url = nextpage.get('href')
                nextpage_songs = get_songs(nextpage_url)
                while not nextpage_songs:
                    print(
                        f'Failed to get the page of [{nextpage_url}], retrying...')
                    rand_sleep(1, 2)
                    nextpage_songs = get_songs(nextpage_url)

                soundtracks = merge_dicts(soundtracks, nextpage_songs)

        else:
            print(
                f'Failed to request {page_url} : HTTP {response.status_code}'
            )

    except requests.RequestException as e:
        print(f'Error making request of {page_url.split("/")[-1]} : {e}')

    return soundtracks


def save_soundtracks(soundtrack_path='./data/soundtracks.json', force_upd=True):
    if force_upd or ((not force_upd) and (not os.path.exists(soundtrack_path))):
        soundtrack_dict = get_songs()
        with open(soundtrack_path, 'w', encoding='utf-8') as json_file:
            json.dump(soundtrack_dict, json_file, ensure_ascii=False, indent=4)

        print(f'Soundtracks have been updated into {soundtrack_path}')
        print(f'{len(soundtrack_dict.keys())} in total')


if __name__ == "__main__":
    create_dir()
    save_soundtracks()
