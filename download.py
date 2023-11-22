import re
import html
import requests
from utils import *


def clean_windows_filename(input_str):
    # Replace illegal characters with spaces
    cleaned_str = re.sub(r'[\\/:*?"<>|]', ' ', input_str)
    # Remove redundant spaces
    cleaned_str = re.sub(r'\s+', ' ', cleaned_str).strip()
    return cleaned_str


def get_score_urls(keyword='genshin'):
    i = 1
    url_title = {}
    while True:
        print(f"Page {i}...", end="\n")
        page_url = f'https://musescore.com/sheetmusic?instrument=2&instrumentation=114&page={i}&text={keyword}'
        try:
            response = requests.get(page_url)

            if re.findall('No results', response.text):
                print(f"{i - 1} pages in total\n", '-' * 50)
                break

            url_pattern = r'https://musescore.com/user/\d+/scores/\d+'
            urls = list(set(re.findall(url_pattern, response.text)))

            for url in urls:
                url_title[url] = get_title(response.text, url)

        except requests.exceptions.RetryError as e:
            print(f"Max retries exceeded: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        i += 1

    return url_title


def get_file_url(id):
    url = f"https://musescore.com/api/jmuse?id={id}&type=midi&index=0&v2=1"
    auth = "38fb9efaae51b0c83b5bb5791a698b48292129e7"
    try:
        response = requests.get(url, headers={"Authorization": auth})
        data = response.json()
        info = data.get("info")
        if info:
            return info.get("url")

    except requests.exceptions.RetryError as e:
        print(f"Max retries exceeded: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return None


def get_title(response, url, substr='file_score_title":"'):
    try:
        response_txt = html.unescape(str(response))
        index = response_txt.index(url)
        last_index = response_txt.rfind(substr, 0, index)
        if last_index != -1:
            title = str(response_txt[last_index + len(substr):index]).split('","')[
                0].replace('\\n.', '').replace('\\n', ' ').replace('.', ' ').strip()
            return clean_windows_filename(title)

    except requests.exceptions.RetryError as e:
        print(f"Max retries exceeded: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return None


def download(urls: dict, save_folder="./data/genshin_mids", region=''):
    create_dir(save_folder)
    for score_url in urls.keys():
        file_url = get_file_url(score_url.split("/")[-1])
        score_name = f'{region}_{urls[score_url]}'
        # score_name = '#'.join(set([urls[score_url]] + tags))
        try:
            response = requests.get(file_url, proxies=PROXY())
            if response.status_code == 200:
                with open(f'{save_folder}/{score_name}.mid', 'wb') as file:
                    file.write(response.content)

                print(f"Downloaded: {score_name}")

            else:
                print(f"Failed to download: {file_url} => {score_name}")

        except requests.exceptions.RetryError as e:
            print(f"Max retries exceeded: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")


if __name__ == "__main__":
    keywords = []
    regions = list(Teyvat.keys())[:5]

    for region in regions:
        keywords.append(region)
        keywords.append(Teyvat[region]['Chinese_name'])

    for keyword in keywords:
        score_urls = get_score_urls(f"genshin impact {region}")
        download(urls=score_urls, region=region)
