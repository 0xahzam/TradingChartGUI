import os
from pathlib import Path
from kivy.config import Config

icon_img = 'icons8-increase-96.ico'

cur_file_path = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
Config.set('kivy', 'window_icon', f'{cur_file_path}/{icon_img}')


from email import message
from logging import root
import mplfinance as mpf
import mysql.connector as con
import numpy
import pandas as pd
import webcolors
import yfinance as yf
import time

from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.screenmanager import FadeTransition, ScreenManager, NoTransition
from kivy.config import Config
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.behaviors.backgroundcolor_behavior import BackgroundColorBehavior

from current_price import *
from function import *
from finding_stock import *

def config_data():
    try:
        t_passw = temp_pass()
        passw = per_pass()
        mycon = con.connect(
            host="localhost", user="root",
            passwd=t_passw if t_passw != '' else passw, database="project"
        )
        cur = mycon.cursor()
        cur.execute("""SELECT * FROM config""")
        out = cur.fetchall()
        dictt = {key:val for key,val in out}
        return dictt
    except:
        pass

def config_table(passw):
    mycon = con.connect(host="localhost", user="root", passwd=passw, database="project")
    cur = mycon.cursor()
    cur.execute("SHOW TABLES LIKE 'config'")
    result = cur.fetchone()
    if not result:
        cur.execute('CREATE TABLE config (Properties varchar(50), def_to varchar(50))')
        t_passw = temp_pass()
        passw = per_pass()
        prop = ['mode','accent','plot_type','plot_color','volume']
        values = ['Light','Gray','Candle','Yahoo','True']
        for i in range(5):
            cur.execute(f"INSERT INTO config (Properties, def_to) VALUES ('{prop[i]}','{values[i]}')")
            cur.execute('COMMIT')
        print('added defaults')

def check_for_property(property, passw):
    mycon = con.connect(host="localhost", user="root", passwd=passw, database='project')
    cur = mycon.cursor()
    cur.execute('SELECT Properties from config')
    properties = cur.fetchall()
    presence = False
    for tuplee in properties:
        if property in tuplee:
            presence = True
    return presence

def add_data(passw, property, valuee):
    config_table(passw)
    mycon = con.connect(host="localhost", user="root", passwd=passw, database='project')
    cur = mycon.cursor()
    in_table = check_for_property(property, passw)
    if in_table == True:
        cur.execute(f'UPDATE config SET def_to = ("{valuee}") WHERE Properties = "{property}"')
    else:
        cur.execute(f"INSERT INTO config (Properties, def_to) VALUES ('{property}','{valuee}')")
    cur.execute('COMMIT')

def per_pass():
    p_pass = ''
    if Path(f'{cur_file_path}/password.txt').is_file():
        with open(f'{cur_file_path}/password.txt','r') as file:
            p_pass = file.readline()
    return p_pass

def temp_pass():
    t_passw = ''
    if Path(f'{cur_file_path}/temp_password.txt').is_file():
        with open(f'{cur_file_path}/temp_password.txt','r') as file:
            t_passw = file.readline()
    return t_passw

def save_temp_sql(passw):
    config_table(passw)
    mycon = con.connect(host="localhost", user="root", passwd=passw, database='project')
    cur = mycon.cursor()
    
    in_table = check_for_property('temp_passw', passw)
    if in_table == True:
        cur.execute(f'UPDATE config SET def_to = ("{passw}") WHERE Properties = "temp_passw"')
    else:
        cur.execute(f"INSERT INTO config (Properties, def_to) VALUES ('temp_passw','{passw}')")
    print('saved temp password')
    cur.execute('COMMIT')

def colour():
    dictt = config_data()
    try:
        if dictt['mode'] == 'Dark':
            i_color = '#FFFFFF'
        else:
            i_color = '#000000'
    except:
        i_color = '#000000'
    return i_color

update_prices(symbol_list)

