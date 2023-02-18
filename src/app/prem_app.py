from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from typing import Tuple, Dict
import sqlite3
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow


class RGBColour:
    def __init__(self, r: int, g: int, b: int, a: float = 1):
        self.r: int = r
        self.g: int = g
        self.b: int = b
        self.alpha: float = a


class AppButton(Button):
    def __init__(
        self,
        text: str,
        font_size: int,
        background_color: RGBColour,
        size_hint: Tuple,
        pos_hint: Dict,
        **kwargs,
    ):
        background_color: Tuple = (
            background_color.r / 255,
            background_color.g / 255,
            background_color.b / 255,
            background_color.alpha,
        )
        super().__init__(
            text=text,
            font_size=font_size,
            background_color=background_color,
            size_hint=size_hint,
            pos_hint=pos_hint,
            **kwargs,
        )


conn = sqlite3.connect("users_db.sqlite")
c = conn.cursor()

c.execute(
    '''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, passwords TEXT)'''
)

class HasAccount(GridLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.rows = 3
        self.spacing = 10
        self.padding = 80

        label = Label(text="Do you have an account?", color = (0, 1, 0.52, 1))
        self.add_widget(label)


        self.yes_button = AppButton(
            "YES",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.yes_button)
        self.yes_button.bind(on_press=self.on_yes_button)

        self.no_button = AppButton(
            "NO",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.no_button)
        self.no_button.bind(on_press=self.on_no_button)
    
  
    def on_yes_button(self,instance):
        self.manager.current = 'login'
    
    
    def on_no_button(self,instance):
        self.manager.current = 'register'


class LoginErrorPage(GridLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.rows = 2
        self.spacing = 10
        self.padding = 80

        label = Label(text="Invalid details, try again", color = (0, 1, 0.52, 1))
        self.add_widget(label)



        self.back_button = AppButton(
            "***Try Again***",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.on_back_button)

    def on_back_button(self,instance):
        self.manager.current = 'login'


class RegisterErrorPage(GridLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.rows = 2
        self.spacing = 10
        self.padding = 80

        label = Label(text="Either the username is taken, or details not filled properly.(Password > 6 chars)", color = (0, 1, 0.52, 1))
        self.add_widget(label)



        self.back_button = AppButton(
            "***Try Again***",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.on_back_button)

    def on_back_button(self,instance):
        self.manager.current = 'register'


class AccountRegisterLayout(GridLayout, Screen):
    # inheritance from Screen class (python's class)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.spacing = 20
        self.padding = 80
        self.add_widget(
            AppButton(
                "Username",
                35,
                RGBColour(46, 204, 113),
                (0.3, 0.1),
                {"x": 0.2, "y": 0.05},
            )
        )
        self.username = TextInput(multiline=False,size_hint = (0.5,0.002))
        self.add_widget(self.username)
        self.add_widget(
            AppButton(
                "Password",
                35,
                RGBColour(90, 34, 139),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.05}
            )
        )
        self.password = TextInput(multiline=False,size_hint = (0.5,0.002),password=True)
        self.add_widget(self.password)
        self.register = AppButton(
            "Register",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.005}
        )
        self.register.bind(on_press=self.register_user)
        self.add_widget(self.register)

        self.back_button = AppButton(
            "Back",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )

        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.go_back)


        self.fpl_logo = Image(source="fpl_logo.png", size_hint = (0.5,0.5))
        self.add_widget(self.fpl_logo)

    def register_user(self, instance):
        # Insert the user's information into the database

        conn = sqlite3.connect("users_db.sqlite")
        c = conn.cursor()

        username = self.username.text
        password = self.password.text
        self.valid_password = False
        self.valid_username = False

        if not username.strip():
            self.manager.current = 'register_error'
        else:
            self.valid_username = True

        if not password.strip():
            
            self.manager.current = "register_error"
        elif len(password) < 6:
            
            self.manager.current = "register_error"

        else:
            self.valid_password = True

        if self.valid_password == True and self.valid_username == True:
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user = c.fetchone()

            if user is not None:
                self.manager.current = 'register_error'
            else:
                c.execute(
                    "INSERT INTO users (username, passwords) VALUES (?, ?)",
                    (username, password),
                )
                conn.commit()
                print("Record inserted successfully.")
                self.manager.current = "login"

    def go_back(self,instance):
        self.manager.current = 'has_account'


