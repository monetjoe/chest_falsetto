from utils import *


def special_point_region(tags):
    if 'Veluriyam Mirage' in tags:
        return 'Sumeru'

    if 'Golden Apple Archipelago' in tags:
        return 'Mondstadt'

    return ''


def get_point_info(point_url):
    response = requests.get(point_url, proxies=PROXY())
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cname_tds = soup.find_all('small', string='(Simplified)')
        tags, cname = [], []
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

        map_h3 = soup.find(
            name='h3',
            class_='pi-data-label',
            string='World Map'
        )
        if map_h3:
            tags.append(map_h3.find_next(
                name='div',
                class_='pi-data-value'
            ).text)

        lv_h3 = soup.find(
            name='h3',
            class_='pi-data-label',
            string='Map Level'
        )
        if lv_h3:
            tags.append(lv_h3.find_next(
                name='div',
                class_='pi-data-value'
            ).text)

        quest_h3 = soup.find(
            name='h3',
            class_='pi-data-label',
            string='Quest'
        )
        if quest_h3:
            tags.append(quest_h3.find_next(
                name='div',
                class_='pi-data-value'
            ).text)

        region = special_point_region(tags)
        if region != '':
            tags.append(region)

        return {
            'Chinese_name': '/'.join(cname),
            'tags': trim_str_list(tags)
        }

    print(f'Failed to get Chinese name of {point_url.split("/")[-1]}')
    return None


def get_points(page_url=f"{DOMAIN}/wiki/Category:Points_of_Interest"):
    points = {}
    response = requests.get(page_url, proxies=PROXY())
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        points_div = soup.find('div', class_='category-page__members')
        point_as = points_div.find_all(
            name='a',
            class_='category-page__member-link'
        )
        for point_a in tqdm(point_as, desc='Updating points of interest...'):
            point_name = point_a.get('title').split('/')[0]
            point_url = f"{DOMAIN}/wiki/{quote(point_name)}"
            point_key = point_name.replace('"', '')
            points[point_key] = get_point_info(point_url)

        nextpage = soup.find('a', class_='category-page__pagination-next')
        if nextpage:
            nextpage_url = nextpage.get('href')
            points = merge_dicts(points, get_points(nextpage_url))

    else:
        print(f'\nFailed to request {page_url} : HTTP {response.status_code}')

    return points


def save_points_of_interest(points_path='./data/points.json', force_upd=True):
    if force_upd or ((not force_upd) and (not os.path.exists(points_path))):
        area_dict = get_points()
        with open(points_path, 'w', encoding='utf-8') as json_file:
            json.dump(area_dict, json_file, ensure_ascii=False, indent=4)

        print(f'Points of interest have been updated into {points_path}.')


if __name__ == "__main__":
    create_dir()
    save_points_of_interest()
