### ---- google_sheets/ozon_sheet_config ----

SERVICE_ACCOUNT_FILENAME = 'service_account.json'
WORKBOOK_NAME = 'Ozon best price bot v2'

PRODUCT_TITLE_COL_NAME = 'A'
OZON_ID_COL_NAME = 'B'
URLS_COL_NAME = 'C'
CURRENT_PRICE_COL_NAME = 'D'
BEST_PRICE_COL_NAME = 'E'
NEW_PRICE_COL_NAME = 'F'

URLS_COL_NUMBER = 3
START_INDEX = 2
END_INDEX = 1000000

FIRST_CELL_LETTER = 'A'
LAST_CELL_LETTER = 'F'

INEFFICIENT_PRICE_FORMATTING = {
    'backgroundColor': {
        'red': 1,
        'green': 1,
        'blue': 0,
    }
}

ERROR_PRICE_FORMATTING = {
    'backgroundColor': {
        'red': 1,
        'green': 0,
        'blue': 0.3,
    }
}

SIDEBAR_BG_COLOR = '#323232'

TEXT_BOX_BG_COLOR = '#1E1E1E'
TEXT_BOX_FG_COLOR = '#FFFFFF'
BUTTON_BG_COLOR = '#909090'

LIST_BOX = {
    'width': 100,
    'height': 30,
    'font': ('Times', 18, 'bold')
}

BUTTON_SIZE = {
    'width': 15,
    'height': 3
}

VERTICAL_SPACE_BETWEEN_BUTTONS = 5


### ---- google_sheets/ozon_sheet_redactor ----

import os
import time
import gspread


# MARK: - Main classes

class OzonSheetRedactor:

    # MARK: - Init

    def __init__(self,
                 service_account_filename=SERVICE_ACCOUNT_FILENAME,
                 workbook_name=WORKBOOK_NAME,
                 product_title_col=PRODUCT_TITLE_COL_NAME,
                 product_id_col=OZON_ID_COL_NAME,
                 urls_col=URLS_COL_NAME,
                 current_price_col=CURRENT_PRICE_COL_NAME,
                 best_price_col=BEST_PRICE_COL_NAME,
                 new_price_col=NEW_PRICE_COL_NAME,
                 urls_col_number=URLS_COL_NUMBER,
                 start_index=START_INDEX,
                 end_index=END_INDEX,
                 inefficient_price_formatting=INEFFICIENT_PRICE_FORMATTING,
                 error_price_formatting=ERROR_PRICE_FORMATTING):

        self.product_title_col = product_title_col
        self.product_id_col = product_id_col
        self.urls_col = urls_col
        self.current_price_col = current_price_col
        self.best_price_col = best_price_col
        self.new_price_col = new_price_col

        self.urls_col_number = urls_col_number
        self.start_index = start_index
        self.end_index = end_index

        self.inefficient_price_formatting = inefficient_price_formatting
        self.error_price_formatting = error_price_formatting

        self.sheet = self.__get_sheet(service_account_filename, workbook_name)


    # MARK: - Public methods

    def get_product_urls(self):
        print('[INFO] Parsing URLs from sheet...')
        # First value is title of column
        urls = self.sheet.col_values(self.urls_col_number)[1:]
        print('[SUCCESS] Done!\n')
        return urls

    def get_new_prices(self, row_index):
        product_title_cell = f'{self.product_title_col}{row_index}'
        product_title = self.sheet.acell(product_title_cell).value
        print(f'[INFO] Getting price for product: {product_title}')

        product_id_cell = f'{self.product_id_col}{row_index}'
        product_id = self.sheet.acell(product_id_cell).value

        price_cell = f'{self.new_price_col}{row_index}'
        price = self.sheet.acell(price_cell).value

        print(f'\t[INFO] product_id: {product_id}, price: {price}\n')

        return product_title, product_id, price
        
    def update_product_prices(self, prices, row_index, update_formatting=True):
        try:
            price_cell_range = f'{self.current_price_col}{row_index}:' \
                               f'{self.new_price_col}{row_index + 1}'
            self.sheet.update(price_cell_range, prices)

            if update_formatting:
                current_row_cell_range = f'{FIRST_CELL_LETTER}{row_index}:'\
                                         f'{LAST_CELL_LETTER}{row_index}'
                self.update_formatting(current_row_cell_range, prices)
        except gspread.exceptions.APIError as e:
            response = e.response.json()
            error = response.get('error')
            code = error.get('code')
            if code == 429:
                print(f'[INFO] "Write requests" limit exceeded, will wait 3 seconds...')
                time.sleep(3)
                print(f'[INFO] Trying again...')
                self.update_product_prices(prices, row_index, update_formatting)
            else:
                print(f'[ERROR] Unexpected error: {e}')
        except Exception as e:
            print(f'[ERROR] Unexpected error: {e}')

    def set_initial_formatting(self, formatting):
        cell_range = f'{FIRST_CELL_LETTER}{self.start_index}:{LAST_CELL_LETTER}{self.end_index}'
        print(f'[INFO] Setting initial formatting {cell_range}...')

        self.sheet.format(cell_range, formatting)
        print('[SUCCESS] Done!\n')

    def update_formatting(self, cell_range, prices):
        print(f'[INFO] Formatting cells {cell_range}...')

        if not prices:
            self.sheet.format(cell_range, self.error_price_formatting)
            return

        prices = prices[0]
        current_price = int(prices[0]) if prices[0] else None
        best_price = int(prices[1]) if prices[1] else None

        if not current_price or not best_price:
            return

        if current_price > best_price:
            self.sheet.format(cell_range, self.inefficient_price_formatting)

        print('[SUCCESS] Done!\n')

    # MARK: - Private methods

    def __get_sheet(self, service_account_filename, workbook_name):
        try:
            gc = gspread.service_account(filename=service_account_filename)
            sh = gc.open(workbook_name)
        except FileNotFoundError:
            print(f"[ERROR] No such file '{service_account_filename}'")
            print(f"[INFO] Добавьте файл '{service_account_filename}' в папку, где лежит программа")
        else:
            return sh.sheet1

    def __price_to_int(self, price):
        try:
            result = float(price.split('\xa0')[0])
        except ValueError:
            return None
        return result


