import os
import re
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import quote

DOMAIN = 'https://genshin-impact.fandom.com'


def PROXY(port=None):
    if port != None:
        return {
            'http': f'http://127.0.0.1:{port}',
            'https': f'http://127.0.0.1:{port}'
        }

    return None


Teyvat = {
    'Mondstadt': {
        'Chinese_name': '蒙德',
        'tags': ['Barbatos', '巴巴托斯', '风神', '风龙']
    },
    'Liyue': {
        'Chinese_name': '璃月',
        'tags': ['Morax', '摩拉克斯', '岩王帝君']
    },
    'Inazuma': {
        'Chinese_name': '稻妻',
        'tags': ['Beelzebul', '巴尔泽布', '雷神', '影']
    },
    'Sumeru': {
        'Chinese_name': '须弥',
        'tags': ['Buer', '布耶尔', '草神', '小吉祥草王', '大慈树王', '草龙']
    },
    'Fontaine': {
        'Chinese_name': '枫丹',
        'tags': ['Focalors', '芙卡洛斯', '水神', '水龙']
    },
    'Natlan': {
        'Chinese_name': '纳塔',
        'tags': ['Pyro', 'War']
    },
    'Snezhnaya': {
        'Chinese_name': '至冬',
        'tags': ['Cryo']
    },
    "Khaenri'ah": {
        'Chinese_name': '坎瑞亚',
        'tags': ['Eclipse Dynasty']
    }
}

Albums = {
    "The Wind and The Star Traveler": "Mondstadt",
    "City of Winds and Idylls": "Mondstadt",
    "Jade Moon Upon a Sea of Clouds": "Liyue",
    "The Stellar Moments": "",
    "Vortex of Legends": "Mondstadt",
    "The Shimmering Voyage": "",
    "Realm of Tranquil Eternity": "Inazuma",
    "The Stellar Moments Vol. 2": "",
    "Islands of the Lost and Forgotten": "Inazuma",
    "Millelith's Watch": "Liyue",
    "The Shimmering Voyage Vol. 2": "",
    "Footprints of the Traveler": "",
    "Footprints of the Traveler (CN)": "",
    "Forest of Jnana and Vidya": "Sumeru",
    "The Stellar Moments Vol. 3": "",
    "The Unfathomable Sand Dunes": "Sumeru",
    "Footprints of the Traveler Vol. 2": "",
    "The Shimmering Voyage Vol. 3": "",
    "Fountain of Belleau": "Fontaine",
    "Fleeting Colors in Flight": "Liyue"
}


def create_dir(dirpath='./data'):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def trim_str_list(input_list, rm_bracket=True):
    output = []
    for s in input_list:
        processed_s = rm_brackets_and_content(s) if rm_bracket else s
        processed_s = processed_s.replace('"', '').strip()
        if processed_s != '':
            output.append(processed_s)

    return list(set(output))


def merge_dicts(dict1, dict2):
    merged_dict = dict1.copy()
    merged_dict.update(dict2)
    return merged_dict


def rm_brackets_and_content(input_string):
    result_string = re.sub(r'\([^)]*\)|\[[^\]]*\]', '', input_string)
    return result_string


def is_decimal(s):
    decimal_pattern = re.compile(r'^\d+\.\d+$')
    return bool(decimal_pattern.match(s))


def find_cross(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    duplicates = set1.intersection(set2)
    if duplicates:
        return list(duplicates)[0]

    return ''
