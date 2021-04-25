import gspread


SERVICE_ACCOUNT_FILENAME = 'service_account.json'
WORKBOOK_NAME = 'Ozon best price bot'

URLS_COL_NAME = 'B'
CURRENT_PRICE_COL_NAME = 'C'
BEST_PRICE_COL_NAME = 'D'

START_INDEX = 2
END_INDEX = 1000000


class OzonSheetRedactor:

    # MARK: - Init

    def __init__(self,
                 service_account_filename=SERVICE_ACCOUNT_FILENAME,
                 workbook_name=WORKBOOK_NAME,
                 urls_col=URLS_COL_NAME,
                 current_price_col=CURRENT_PRICE_COL_NAME,
                 best_price_col=BEST_PRICE_COL_NAME,
                 start_index=START_INDEX,
                 end_index=END_INDEX):

        self.urls_col = urls_col
        self.current_price_col = current_price_col
        self.best_price_col = best_price_col

        self.start_index = start_index
        self.end_index = end_index

        self.sheet = self.__get_sheet(service_account_filename, workbook_name)


    # MARK: - Public methods

    def get_product_urls(self):
        print('[INFO] Parsing URLs from sheet...')

        cell_range = f'{self.urls_col}{self.start_index}:{self.urls_col}{self.end_index}'
        url_table = self.sheet.get(cell_range)

        print('[SUCCESS] Done!\n')
        return list(map(lambda url_row: url_row[0] if len(url_row) else None, url_table))

    def update_product_prices(self, prices):
        self.sheet.update(f'{self.current_price_col}{self.start_index}', prices)

    def format_products_with_inefficient_price(self, formatting):
        FIRST_CELL_LETTER = 'A'
        LAST_CELL_LETTER = 'D'

        current_index = self.start_index
        price_cells_range = f'{self.current_price_col}{self.start_index}:' \
                            f'{self.best_price_col}{self.end_index}'

        print(f'[INFO] Formatting cells {price_cells_range}...')

        price_table = self.sheet.get(price_cells_range)

        for price_row in price_table:

            if len(price_row) < 2:
                continue

            current_price = self.__price_to_int(price_row[0])
            best_price = self.__price_to_int(price_row[1])

            if current_price > best_price:
                cell_range = f'{FIRST_CELL_LETTER}{current_index}:{LAST_CELL_LETTER}{current_index}'
                self.sheet.format(cell_range, formatting)

            current_index += 1

        print('[SUCCESS] Done!\n')

    # MARK: - Private methods

    def __get_sheet(self, service_account_filename, workbook_name):
        gc = gspread.service_account(filename=service_account_filename)
        sh = gc.open(workbook_name)
        return sh.sheet1

    def __price_to_int(self, price):
        return float(price.split('\xa0')[0])
