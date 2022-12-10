import requests
from datetime import datetime, timedelta


class MoltinApi:

    def __init__(self, moltin_client_id):
        self.moltin_client_id = moltin_client_id
        self.token = None
        self.expires_at = None


    def get_products(self):
        moltin_token = self.get_moltin_token()
        url = 'https://api.moltin.com/v2/products'
        headers = {
            "Authorization": f'Bearer {moltin_token}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        products = response.json()
        return products['data']


    def get_product(self, product_id):
        moltin_token = self.get_moltin_token()
        url = f'https://api.moltin.com/v2/products/{product_id}'
        headers = {
            "Authorization": f'Bearer {moltin_token}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        products = response.json()
        return products['data']


    def add_product(self, cart_id, product_id, quantity):
        moltin_token = self.get_moltin_token()
        headers = {
            'Authorization': f'Bearer {moltin_token}',
            'Content-Type': 'application/json',
        }

        json_data = {
            'data': {
                'id': product_id,
                'type': 'cart_item',
                'quantity': quantity,
            },
        }

        response = requests.post(
            url=f'https://api.moltin.com/v2/carts/{cart_id}/items',
            headers=headers,
            json=json_data,
        )
        response.raise_for_status()


    def get_cart(self, cart_id):
        moltin_token = self.get_moltin_token()
        headers = {
            'Authorization': f'Bearer {moltin_token}',
        }
        response = requests.get(
            f'https://api.moltin.com/v2/carts/{cart_id}',
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


    def get_cart_items(self, cart_id):
        moltin_token = self.get_moltin_token()
        headers = {
            'Authorization': f'Bearer {moltin_token}',
        }
        response = requests.get(
            f'https://api.moltin.com/v2/carts/{cart_id}/items/',
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


    def get_main_image(self, image_id):
        moltin_token = self.get_moltin_token()
        headers = {
            'Authorization': f'Bearer {moltin_token}',
        }

        response = requests.get(
            url=f'https://api.moltin.com/v2/files/{image_id}',
            headers=headers
        )
        response.raise_for_status()

        return response.json()['data']['link']['href']


    def delete_cart_items(self, cart_id, product_id):
        moltin_token = self.get_moltin_token()
        headers = {
            'Authorization': f'Bearer {moltin_token}',
        }

        response = requests.delete(
            url=f'https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}',
            headers=headers
        )
        response.raise_for_status()


    def create_customer(self, name, email):
        moltin_token = self.get_moltin_token()
        headers = {
            'Authorization': f'Bearer {moltin_token}',
            'Content-Type': 'application/json',
        }

        json_data = {
            'data': {
                'type': 'customer',
                'name': name,
                'email': email
            },
        }

        response = requests.post(
            'https://api.moltin.com/v2/customers',
            headers=headers,
            json=json_data
        )
        response.raise_for_status()


    def get_customer(self, id):
        moltin_token = self.get_moltin_token()
        headers = {
            'Authorization': f'Bearer {moltin_token}',
        }

        response = requests.get(
            f'https://api.moltin.com/v2/customers/{id}',
            headers=headers
        )
        response.raise_for_status()
        customer = response.json()
        return customer


    def get_moltin_token(self):
        if not self.token or datetime.now() > self.expires_at:
            data = {
                'client_id': self.moltin_client_id,
                'grant_type': 'implicit',
            }

            response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
            response.raise_for_status()
            token_data = response.json()
            self.token = token_data['access_token']
            self.expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
        return self.token
