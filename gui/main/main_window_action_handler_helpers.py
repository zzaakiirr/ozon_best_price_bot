import random
from itertools import cycle

import requests
from bs4 import BeautifulSoup


# Need to set 'User-Agent' header for pretending not to be a robot while accessing URL
# More info: https://stackoverflow.com/a/36971955
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)' \
        'AppleWebKit/537.36 (KHTML, like Gecko)' \
        'Chrome/39.0.2171.95 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X)' \
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1' \
        'Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)' \
        'AppleWebKit/605.1.15 (KHTML, like Gecko)' \
        'Version/12.1.1 Safari/605.1.15',
]
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us',
    'DNT': '1',
}


def parse_html_as_soup(product_url, headers=HEADERS):
    try:
        headers['User-Agent'] = random.choice(USER_AGENTS)
        headers['Referer'] = f'https://www.google.com/url?q={product_url}' \
                              '&sa=D&source=editors' \
                              '&ust=1623878008220000' \
                              '&usg=AOvVaw1yjR2IzLGGF7f92nlr8Wj3'

        response = requests.get(product_url, headers=headers)
        status_code = response.status_code
        if status_code != 200:
            raise
    except:
        print(f'[ERROR] Cannot parse product url: {product_url}')
        return None

    return BeautifulSoup(response.text, 'lxml')
