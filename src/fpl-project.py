def game_week_info():
    import requests
    fpl_data = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    # Requesting data using API.
    print(fpl_data.status_code)
    # To check if healthy connection with API has been made, should return a code value of 200.
    fpl_data = fpl_data.json()
    # Decoding data into json - is user friendly and machine friendly, in terms of being able to read.
    fpl_data = fpl_data["events"]
    user_game_week = int(input("Enter desired game week: "))
    game_week_num = user_game_week - 1
    # Indexing starts from 0 thus I havse to minus 1 from input.
    game_week = fpl_data[game_week_num]
    print(game_week)


def player_form():
    import requests
    player_data = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    print(player_data.status_code)
    # To check if healthy connection with API has been made, should return a code value of 200.
    player_data = player_data.json()
    player_data = player_data["elements"]
    print(player_data)
    #31
    player_name = str(input("Enter surname of player you wish to know about"))
    specific_player_info = player_data[0]
    print(specific_player_info)


if __name__ == '__main__':
    # game_week_info()
    player_form()
