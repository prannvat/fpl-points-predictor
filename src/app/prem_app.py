import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
import psycopg2
from typing import Tuple, Dict
import sqlite3
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.core.window import Window
from kivy.uix.slider import Slider
from functools import partial
from kivy.properties import StringProperty
import numpy as np
from sklearn.preprocessing import StandardScaler
import tensorflow
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from model import training_model
import inspect  


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


conn = sqlite3.connect('users_db.sqlite')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, passwords TEXT)''')
# c.execute("INSERT INTO users (username, passwords) VALUES (?, ?)", ('loremipsium', 'testpassword'))
# conn.commit()
# print("Record inserted successfully.")

# conn.close()
class AccountRegisterLayout(GridLayout,Screen):
    # inheritance from Screen class (python's class)
    def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.cols = 2
            self.spacing = 20
            self.padding = 40
            self.add_widget(AppButton(
            "Username",
            35,
            RGBColour(46,204,113),
            (0.3,0.1),
            {"x":0.2,"y":0.2}))
            self.username = TextInput(multiline=False)
            self.add_widget(self.username)
            self.add_widget(AppButton(
            "Password",
            35,
            RGBColour(90,34,139),
            (0.1,0.1),
            {"x":0.2,"y":0.2}))
            self.password = TextInput(multiline=False, password=True)
            self.add_widget(self.password)
            self.register = AppButton(
            "Register",
            35,
            RGBColour(46,204,113),
            (0.3,0.6),
            {"x":0.2,"y":0.2})
            self.register.bind(on_press=self.register_user)
            self.add_widget(self.register)

        
    def register_user(self, instance):
        # Insert the user's information into the database
        
        conn = sqlite3.connect('users_db.sqlite')
        c = conn.cursor()

        username = self.username.text
        password = self.password.text

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user is not None:
            print(f"Username '{username}' already exists.")
        else:
            c.execute("INSERT INTO users (username, passwords) VALUES (?, ?)", (username, password))
            conn.commit()
            print("Record inserted successfully.")
            self.manager.current = 'menu'
            
            
    
    
    
     
        
        
class LoginLayout(GridLayout,Screen):
    '''A sub class of Parent python class called Gridlayout - login in screen'''

    def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.cols = 2
            self.spacing = 20
            self.padding = 40
            self.add_widget(AppButton(
            "Username",
            35,
            RGBColour(46,204,113),
            (0.1,0.1),
            {"x":0.2,"y":0.2}))
            self.username = TextInput(multiline=False)
            self.add_widget(self.username)
            self.add_widget(AppButton(
            "Password",
            35,
            RGBColour(90,34,139),
            (0.1,0.1),
            {"x":0.2,"y":0.2}))
            self.password = TextInput(multiline=False, password=True)
            self.add_widget(self.password)
            self.submit = AppButton(
            "Submit",
            35,
            RGBColour(46,204,113),
            (0.3,0.6),
            {"x":0.2,"y":0.2})
            self.submit.bind(on_press=self.login)
            self.add_widget(self.submit)
            
        

    def login(self, instance):
        # Check if the username and password match a user in the database
        c.execute("SELECT * FROM users WHERE username=? AND passwords=?",
        (self.username.text, self.password.text))
        user = c.fetchone()

        if user:
            print('yes')
            
            self.manager.current = 'menu'
            # ...
            
        else:
            print("try again")
    
    
        
    


class MainMenu(GridLayout, Screen):
    '''Allows users to choose between options in main menu'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)   
        self.cols= 1
        self.spacing = 10
        self.padding = 30
        self.fpl_logo = Image(source='fpl_logo.png')
        self.add_widget(self.fpl_logo)
        self.search_button = AppButton(
                        'Search',
                        35,
                        RGBColour(46,204,113),
                        (0.1,0.1),
                        {"x":0.2, "y":0.2})
        self.add_widget(self.search_button)
        self.search_button.bind(on_press=self.open_search_screen)
        

        self.players_info_button = AppButton(
                            'Players Information',
                            35,
                            RGBColour(46,204,113),
                            (0.1,0.1),
                            {"x":0.2, "y":0.2})
        
        self.add_widget(self.players_info_button)
        self.players_info_button.bind(on_press=self.player_info)

        self.back_button = AppButton(
                            'Back',
                            35,
                            RGBColour(46,204,113),
                            (0.1,0.1),
                            {"x":0.2, "y":0.2})
        
        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.go_back_login)
        
    def open_search_screen(self, instance):
            self.manager.current = 'search_bar'
    
    def player_info(self,instance):
        self.manager.current = 'player_info'
    
    def go_back_login(self, instance):
        self.manager.current = 'login'



