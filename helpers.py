import requests
from bs4 import BeautifulSoup


# Need to set 'User-Agent' header for pretending not to be a robot while accessing URL
# More info: https://stackoverflow.com/a/36971955
HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)' \
                'AppleWebKit/537.36 (KHTML, like Gecko)' \
                'Chrome/39.0.2171.95 Safari/537.36'
}


def parse_html_as_soup(product_url, headers=HEADERS):
  response = requests.get(product_url, headers=headers)
  status_code = response.status_code

  if status_code != 200:
    print(f'Error while parsing product url: {product_url}, status_code: {status_code}')

  return BeautifulSoup(response.text, 'lxml')