class LoginLayout(GridLayout, Screen):
    """A sub class of Parent python class called Gridlayout - login in screen"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.spacing = 20
        self.padding = 80
        self.add_widget(
            AppButton(
                "Username",
                35,
                RGBColour(46, 204, 113),
                (0.3, 0.1),
                {"x": 0.2, "y": 0.05},
            )
        )
        self.username = TextInput(multiline=False,size_hint = (0.5,0.002))
        self.add_widget(self.username)
        self.add_widget(
            AppButton(
                "Password",
                35,
                RGBColour(90, 34, 139),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.05}
            )
        )
        self.password = TextInput(multiline=False,size_hint = (0.5,0.002),password=True)
        self.add_widget(self.password)
        self.register = AppButton(
            "Submit",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.005}
        )
        self.register.bind(on_press=self.login)
        self.add_widget(self.register)

        self.back_button = AppButton(
            "Back",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )

        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.go_back)
        self.fpl_logo = Image(source="fpl_logo.png", size_hint = (0.5,0.5), pos_hint = (1,0.5))
        self.add_widget(self.fpl_logo)
        
    def login(self, instance):
        # Check if the username and password match a user in the database
        conn = sqlite3.connect("users_db.sqlite")
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND passwords=?",
            (self.username.text, self.password.text),
        )
        user = c.fetchone()

        if user:
            print("Login successful")
            
            self.manager.current = "menu"
            username_value = self.username
            self.username_value = username_value.text
            return self.username_value
            # ...

        else:
            self.manager.current = 'login_error'
        
    def go_back(self,instance):
        self.manager.current = 'has_account'


class MainMenu(GridLayout, Screen):
    """Allows users to choose between options in main menu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 30
        self.fpl_logo = Image(source="fpl_logo.png")
        self.add_widget(self.fpl_logo)
        self.search_button = AppButton(
            "Search",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.search_button)
        self.search_button.bind(on_press=self.open_search_screen)

        self.players_info_button = AppButton(
            "Players Information",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2},
        )

        self.add_widget(self.players_info_button)
        self.players_info_button.bind(on_press=self.player_info)

        self.my_team_button = AppButton(
            "My Team",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )

        self.add_widget(self.my_team_button)
        self.my_team_button.bind(on_press=self.display_team)

        self.back_button = AppButton(
            "Back",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )

        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.go_back_login)

    def display_team(self, instance):
        self.manager.current = "433"

    def open_search_screen(self, instance):
        self.manager.get_screen('search_bar').previous = self.name
        self.manager.current = "search_bar"

    def player_info(self, instance):
        self.manager.current = "player_info"

    def go_back_login(self, instance):
        self.manager.current = "login"


class SearchBar(GridLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        
        self.spacing = 30
        self.padding = 80
        self.previous = ''
        self.prediction_num = 0
        # Create a text input widget
        self.search_input = TextInput(
            hint_text="Enter player name",
            size_hint = (0.1,0.1),
            
            multiline=False
        )
        self.fpl_logo = Image(source="fpl_logo.png")
        self.add_widget(self.fpl_logo)
        # Create a search button widget
        self.search_button = AppButton(
            "Search",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.5, "y": 0.5},
        )

        # Add the text input and search button to the layout
        self.add_widget(self.search_input)
        self.search_button.bind(on_press=self.predict)
        self.add_widget(self.search_button)
        self.back_button = AppButton(
            "Back",
            35,
            RGBColour(90, 34, 139),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )

        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.go_back)

    def go_back(self, instance):

        self.manager.current = self.previous

    def search(self, instance, player_name):
        try:
                # Connect to the SQL database
            conn = sqlite3.connect("fpl_players_db.sqlite")
            c = conn.cursor()

                # Search for the player in the database
            c.execute(
                "SELECT * FROM fpl_player_final_table WHERE web_name=?", (player_name,))

            result = c.fetchall()[-1]

                # return result

            if result:

                return result
                
        except Exception as e:
            self.manager.current = 'search_error'
           
        finally:
            conn.close()

    def _get_player_average_and_sum(self, player_name) -> tuple[float, float]:
        conn = sqlite3.connect("fpl_players_db.sqlite")
        cur = conn.cursor()
        query = """
        SELECT AVG (total_points) 
        FROM fpl_player_final_table 
        WHERE web_name = ? 
        GROUP BY web_name
        """
        
        average = cur.execute(
            query, (player_name,)
        ).fetchall()
        
        print(type(average))
        
       
       
        conn.close()
        conn = sqlite3.connect("fpl_players_db.sqlite")
        cur = conn.cursor()
        query = """
        SELECT SUM(fpl_player_stats_table.total_points)
        FROM fpl_player_table
        INNER JOIN fpl_player_stats_table
        ON fpl_player_table.element = fpl_player_stats_table.element
        WHERE fpl_player_table.web_name = ? AND fpl_player_stats_table.web_name = ?
        """
        season_points = cur.execute(
            query, (player_name, player_name)
        ).fetchall()  # fetchall() retrieves all the rows returned from SELECT statement
        
        
        
        
        
        
        return average, season_points


    def predict(self, instance):
        player_name = self.search_input.text
        arr = self.search(instance, player_name)
        if arr == None:
            self.manager.current = 'search_error'
            
        else:
        # Load the saved model
            loaded_model = tensorflow.keras.models.load_model("fpl_predictor.h5")

            # Get the new sample data
            new_sample = np.array([[arr[:6]]])
            new_sample = new_sample.reshape(-1, 6)

            # Scale the new sample data using the same scaler that was used to scale the training data
            scaler = StandardScaler()

            data = np.loadtxt("training.csv", delimiter=",")

            # Load data from CSV file

            # Split data into input and output
            X = data[:, :6]
            y = data[:, 6]

            # Split data into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2)

            # Scale the input data
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            # scaler.fit(data)
            new_sample = scaler.transform(new_sample)

            # Make predictions using the loaded model
            
            prediction = loaded_model.predict(new_sample)
            int_array = prediction.astype(int)
            prediction = int_array[0]
            self.prediction_num = prediction.item()
            prediction_val = self.prediction_num
            print(prediction_val)
            display_screen = self.manager.get_screen('display_prediction')
            average, season_points = self._get_player_average_and_sum(player_name)
            display_screen.update_score_label(player_name, prediction_val, average, season_points)
            self.manager.current = 'display_prediction'

    

