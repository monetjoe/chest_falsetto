import re
import os
import html
import requests


def create_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def get_score_urls(keyword='genshin'):
    i = 1
    url_title = {}
    while True:
        print(f"Page {i}...", end="\n")
        page_url = f'https://musescore.com/sheetmusic?instrument=2&instrumentation=114&page={i}&text={keyword}'
        response = requests.get(page_url)

        if re.findall('No results', response.text):
            print(f"{i - 1} pages in total\n", '-' * 50)
            break

        url_pattern = r'https://musescore.com/user/\d+/scores/\d+'
        urls = list(set(re.findall(url_pattern, response.text)))

        for url in urls:
            url_title[url] = get_title(response.text, url)

        i += 1

    return url_title


def get_file_url(id):
    url = f"https://musescore.com/api/jmuse?id={id}&type=midi&index=0&v2=1"
    auth = "38fb9efaae51b0c83b5bb5791a698b48292129e7"
    response = requests.get(url, headers={"Authorization": auth})
    data = response.json()
    info = data.get("info")
    if info:
        return info.get("url")


def get_title(response, url, substr='file_score_title":"'):
    response_txt = html.unescape(str(response))
    index = response_txt.index(url)
    last_index = response_txt.rfind(substr, 0, index)
    if last_index != -1:
        return str(response_txt[last_index + len(substr):index]).split('","')[0].replace('\\n.', '.').replace('\\n', '_')
    else:
        return None


def download(urls: dict, save_folder="./genshin"):
    create_dir(save_folder)
    for score_url in urls.keys():
        file_url = get_file_url(score_url.split("/")[-1])
        score_name = urls[score_url]
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(f'{save_folder}/{score_name}.mid', 'wb') as file:
                file.write(response.content)

            print(f"Downloaded: {score_name}")

        else:
            print(f"Failed to download: {file_url} => {score_name}")


if __name__ == "__main__":
    score_urls = get_score_urls("genshin furina")
    download(urls=score_urls)
