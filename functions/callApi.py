import requests

def call_api(url, method='GET', payload=None, headers=None):
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=payload, headers=headers)
        else:
            raise ValueError("Only 'GET' and 'POST' methods are supported.")

        response.raise_for_status()  # Raise exception for 4xx/5xx errors
        return response.json()
    except requests.RequestException as e:
        
        return None
