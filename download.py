import re
import html
import requests
from utils import *


def get_scores(keyword='genshin', region='Teyvat'):
    i = 1
    scores = {}
    while True:
        # print(f"Page {i}...", end="\n")
        page_url = f'https://musescore.com/sheetmusic?instrument=2&instrumentation=114&page={i}&text={keyword}'
        try:
            response = requests.get(page_url, proxies=PROXY())

            if re.findall('No results', response.text):
                # print(f"[{keyword}] {i - 1} pages in total\n", '-' * 50)
                break

            url_pattern = r'https://musescore.com/user/\d+/scores/\d+'
            urls = list(set(re.findall(url_pattern, response.text)))

            for url in urls:
                score_id = url.split('/')[-1]
                score_title = get_title(response.text, url)
                while not score_title:
                    print(f'Failed to get title of {url}, retrying...')
                    rand_sleep(1, 2)
                    score_title = get_title(response.text, url)

                scores[score_id] = {
                    'url': url,
                    'title': score_title,
                    'region': region
                }

        except requests.exceptions.RetryError as e:
            print(f"Max retries exceeded: {e}, retrying...")
            i -= 1

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}, retrying...")
            i -= 1

        i += 1

    return scores


def get_file_url(id):
    url = f"https://musescore.com/api/jmuse?id={id}&type=midi&index=0&v2=1"
    auth = "38fb9efaae51b0c83b5bb5791a698b48292129e7"
    try:
        response = requests.get(
            url, headers={"Authorization": auth}, proxies=PROXY())
        data = response.json()
        info = data.get("info")
        if info:
            return info.get("url")

    except requests.exceptions.RetryError as e:
        print(f"Max retries exceeded: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return None


def get_title(response, url, substr='"file_score_title":"'):
    try:
        response_txt = html.unescape(str(response))
        index = response_txt.index(url)
        fst_index = response_txt.find(substr, 0, index)
        if fst_index != -1:
            piece_with_title = str(response_txt[fst_index:index])
            waiting_list = piece_with_title.split(substr)
            waiting_list.reverse()
            for item in waiting_list:
                title = item.split('","')[0].replace('\\n.', '').replace(
                    '\\n', ' ').replace('.', ' ').strip()
                if title != '':
                    return clean_windows_filename(title)

    except requests.exceptions.RetryError as e:
        print(f"Max retries exceeded: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return None


def download(file_url, save_path):
    success = False
    try:
        response = requests.get(file_url, proxies=PROXY())
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)

            success = True
            print(f"Downloaded: {save_path}")

        else:
            print(f"Failed to download: {file_url} => {save_path}")

    except requests.exceptions.RetryError as e:
        print(f"Max retries exceeded: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return success


def relabel_scores(scores: dict, regions=list(Teyvat.keys())[:5], keywords_json='./data/keywords.json'):
    result = scores

    with open(keywords_json, 'r', encoding='utf-8') as json_file:
        regions_tag = json.load(json_file)

    for score_id in scores.keys():
        if scores[score_id]['region'] == "Teyvat":
            score_title = scores[score_id]['title']
            for region in regions:
                region_tags = [region] + regions_tag[region]
                for region_tag in region_tags:
                    if region_tag.lower() in score_title.lower():
                        result[score_id]['region'] = region

    return result


def save_scores(keywords_json='./data/keywords.json', scores_json='./data/scores.json'):
    if os.path.exists(scores_json):
        print('scores.json already exists, skip...')
        return

    with open(keywords_json, 'r', encoding='utf-8') as json_file:
        regions = json.load(json_file)

    # load scores without label
    score_infos = get_scores("genshin", "Teyvat")
    score_infos = merge_dicts(score_infos, get_scores("原神", "Teyvat"))

    # add label for scores, may cover some of above
    for region in regions.keys():
        keywords = [region] + regions[region]
        for keyword in tqdm(keywords, desc=f'Getting scores by keywords from {region}...'):
            keyword_scores = get_scores(f"genshin {keyword}", region)
            keyword_scores = merge_dicts(
                keyword_scores,
                get_scores(f"原神 {keyword}", region)
            )
            score_infos = merge_dicts(score_infos, keyword_scores)

    scores = relabel_scores(score_infos)
    with open(scores_json, 'w', encoding='utf-8') as json_file:
        json.dump(scores, json_file, ensure_ascii=False, indent=4)

    print(f'{len(scores.keys())} in total')


def download_scores(scores_json='./data/scores.json', save_dir="./data/genshin_mids"):
    print('Downloading scores...')
    with open(scores_json, 'r', encoding='utf-8') as json_file:
        scores = json.load(json_file)

    create_dir(save_dir)
    for score_id in scores.keys():
        score_url = get_file_url(score_id)
        while not score_url:
            print(f'Failed to get the url of {score_id}, retrying...')
            rand_sleep(1, 2)
            score_url = get_file_url(score_id)

        score_label = scores[score_id]['region']
        score_title = scores[score_id]['title']
        save_path = f'{save_dir}/{score_label}_{score_id}_{score_title}.mid'
        dld_success = download(score_url, save_path)
        while not dld_success:
            print(f'Failed to download {score_id}, retrying...')
            rand_sleep(3, 5)
            dld_success = download(score_url, save_path)


if __name__ == "__main__":
    save_scores()
    download_scores()
