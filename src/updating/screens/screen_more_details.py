'''
Created on 21st January 2020
Screen that shows user-friendly progress of updates, and any key error messages

@author: Letty
'''
import os, sys

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, DictProperty
from kivy.clock import Clock
from kivy.graphics import RoundedRectangle, Color
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label

Builder.load_string("""

#:import hex kivy.utils.get_color_from_hex

<ScrollableVerboseOutput>:
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

<ButtonMWithCanvas>

    canvas.before:
        Color:
            rgba: hex('#1976d2ff')
        RoundedRectangle:
            pos: self.pos
            size: self.size

<MoreDetailsScreenClass>

    # verbose_ouput: verbose_ouput
    update_error_log: update_error_log

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
                    text: "More Details"
                    color: hex('#f9f9f9ff')
                    font_size: 30
                    halign: "center"
                    valign: "bottom"
                    markup: True

            BoxLayout:
                size_hint: (None,None)
                width: dp(780)
                height: dp(320)
                padding: 20
                spacing: 0
                orientation: 'horizontal'

                # ScrollableVerboseOutput:
                #     id: verbose_ouput


                RstDocument:
                    id: update_error_log
                    background_color: hex('#f9f9f9ff')
                    base_font_size: 26
                    underline_color: '333333'
                    colors: root.color_dict
                    size: (self.size - 20)
                    pos: self.pos
                    do_scroll_x: True
                    scroll_x: 1
                    do_scroll_y: True
                    scroll_type: ['content']

            BoxLayout:
                size_hint: (None,None)
                width: dp(780)
                height: dp(80)
                padding: [300, 10]
                spacing: 0
                orientation: 'horizontal'

                ButtonMWithCanvas
                    text: 'Back to basic screen'
                    color: hex('#f9f9f9ff')
                    on_press: root.go_back()

""")

class ScrollableVerboseOutput(ScrollView):
    text = StringProperty('')

class ButtonMWithCanvas(ButtonBehavior, Label):
    text = StringProperty('')

class MoreDetailsScreenClass(Screen):

    verbose_buffer = ['Starting update...']
    color_dict = DictProperty({
                    'background': 'f9f9f9ff',
                    'link': 'ce5c00ff',
                    'paragraph': '333333ff',
                    'title': '333333ff',
                    'bullet': 'f9f9f9ff'})

    def __init__(self, **kwargs):

        super(MoreDetailsScreenClass, self).__init__(**kwargs)
        self.sm = kwargs['screen_manager']
        self.vm = kwargs['version_manager']

        # Clock.schedule_interval(self.update_user_friendly_display, 2)

    def on_pre_enter(self):
        self.show_rst()

    # def add_to_verbose_buffer(self, message):
    #     self.verbose_buffer.append(message)

    # def update_user_friendly_display(self, dt):
    #     self.verbose_ouput.text = '\n'.join(self.verbose_buffer)
    #     if len(self.verbose_buffer) > 60:
    #         del self.verbose_buffer[0:len(self.verbose_buffer)-60]

    def show_rst(self):
        self.update_error_log.source = './update_error_log.txt'


    def go_back(self):
        self.sm.current = 'updating'




