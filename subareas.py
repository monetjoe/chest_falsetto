from utils import *
import requests
from bs4 import BeautifulSoup


areas, subareas, soundtracks = {}, {}, {}


def get_areas(region='Mondstadt'):
    page_url = f"https://genshin-impact.fandom.com/wiki/{region}"
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        areas_div = soup.find('div', id='gallery-2')
        area_divs = areas_div.find_all('div', class_='wikia-gallery-item')
        for area_div in area_divs:
            area_a = area_div.find('a')
            area_url = area_a.get('href')
            area_name = area_a.get('title')
            areas[area_name] = {
                'Chinese_name': get_subareas(area_url),
                'tags': list(set([region] + Teyvat[region]['tags']))
            }


def get_subareas(area_url='https://genshin-impact.fandom.com/wiki/Lisha'):
    response = requests.get(area_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cname = soup.find('span', lang='zh-Hans').text
        print(cname)


def get_subarea(area_url):
    response = requests.get(area_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)


if __name__ == "__main__":
    get_subareas()
