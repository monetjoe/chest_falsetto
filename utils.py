import os
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
        'tags': []
    }
}

Archon = {
    'Venti': 'Barbatos',
    'Zhongli': 'Morax',
    'Raiden_Shogun': 'Beelzebul',
    'Nahida': 'Buer',
    'Furina': 'Focalors'
}


def create_dir(dirpath='./data'):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def trim_str_list(input_list):
    """
    Removes leading and trailing whitespace from all elements in a list of strings.

    Parameters:
    - input_list (list): A list of strings.

    Returns:
    - list: A new list with leading and trailing whitespace removed from each element.
    """
    result_list = [s.strip() for s in input_list]
    return result_list


def merge_dicts(dict1, dict2):
    """
    Merge two dictionaries.

    Parameters:
    - dict1 (dict): The first dictionary.
    - dict2 (dict): The second dictionary.

    Returns:
    - dict: The merged dictionary.
    """
    merged_dict = dict1.copy()
    merged_dict.update(dict2)
    return merged_dict
