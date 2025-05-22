import requests
from pprint import pprint

print = pprint

url = 'http://127.0.0.1:5000/dados'

token = 'AB_4g1dhJvysdrfR9HPax49hjYh2nv5UhjqbMz5a2RMG1'

header = {
    'Authorization': f'Bearer {token}',
}

response = requests.get(url=url, headers=header)

if __name__ == '__main__':
    if response.status_code >= 200 or response.status_code <= 299:
        print(response.status_code)
        print(response.reason)
        print(response.json())
    else:
        print(response.status_code)
        print(response.reason)
        print(response.json())