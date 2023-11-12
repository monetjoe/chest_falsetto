from html import unescape
from utils import *


def get_boss_info(boss_url):
    cname, tags = [], []
    response = requests.get(boss_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cname_tds = soup.find_all('small', string='(Simplified)')
        if len(cname_tds) > 0:
            for cname_td in cname_tds:
                cname.append(
                    cname_td.find_next(name='span', lang='zh-Hans').text
                )

        loc_h3 = soup.find(
            name='h3',
            class_='pi-data-label',
            string=unescape('Loca&shy;tion(s)')
        )
        if loc_h3:
            tags += loc_h3.find_next(
                name='div',
                class_='pi-data-value'
            ).text.split(',')

    else:
        print(f'Failed to get Chinese name of {boss_url.split("/")[-1]}')

    return cname, tags


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
            cname, tags = get_boss_info(boss_url)
            for boss_tag in boss_tags:
                tags.append(boss_tag.get('title'))

            weeklybosses[boss_name] = {
                'Chinese_name': '/'.join(trim_str_list(cname)),
                'tags': trim_str_list(tags)
            }

    else:
        print(f'\nFailed to request {page_url} : HTTP {response.status_code}')

    return weeklybosses


def save_weekly_bosses(boss_path='./data/bosses.json', force_upd=True):
    if force_upd or ((not force_upd) and (not os.path.exists(boss_path))):
        area_dict = get_bosses()
        with open(boss_path, 'w', encoding='utf-8') as json_file:
            json.dump(area_dict, json_file, ensure_ascii=False, indent=4)

        print(f'Weekly bosses have been updated into {boss_path}.')


if __name__ == "__main__":
    create_dir()
    save_weekly_bosses()
