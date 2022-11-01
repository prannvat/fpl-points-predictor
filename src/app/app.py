

import kivy
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
kivy.require("2.1.0")
from typing import Tuple, Dict

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


class AppLabel(Label):
    def __init__(self):
        pass


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