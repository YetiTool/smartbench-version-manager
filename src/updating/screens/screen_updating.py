'''
Created on 21st January 2020
Screen that shows user-friendly progress of updates, and any key error messages

@author: Letty
'''
import os, sys

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.clock import Clock

Builder.load_string("""

#:import hex kivy.utils.get_color_from_hex

<ScrollableBasicOutput>:
    scroll_y:0

    canvas.before:
        Color:
            rgba: hex('#f9f9f9ff')
        Rectangle:
            size: self.size
            pos: self.pos
    
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
        font_size: 20
        max_lines: 100
        color: hex('#333333ff')

<UpdatingScreenClass>

    user_friendly_output: user_friendly_output

    BoxLayout:
        height: dp(800)
        width: dp(480)
        canvas.before:
            Color: 
                rgba: hex('#f9f9f9ff')
            Rectangle: 
                size: self.size
                pos: self.pos

        BoxLayout:
            padding: 0
            spacing: 10
            orientation: "vertical"
            BoxLayout:
                padding: 0
                spacing: 0
                canvas:
                    Color:
                        rgba: hex('#1976d2ff')
                    Rectangle:
                        pos: self.pos
                        size: self.size
                Label:
                    size_hint: (None,None)
                    height: dp(60)
                    width: dp(800)
                    text: "Updating..."
                    color: hex('#f9f9f9ff')
                    font_size: 30
                    halign: "center"
                    valign: "bottom"
                    markup: True

            BoxLayout:
                size_hint: (None,None)
                width: dp(780)
                height: dp(340)
                padding: 10
                spacing: 0
                orientation: 'horizontal'

                ScrollableBasicOutput:
                    id: user_friendly_output

            BoxLayout:
                size_hint: (None,None)
                width: dp(780)
                height: dp(60)
                padding: [300, 20]
                spacing: 0
                orientation: 'horizontal'

                Button:
                    canvas.before:
                        Color:
                            rgba: hex('#1976d2ff')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                    text: 'Check Details'
                    color: hex('#f9f9f9ff')
                    on_press: root.check_details()



""")

class ScrollableBasicOutput(ScrollView):
    text = StringProperty('')

class UpdatingScreenClass(Screen):

    basic_buffer = ['Starting update...']

    def __init__(self, **kwargs):

        super(UpdatingScreenClass, self).__init__(**kwargs)
        self.sm = kwargs['screen_manager']
        self.vm = kwargs['version_manager']

        # Clock.schedule_interval(self.update_user_friendly_display, 2) 

    def on_enter(self):
        if sys.platform != 'win32' and sys.platform != 'darwin':
            Clock.schedule_once(lambda dt: self.vm.standard_update(), 5)

    def add_to_user_friendly_buffer(self, message):

        print(str(message))
        self.basic_buffer.append(str(message))

    # def update_user_friendly_display(self, dt):
        self.user_friendly_output.text = '\n'.join(self.basic_buffer)
        if len(self.basic_buffer) > 100:
            del self.basic_buffer[0:len(self.basic_buffer)-100]

    def check_details(self):
        self.sm.current = 'more_details'





