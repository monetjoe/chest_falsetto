from html import unescape
from utils import *


def get_character_info(char_url):
    cname, affiliation = [], []
    try:
        response = requests.get(f'{DOMAIN}{char_url}', proxies=PROXY())
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cname_tds = soup.find_all('small', string='(Simplified)')
            if len(cname_tds) > 0:
                for cname_td in cname_tds:
                    cname.append(
                        cname_td.find_next(name='span', lang='zh-Hans').text
                    )

            org_h3 = soup.find(
                name='h3',
                string=unescape('Affil&shy;i&shy;a&shy;tion'),
                class_='pi-data-label'
            )
            if org_h3:
                affiliation = [org_h3.find_next(
                    name='div',
                    class_='pi-data-value'
                ).text]

            orgs_h3 = soup.find(
                name='h3',
                string=unescape('Affil&shy;i&shy;a&shy;tions'),
                class_='pi-data-label'
            )
            if orgs_h3:
                orgs_ul = orgs_h3.find_next('ul')
                for org_li in orgs_ul:
                    affiliation.append(org_li.text)

        else:
            print(f'\nFailed to get Chinese name of {char_url.split("/")[-1]}')

    except requests.exceptions.RetryError as e:
        print(f"Max retries exceeded: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return cname, affiliation


def get_characters(page_url=f"{DOMAIN}/wiki/Character/List"):
    characters = {}
    response = requests.get(page_url, proxies=PROXY())
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        char_tab = soup.find('tbody')
        char_trs = char_tab.find_all('tr')
        for char_tr in tqdm(char_trs[1:], desc='Updating characters...'):
            char_tds = char_tr.find_all('td')
            if char_tds[5].find('a') == None:
                continue

            url = char_tds[0].find('a').get('href')
            name = char_tds[1].find('a').text.strip()
            element = char_tds[3].find('a').get('href').split('/')[-1]
            weapon = char_tds[4].find('a').get('href').split('/')[-1]
            region = char_tds[5].find('a').get('href').split('/')[-1]
            gender = char_tds[6].find('a').get('href').split(
                ':')[-1].replace('_Characters', '').replace('_', ' ')

            tags = [element, region, gender, weapon]
            cname, affiliation = get_character_info(url)
            while (not cname) and (not affiliation):
                print(f'Failed to get [{name}] info, retrying...')
                rand_sleep(1, 2)
                cname, affiliation = get_character_info(url)

            if len(affiliation) > 0:
                tags += affiliation

            characters[name] = {
                'Chinese_name': '/'.join(cname),
                'tags': trim_str_list(tags)
            }

    else:
        print(f'Failed to request {page_url} : HTTP {response.status_code}')

    return characters


def save_characters(character_path=f'./data/characters.json', force_upd=True):
    if force_upd or ((not force_upd) and (not os.path.exists(character_path))):
        char_dict = get_characters()
        with open(character_path, 'w', encoding='utf-8') as json_file:
            json.dump(char_dict, json_file, ensure_ascii=False, indent=4)

        print(f'Characters have been updated into {character_path}')
        print(f'{len(char_dict.keys())} in total')


if __name__ == "__main__":
    create_dir()
    save_characters()
