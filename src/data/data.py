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
    # specific_player_df = specific_player_df[['difficulty','is_home','total_points','minutes','goals_scored','assists']]
    specific_player_df = specific_player_df[["difficulty"]]
    return specific_player_df


# TODO: What does this do???
def past_season_gameweek_info(user_choice_player):
    """Get sum stats for past seasons players have played in the league:"""
    element_summary_url = requests.get(
        BASE_URL + "element-summary/" + str(user_choice_player) + "/"
    ).json()

    # extract 'history' data from response into dataframe
    specific_player_df = pd.json_normalize(element_summary_url["history"])

    return specific_player_df


def get_per_season_stats_for(player_code: int):
    """TODO:"""
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
    # player_points_csv = training_df.to_csv(
    #      header=[
    #        "id_player",
    #        "opponent_team",
    #        "was_home",
    #        "round",
    #        "transferred_in",
    #        "selected",
    #        "total_points"
    #     ],

    #     index=False,
    # )
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

    # cur.execute(" DROP TABLE fpl_player_model_table")
    # conn.commit()
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

# Retrieve the data from the table
c.execute("SELECT * FROM fpl_player_stats_table")
data = c.fetchall()

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

# Call the merge sort function on the data
sorted_data = merge_sort(data, col=2)

# Create the new table
c.execute("CREATE TABLE IF NOT EXISTS sorted_table (element INTEGER PRIMARY KEY, web_name TEXT, total_points INTEGER)")

# Insert the sorted data into the new table
for row in sorted_data:
    c.execute("INSERT INTO sorted_table (element, web_name, total_points) VALUES (?, ?, ?)", row)

# Commit the changes and close the connection
conn.commit()
class Player:
    def __init__(self, name, position, children=None):
        self.name = name
        self.position = position
        self.children = [] if children is None else children


def traverse_team(node):
    print(node.name, node.position)
    for child in node.children:
        traverse_team(child)


# Define players in the team
goalkeeper = Player("Alisson Becker", "Goalkeeper")
defenders = [
    Player("Trent Alexander-Arnold", "Right Back"),
    Player("Joe Gomez", "Center Back"),
    Player("Virgil van Dijk", "Center Back"),
    Player("Andrew Robertson", "Left Back"),
]
midfielders = [
    Player("Jordan Henderson", "Central Midfield"),
    Player("Georginio Wijnaldum", "Central Midfield"),
    Player("James Milner", "Central Midfield"),
    Player("Naby Keita", "Central Midfield"),
]
forwards = [
    Player("Sadio Mane", "Left Wing"),
    Player("Roberto Firmino", "Centre Forward"),
    Player("Mohamed Salah", "Right Wing"),
]

# Build the team hierarchy
team = Player("Liverpool", "Team", [goalkeeper] + defenders + midfielders + forwards)

# Traverse the team hierarchy


if __name__ == "__main__":

    # df = total_stats_sum_df()
    # print(df)
    # print(model_df)
    print(total_stats_sum_df())
  
    