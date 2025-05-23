import requests

url = 'http://127.0.0.1:5000/tv/0'

token = 'AB_4g1dhJvysdrfR9HPax49hjYh2nv5UhjqbMz5a2RMG1'

header = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

data = {
    "marca": "PICA",
    "modelo": "awdsregsgr",
    "tela": "QLED",
    "preco": "3603.09"
}

response = requests.post(url=url, headers=header, json=data)

if __name__ == '__main__':
    if response.status_code >= 200 or response.status_code <= 299:
        print(response.status_code)
        print(response.reason)
        print(response.json())
    else:
        print(response.status_code)
        print(response.reason)
        print(response.json())