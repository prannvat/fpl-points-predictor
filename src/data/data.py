"""Module that handles retrieving all the data from the FPL API."""

import requests
import pandas as pd
import numpy as np
import csv
import sqlite3


BASE_URL = "https://fantasy.premierleague.com/api/"  # the base url for all of the FPL endpoints


def get_all_gameweek_data_for(player_code: int):
    """Gets all gameweek data for season for every player:"""
    # Getting gameweek information for specific players
    element_summary_URL = requests.get(
        BASE_URL + "element-summary/" + str(player_code) + "/"
    ).json()
    # ^^sending GET request to https://fantasy.premierleague.com/api/element-summary/{PID}/
    fixtures_df = pd.json_normalize(element_summary_URL["fixtures"])
    fixtures_df[["difficulty"]]
    specific_player_df = pd.json_normalize(element_summary_URL["history"])

    specific_player_df = pd.merge(
        specific_player_df,
        fixtures_df[["difficulty", "is_home"]],
        left_on="round",
        right_on="difficulty",
    )
    
    specific_player_df = specific_player_df[["difficulty"]]
    return specific_player_df



def past_season_gameweek_info(user_choice_player):
    '''Previous fixtures and results for players'''
    element_summary_url = requests.get(
        BASE_URL + "element-summary/" + str(user_choice_player) + "/"
    ).json()

    # extract 'history' data from response into dataframe
    specific_player_df = pd.json_normalize(element_summary_url["history"])

    return specific_player_df


def get_per_season_stats_for(player_code: int):
    """Get sum stats for past seasons players have played in the league:"""
    # Getting gameweek information for specific players
    request_URL = requests.get(
        BASE_URL + "element-summary/" + str(player_code) + "/"
    ).json()
    # ^^sending GET request to https://fantasy.premierleague.com/api/element-summary/{PID}/

    specific_player_df_history = pd.json_normalize(request_URL["history_past"])
    return specific_player_df_history


def get_all_players_stats_for_this_season():
    """Makes a table with all the stats of all players in each gameweek seperately"""
    request_URL = requests.get(BASE_URL + "bootstrap-static/").json()
    # request_URL = requests.get(BASE_URL+'event/'+str(gameweek)+'/live/').json()
    # I can now get player data usimg the 'elements' field of the API:
    player_info = request_URL["elements"]
    # using Pandas, I can now make the data I have be in a tabular format.
    # Pandas is a library made for exactly this purpose.
    pd.set_option("display.max_columns", None)
    # now I can create dataframe using the players info
    player_info = pd.json_normalize(request_URL["elements"])

    # creating dataframe for teams:
    teams_info = pd.json_normalize(request_URL["teams"])
    # player positions using the 'element-types' field:
    player_positions = pd.json_normalize(request_URL["element_types"])
    # creating a points table which will contain all the info for all
    player_info = player_info[
        ["id", "first_name", "second_name", "web_name", "team", "element_type"]
    ]
    # i will join the teamn names to the table
    player_info = player_info.merge(
        teams_info[["id", "name"]],
        left_on="team",
        right_on="id",
        suffixes=["_player", None],
    ).drop(["team", "id"], axis=1)
    # joining player positions:
    player_info = player_info.merge(
        player_positions[["id", "singular_name_short"]],
        left_on="element_type",
        right_on="id",
    ).drop(["element_type", "id"], axis=1)
    # next, i will use the progress_apply() dataframe method,
    # that comes with pandas,
    #  to apply past_season_gameweek_info() function
    # to every row in players_info dataframe.
    # getting gameweek histories for each player

    from tqdm.auto import tqdm

    tqdm.pandas()
    player_points = player_info["id_player"].progress_apply(past_season_gameweek_info)
    # combining results into one dataframe
    player_points = pd.concat(df for df in player_points)
    player_points = player_info[["id_player", "web_name", "singular_name_short"]].merge(
        player_points, left_on="id_player", right_on="element"
    )

    return player_points


