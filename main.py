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
def get_product_prices(product_urls):
    parser = ozon_parser.OzonParser()
    prices = []

    for product_url in product_urls:

      # if not product_url:
      #   break

      print(product_url)

      soup = helpers.parse_html_as_soup(product_url)
      current_price = parser.find_current_price(soup)
      best_price = parser.find_best_price(soup)

      print(f'\t[INFO] Current price: {current_price}, Best price: {best_price}\n')

      prices.append([current_price, best_price])

    return prices


def main():
    sheet_redactor = google_sheets.OzonSheetRedactor()
    product_urls = sheet_redactor.get_product_urls()

    product_prices = get_product_prices(product_urls)

    sheet_redactor.update_product_prices(product_prices)

    sheet_redactor.format_products_with_inefficient_price({
        'backgroundColor': {
            'red': 30.0,
        }
    })


if __name__ == '__main__':
    main()

    # Add pause after program execution
    input()
