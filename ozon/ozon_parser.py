# MARK: - Constants

BEST_PRICE_STR = 'Есть дешевле, '
CURRENT_PRICE_STR = '\"finalPrice\"'
TARGET_TAG_ATTRS = 'span,_i_J'

# MARK: - Main classes

class OzonParser:

    # MARK: - Public static methods

    @classmethod
    def find_current_price(cls, soup):
        print('\t[INFO] Searching for current price...')

        try:
            current_price = cls._find_current_price(soup).split('\xa0')[0]
            float(current_price)
        except ValueError:
            print('\t[ERROR] Cannot parse current price\n')
            return None

        print('\t[SUCCESS] Done!\n')
        return f'{current_price}'

    @classmethod
    def find_best_price(cls,
                        soup,
                        target_tag_attrs=TARGET_TAG_ATTRS,
                        target_str=BEST_PRICE_STR):
        print('\t[INFO] Searching for best price...')

        target_tag_name, target_tag_class = target_tag_attrs.split(',')
        target_tags = soup.find_all(target_tag_name, class_=target_tag_class)

        for target_tag in target_tags:
            if len(target_tag.contents):
                tag_text = target_tag.contents[0]
            else:
                tag_text = ''
            if target_str in tag_text:
                _, best_price = tag_text.split(', ')

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
