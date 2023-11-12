import os
import re
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import quote

DOMAIN = 'https://genshin-impact.fandom.com'

Teyvat = {
    'Mondstadt': {
        'Chinese_name': '蒙德',
        'tags': ['Anemo', 'Freedom']
    },
    'Liyue': {
        'Chinese_name': '璃月',
        'tags': ['Geo', 'Contracts']
    },
    'Inazuma': {
        'Chinese_name': '稻妻',
        'tags': ['Electro', 'Eternity']
    },
    'Sumeru': {
        'Chinese_name': '须弥',
        'tags': ['Dendro', 'Wisdom']
    },
    'Fontaine': {
        'Chinese_name': '枫丹',
        'tags': ['Hydro', 'Justice']
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

Archon = {
    'Venti': 'Barbatos',
    'Zhongli': 'Morax',
    'Raiden Shogun': 'Beelzebul',
    'Nahida': 'Buer',
    'Furina': 'Focalors'
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