def total_stats_sum_df():  # this gives the sum of everything and orders the stats in most points scored.
    total_stats_season_df = get_all_players_stats_for_this_season()
    total_stats_season_df = (
        total_stats_season_df.groupby(["element", "web_name", "singular_name_short"])
        .agg(
            {
                "total_points": "sum",
                "goals_scored": "sum",
                "assists": "sum",
                "goals_conceded": "sum",
            }
        )
        .reset_index()
        .sort_values("total_points", ascending=False)
    )
    writer = pd.ExcelWriter("player_points.xlsx")
    total_stats_season_df.to_excel(writer)
    writer.save()
    writer = pd.ExcelWriter("player_points.xlsx")
    total_stats_season_df.to_excel(writer)
    writer.save()
    return total_stats_season_df


def get_dataset_to_train_nnetwork():

    training_df = get_all_players_stats_for_this_season()

    training_df = training_df[
        [
            "id_player",
            "opponent_team",
            "was_home",
            "round",
            "transfers_in",
            "selected",
            "total_points",
        ]
    ]
    training_df["was_home"] = training_df["was_home"].astype(int)
    training_df.to_csv("testsql.csv", index=False)
    training_list = training_df.values.tolist()
    
    file = open("training.csv", "w")
    writer = csv.writer(file)
    writer.writerows(training_list)
    return training_df


