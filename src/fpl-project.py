from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
from pickle import TRUE
import requests , json
import pandas as pd
import numpy as np 
from pprint import pprint

if __name__ == '__main__':
    # game_week_info()
    
    main_url = 'https://fantasy.premierleague.com/api/' #the base url for all of the FPL endpoints

    # getting data from bootstrap-static endpoint below:
    bootstrap_URL = requests.get(main_url+'bootstrap-static/').json()
    pprint(bootstrap_URL, indent=2, depth=1, compact=True)
    # the above shows the main top-level columns only 
    # I can now get player data usimg the 'elements field of the API:
    player_info = bootstrap_URL['elements']
    #pprint(player_info[0]) #show player data according to what player using index value.

    # usingPandas, I can now make the data I have be in a tabular format.
    #Pandas is a library made for exactly this purpose.
    pd.set_option('display.max_columns', None)
    #now I can create dataframe using the players info
    player_info = pd.json_normalize(bootstrap_URL['elements'])
    #print(player_info[['id', 'web_name', 'team', 'element_type','threat']].head())

    #creating dataframe for teams:
    teams_info = pd.json_normalize(bootstrap_URL['teams'])
    #print(teams_info.head())

    #player positions using the 'elemebt-types' field:
    player_positions = pd.json_normalize(bootstrap_URL['element_types'])
    #print(player_positions.head())
    #now i will join the olayers to the teams:
    merged_table = pd.merge(left=player_info, right=teams_info, left_on ='team', right_on='id')
    print(merged_table[['first_name','second_name', 'name']])
    #adding the player positions:
    merged_table = merged_table.merge(player_positions, left_on='element_type' ,right_on='id')
    
    #now I will rename the column names to more suitable and meaningful names:
    merged_table = merged_table.rename(columns={'name':'club_name', 'singular_name':'player_position'})
    print(merged_table[['first_name','second_name', 'club_name','player_position']])