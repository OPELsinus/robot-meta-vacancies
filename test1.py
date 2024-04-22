import requests

data = {
    "process": 51,
    "config": 62,
    "machines": [2]
}

requests.post('https://rpa.magnum.kz:8443/enqueue', json=data, verify=False)
