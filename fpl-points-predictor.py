def request_data():
    import requests
    import json
    fpl_api = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    print(fpl_api.status_code)
    fpl_api.text
    fpl_data = fpl_api.json()
    fpl_data = fpl_data["elements"]
    print(fpl_data)


if __name__ == '__main__':
    request_data()