class SearchBar(GridLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        # Create a text input widget
        self.search_input = TextInput(hint_text='Enter player name',size_hint = (0.1,0.1), multiline=False)

        # Create a search button widget
        self.search_button = AppButton(
                            'Search',
                            35,
                            RGBColour(46,204,113),
                            (1,1),
                            {"x":0.5, "y":0.5}, 
                            on_press=self.predict)
         
        # Add the text input and search button to the layout
        self.add_widget(self.search_input)
        
        self.add_widget(self.search_button)
        # self.search_button.bind(on_press= self.predict)
        self.back_button = AppButton(
                            'Back',
                            35,
                            RGBColour(90,34,139),
                            (0.1,0.1),
                            {"x":0.2, "y":0.2})
        
        self.add_widget(self.back_button)
        self.back_button.bind(on_press=self.go_back_menu)

    def go_back_menu(self, instance):
        self.manager.current = 'menu'
    
   

    
    def search(self,instance):
        # Get the player name from the text input
        player_name = self.search_input.text

        # Connect to the SQL database
        conn = sqlite3.connect('fpl_players_db.sqlite')
        c = conn.cursor()

        # Search for the player in the database
        c.execute("SELECT * FROM fpl_player_final_table WHERE web_name=?", (player_name,))

       
        result = c.fetchall()[-1]
        # if results:
        #     result = results[-1]
        # else:
        #     result = (0,0,0,0,0,0,0)
       
        # Get the result of the search
        # result = c.fetchall()[-1]
        
        # if result != None:
            # testt = True
        print(result)
        print(type(result))
        return result
        
        
    def predict(self,instance):
        arr = self.search(instance)
        # data = inspect.signature(training_model.train_model).return_annotation
        
        data = training_model.train_model()
        # Load the saved model
        loaded_model = tensorflow.keras.models.load_model('fpl_predictor.h5')

        # Get the new sample data
        new_sample = np.array([[arr[:6]]])
        new_sample = new_sample.reshape(-1, 6)

        # Scale the new sample data using the same scaler that was used to scale the training data
        scaler = StandardScaler()
        scaler.fit(data)
        new_sample = scaler.transform(new_sample)

        # Make predictions using the loaded model
        prediction = loaded_model.predict(new_sample)
       
       
       
        # data = np.loadtxt("training.csv", delimiter=",")
        
        # loaded_model = tensorflow.keras.models.load_model('fpl_predictor.h5')
        
        # new_sample = np.array([[arr[:6]]])
        # print(new_sample)
        # type(new_sample)
        # new_sample = new_sample.reshape(-1, 6)
        
        
        # # scaler = StandardScaler()
        # # scaler.fit(data)
        # # # Scale the new sample
        # # new_sample = scaler.transform(new_sample)
        # # prediction = loaded_model.predict(new_sample)
        # # Use the model to make a prediction
    


        # scaler_fit = StandardScaler()
        # scaler_fit.fit(data)
        
        # # Create a separate scaler for transforming the new sample
        # scaler_transform = StandardScaler()
        # # scaler_transform.mean_ = scaler_fit.mean_
        # # scaler_transform.var_ = scaler_fit.var_
        
        # # Scale the new sample
        # new_sample = scaler_transform.transform(new_sample)
        # prediction = loaded_model.predict(new_sample)

        print("Prediction:", prediction)
    
    
    
   
 # Connect to the database
conn = sqlite3.connect("fpl_players_db.sqlite")
cursor = conn.cursor()

    # Fetch data from the SQL table
cursor.execute("SELECT * from fpl_player_table")
players = cursor.fetchall()

    # Define the Kivy GUI
class Prediction(GridLayout, Screen):

    pass
   


class PlayerInfoLayout(GridLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Connect to the SQLite database and retrieve the data
        conn = sqlite3.connect("fpl_players_db.sqlite")
        cur = conn.cursor()
        cur.execute("SELECT * FROM fpl_player_stats_table")
        data = cur.fetchall()

        # Set the number of columns in the table
        self.cols = len(data[0])
        print(len(data[0]))
        # Loop through the data and add a label for each row
        for row in data:
            for value in row:
                label = Label(text=str(value), color=(0,1,0.52,1), size_hint_y=None, height=100)
                self.add_widget(label)


class PremierLeagueApp(App): #inherits from parent class App(kivy's class)
    '''Main class, through which screens are switched'''
    def build(self):
        
        
        screen_manager = ScreenManager()
        screen_manager.add_widget(AccountRegisterLayout(name='register'))
        screen_manager.add_widget(LoginLayout(name='login'))
        screen_manager.add_widget(MainMenu(name='menu'))
        screen_manager.add_widget(SearchBar(name='search_bar'))
        screen_manager.add_widget(PlayerInfoLayout(name='player_info'))
        # screen_manager.add_widget(DisplayResult(name='result_display'))
         # Create a scroll view widget
        # scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, 200),
        #                  scroll_y=1, do_scroll_x=0,
        #                  do_scroll_y=1, bar_width=10,
        #                  bar_color=(0.7, 0.7, 0.7, 1),
        #                  bar_inactive_color=(0.3, 0.3, 0.3, 1),
        #                  effect_cls="ScrollEffect")
        
        # # Create a table layout widget and add it to the scroll view
        # table = PlayerInfoLayout()
        # scroll_view.add_widget(table)
    
        
        
        account_exists = str(input("Do you have an account y/n: "))
        validInput = False
        while validInput == False:
            if account_exists == 'n':
                screen_manager.current = 'register'
                validInput = True
            
            
            elif account_exists == 'y':
                screen_manager.current = 'login'
                validInput = True
            else:
                account_exists = str(input("Do you have an account y/n: "))
                
            # print(training_model.make_prediction())
       
        return screen_manager
       



        



 

if __name__ == '__main__':
    PremierLeagueApp().run()


