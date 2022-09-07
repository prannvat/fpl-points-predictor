from unittest import result
import requests , json
import pandas as pd
import numpy as np 
from pprint import pprint


def current_season_gameweek_info(user_choice_player):
    # Getting gameweek information for specific players
    request_URL = requests.get(main_url+'element-summary/'+str(user_choice_player)+'/').json()
    # ^^sending GET request to https://fantasy.premierleague.com/api/element-summary/{PID}/
    specific_player_df = pd.json_normalize(request_URL['history'])
    return specific_player_df

def past_seasons_info(user_choice_player):
     # Getting gameweek information for specific players
    request_URL = requests.get(main_url+'element-summary/'+str(user_choice_player)+'/').json()
    # ^^sending GET request to https://fantasy.premierleague.com/api/element-summary/{PID}/
    specific_player_df = pd.json_normalize(request_URL['history_past'])
    return specific_player_df


if __name__ == '__main__':
    # game_week_info()
    main_url = 'https://fantasy.premierleague.com/api/' # the base url for all of the FPL endpoints
    # getting data from bootstrap-static endpoint below:
    request_URL = requests.get(main_url+'bootstrap-static/').json()
    # I can now get player data usimg the 'elements field of the API:
    player_info = request_URL['elements']
    # using Pandas, I can now make the data I have be in a tabular format.
    # Pandas is a library made for exactly this purpose.
    pd.set_option('display.max_columns', None)
    # now I can create dataframe using the players info
    player_info = pd.json_normalize(request_URL['elements'])
    # creating dataframe for teams:
    teams_info = pd.json_normalize(request_URL['teams'])
    # player positions using the 'element-types' field:
    player_positions = pd.json_normalize(request_URL['element_types'])
    request_URL = requests.get(main_url+'element-summary/9/').json() 
    current_season_gameweek_info(4)[['round','total_points','minutes','goals_scored','assists']]
    # using 4 as a random place holder, same with 2 below
    (past_seasons_info(2)[['season_name','total_points','minutes','goals_scored','assists']])
    # creating a points table which will contain all the info for all
    player_info = player_info[['id','first_name','second_name', 'web_name', 'team','element_type']]
    # i will join the teamn names to the table
    player_info = player_info.merge(teams_info[['id', 'name']], left_on='team', right_on='id',suffixes=['_player', None]).drop(['team', 'id'], axis=1)
    #joining player positions:
    player_info = player_info.merge(player_positions[['id','singular_name_short']], left_on='element_type', right_on='id').drop(['element_type','id'], axis=1)
    # next, i will use the progress_apply() dataframe method that comes with pandas to apply get_gameweek_history() function to every row in players_info dataframe.
    # getting gameweek histores for each player
    from tqdm.auto import tqdm
    tqdm.pandas()
    player_points = player_info['id_player'].progress_apply(current_season_gameweek_info)
    # combining results into one dataframe
    player_points = pd.concat(df for df in player_points)
    player_points = player_info[['id_player', 'web_name','singular_name_short']].merge(player_points, left_on='id_player',right_on='element')
    player_points = player_points.groupby(['element','web_name', 'singular_name_short']).agg({'total_points':'sum', 'goals_scored':'sum', 'assists':'sum'}).reset_index().sort_values('total_points', ascending=False) 
    print(player_points)
    # player_points.describe()
    writer = pd.ExcelWriter('player_points.xlsx')
    player_points.to_excel(writer)
    writer.save()
