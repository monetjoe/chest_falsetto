import os
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from utils import *


def get_point_info(point_url):
    response = requests.get(point_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cname = soup.find('span', lang='zh-Hans')
        if cname:
            cname = cname.text
        else:
            cname = ''

        tags = soup.find_all(
            name='div',
            class_='pi-data-value',
            limit=2
        )[1].text.split(',')

        return {
            'Chinese_name': cname,
            'tags': trim_str_list(tags)
        }

    print(f'Failed to get Chinese name of {point_url.split("/")[-1]}')
    return None


def get_points(page_url=f"{DOMAIN}/wiki/Category:Points_of_Interest"):
    points = {}
    response = requests.get(page_url)
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
            points[point_name.replace('"', '')] = get_point_info(
                point_url
            )

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
            json.dump(area_dict, json_file, ensure_ascii=False)

        print(f'Points of interest have been updated into {points_path}.')


if __name__ == "__main__":
    create_dir()
    save_points_of_interest()
