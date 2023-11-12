from utils import *


def get_area_info(area_url):
    tags, cname = [], []
    response = requests.get(area_url)
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
            string='Location'
        )
        if loc_h3:
            tags += loc_h3.find_next(
                name='div',
                class_='pi-data-value'
            ).text.split(',')

        events_h3 = soup.find(
            name='h3',
            class_='pi-data-label',
            string='Events'
        )
        if events_h3:
            events_div = events_h3.find_next(
                name='div',
                class_='pi-data-value'
            )
            event_as = events_div.find_all('a')
            for event_a in event_as:
                tags.append(event_a.get('title'))

        event_h3 = soup.find(
            name='h3',
            class_='pi-data-label',
            string='Event'
        )
        if event_h3:
            tags.append(event_h3.find_next(
                name='div',
                class_='pi-data-value'
            ).text)

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
                    ret1, ret2 = get_area_info(f'{DOMAIN}{sub_url}')
                    cname += ret1
                    tags += ret2

    else:
        print(f'\nFailed to get Chinese name of {area_url.split("/")[-1]}')

    return cname, tags


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
                    name='div',
                    class_='lightbox-caption'
                ).find('a')
                area_name = area_a.text.strip()
                area_url = f'{DOMAIN}/wiki/{quote(area_name)}'
                cname, tags = get_area_info(area_url)
                areas[area_name.replace('"', '')] = {
                    'Chinese_name': '/'.join(trim_str_list(cname)),
                    'tags': trim_str_list(tags)
                }

            i += 1

    else:
        print(f'Failed to request {page_url} : HTTP {response.status_code}')

    return areas


def save_areas(areas_path='./data/areas.json', force_upd=True):
    if force_upd or ((not force_upd) and (not os.path.exists(areas_path))):
        area_dict = get_areas()
        with open(areas_path, 'w', encoding='utf-8') as json_file:
            json.dump(area_dict, json_file, ensure_ascii=False, indent=4)

        print(f'Areas have been updated into {areas_path}.')


if __name__ == "__main__":
    create_dir()
    save_areas()
