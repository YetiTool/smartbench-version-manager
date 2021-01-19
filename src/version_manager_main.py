# import sys, os
# from datetime import datetime
# import os.path
# from os import path

from kivy.config import Config
from kivy.clock import Clock
Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'maxfps', '60')
Config.set('kivy', 'KIVY_CLOCK', 'interrupt')
Config.write()

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window

from updating import version_manager

class SBVersionManagerUI(App):

    def build(self):
g
        log("Starting App:")
        
        # Establish screens
        sm = ScreenManager(transition=NoTransition())

        vm = version_manager.VersionManager(sm)

        return sm

if __name__ == '__main__':

    SBVersionManagerUI().run()