symbol_list = [
    "AAPL","TSLA","ADBE","GOOGL","AMZN","SONY","SPOT","MSFT","FB","KO","SNAP","GME",
    "MRNA","NFLX","QCOM","SQ","COIN","INFY","BA","ZM"
]

company_name_list = [
    "Apple Inc.","Tesla Inc.","Adobe Inc.", "Alphabet Inc.","Amazon, Inc.",
    "Sony Group Corporation","Spotify Technology S.A.","Microsoft Corporation","Facebook,Inc.",
    "The Coca-Cola Company","Snap Inc.","Gamestop Corporation","Moderna, Inc.","Netflix, Inc.","Qualcomm Incorporated",
    "Square, Inc.","Coinbase Global, Inc.","Infosys Ltd","Boeing Company (The)","Zoom video communications, Inc."
]

icon_list=[
    'apple','bolt','adobe','google','amazon','alpha-s','spotify',"microsoft",
    'facebook','bottle-soda-classic','snapchat','gamepad-variant','','netflix','alpha-q-circle','numeric-0-box-outline',
    'alpha-c-circle','','airplane-takeoff','video-box'
]

hexxx = [
    colour(),'#D0D0D0','#CC0000','#4081EC','#F48944',colour(),'#04C149','#68C6FF','#3053FF','#990000','#EECB4A','#CD2E2E','','#E50914',
    '#3053FF',colour(),'#154FE9','','#0037A2','#519CFE'
]

def torgb(hexx):
    deci = ''
    try:
        deci = list(numpy.array(webcolors.hex_to_rgb(str(hexx)))/255)
    except:
        pass
    return deci

class PassScreen(MDScreen):

    def show_dialogb(self):
        close_button = MDFlatButton(
            text = 'Close',
            font_size = 15,
            on_release = self.close_dialogb,
            opacity = 0.5
        )
        self.dialogb = MDDialog(
            title = "SQL password",
            auto_dismiss = False,
            type = "custom",
            #size_hint = (0.7, 1),
            content_cls = BoxInDialog(),
            buttons = [close_button]
            )
        self.dialogb.open()

    def close_dialogb(self, obj):
        self.dialogb.dismiss()
        self.change()

    def change(self):
        self.manager.current = 'main'

class BoxInDialog(MDBoxLayout):
    
    def check_connect(self, passww):
        try:
            import mysql.connector as con
            mycon = con.connect(host=" localhost",
                            user="root", 
                            passwd=passww)

            if mycon.is_connected():
                self.ids.passww.helper_text = 'Connected'
                return True
        except:
            self.ids.passww.helper_text = 'Wrong Password'
            return False

    def eye_but_press(self):
        cur_icon = self.ids.eye_but.icon
        if cur_icon == 'eye-off':
            self.ids.eye_but.icon = 'eye'
            self.ids.passww.password = False
        else:
            self.ids.eye_but.icon = 'eye-off'
            self.ids.passww.password = True

    def go_but_press(self, password, state_checkbox):
        if state_checkbox == 'down':
            self.save_pass()
            config_table(self.ids.passww.text)
            self.ids.passww.helper_text = 'Connected & Saved'
        else:
            config_table(self.ids.passww.text)
            save_temp_sql(self.ids.passww.text)
            with open(f'{cur_file_path}/temp_password.txt', 'w') as file:
                file.writelines(self.ids.passww.text)

    def save_pass(self):
        with open(f'{cur_file_path}/password.txt', 'w') as file:
            file.writelines(self.ids.passww.text)