class PlayerSearchError(GridLayout, Screen):
    def __init__(self, **kwargs):
            super().__init__(**kwargs)
            
            self.rows = 2
            self.spacing = 10
            self.padding = 80

            label = Label(text="----Error: not a valid input----", color = (0, 1, 0.52, 1))
            self.add_widget(label)



            self.back_button = AppButton(
                "***Try Again***",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
            )
            self.add_widget(self.back_button)
            self.back_button.bind(on_press=self.on_back_button)

    def on_back_button(self,instance):
        self.manager.current = 'search_bar'

class DisplayPrediction(GridLayout,Screen):

    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        
        self.rows = 2
        self.spacing = 10
        self.padding = 80
        self.previous = ''
       
        # print(prediction)

        self.label = Label(text=f"No Prediction Found!!", color = (0, 1, 0.52, 1))
        self.add_widget(self.label)



        self.back_button = AppButton(
            "Back",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.on_back_button)

    def update_score_label(self, player_name, score, average, season_points):
        self.label.text = f"===== {player_name} Point Prediction: {score} points=====\n====={player_name} average points this season: {average}. \n {player_name} total points this season: {season_points}"
    
    def on_back_button(self,instance):
        self.manager.current = 'search_bar'

class UserTeamLayout(GridLayout, Screen):
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self.cols = 3
        self.spacing = 10
        self.padding = 30
        # Add buttons to the layout
        
        self.gkbutton = AppButton(
                "GK",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.gkbutton)
        self.gkbutton.bind(on_press=self.open_search_screen)
        self.cb1Button = AppButton(
                "CB",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.cb1Button)
        self.cb1Button.bind(on_press=self.open_search_screen)
        self.cb2Button = AppButton(
                "CB",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.cb2Button)
        self.cb2Button.bind(on_press=self.open_search_screen)
        self.lbButton = AppButton(
                "LB",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.lbButton)
        self.lbButton.bind(on_press=self.open_search_screen)

        self.rbButton = AppButton(
                "RB",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1), {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.rbButton)
        self.rbButton.bind(on_press=self.open_search_screen)
        self.cdmButton = AppButton(
                "CDM",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.cdmButton)
        self.cdmButton.bind(on_press=self.open_search_screen)
        self.cmButton = AppButton(
                "CM",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.cmButton)
        self.cmButton.bind(on_press=self.open_search_screen)

        self.camButton = AppButton(
                "CAM",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.camButton)
        self.camButton.bind(on_press=self.open_search_screen)

        self.lwButton = AppButton(
                "LW",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.lwButton)
        self.lwButton.bind(on_press=self.open_search_screen)

        self.rwButton = AppButton(
                "RW",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.rwButton)
        self.rwButton.bind(on_press=self.open_search_screen)

        self.stButton = AppButton(
                "ST",
                35,
                RGBColour(46, 204, 113),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.stButton)
        self.stButton.bind(on_press=self.open_search_screen)

        self.back_button = AppButton(
                "Back",
                35,
                RGBColour(90, 34, 139),
                (0.1, 0.1),
                {"x": 0.2, "y": 0.2}
        )
        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.go_back_menu)

    def open_search_screen(self, instance):
        self.manager.get_screen('search_bar').previous = self.name
        self.manager.current = "search_bar"
        self.first_instance = LoginLayout()
        
        # username_value = self.first_instance.username_value
        
        # # Connect to the database
        # conn = sqlite3.connect("users_db.sqlite")
        # cursor = conn.cursor()
        # prediction = SearchBar().predict(instance)
        # self.player = SearchBar()
        # player_name = self.player.search_input.text
        # self.username = LoginLayout()
        # username_value = self.username.login(instance)
        # print(username_value)
        # self.predict = SearchBar()
        # prediction_value = self.predict.predict(instance)
        # predicted_points = prediction_value.prediction
        
        
        
        # table_name = username+'_team'
        # # Fetch data from the SQL table
        # cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (player TEXT, predicted_points INTEGER) ''')
        
        # cursor.execute(
        #     f"INSERT OR IGNORE INTO {table_name} (player, predicted_points) VALUES (?,?)",
        #     (player_name, predicted_points)
        #  )

    def go_back_menu(self, instance):

        self.manager.current = 'menu'


