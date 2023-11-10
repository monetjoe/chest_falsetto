import re
import requests
from bs4 import BeautifulSoup

page_url = "https://ambr.top/chs/archive/monster/?mode=BOSS"
response = requests.get(page_url)
if response.status_code == 200:
    url_pattern = r'chs/archive/monster/\d+/'
    urls = re.findall(url_pattern, response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    urls = soup.find_all('img')
    print(urls)
