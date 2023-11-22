import os
import subprocess
from tqdm import tqdm
from utils import *

mscore3 = "D:/Program Files/MuseScore 3/bin/MuseScore3.exe"


def midi_to_mxl(midi_file, mxl_file):
    command = [mscore3, "-o", mxl_file, midi_file]
    result = subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode != 0:
        print(result)


def batch_midi2mxl(game='genshin'):
    create_dir(f'data/{game}_xmls')
    for foldername, _, filenames in os.walk(f'data/{game}_mids'):
        for filename in tqdm(filenames, desc='Converting midi to mxl...'):
            if filename.endswith('.mid'):
                midi_file = os.path.join(
                    foldername, filename).replace('\\', '/')
                mxl_file = midi_file.replace(
                    '.mid', '.mxl').replace(f'/{game}/', f'/{game}_xmls/')
                midi_to_mxl(midi_file, mxl_file)


if __name__ == '__main__':
    batch_midi2mxl()
