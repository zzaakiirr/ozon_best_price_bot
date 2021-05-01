import gspread


SERVICE_ACCOUNT_FILENAME = 'service_account.json'
WORKBOOK_NAME = 'Ozon best price bot v2'

URLS_COL_NAME = 'B'
CURRENT_PRICE_COL_NAME = 'C'
BEST_PRICE_COL_NAME = 'D'

START_INDEX = 2
END_INDEX = 1000000

FIRST_CELL_LETTER = 'A'
LAST_CELL_LETTER = 'D'

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


class OzonSheetRedactor:

    # MARK: - Init

    def __init__(self,
                 service_account_filename=SERVICE_ACCOUNT_FILENAME,
                 workbook_name=WORKBOOK_NAME,
                 urls_col=URLS_COL_NAME,
                 current_price_col=CURRENT_PRICE_COL_NAME,
                 best_price_col=BEST_PRICE_COL_NAME,
                 start_index=START_INDEX,
                 end_index=END_INDEX,
                 inefficient_price_formatting=INEFFICIENT_PRICE_FORMATTING,
                 error_price_formatting=ERROR_PRICE_FORMATTING):

        self.urls_col = urls_col
        self.current_price_col = current_price_col
        self.best_price_col = best_price_col

        self.start_index = start_index
        self.current_index = start_index
        self.end_index = end_index

        self.inefficient_price_formatting = inefficient_price_formatting
        self.error_price_formatting = error_price_formatting

        self.sheet = self.__get_sheet(service_account_filename, workbook_name)


    # MARK: - Public methods

    def get_product_urls(self):
        print('[INFO] Parsing URLs from sheet...')

        cell_range = f'{self.urls_col}{self.start_index}:{self.urls_col}{self.end_index}'
        url_table = self.sheet.get(cell_range)

        print('[SUCCESS] Done!\n')
        return list(map(lambda url_row: url_row[0] if len(url_row) else None, url_table))

    def update_product_prices(self, prices, update_formatting=True):
        try:
            price_cell_range = f'{self.current_price_col}{self.current_index}:' \
                               f'{self.best_price_col}{self.current_index + 1}'
            self.sheet.update(price_cell_range, prices)

            if update_formatting:
                current_row_cell_range = f'{FIRST_CELL_LETTER}{self.current_index}:'\
                                         f'{LAST_CELL_LETTER}{self.current_index}'
                self.update_formatting(current_row_cell_range, prices)
        except Exception as e:
            print(f'[ERROR] Unexpected error: {e}')
        self.current_index += 1

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
        return sh.sheet1

    def __price_to_int(self, price):
        try:
            result = float(price.split('\xa0')[0])
        except ValueError:
            return None
        return result