### ---- gui/main/main_window_action_handler ----


# MARK: - Main classes

class MainWindowActionHandler:

    # MARK: - Init

    def __init__(self, window, sheet_redactor = OzonSheetRedactor()):
        self.window = window
        self.sheet_redactor = sheet_redactor

    # MARK: - Public methods

    def start_button_tapped(self):
        self.sheet_redactor.set_initial_formatting({
            'backgroundColor': {
                'red': 1,
                'green': 1,
                'blue': 1,
            }
        })

        product_urls = self.sheet_redactor.get_product_urls()
        current_row_index = self.sheet_redactor.start_index

        for product_url in product_urls:
            product_prices = self.__get_product_prices(product_url)
            self.sheet_redactor.update_product_prices(product_prices, current_row_index, update_formatting=True)
            current_row_index += 1

        print('\n[INFO] Completed!\n')

    def get_new_prices_button_tapped(self):
        print('[INFO] Loading new prices. Please wait...')

        new_prices_info, new_prices_api_body = self.__get_new_product_prices()
        update_prices_window_presenter = UpdatePricesWindowPresenter(self.window,
                                                                     new_prices_info,
                                                                     new_prices_api_body)
        update_prices_window_presenter.start()

    # MARK: - Private methods

    """
    Returns 2d array containing current price & best price for each URL
        Example: [
            [1, 2],
            [3, 4]
        ]
        means that 1st product has current price = 1 and best price = 2
                   2nd product has current price = 3 and best price = 4
    """
    def __get_product_prices(self, product_url):
        parser = OzonParser()
        prices = []

        print(product_url)

        soup = parse_html_as_soup(product_url)
        i = 0
        while 'name="robots"' in str(soup) or (soup is None and i <= 10):
            print('[WARNING] Bot was spotted. Waiting 0.5 seconds...')
            time.sleep(0.5)
            soup = parse_html_as_soup(product_url)
            i += 1

        current_price = parser.find_current_price(soup)
        best_price = parser.find_best_price(soup)

        if current_price and best_price and current_price > best_price:
            new_price = int(best_price) - 1
        else:
            new_price = None

        print(f'\t[INFO] Current price: {current_price}, Best price: {best_price}\n')

        prices.append([current_price, best_price, new_price])

        return prices

    def __get_new_product_prices(self):
        new_prices_api_body = []
        new_prices_info = []

        for row_index in range(self.sheet_redactor.start_index, self.sheet_redactor.end_index):
            product_title, product_id, new_price = self.sheet_redactor.get_new_prices(row_index)

            if not product_id or not new_price:
                break

            # TODO: Create class Product instead of this workaround
            new_price_api_body = {
                'product_id': int(product_id),
                'price': new_price
            }
            new_prices_api_body.append(new_price_api_body)

            new_price_info = {
                'product_title': product_title,
                'price': int(new_price)
            }
            new_prices_info.append(new_price_info)

        return new_prices_info, new_prices_api_body


