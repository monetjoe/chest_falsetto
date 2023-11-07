import re
import requests
from bs4 import BeautifulSoup


def get_score_urls(text='genshin'):
    score_urls = []
    i = 1
    while True:
        print(f"第{i}页...", end="")
        page_url = f'https://musescore.com/sheetmusic?instrument=2&instrumentation=114&page={i}&text={text}'
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        url_pattern = r'https://musescore.com/user/\d+/scores/\d+'

        urls = re.findall(url_pattern, response.text)

        if re.findall('No results', response.text):
            print(f"共{i - 1}页")
            break
        i += 1
        score_urls += urls
    score_urls = list(set(score_urls))
    return score_urls


def get_file_url(id):
    url = f"https://musescore.com/api/jmuse?id={id}&type=midi&index=0&v2=1"
    auth = "38fb9efaae51b0c83b5bb5791a698b48292129e7"
    response = requests.get(url, headers={"Authorization": auth})
    data = response.json()
    info = data.get("info")
    if info:
        return info.get("url")


def download(urls, save_folder="./genshin"):
    for score_url in urls:
        file_url = get_file_url(score_url.split("/")[-1])
        score_name = file_url.split('-Signature=')[1]
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(f'{save_folder}/{score_name}.mid', 'wb') as file:
                file.write(response.content)
            print(f"下载完成: {file_url} => {score_name}")
        else:
            print(f"下载失败: {file_url}")
        print("-" * 50)


if __name__ == "__main__":
    score_urls = get_score_urls("furina")
    download(urls=score_urls)
