from utils import *


def get_subarea_info(subarea_url):
    cname, tags = [], []
    response = requests.get(subarea_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cname_tds = soup.find_all('small', string='(Simplified)')

        if len(cname_tds) > 0:
            for cname_td in cname_tds:
                cname.append(cname_td.find_next('span', lang='zh-Hans').text)

        loc_h3 = soup.find(
            name='h3',
            class_='pi-data-label',
            string='Location'
        )
        if loc_h3:
            tags += loc_h3.find_next(
                name='div',
                class_='pi-data-value'
            ).text.split(',')

        sub_div = soup.find('div', class_='custom-tabs-default')
        if sub_div:
            offset_span = sub_div.find('span', class_='active-tab')
            offset_span_txt = offset_span.text

            if offset_span_txt == 'Story':
                tags.append(soup.find('h1').text)

            elif is_decimal(offset_span_txt):
                tags.append(f'Version {offset_span_txt.strip()}')

            sub_spans = list(offset_span.find_all_next(
                name='span',
                class_='inactive-tab'
            ))

            for sub_span in sub_spans:
                sub_a = sub_span.find('a')
                if sub_a.text != 'Map' and sub_a.text != 'Gallery':
                    sub_url = sub_a.get('href')
                    ret1, ret2 = get_subarea_info(f'{DOMAIN}{sub_url}')
                    cname += ret1
                    tags += ret2

    else:
        print(f'\nFailed to get Chinese name of {subarea_url.split("/")[-1]}')

    return cname, tags


def get_subareas(page_url=f"{DOMAIN}/wiki/Category:Subareas"):
    subareas = {}
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        subareas_div = soup.find('div', class_='category-page__members')
        subarea_as = subareas_div.find_all(
            name='a',
            class_='category-page__member-link'
        )
        for subarea_a in tqdm(subarea_as, desc='Updating subareas...'):
            subarea_name = subarea_a.get('title').split('/')[0]
            subarea_url = f"{DOMAIN}/wiki/{quote(subarea_name)}"
            cname, tags = get_subarea_info(subarea_url)
            subareas[subarea_name.replace('"', '')] = {
                'Chinese_name': '/'.join(cname),
                'tags': trim_str_list(tags)
            }

        nextpage = soup.find('a', class_='category-page__pagination-next')
        if nextpage:
            nextpage_url = nextpage.get('href')
            subareas = merge_dicts(subareas, get_subareas(nextpage_url))

    else:
        print(f'Failed to request {page_url} : HTTP {response.status_code}')

    return subareas


def save_subareas(subareas_path='./data/subareas.json', force_upd=True):
    if force_upd or ((not force_upd) and (not os.path.exists(subareas_path))):
        area_dict = get_subareas()
        with open(subareas_path, 'w', encoding='utf-8') as json_file:
            json.dump(area_dict, json_file, ensure_ascii=False, indent=4)

        print(f'Subareas have been updated into {subareas_path}.')


if __name__ == "__main__":
    create_dir()
    save_subareas()
