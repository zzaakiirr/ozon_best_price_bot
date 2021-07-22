BEST_PRICE_STR = 'Есть дешевле, '
CURRENT_PRICE_STR = '\"finalPrice\"'


class OzonParser:

    # MARK: - Public static methods

    @classmethod
    def find_current_price(cls, soup):
        print('\t[INFO] Searching for current price...')

        try:
            current_price = cls._find_current_price(soup)
            float(current_price)
        except ValueError:
            print('\t[ERROR] Cannot parse current price\n')
            return None

        print('\t[SUCCESS] Done!\n')
        return f'{current_price}'

    @classmethod
    def find_best_price(cls, soup, target_str=BEST_PRICE_STR):
        print('\t[INFO] Searching for best price...')

        target_divs = soup.find_all('div', class_='kxa6')

        for target_div in target_divs:
            if len(target_div.contents):
                div_text = target_div.contents[0]
            else:
                div_text = ''
            if target_str in div_text:
                _, best_price = div_text.split(', ')

                print('\t[SUCCESS] Done!\n')
                return best_price[:-1]

        print('\t[WARNING] Cannot parse best price\n')
        return None

    # MARK: - Private static methods

    @classmethod
    def _find_current_price(cls, soup):
        current_price = cls._find_current_price_by_xpath(soup)
        if current_price:
            return current_price

        html_text = str(soup)
        return cls._find_current_price_by_keyword(html_text)

    @classmethod
    def _find_current_price_by_keyword(cls, html_text):
        current_price_index = html_text.index(CURRENT_PRICE_STR)
        start_index = current_price_index + len(CURRENT_PRICE_STR) + 1
        end_index = html_text.index(',', current_price_index)
        return html_text[start_index:end_index]

    @classmethod
    def _find_current_price_by_xpath(cls, soup):
        target_tags = soup.select('.c2h5 span:first-child')
        if len(target_tags) != 1 or len(target_tags[0].contents) == 0:
            return None
        return target_tags[0].contents[0]
