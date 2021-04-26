BEST_PRICE_STR = 'Есть дешевле, '
CURRENT_PRICE_STR = '\"finalPrice\"'

class OzonParser:

    # MARK: - Public static methods

    @staticmethod
    def find_current_price(soup):
        print('\t[INFO] Searching for current price...')

        html_text = str(soup)

        current_price_index = html_text.index(CURRENT_PRICE_STR)
        start_index = current_price_index + len(CURRENT_PRICE_STR) + 1
        end_index = html_text.index(',', current_price_index)
        current_price = html_text[start_index:end_index]

        try:
            float(current_price)
        except ValueError:
            print('\t[ERROR] Cannot parse current price\n')
            return ''

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
        return ''
