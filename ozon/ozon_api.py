import os
import json
import requests


# MARK: - Constants

CLIENT_ID_TEST = os.environ.get('CLIENT_ID')
API_KEY_TEST = os.environ.get('API_KEY')
BASE_URI_TEST = 'https://cb-api.ozonru.me'


# MARK: - Main classes

class OzonAPI:

    # MARK: - Init

    def __init__(self, base_uri=BASE_URI_TEST, client_id=CLIENT_ID_TEST, api_key=API_KEY_TEST):
        self.base_uri = base_uri
        self.client_id = client_id
        self.api_key = api_key
        self.headers = {
            'Client-Id': self.client_id,
            'Api-Key': self.api_key
        }

    # MARK: - Public methods

    # Swagger: https://api-seller.ozon.ru/docs/#/ProductAPI/ProductAPI_ImportProductsPrices
    def update_prices(self, prices):
        print('[INFO] Updating prices...')

        url = f'{self.base_uri}/v1/product/import/prices'
        payload = { 'prices': prices }
    
        try:
            response = requests.post(url, data=json.dumps(payload), headers=self.headers)
        # TODO: Catch more specific exceptions
        except Exception as e:
            print(f'[ERROR] Cannot update prices. Unexpected exception: {e}')
            return

        if response.status_code == 200:
            response_data = response.json()
            results = response_data['result']

            for result in results:
                if result.get('updated'):
                    product_id = result['product_id']
                    print(f'\t[SUCCESS] Successfully updated price for product with id: {product_id}')
                else:
                    errors = result.get('errors', '?')
                    print(f'\t[ERROR] Failed to update prices wia API request with errors: {errors}')
