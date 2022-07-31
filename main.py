import os
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from bs4 import BeautifulSoup as bs
from pathlib import Path

PARENT_DIR = Path(__file__).parent
TOPICS_FOLDER = PARENT_DIR / "topics"
CONF_PATH = PARENT_DIR / "conf.json"

HEADERS = {
    'Request Line': 'GET / HTTP/1.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': '_ga=GA1.2.1858266193.1658776486; _gid=GA1.2.239378975.1658776486',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.134 YaBrowser/22.7.1.806 Yowser/2.5 Safari/537.36'
}


def get_settings(conf_path: str):
    with open(conf_path) as file:
        configuration = json.load(file)
    return configuration["num_pages"], \
           configuration["links"], \
           configuration['base_url']


def get_page(link: str):
    # session = requests.Session()
    # retry = Retry(connect=3, backoff_factor=0.5)
    # adapter = HTTPAdapter(max_retries=retry)
    # session.mount('http://', adapter)
    # session.mount('https://', adapter)
    # request = session.get(link, headers=HEADERS)

    session = requests.Session()
    request = session.get(link, headers=HEADERS)

    # print(request)
    # request = requests.get(link, headers=HEADERS)
    if not request.ok:
        print("Request failed")
    soup = bs(request.text, features="html.parser")
    return soup


def get_all_links(soup, base):
    topics, groups, other_pages = {}, {}, []
    all_links = soup.find_all('a')
    for link in all_links:
        _link = link.get('href')
        _text = link.text
        if 'topic' in _link:
            if _text not in topics:
                topics[_text] = _link
            else:
                'Duplicate Topic/Text'
        elif 'group' in _link:
            if _text not in groups:
                groups[_text] = _link
            else:
                'Duplicate Group/Name'
        elif '?start=' in _link:
            if base+_link not in other_pages:
                other_pages.append(base+_link)
            else:
                'Duplicate Page Link'
        else:
            'Skip Link'
    return topics, groups, other_pages


def get_topic_page(topic, link, page_id):
    if not TOPICS_FOLDER.exists():
        os.mkdir(TOPICS_FOLDER)
    with open(TOPICS_FOLDER/f'{page_id}.txt', 'w', encoding='utf-8') as file:
        request = requests.get(link, headers=HEADERS)
        article_soup = bs(request.text, features="html.parser")
        main_text = ""
        main_text += topic + '\n'
        try:
            paragraphs = article_soup.find("div", attrs={"class": "rich-content topic-richtext"}).find_all("p")
            for paragraph in paragraphs:
                main_text += paragraph.text
        except AttributeError:
            "Page does not include any content"
        file.write(main_text)


if __name__ == '__main__':
    pages_count, source_link, base_url = get_settings(CONF_PATH)

    page_soup = get_page(source_link)
    _pt_topics, _pt_groups, _pt_pages = get_all_links(page_soup, base_url)
    counter = 0
    for _pt_topic in _pt_topics:
        # print(_pt_topic, _pt_topics)
        get_topic_page(_pt_topic, _pt_topics[_pt_topic], counter)
        counter+= 1
        print('text is written')
