from ozon.ozon_api import OzonAPI


# MARK: - Main classes

class UpdatePricesWindowActionHandler:

    # MARK: - Init

    def __init__(self, new_prices):
        self.new_prices = new_prices
        self.api = OzonAPI()

    # MARK: - Public methods

    def update_button_tapped(self):
        self.api.update_prices(self.new_prices)