def sql_player_database(df):

    """Using sqlite3 to make all sql tables. Uses all techniques."""

    # print(model_df)
    player_df = df[["element", "web_name", "singular_name_short"]]
    players_stats_df = df[["element", "web_name", "total_points"]]
    # print(players_stats_df)
    conn = sqlite3.connect("fpl_players_db.sqlite")
    cur = conn.cursor()
    # #Creating these tables on my sql database, they can then be used for aggregate functions etc and cross-parameterized sql.
    fpl_player_table = """
                CREATE TABLE IF NOT EXISTS fpl_player_table (
                element INTEGER PRIMARY KEY,
                web_name TEXT,
                singular_name_short TEXT
                );
                """
    cur.execute(fpl_player_table)
    # INSERT OR IGNORE INTO only exerts if it doesn't already exist in table.
    for _, row in player_df.iterrows():
        cur.execute(
            "INSERT OR IGNORE INTO fpl_player_table (element, web_name, singular_name_short) VALUES (?,?,?)",
            (row["element"], row["web_name"], row["singular_name_short"]),
        )
    conn.commit()

    fpl_player_stats_table = """
                CREATE TABLE IF NOT EXISTS fpl_player_stats_table (
                element INTEGER PRIMARY KEY,
                web_name TEXT,
                total_points INTEGER
                );
                """
    cur.execute(fpl_player_stats_table)

    for _, row in players_stats_df.iterrows():
        cur.execute(
            "INSERT OR IGNORE INTO fpl_player_stats_table (element, web_name, total_points) VALUES (?,?,?)",
            (row["element"], row["web_name"], row["total_points"]),
        )
    conn.commit()

   
    # Create the table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS fpl_player_model_table (
    id_player INTEGER,
    opponent_team INTEGER,
    was_home INTEGER,
    round INTEGER,
    transfers_in INTEGER,
    selected INTEGER,
    total_points INTEGER,
    PRIMARY KEY (id_player, round)
    );
    """
    )

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv("testsql.csv")

    # Insert the data from the DataFrame into the table
    df.to_sql("fpl_player_model_table", conn, if_exists="replace", index=False)

    conn.commit()

    query = """
    CREATE TABLE IF NOT EXISTS fpl_player_final_table AS
    SELECT *
    FROM fpl_player_model_table
    JOIN fpl_player_table
    ON fpl_player_model_table.id_player = fpl_player_table.element"""

    try:
        cur.execute(query)
        conn.commit()
    except Exception as e:
        print("Error:", e)

    user_search = str(input("Enter player Name:"))
    # CROSS-PARAMETERIZED SQL ASWELL AS AGGREGATE FUNCTIONS.
    query = """
    SELECT AVG(fpl_player_stats_table.total_points)
    FROM fpl_player_table
    INNER JOIN fpl_player_stats_table
    ON fpl_player_table.element = fpl_player_stats_table.element
    WHERE fpl_player_table.web_name = ? AND fpl_player_stats_table.web_name = ?
    """

    # '?' is used as a placeholder for values in SQL table. Known as parameterized SQL.
    result = cur.execute(
        query, (user_search, user_search)
    ).fetchall()  # fetchall() retrieves all the rows returned from SELECT statement
    print(result)

    conn.close()

    # Creating player database with their points

# Connect to the database

'''Below is all to get all the player info sorted in terms of points for the GUI'''
conn = sqlite3.connect('fpl_players_db.sqlite')
c = conn.cursor()



# Define the merge sort function
def merge_sort(data, col):
    if len(data) <= 1:
        return data
    mid = len(data) // 2
    left = data[:mid]
    right = data[mid:]
    left = merge_sort(left, col)
    right = merge_sort(right, col)
    return merge(left, right, col)

def merge(left, right, col):
    result = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        if left[i][col] >= right[j][col]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result += left[i:]
    result += right[j:]
    return result


import heapq

def optimize_fpl_team(start_team, graph):
    # Set all nodes to unvisited and initialize weights to infinity
    unvisited = set(graph.keys())
    weights = {node: float('inf') for node in graph.keys()}
    weights[start_team] = 0
    
    # Initialize the priority queue with the start node
    pq = []
    heapq.heappush(pq, (weights[start_team], start_team))
    
    while pq:
        # Extract the node with the lowest weight
        curr_weight, curr_node = heapq.heappop(pq)
        
        # Mark the node as visited
        unvisited.remove(curr_node)
        
        # Update the weights of unvisited neighbors
        for neighbor, weight in graph[curr_node].items():
            if neighbor in unvisited:
                new_weight = curr_weight + weight
                if new_weight < weights[neighbor]:
                    weights[neighbor] = new_weight
                    heapq.heappush(pq, (new_weight, neighbor))
    
    # Extract the optimized FPL team
    optimized_team = []
    curr_node = start_team
    while curr_node:
        optimized_team.append(curr_node)
        min_weight = float('inf')
        next_node = None
        for neighbor, weight in graph[curr_node].items():
            if weights[neighbor] < min_weight:
                min_weight = weights[neighbor]
                next_node = neighbor
        curr_node = next_node if next_node != start_team else None
    
    return optimized_team

graph = {
    'Salah': {'Mane': 15, 'Alexander-Arnold': 10},
    'Mane': {'Salah': 15, 'Firmino': 5},
    'Alexander-Arnold': {'Salah': 10, 'Robertson': 8},
    'Robertson': {'Alexander-Arnold': 8, 'Firmino': 4},
    'Firmino': {'Mane': 5, 'Robertson': 4},
}


if __name__ == "__main__":

    df = total_stats_sum_df()
    # print(df)
    # print(model_df)

    sql_player_database(df)
    print(get_all_players_stats_for_this_season())
    
    conn = sqlite3.connect('fpl_players_db.sqlite')
    c = conn.cursor()
    # Call the merge sort function on the data
    # Retrieve the data from the table
    c.execute("SELECT * FROM fpl_player_stats_table")
    
    data = c.fetchall()
    sorted_data = merge_sort(data, col=2)

    # c.execute("DROP TABLE sorted_table")
    # # # Create the new table
    c.execute("CREATE TABLE IF NOT EXISTS sorted_table (element INTEGER PRIMARY KEY, web_name TEXT, total_points INTEGER)")

    
    # # print(sorted_data)
    # # Insert the sorted data into the new table
    for row in sorted_data:
        # import pdb; pdb.set_trace()
        print(row)
        
        c.execute("INSERT sorted_table (element, web_name, total_points) VALUES (?, ?, ?)", (row))

    # # Commit the changes and close the connection
    conn.commit()