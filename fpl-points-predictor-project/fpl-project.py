def game_week_info():
    import requests
    import json
    fpl_data = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    print(fpl_data.status_code)
    fpl_data.text
    fpl_data = fpl_data.json()
    fpl_data = fpl_data["events"]
    user_game_week = int(input("Enter desired game week: "))
    game_week_num = user_game_week - 1
    game_week = fpl_data[game_week_num]
    print(game_week)




if __name__ == '__main__':
    game_week_info()
