"""Module that handles retrieving all the data from the FPL API."""

import requests
import pandas as pd
import numpy as np
import csv
from sqlalchemy import create_engine

BASE_URL = "https://fantasy.premierleague.com/api/"  # the base url for all of the FPL endpoints


def get_all_gameweek_data_for(player_code: int):
    """TODO:"""
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
def current_season_gameweek_info(user_choice_player):
    """TODO:"""
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
    #  to apply get_gameweek_history() function
    # to every row in players_info dataframe.
    # getting gameweek histories for each player
    from tqdm.auto import tqdm

    tqdm.pandas()
    player_points = player_info["id_player"].progress_apply(
        current_season_gameweek_info
    )
    # combining results into one dataframe
    player_points = pd.concat(df for df in player_points)
    player_points = player_info[["id_player", "web_name", "singular_name_short"]].merge(
        player_points, left_on="id_player", right_on="element"
    )

    return player_points


def total_stats_sum_df():  # this gives the sum of everything and orders the stats in most points scored.
    total_stats_season_df = weekly_stats_df()
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


def getting_player_images():

    image_url = (
        "https://resources.premierleague.com/premierleague/photos/players/110x140/p"
        + image_code
        + ".png"
    )
    print("lorem ipsium")


def search():
    """Module that handles the search of the player and the data from which model will make prediction."""
    player_points = get_all_gameweek_data_for()
    engine = create_engine("sqlite://", echo=False)
    player_points.to_sql("players", engine, if_exists="replace", index=False)
    user_search_player = input(str("Enter player name: "))
    # using sql, i can ask for a user input of what player they want, and that players data is accessed.
    results = engine.execute(
        "Select * from players where web_name= (?)", user_search_player
    )
    one_player_df = pd.DataFrame(results, columns=player_points.columns)
    player_stats_df = user_search_player + ".xlsx"
    one_player_df.to_excel(player_stats_df, index=False)
    return one_player_df


def getting_dataset_to_train_nnetwork():

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


if __name__ == "__main__":
    getting_dataset_to_train_nnetwork()
