
# from kivy.app import App
# from kivy.uix.button import Button
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.popup import Popup
# from kivy.uix.textinput import TextInput
# from kivy.uix.label import Label
# import openpyxl

# class MyApp(App):
#     def build(self):
#         layout = BoxLayout(orientation='vertical')

#         # create the "PLAYERS" button
#         players_button = Button(text='PLAYERS')
#         players_button.bind(on_press=self.open_players_file)
#         layout.add_widget(players_button)

#         # create the "SEARCH" button
#         search_button = Button(text='SEARCH')
#         search_button.bind(on_press=self.open_search_bar)
#         layout.add_widget(search_button)

#         return layout

#     def open_players_file(self, instance):
#         try:
#             wb = openpyxl.load_workbook('player_points_weekly.xlsx')
#             sheet = wb.active
#             data = [[sheet.cell(row=row, column=col).value for col in range(1, sheet.max_column + 1)] for row in range(1, sheet.max_row + 1)]
#             print(data)
#         except FileNotFoundError:
#             print("File not found")

#     def open_search_bar(self, instance):
#         search_popup = Popup(title='SEARCH', content=TextInput(hint_text='Enter player name'), size_hint=(None, None), size=(400, 400))
#         search_popup.open()

# if __name__ == "__main__":
#     MyApp().run()






# 
import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
import psycopg2
from typing import Tuple, Dict

class PremierLeagueApp(App):
        



    def build(self):
            return LoginScreen()



class RGBcolour:
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


class LoginScreen(GridLayout,PremierLeagueApp):
    '''A sub class of the main parent Class called PremierLeagueApp and a python class called Gridlayout'''
    
    def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.cols = 2
            self.add_widget(Button(text='Username'))
            self.username = TextInput(multiline=False)
            self.add_widget(self.username)
            self.add_widget(Button(text='Password'))
            self.password = TextInput(multiline=False, password=True)
            self.add_widget(self.password)
            self.submit = Button(text='Submit')
            self.submit.bind(on_press=self.submit_form)
            self.add_widget(self.submit)

    def submit_form(self, instance):
            # Get the input values
            username = self.username.text
            password = self.password.text

            # Connect to the database
            conn = psycopg2.connect(
                host="Prannvats-MacBook-Pro.local",
                database="userLogin",
                user="username",
                password="password"  
            )
 
            # Create a cursor
            cur = conn.cursor()

            # Insert the data into the table
            cur.execute("""
                INSERT INTO users (username, password)
                VALUES (%s, %s)
            """, (username, password))

            # Commit the changes
            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()

        
    def menu(self): 
            '''Allows users to choose between options in main menu''' 
            layout = GridLayout(cols=3, spacing=10, padding=10)
            layout.add_widget(Image(source='premlogo.png'))
            
            search_button = Button(text='Search')
            search_button.bind(on_press=self.open_search_screen)
            layout.add_widget(search_button)
            
            players_info_button = Button(text='Players Information')
            layout.add_widget(players_info_button)
            
            self.screen_manager = ScreenManager()
            self.screen_manager.add_widget(Screen(name='main'))
            self.screen_manager.add_widget(Screen(name='search'))
            
            layout.add_widget(self.screen_manager)
            
            return layout
        
    def open_search_screen(self, instance):
            self.screen_manager.current = 'search'
            search_screen = self.screen_manager.get_screen('search')
            search_bar = TextInput(text='Enter your search')
            
            search_screen.add_widget(search_bar)
        
    def search_players(self, playerName):
            pass



if __name__ == '__main__':
    PremierLeagueApp().run()
    
    