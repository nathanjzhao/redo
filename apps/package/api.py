import requests

class APIClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def _send_request(self, endpoint, method='GET', data=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {'x-api-key': self.api_key}

        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed with status code: {response.status_code}")

    def get_data(self):
        return self._send_request('data')

    def create_item(self, item_data):
        return self._send_request('items', method='POST', data=item_data)