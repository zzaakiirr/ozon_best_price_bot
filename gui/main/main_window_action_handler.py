import time
import configparser

from ozon.ozon_parser import OzonParser
from google_sheets.ozon_sheet_redactor import OzonSheetRedactor

from gui.main.main_window_action_handler_helpers import parse_html_as_soup
from gui.update_prices.update_prices_window_presenter import (
    UpdatePricesWindowPresenter
)


SETTINGS_FILE_PATH = 'settings.ini'


# MARK: - Main classes

class MainWindowActionHandler:

    # MARK: - Init

    def __init__(self, window, settings_file_path=SETTINGS_FILE_PATH):
        self.window = window

        self.settings = configparser.ConfigParser()
        self.settings.read(settings_file_path)
        sheet_start_index = self.settings.getint(
            'ozon_sheet_redactor',
            'start_index',
        )

        self.sheet_redactor = OzonSheetRedactor(
            start_index=sheet_start_index
        )
        self.current_row_index = self.sheet_redactor.start_index - 1

    # MARK: - Public methods

    def start_button_tapped(self, start_row_number=1, infinite_mode=False):
        self.__update_start_index(start_row_number)
 
        self.sheet_redactor.set_initial_formatting({
            'backgroundColor': {
                'red': 1,
                'green': 1,
                'blue': 1,
            }
        })

        product_urls = self.sheet_redactor.get_product_urls()
        self.current_row_index = self.sheet_redactor.start_index

        for product_url in product_urls:
            product_prices = self.__get_product_prices(
                product_url,
                infinite_mode
            )
            self.sheet_redactor.update_product_prices(
                product_prices,
                self.current_row_index,
                update_formatting=True
            )
            self.current_row_index += 1

        print('\n[INFO] Completed!\n')

    def get_new_prices_button_tapped(self):
        print('[INFO] Fetching new prices. Please wait...')

        new_prices_info = self.sheet_redactor.get_products_for_price_updating()
        update_prices_window_presenter = UpdatePricesWindowPresenter(
            self.window,
            new_prices_info
        )
        update_prices_window_presenter.start()

    def on_exit(self):
        self.__update_settings()
        self.window.destroy()

    # MARK: - Private methods

    def __update_start_index(self, start_row_number, default_number=1):
        try:
            start_row_number = int(start_row_number)
        except ValueError:
            start_row_number = default_number

        self.sheet_redactor.start_index = start_row_number

    def __update_settings(self):
        self.settings.set(
            'ozon_sheet_redactor',
            'start_index',
            str(self.current_row_index)
        )
        with open(SETTINGS_FILE_PATH, 'w') as settings_file:
            self.settings.write(settings_file)

    def __get_product_prices(self,
                             product_url,
                             infinite_mode=False,
                             max_attempt_count=10):
        """
        Returns 2d array containing current price & best price for each URL
            Example: [
                [1, 2],
                [3, 4]
            ]
            means that 1st product has current price = 1 and best price = 2
                       2nd product has current price = 3 and best price = 4
        """
        print(product_url)

        if 'http' not in product_url:
            print(f'\n[ERROR] No schema supplied. URL: {product_url}')
            return None

        attempt = 0
        current_price, best_price, new_price = None, None, None
        # TODO: Implement helper method which runs something N times
        while current_price is None and (
              attempt < max_attempt_count or infinite_mode):
            soup = self.__parse_html_as_soup(product_url)
            if soup is None:
                continue

            html_text = str(soup).lower()
            if 'не существует' in html_text:
                return None

            current_price = OzonParser.find_current_price(soup)
            best_price = OzonParser.find_best_price(soup)
            attempt += 1

        if current_price and best_price and current_price > best_price:
            new_price = int(best_price) - 1

        print(f'\t[INFO] Current price: {current_price}, ' \
              f'Best price: {best_price}\n')

        return [[current_price, best_price, new_price]]

    def __parse_html_as_soup(self, product_url, max_attempt_count=10):
        soup = parse_html_as_soup(product_url)
        attempt = 0
        while ('name="robots"' in str(soup).lower() or soup is None) and (
               attempt < max_attempt_count):
            print('[WARNING] Bot was spotted. Trying again after 30 seconds')
            time.sleep(10)
            soup = parse_html_as_soup(product_url)
            attempt += 1
        return soup
