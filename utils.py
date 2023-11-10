DATA_DIR = './data'
CHARACTER_PATH = f'{DATA_DIR}/characters.json'

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
    }
}

Archon = {
    'Venti': 'Barbatos',
    'Zhongli': 'Morax',
    'Raiden_Shogun': 'Beelzebul',
    'Nahida': 'Buer',
    'Furina': 'Focalors'
}


def create_dir(dirpath):
    import os
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