### ---- gui/main/main_window_action_handler_helpers ----

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

        response = requests.get(product_url, headers=headers, timeout=2)
        status_code = response.status_code
        if status_code != 200:
            raise
    except:
        print(f'[ERROR] Cannot parse product url: {product_url}')
        return None

    return BeautifulSoup(response.text, 'lxml')


### --- gui/main/main_window_presenter

import sys
import threading
import tkinter as tk

# MARK: - Main classes

class MainWindowPresenter:

    # MARK: - Init

    def __init__(self,
                 window_title='OzonBot',
                 start_button_text='Start',
                 get_new_prices_button_text='Get new prices',
                 exit_button_text='Exit'): 

        self.window_title = window_title
        self.start_button_text = start_button_text
        self.get_new_prices_button_text = get_new_prices_button_text
        self.exit_button_text = exit_button_text


    # MARK: - Public methods

    def start(self):
        self.__init_ui_elements()
        self.__configure_window(self.window_title)
        self.__pack_widgets()
        self.window.mainloop()

    # MARK: - Private methods

    def __init_ui_elements(self):
        self.window = tk.Tk()

        action_handler = MainWindowActionHandler(self.window)
      
        self.sidebar_frame = tk.Frame(self.window, bg=SIDEBAR_BG_COLOR)

        self.text_box = tk.Text(master=self.window,
                                state='disabled',
                                bg=TEXT_BOX_BG_COLOR,
                                fg=TEXT_BOX_FG_COLOR)

        sys.stdout = StdoutRedirector(self.text_box)

        start_button_command = lambda: self.__start_submit_thread(
            action_handler.start_button_tapped
        )
        self.start_button = tk.Button(self.sidebar_frame,
                                      text=self.start_button_text,
                                      command=start_button_command,
                                      width=BUTTON_SIZE['width'],
                                      height=BUTTON_SIZE['height'],
                                      bg=BUTTON_BG_COLOR)

        get_new_prices_button_command = lambda: self.__start_submit_thread(
            action_handler.get_new_prices_button_tapped
        )
        self.get_new_prices_button = tk.Button(self.sidebar_frame,
                                       text=self.get_new_prices_button_text,
                                       command=get_new_prices_button_command,
                                       width=BUTTON_SIZE['width'],
                                       height=BUTTON_SIZE['height'],
                                       bg=BUTTON_BG_COLOR)

        self.exit_button = tk.Button(self.sidebar_frame,
                                     text=self.exit_button_text,
                                     command=self.window.destroy,
                                     width=BUTTON_SIZE['width'],
                                     height=BUTTON_SIZE['height'],
                                     bg=BUTTON_BG_COLOR)

    def __configure_window(self, title):
        self.window.title(title)
        self.window.configure(bg=SIDEBAR_BG_COLOR)
        self.window.resizable(False, False)

    def __pack_widgets(self, sidebar_side=tk.LEFT, text_side=tk.RIGHT):
        self.sidebar_frame.pack(side=sidebar_side)
        self.text_box.pack(side=text_side)
        self.start_button.pack(pady=VERTICAL_SPACE_BETWEEN_BUTTONS)
        self.get_new_prices_button.pack()
        self.exit_button.pack(pady=VERTICAL_SPACE_BETWEEN_BUTTONS)

    # MARK: - Threading

    def __start_submit_thread(self, event):
        self.submit_thread = threading.Thread(target=event)
        self.submit_thread.daemon = True
        self.submit_thread.start()
        self.window.after(20, self.__check_submit_thread)
        self.get_new_prices_button.configure(state='disable')
        self.start_button.configure(state='disable')

    def __check_submit_thread(self):
        if self.submit_thread.is_alive():
            self.window.after(20, self.__check_submit_thread)
        else:
            self.get_new_prices_button.configure(state='normal')
            self.start_button.configure(state='normal')


