import time

from ozon.ozon_parser import OzonParser
from google_sheets.ozon_sheet_redactor import OzonSheetRedactor

from gui.main.main_window_action_handler_helpers import parse_html_as_soup
from gui.update_prices.update_prices_window_presenter import (
    UpdatePricesWindowPresenter
)


# MARK: - Main classes

class MainWindowActionHandler:

    # MARK: - Init

    def __init__(self, window):
        self.window = window
        self.sheet_redactor = OzonSheetRedactor()

    # MARK: - Public methods

    def start_button_tapped(self, start_row_number=1):
        self.__update_start_index(start_row_number)
 
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
            self.sheet_redactor.update_product_prices(
                product_prices,
                current_row_index,
                update_formatting=True
            )
            current_row_index += 1

        print('\n[INFO] Completed!\n')

    def get_new_prices_button_tapped(self):
        print('[INFO] Fetching new prices. Please wait...')

        new_prices_info = self.sheet_redactor.get_products_for_price_updating()
        update_prices_window_presenter = UpdatePricesWindowPresenter(
            self.window,
            new_prices_info
        )
        update_prices_window_presenter.start()

    # MARK: - Private methods

    def __update_start_index(self, start_row_number, default_number=1):
        try:
            start_row_number = int(start_row_number)
        except ValueError:
            start_row_number = default_number

        self.sheet_redactor.start_index = start_row_number

    """
    Returns 2d array containing current price & best price for each URL
        Example: [
            [1, 2],
            [3, 4]
        ]
        means that 1st product has current price = 1 and best price = 2
                   2nd product has current price = 3 and best price = 4
    """
    def __get_product_prices(self, product_url, max_attempt_count=10):
        print(product_url)

        prices = []
        attempt = 0
        current_price, best_price, new_price = None, None, None
        # TODO: Implement helper method which runs something N times
        while current_price is None and attempt < max_attempt_count:
            soup = self.__parse_html_as_soup(product_url)
            if soup is None:
                continue

            current_price = OzonParser.find_current_price(soup)
            best_price = OzonParser.find_best_price(soup)
            attempt += 1

        if current_price and best_price and current_price > best_price:
            new_price = int(best_price) - 1

        print(f'\t[INFO] Current price: {current_price}, ' \
              f'Best price: {best_price}\n')

        prices.append([current_price, best_price, new_price])

        return prices

    def __parse_html_as_soup(self, product_url, max_attempt_count=10):
        soup = None
        attempt = 0
        while 'name="robots"' in str(soup) or (soup is None and
                                               attempt < max_attempt_count):
            print('[WARNING] Bot was spotted. Trying again...')
            time.sleep(0.5)
            soup = parse_html_as_soup(product_url)
            attempt += 1
        return soup
