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
        prices = []

        print(product_url)

        soup = parse_html_as_soup(product_url)
        i = 0
        while 'name="robots"' in str(soup) or (soup is None and i <= 10):
            print('[WARNING] Bot was spotted. Trying again...')
            time.sleep(0.5)
            soup = parse_html_as_soup(product_url)
            i += 1

        if soup is None:
            current_price, best_price = None, None
        else:
            current_price = OzonParser.find_current_price(soup)
            best_price = OzonParser.find_best_price(soup)

        if current_price and best_price and current_price > best_price:
            new_price = int(best_price) - 1
        else:
            new_price = None

        print(f'\t[INFO] Current price: {current_price}, ' \
              f'Best price: {best_price}\n')

        prices.append([current_price, best_price, new_price])

        return prices
