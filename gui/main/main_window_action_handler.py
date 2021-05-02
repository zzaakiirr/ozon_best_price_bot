import ozon.ozon_parser as ozon_parser
import google_sheets.ozon_sheet_redactor as ozon_sheet_redactor

import gui.main.main_window_action_handler_helpers as helpers
from gui.update_prices.update_prices_window_presenter import UpdatePricesWindowPresenter


# MARK: - Main classes

class MainWindowActionHandler:

    # MARK: - Init

    def __init__(self, window, sheet_redactor = ozon_sheet_redactor.OzonSheetRedactor()):
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

    def update_button_tapped(self):
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
        parser = ozon_parser.OzonParser()
        prices = []

        print(product_url)

        soup = helpers.parse_html_as_soup(product_url)
        if not soup:
            prices.append(['', ''])
            return

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