# Connect to the database
conn = sqlite3.connect("fpl_players_db.sqlite")
cursor = conn.cursor()

# Fetch data from the SQL table
cursor.execute("SELECT * from fpl_player_table")
players = cursor.fetchall()


class PlayerInfoLayout(GridLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Connect to the SQLite database and retrieve the data
        conn = sqlite3.connect("fpl_players_db.sqlite")
        cur = conn.cursor()
        cur.execute("SELECT * FROM sorted_table")
        data = cur.fetchall()

        # Set the number of columns in the table
        self.cols = len(data[0])
        # Calculate the minimum height of the label layout
        self.minimum_height = len(data) * 100
        # Create a layout to hold the labels
        self.back_button = AppButton(
            "Back",
            35,
            RGBColour(46, 204, 113),
            (0.1, 0.1),
            {"x": 0.2, "y": 0.2}
        )
        self.back_button.bind(on_press=self.go_back_to_menu)
        self.add_widget(self.back_button)
        
        scroll_view = ScrollView(size_hint=(1, 0.9))
        scroll_content = GridLayout(size_hint_y=None)
        scroll_content.bind(minimum_height=scroll_content.setter('height'))
        
        label_layout = GridLayout(
            cols=self.cols, size_hint_y=None, height=self.minimum_height
        )
        label_layout.bind(minimum_height=label_layout.setter("height"))

        # Loop through the data and add a label for each row
        for row in data:
            for value in row:
                label = Label(
                    text=str(value), color=(0, 1, 0.52, 1), size_hint_y=None, height=100
                )
                label_layout.add_widget(label)

        # Add the label layout to the ScrollView
        
        scroll_view.add_widget(label_layout)
        self.add_widget(scroll_view)
    def go_back_to_menu(self,instance):
        self.manager.current = 'menu'
class PremierLeagueApp(App):  # inherits from parent class App(kivy's class)
    """Main class, through which screens are defined so they can be switched between"""
    # some_data = None
    def build(self):
        
        
        screen_manager = ScreenManager()
        screen_manager.add_widget(HasAccount(name="has_account"))
        screen_manager.add_widget(AccountRegisterLayout(name="register"))
        screen_manager.add_widget(LoginLayout(name="login"))
        screen_manager.add_widget(MainMenu(name="menu"))
        screen_manager.add_widget(SearchBar(name="search_bar"))
        screen_manager.add_widget(PlayerInfoLayout(name="player_info"))
        screen_manager.add_widget(LoginErrorPage(name="login_error"))
        screen_manager.add_widget(RegisterErrorPage(name="register_error"))
        screen_manager.add_widget(PlayerSearchError(name="search_error"))
        screen_manager.add_widget(UserTeamLayout(name="433"))
        screen_manager.add_widget(DisplayPrediction(name="display_prediction"))
        screen_manager.current = "has_account"
        return screen_manager


if __name__ == "__main__":
    PremierLeagueApp().run()
