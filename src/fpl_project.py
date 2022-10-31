import requests, json
import pandas as pd
import numpy as np
from pprint import pprint

from sqlalchemy import create_engine
from PIL import Image
from typing import Tuple, Dict

import kivy

kivy.require("2.1.0")
from kivy.app import App  # the base class must inherit ftom the App class
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import ListProperty
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
import csv


class RGBColour:
    def __init__(self, r: int, g: int, b: int, a: float = 1):
        self.r: int = r
        self.g: int = g
        self.b: int = b
        self.alpha: float = a
        # Kivy takes rgba in float values from 0 to 1
        # (it divides actual rgb values by 255)
        # so it is easier to have a class for rgba
        # and the background_colour can be of type class RGBColour.


class AppButton(Button):
    # my AppButton class is inheriting from Kivy's Button class.
    def __init__(
        self,
        text: str,
        font_size: int,
        background_colour: RGBColour,
        size_hint: Tuple,
        pos_hint: Dict,
        **kwargs,
    ):
        background_colour: Tuple = (
            background_colour.r / 255,
            background_colour.g / 255,
            background_colour.b / 255,
            background_colour.alpha,
        )
        # inheritance below
        super().__init__(
            text=text,
            font_size=font_size,
            background_color=background_colour,
            size_hint=size_hint,
            pos_hint=pos_hint,
            **kwargs,
        )


# class AppLabel(Label):
#     def __init__(self):
#         pass


class MyApp(App):
    def build(self):
        logoBtn = AppButton(
            "FPL Point Predictor!",
            15,
            RGBColour(0, 255, 133),
            (0.5, 0.5),
            {"x": 0.25, "y": 0.25},
        )
        logoBtn.bind(on_press=self.logoBtnPressed)
        return logoBtn

    def logoBtnPressed(self, event):
        f = open("player_points_weekly.xlsx", "r")
        print(f.read())


def every_gameweek_for_player_df(user_choice_player):
    # Getting gameweek information for specific players
    element_summary_URL = requests.get(
        main_url + "element-summary/" + str(user_choice_player) + "/"
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


def current_season_gameweek_info(user_choice_player):

    element_summary_url = requests.get(
        main_url + "element-summary/" + str(user_choice_player) + "/"
    ).json()

    # extract 'history' data from response into dataframe
    specific_player_df = pd.json_normalize(element_summary_url["history"])

    return specific_player_df


def past_seasons_info(user_choice_player_history):
    # Getting gameweek information for specific players
    request_URL = requests.get(
        main_url + "element-summary/" + str(user_choice_player_history) + "/"
    ).json()
    # ^^sending GET request to https://fantasy.premierleague.com/api/element-summary/{PID}/

    specific_player_df_history = pd.json_normalize(request_URL["history_past"])
    return specific_player_df_history


def weekly_stats_df():  # makes a table with all the stats of all players in each gameweek seperately
    request_URL = requests.get(main_url + "bootstrap-static/").json()
    # request_URL = requests.get(main_url+'event/'+str(gameweek)+'/live/').json()
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
    # next, i will use the progress_apply() dataframe method that comes with pandas to apply get_gameweek_history() function to every row in players_info dataframe.
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
    player_points_csv = player_points.to_csv(
        header=[
            "id_player",
            "web_name",
            "singular_name_short",
            "element",
            "fixture",
            "opponent_team",
            "total_points",
            "was_home",
            "kickoff_time",
            "team_h_score",
            "team_a_score",
            "round",
            "minutes",
            "goals_scored",
            "assists",
            "clean_sheets",
            "goals_conceded",
            "own_goals",
            "penalties_saved",
            "penalties_missed",
            "yellow_cards",
            "red_cards",
            "saves",
            "bonus",
            "bps",
            "influence",
            "creativity",
            "threat",
            "ict_index",
            "value",
            "transfers_balance",
            "selected",
            "transfers_in",
            "transfers_out",
        ],
        index=False,      
    )
    player_points_csv[7] = player_points_csv[7].astype(int)
    
    return player_points_csv


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

    player_points = weekly_stats_df()
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
    # i need a list of all my data in a manner which i can then use a model on.
    training_df = weekly_stats_df().astype
    training_df = training_df[
        [0,5,7,11,32,31,6]
    ]
     # as the weekly_stats_df() returns a csv, 
    # I am only taking the columns I want by calling their index values.
    # training_df[2] = training_df[2].astype(int)
    # making a dataframe first using previous function and then changing into list.
    # training_list = training_df.values.tolist()
    # new_list = np.array(training_list)
    
    # with open("training_data.csv", "w") as f:
    #     mywriter = csv.writer(f, delimiter=",")
    #     mywriter.writerows(new_list)
    return training_df


def keras_model():
    dataset = getting_dataset_to_train_nnetwork()
    matrix_dataset = np.array(dataset)
    X = matrix_dataset[:, 0:5]
    y = matrix_dataset[:, 6]
    model = Sequential()
    # to work out how many layers will be good the best thing to do is experimentation:

    # using three layers for now,
    """ first layer will have 12 nodes
        second layer will have 8 nodes
        third layer will have  1 node   """

    model.add(Dense(12, input_shape=(5,), activation="relu"))
    # using the ReLU activation function as better performance is acheieved using it compared to Tanh function or just the sigmoid function.
    model.add(Dense(8, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))
    # compiling the training model.
    # I am using the 'adam' optimizer (version of gradient descent)
    # I am using cross entropy as the loss argument.
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

    model.fit(X, y, epochs=150, batch_size=10)

    accuracy = model.predict(y)
    print("Accuracy: %.2f" % (accuracy * 100))


def evaluate():
    # it is impossible to predict the exact points very accurately, therefore i have to make my own
    # evaluation function which will evaluate my model in a suitable range.

    pass


if __name__ == "__main__":
    # game_week_info()
    main_url = "https://fantasy.premierleague.com/api/"  # the base url for all of the FPL endpoints
    # getting data from bootstrap-static endpoint below:
    request_URL = requests.get(main_url + "bootstrap-static/").json()

    request_URL = requests.get(main_url + "element-summary/9/").json()

    # MyApp().run()
    print(getting_dataset_to_train_nnetwork())
