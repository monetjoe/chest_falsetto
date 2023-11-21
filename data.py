from areas import save_areas
from subareas import save_subareas
from bosses import save_weekly_bosses
from characters import save_characters
from soundtracks import save_soundtracks
from points import save_points_of_interest
from utils import *


def extract_melody(abc):
    lines = abc.split("\n")
    melody = []

    for line in lines:
        if line.startswith("V:") or line.startswith("%%"):
            if line == "V:2":
                break
            continue
        else:
            melody.append(line)

    return "\n".join(melody)


if __name__ == "__main__":
    create_dir()
    save_weekly_bosses()
    save_areas()
    save_characters()
    save_subareas()
    save_points_of_interest()
    save_soundtracks()
