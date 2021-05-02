import ozon.ozon_api as ozon_api


# MARK: - Main classes

class UpdatePricesWindowActionHandler:

    # MARK: - Init

    def __init__(self, new_prices):
        self.new_prices = new_prices

    # MARK: - Public methods

    def update_button_tapped(self):
        api = ozon_api.OzonAPI()
        api.update_prices(self.new_prices)
