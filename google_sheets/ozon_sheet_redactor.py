import os
import time
import gspread

from google_sheets.ozon_sheet_config import (
    SERVICE_ACCOUNT_FILENAME,
    WORKBOOK_NAME,

    CURRENT_PRICE_COL_NAME,
    BEST_PRICE_COL_NAME,
    NEW_PRICE_COL_NAME,

    PRODUCT_TITLE_COL_NUMBER,
    OZON_ID_COL_NUMBER,
    NEW_PRICE_COL_NUMBER,
    URLS_COL_NUMBER,

    START_INDEX,
    END_INDEX,

    FIRST_CELL_LETTER,
    LAST_CELL_LETTER,

    INEFFICIENT_PRICE_FORMATTING,
    ERROR_PRICE_FORMATTING
)


# MARK: - Main classes

class OzonSheetRedactor:

    # MARK: - Init

    def __init__(self,
                 service_account_filename=SERVICE_ACCOUNT_FILENAME,
                 workbook_name=WORKBOOK_NAME,
                 current_price_col=CURRENT_PRICE_COL_NAME,
                 best_price_col=BEST_PRICE_COL_NAME,
                 new_price_col=NEW_PRICE_COL_NAME,
                 product_title_col_number=PRODUCT_TITLE_COL_NUMBER,
                 product_id_col_number=OZON_ID_COL_NUMBER,
                 new_price_col_number=NEW_PRICE_COL_NUMBER,
                 urls_col_number=URLS_COL_NUMBER,
                 start_index=START_INDEX,
                 end_index=END_INDEX,
                 inefficient_price_formatting=INEFFICIENT_PRICE_FORMATTING,
                 error_price_formatting=ERROR_PRICE_FORMATTING):

        self.current_price_col = current_price_col
        self.best_price_col = best_price_col
        self.new_price_col = new_price_col

        self.product_title_col_number = product_title_col_number
        self.product_id_col_number = product_id_col_number
        self.new_price_col_number = new_price_col_number
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

    def get_products_for_price_updating(self):
        products = []
        # First row is header
        product_rows = self.sheet.get_all_values()[1:]

        for product_row in product_rows:
            product_title = product_row[self.product_title_col_number - 1]
            product_id = product_row[self.product_id_col_number - 1]
            new_price = product_row[self.new_price_col_number - 1]

            if not product_id or not new_price:
                continue 

            try:
                products.append({
                    'product_title': product_title,
                    'product_id': int(product_id),
                    'price': new_price,
                })
            except ValueError:
                pass

        return products
        
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
                print(f'[INFO] "Write requests" limit exceeded, will sleep 5 seconds...')
                time.sleep(5)
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