# MARK: - Helpers

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.configure(state='normal')
        self.text_space.insert(tk.END, string)
        self.text_space.see(tk.END)
        self.text_space.configure(state='disable')

    def flush(self):
        pass


### ---- gui/update_prices/update_prices_action_handler

# MARK: - Main classes

class UpdatePricesWindowActionHandler:

    # MARK: - Init

    def __init__(self, new_prices):
        self.new_prices = new_prices

    # MARK: - Public methods

    def update_button_tapped(self):
        api = OzonAPI()
        api.update_prices(self.new_prices)


### ---- gui/update_prices/update_prices_window_presenter

import threading
import tkinter as tk


# MARK: - Main classes

class UpdatePricesWindowPresenter:
    def __init__(self,
                 root_window,
                 new_prices_info,
                 new_prices_api_body,
                 window_title='Update prices',
                 update_button_text='Update',
                 exit_button_text='Exit'):

        self.root_window = root_window

        self.window_title = window_title
        self.new_prices_info = new_prices_info
        self.new_prices_api_body = new_prices_api_body

        self.window_title = window_title
        self.update_button_text = update_button_text
        self.exit_button_text = exit_button_text

    # MARK: - Public methods

    def start(self):
        self.__init_ui_elements()
        self.__configure_window(self.window_title)
        self.__configure_scroll_bar()
        self.__show_ui()

    # MARK: - Private methods

    def __init_ui_elements(self):
        action_handler = UpdatePricesWindowActionHandler(self.new_prices_api_body)

        self.window = tk.Toplevel(self.root_window)
        self.sidebar_frame = tk.Frame(self.window, bg=SIDEBAR_BG_COLOR)

        update_button_command = lambda: self.__start_submit_thread(
            action_handler.update_button_tapped
        )
        self.update_button = tk.Button(self.sidebar_frame,
                                      text=self.update_button_text,
                                      command=update_button_command,
                                      width=BUTTON_SIZE['width'],
                                      height=BUTTON_SIZE['height'],
                                      bg=BUTTON_BG_COLOR)

        self.exit_button = tk.Button(self.sidebar_frame,
                                     text=self.exit_button_text,
                                     command=self.window.destroy,
                                     width=BUTTON_SIZE['width'],
                                     height=BUTTON_SIZE['height'],
                                     bg=BUTTON_BG_COLOR)

        self.scroll_bar = tk.Scrollbar(self.window)
        self.list_box = tk.Listbox(self.window,
                                   yscrollcommand=self.scroll_bar.set,
                                   width=LIST_BOX['width'],
                                   height=LIST_BOX['height'],
                                   font=LIST_BOX['font'])



    def __configure_window(self, title):
        self.window.title(title)
        self.window.configure(bg=SIDEBAR_BG_COLOR)
        self.window.resizable(False, False)

    def __configure_scroll_bar(self):
        self.scroll_bar.config(command=self.list_box.yview)

    def __show_ui(self, sidebar_side=tk.LEFT):
        self.sidebar_frame.pack(side=sidebar_side)
        self.update_button.pack(pady=VERTICAL_SPACE_BETWEEN_BUTTONS)
        self.exit_button.pack()

        self.__populate_list_box()
        self.list_box.pack(side=tk.LEFT, fill=tk.BOTH)

        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

    def __populate_list_box(self):
        for new_price_info in self.new_prices_info:
            product_title = new_price_info['product_title']
            product_price = new_price_info['price']
            self.list_box.insert(tk.END, f'{product_title} --- {product_price}')

    # MARK: - Threading

    # TODO: Fix repeating this in MainWindowPresenter
    def __start_submit_thread(self, event):
        self.submit_thread = threading.Thread(target=event)
        self.submit_thread.daemon = True
        self.submit_thread.start()
        self.window.after(20, self.__check_submit_thread)
        self.update_button.configure(state='disable')

    def __check_submit_thread(self):
        if self.submit_thread.is_alive():
            self.window.after(20, self.__check_submit_thread)
        else:
            self.update_button.configure(state='normal')


