BEST_PRICE_STR = 'Есть дешевле, '


class OzonParser:

  # MARK: - Public static methods

  @staticmethod
  def find_current_price(soup):
    print('\t[INFO] Searching for current price...')

    target_tags = soup.select('.c2h5 span:first-child')

    if len(target_tags):
      print('\t[SUCCESS] Done!\n')
      return target_tags[0].contents[0] 

    print('\t[ERROR] Cannot parse current price\n')
    return None

  @staticmethod
  def find_best_price(soup, target_str=BEST_PRICE_STR):
    print('\t[INFO] Searching for best price...')

    target_divs = soup.find_all('div', class_='kxa6')

    for target_div in target_divs:
      div_text = target_div.contents[0] if len(target_div.contents) else ''
      if target_str in div_text:
        _, best_price = div_text.split(', ')

        print('\t[SUCCESS] Done!\n')
        return best_price

    print('\t[WARNING] Cannot parse best price\n')
    return None
