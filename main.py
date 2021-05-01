import ozon_parser
import google_sheets
import helpers


"""
Returns 2d array containing current price & best price for each URL
    Example: [
        [1, 2],
        [3, 4]
    ]
    means that 1st product has current price = 1 and best price = 2
               2nd product has current price = 3 and best price = 4
"""
def get_product_prices(product_url):
    parser = ozon_parser.OzonParser()
    prices = []

    print(product_url)

    soup = helpers.parse_html_as_soup(product_url)
    if not soup:
        prices.append(['', ''])
        return

    current_price = parser.find_current_price(soup)
    best_price = parser.find_best_price(soup)

    print(f'\t[INFO] Current price: {current_price}, Best price: {best_price}\n')

    prices.append([current_price, best_price])

    return prices


def submit():
    sheet_redactor = google_sheets.OzonSheetRedactor()

    sheet_redactor.set_initial_formatting({
        'backgroundColor': {
            'red': 1,
            'green': 1,
            'blue': 1,
        }
    })

    product_urls = sheet_redactor.get_product_urls()

    for product_url in product_urls:
        product_prices = get_product_prices(product_url)
        sheet_redactor.update_product_prices(product_prices, update_formatting=True)

    print('\n[INFO] Completed!')


if __name__ == '__main__':
    submit()

    # Add pause after program execution
    input()
