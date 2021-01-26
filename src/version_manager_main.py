import sys, os
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

from updating import version_manager_module

from updating.screens import screen_updating, screen_more_details

class SBVersionManagerUI(App):

    def build(self):
        
        sm = ScreenManager(transition=NoTransition())
        vm = version_manager_module.VersionManager(sm)

        updating_screen = screen_updating.UpdatingScreenClass(name = 'updating', screen_manager = sm, version_manager = vm)
        more_details_screen = screen_more_details.MoreDetailsScreenClass(name = 'more_details', screen_manager = sm, version_manager = vm)
        sm.add_widget(updating_screen)
        sm.add_widget(more_details_screen)

        sm.current = 'updating'

        if sys.platform != 'win32' and sys.platform != 'darwin':
            vm.start_version_manager()

        return sm

if __name__ == '__main__':

    SBVersionManagerUI().run()