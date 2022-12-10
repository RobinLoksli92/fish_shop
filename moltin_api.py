import requests
from datetime import datetime, timedelta


class MoltinApi:

    def __init__(self, moltin_client_id):
        self.token = None


    def get_products(self, moltin_token):
        url = 'https://api.moltin.com/v2/products'
        headers = {
            "Authorization": f'Bearer {moltin_token}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        products = response.json()
        return products['data']


    def get_product(self, moltin_token, product_id):
        url = f'https://api.moltin.com/v2/products/{product_id}'
        headers = {
            "Authorization": f'Bearer {moltin_token}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        products = response.json()
        return products['data']


    def add_product(self, moltin_token, cart_id, product_id, quantity):
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


    def get_cart(self, moltin_token, cart_id):
        headers = {
            'Authorization': f'Bearer {moltin_token}',
        }
        response = requests.get(
            f'https://api.moltin.com/v2/carts/{cart_id}',
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


    def get_cart_items(self, moltin_token, cart_id):
        headers = {
            'Authorization': f'Bearer {moltin_token}',
        }
        response = requests.get(
            f'https://api.moltin.com/v2/carts/{cart_id}/items/',
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


    def get_main_image(self, image_id, moltin_token):

        headers = {
            'Authorization': f'Bearer {moltin_token}',
        }

        response = requests.get(
            url=f'https://api.moltin.com/v2/files/{image_id}',
            headers=headers
        )
        response.raise_for_status()

        return response.json()['data']['link']['href']


    def delete_cart_items(self, moltin_token, cart_id, product_id):
        headers = {
            'Authorization': f'Bearer {moltin_token}',
        }

        response = requests.delete(
            url=f'https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}',
            headers=headers
        )
        response.raise_for_status()


    def create_customer(self, moltin_token, name, email):
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


    def get_customer(self, moltin_token, id):
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


    def get_moltin_token(self, moltin_client_id):
        data = {
            'client_id': moltin_client_id,
            'grant_type': 'implicit',
        }

        response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
        response.raise_for_status()
        token = response.json()
        expires_in = token['expires_in']
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        token['expires_at'] = expires_at
        return token


    def check_moltin_token(self, moltin_client_id):
        if not self.token or datetime.now() > self.token['expires_at']:
            self.token = self.get_moltin_token(moltin_client_id)
            return self.token
        return self.token