class MainScreen(MDScreen):
    settingss = None
    def Pressed(self):
        textt = self.ids.symbol_field.text.upper()
        if textt.lower() == 'credits':
            self.creditss()
        elif textt.isalpha() == True:
            if yf.Ticker(textt).info['regularMarketPrice'] == None:
                self.ids.symbol_field.error = True
                self.ids.symbol_field.helper_text = 'Incorrect Stock Name!!'
            else:
                timeperiod = '1y'
                dictt = config_data()
                t_passw = temp_pass()
                passw = per_pass()
                self.ids.symbol_field.error = False
                onpress(t_passw if t_passw != '' else passw,textt, timeperiod, dictt)
        else:
            self.ids.symbol_field.error = True
            self.ids.symbol_field.helper_text = 'Only Letters allowed!!'

    def creditss(self):
        self.credits = MDDialog(
            title = 'Credits',
            auto_dismiss = True,
            type = 'custom',
            content_cls = credits_content()
        )
        self.credits.open()

    def settings(self):
        close_button = MDFlatButton(
            text = 'Close',
            font_size = 15,
            on_release = self.close_settings,
            opacity = 0.5
        )
        save_button = MDFlatButton(
            text = 'Save Changes',
            font_size = 15,
            on_release = self.savee,
            opacity = 0.5
        )
        if not self.settingss:
            self.settingss = MDDialog(
                        title = 'Settings',
                        auto_dismiss = False,
                        type = 'custom',
                        content_cls = Settings_Dialog(),
                        size_hint_x =  None,
                        width =  dp(400),
                        buttons = [save_button, close_button]
            )
        self.settingss.open()

    def close_settings(self, obj):
        self.settingss.dismiss()
    
    def savee(self, obj):
        setd = Settings_Dialog()
        print('Saving changes.')
        setd.save_changes()
        self.settingss.dismiss()
        time.sleep(2)
        MDApp.get_running_app().restart()


class credits_content(MDBoxLayout):
    pass

class Settings_Dialog(MDGridLayout):
    colorr = ''
    typee = ''
    accent = ''
    volume = ''
    mode = ''
    dictt = config_data()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        typee = ['Candle', 'Line', 'Renko', 'Pnf']
        type_g = [
                {
                    'text': f'{typee[i]}',
                    "viewclass": "OneLineListItem",
                    'font_size': 10,
                    'on_release': lambda x = f'{typee[i]}':self.set_item_type(x),
                    "font_style": "Caption",
                }
            for i in range(len(typee))
        ]
        colorr = [
            'Binance', 'Blueskies', 'Brasil', 'Charles', 'Checkers', 'Classic', 'Default',
            'Ibd', 'Kenan', 'Mike', 'Nightclouds', 'Sas', 'Starsandstripes', 'Yahoo'
        ]
        color_g = [
                {
                    "viewclass": "OneLineListItem",
                    'text': f'{colorr[i]}',
                    'font_size': 10,
                    'on_release': lambda x = f'{colorr[i]}':self.set_item_color(x),
                    "font_style": "Caption",
                }
            for i in range(len(colorr))
        ]
        accent = [
            'Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue',
            'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Lime',
            'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray'
        ]
        accent_items = [
                {
                    'text': f'{accent[i]}',
                    'viewclass': 'OneLineListItem',
                    'font_size': 10,
                    'on_release': lambda x = f'{accent[i]}': self.set_item_accent(x),
                    "font_style": "Caption",
                }
            for i in range(len(accent))
        ]

        self.accent_color = MDDropdownMenu(
            caller = self.ids.accent_c,
            items = accent_items,
            width_mult = 2,
            max_height = 200
        )
        self.accent_color.bind()

        self.plot_type = MDDropdownMenu(
            caller = self.ids.g_type,
            items = type_g,
            width_mult=2,
            max_height = 200
        )
        self.plot_type.bind()

        self.plot_color = MDDropdownMenu(
            caller = self.ids.g_color,
            items = color_g,
            width_mult=2,
            max_height = 200
        )
        self.plot_color.bind()
    
    def set_item_accent(self, text_item):
        Settings_Dialog.accent = text_item
        self.ids.accent_c.set_item(text_item)
        self.ids.accent_c.current_item = text_item
        self.accent_color.dismiss()

    def set_item_type(self, text_item):
        Settings_Dialog.typee = text_item
        self.ids.g_type.set_item(text_item)
        self.ids.g_type.current_item = text_item
        self.plot_type.dismiss()

    def set_item_color(self, text_item):
        Settings_Dialog.colorr = text_item
        self.ids.g_color.set_item(text_item)
        self.ids.g_color.current_item = text_item
        self.plot_color.dismiss()
    
    def save_vol(self, textt):
        Settings_Dialog.volume = f'{textt}'

    def save_mode(self, textt):
        if textt == 'down':
            textt = 'Dark'
        else:
            textt = 'Light'
        Settings_Dialog.mode = textt

    def dict_data(self):
        dataa = config_data()
        return dataa

    def save_changes(self):
        t_passw = temp_pass()
        passw = per_pass()
        prop = ['mode','accent','plot_type','plot_color','volume']
        values = [
            Settings_Dialog.mode,
            Settings_Dialog.accent,
            Settings_Dialog.typee,
            Settings_Dialog.colorr,
            Settings_Dialog.volume
        ]
        for i in range(5):
            if values[i] == '':
                pass
            else:
                add_data(t_passw if t_passw != '' else passw, prop[i], values[i])