### ---- ozon/ozon_api

import json


# MARK: - Constants

CLIENT_ID = '73927'
API_KEY = '8b160fb8-8fa8-458c-856f-557e319b59ec'
BASE_URI = 'http://api-seller.ozon.ru'

# CLIENT_ID_TEST = '836'
# API_KEY_TEST = '0296d4f2-70a1-4c09-b507-904fd05567b9'
# BASE_URI_TEST = 'https://cb-api.ozonru.me'


# MARK: - Main classes

class OzonAPI:

    # MARK: - Init

    def __init__(self, base_uri=BASE_URI, client_id=CLIENT_ID, api_key=API_KEY):
        self.base_uri = base_uri
        self.client_id = client_id
        self.api_key = api_key
        self.headers = {
            'Client-Id': self.client_id,
            'Api-Key': self.api_key
        }

    # MARK: - Public methods

    # Swagger: https://api-seller.ozon.ru/docs/#/ProductAPI/ProductAPI_ImportProductsPrices
    def update_prices(self, prices):
        print('[INFO] Updating prices...')

        url = f'{self.base_uri}/v1/product/import/prices'
        payload = { 'prices': prices }
    
        try:
            response = requests.post(url, data=json.dumps(payload), headers=self.headers)
        # TODO: Catch more specific exceptions
        except Exception as e:
            print(f'[ERROR] Cannot update prices. Unexpected exception: {e}')
            return

        if response.status_code == 200:
            response_data = response.json()
            results = response_data['result']

            for result in results:
                if result.get('updated'):
                    product_id = result['product_id']
                    print(f'\t[SUCCESS] Successfully updated price for product with id: {product_id}')
                else:
                    errors = result.get('errors', '?')
                    print(f'\t[ERROR] Failed to update prices wia API request with errors: {errors}')


### --- ozon/ozon_parser

BEST_PRICE_STR = 'Есть дешевле, '
CURRENT_PRICE_STR = '\"finalPrice\"'


class OzonParser:

    # MARK: - Public static methods

    @staticmethod
    def find_current_price(soup):
        print('\t[INFO] Searching for current price...')

        html_text = str(soup)

        try:
            current_price_index = html_text.index(CURRENT_PRICE_STR)
        except ValueError:
            print('\t[ERROR] Cannot find current price index\n')
            return None

        start_index = current_price_index + len(CURRENT_PRICE_STR) + 1
        end_index = html_text.index(',', current_price_index)
        current_price = html_text[start_index:end_index]

        try:
            float(current_price)
        except ValueError:
            print('\t[ERROR] Cannot parse current price\n')
            return None

        print('\t[SUCCESS] Done!\n')
        return f'{current_price}'

    @staticmethod
    def find_best_price(soup, target_str=BEST_PRICE_STR):
        print('\t[INFO] Searching for best price...')

        target_divs = soup.find_all('div', class_='kxa6')

        for target_div in target_divs:
            div_text = target_div.contents[0] if len(target_div.contents) else ''
            if target_str in div_text:
                _, best_price = div_text.split(', ')

                print('\t[SUCCESS] Done!\n')
                return best_price[:-1]

        print('\t[WARNING] Cannot parse best price\n')
        return None


# MARK: - Main flow

if __name__ == '__main__':
    main_window_presenter = MainWindowPresenter()
    main_window_presenter.start()
