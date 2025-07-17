import requests


def login_to_wialon():
    TOKEN = "e2075897d80054d9eb5e7f9a1f50e0fe3D47139A929B4A9D6919002DF3BB0DA8992C7C89"
    login_url = f"https://hst-api.wialon.com/wialon/ajax.html?svc=token/login&params={{\"token\":\"{TOKEN}\"}}"
    response = requests.get(login_url)
    data = response.json()
    print(data)
    return data.get("eid")  # this is your S