class Table(MDScreen):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        prices = price_list()
        col_d=[
            ("No.", dp(10)),
            ("Symbol", dp(20)),
            ("Company Name", dp(70)),
            ("Current Price($)", dp(30))
        ]
        row_d=[
            (str(i+1), symbol_list[i], (icon_list[i], (torgb(hexxx[i]) if torgb(hexxx[i]) != '' else None), company_name_list[i]), f'${prices[i]}') for i in range(20)
        ]
        data_tables = MDDataTable(
            pos_hint={"center_x": .5, "center_y": .5},
            size_hint=(0.9, 0.9),
            elevation=15,
            #use_pagination=True,
            rows_num=20,
            column_data=col_d,
            row_data=row_d)
        data_tables.bind(on_row_press= self.on_row_press)
        self.add_widget(data_tables)

    def on_row_press(self, instance_table, instance_row):
        dictt = config_data()
        click = instance_row.text
        x , position = type_col(click)
        passw = per_pass()
        t_passw = temp_pass()
        onpress(t_passw if t_passw != '' else passw, symbol_list[position], '1y', dictt)

sm = ScreenManager()
sm.add_widget(PassScreen(name='pass'))
sm.add_widget(MainScreen(name='main'))    

class StonkkApp(MDApp):
    icon = f'{cur_file_path}/{icon_img}'

    def build(self):
        dictt = config_data()
        screen = Builder.load_file('layout.kv')
        self.theme_cls.theme_style = dictt['mode'] if dictt != None else 'Light'
        self.theme_cls.primary_palette = dictt['accent'] if dictt != None else 'Gray'
        return screen
    
    def pwd_present(obj):
        my_file = Path(f'{cur_file_path}/password.txt')
        presentt = False

        def check_connect(passww):
            try:
                import mysql.connector as con
                mycon = con.connect(
                    host=" localhost",
                    user="root", 
                    passwd=passww
                )
                if mycon.is_connected():
                    connect = True
            except:
                connect = False
            return connect

        if my_file.is_file():
            with open(f'{cur_file_path}/password.txt','r') as file:
                passs = file.readline()
                connect = check_connect(passs)
                if connect == True:
                    presentt = True
        return presentt
    
    def restart(self):
        Builder.unload_file('layout.kv')
        self.root.clear_widgets()
        self.stop()
        return StonkkApp().run()

StonkkApp().run()

def del_temp_sql():
    passw = temp_pass()
    mycon = con.connect(host="localhost", user="root", passwd=passw, database='project')
    cur = mycon.cursor()
    cur.execute(f'DELETE FROM config WHERE Properties = "temp_passw";')
    print('Deleted temp_passw')
    cur.execute('COMMIT')

if Path(f'{cur_file_path}/temp_password.txt').is_file():
    del_temp_sql()
    os.remove(f'{cur_file_path}/temp_password.txt')