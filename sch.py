import time
import datetime
import telebot
import pyowm
from pyowm import timeutils
import random
import schedule
import mysql.connector
from mysql.connector import Error
from bs4 import BeautifulSoup
import requests


bot = telebot.TeleBot("1005149662:AAHV4mWgeo5qhHUxZXtxgI2L-hq4_yAMR7E")
owm = pyowm.OWM("3f152ae62a9f057cdb1a9851e3b676cd", language='ua')

class Weather:
    def __init__(self, city):
        self.city = city
    
    def show_weather(self):
        i = 0
        while i<=5:
            try:
                point = owm.weather_at_place(self.city)
                p_n = point.get_location()
                point_name = p_n.get_name()
                place = point.get_weather()
                place_temp = place.get_temperature('celsius')
                place_hum = place.get_humidity()
                place_wind = place.get_wind()
                place_status = place.get_detailed_status()
                place_pressure = place.get_pressure()
                result = f"*{place_status.capitalize()} у місті {point_name}.*\nТемпература: {place_temp['temp']}℃\nВологість: {place_hum}%\nТиск: {place_pressure['press']} hPa\nШвидкість вітру: {place_wind['speed']} м/с"
                return result
            except Exception:
                i+=1
                time.sleep(2)
                continue

    def show_forecast(self):
        i = 0
        while i<=5:
            try:
                place = owm.three_hours_forecast(self.city)
                tomorrow9 = timeutils.tomorrow(9)
                tomorrow12 = timeutils.tomorrow(12)
                tomorrow18 = timeutils.tomorrow(18)
                tomorrow21 = timeutils.tomorrow(21)
                t9 = place.get_weather_at(tomorrow9)
                t12 = place.get_weather_at(tomorrow12)
                t18 = place.get_weather_at(tomorrow18)
                t21 = place.get_weather_at(tomorrow21)
                temp9 = t9.get_temperature('celsius')['temp']
                temp12 = t12.get_temperature('celsius')['temp']
                temp18 = t18.get_temperature('celsius')['temp']
                temp21 = t21.get_temperature('celsius')['temp']
                if place.will_be_rainy_at(tomorrow12):
                    rain = 'Дощитиме'
                else: rain = 'Буде сухо'
                if place.will_be_sunny_at(tomorrow12):
                    sun = 'та сонячно.'
                else: sun = 'та хмарно.'
                return f"*{rain} {sun}*\n9:00 - {temp9}℃\n12:00 - {temp12}℃\n18:00 - {temp18}℃\n21:00 - {temp21}℃"
            except Exception:
                i+=1
                time.sleep(2)
                continue

def tm():
    now = datetime.datetime.now()
    hour = now.hour+3
    if hour >= 6 and hour <12:
        daytime = 'Доброго ранку'
    elif hour >=12 and hour <18:
        daytime = 'Доброго дня'
    elif hour >=18 and hour <22:
        daytime = 'Доброго вечора'
    else:
        daytime = 'Доброї ночі'
    greeting = f'{daytime}'
    return greeting

stickers = ['CAACAgIAAxkBAALrvV7fu3s0_zfs8xasvoJQGKsHrJBhAAJoAgAC8QSXE1UbOzpI8oUuGgQ',
'CAACAgIAAxkBAALrv17fu6XUVxQlZmdTxJv2WTNT6BysAAKCAgAC8QSXE8_dt4mE8z_cGgQ',
'CAACAgIAAxkBAALrwV7fu9_964BHMVkmSFabog0eiPbxAAJPAgAC8QSXE84NMf5xGmBZGgQ',
'CAACAgIAAxkBAALrw17fvAdLcRKQvY1CoC6btQayK37WAAI5AgAC8QSXE7k1LhusXmHPGgQ',
'CAACAgIAAxkBAALrxV7fvDUvuxKlU2pPJBgNF4IzdukQAAIrAgAC8QSXE4M9zmlXSH6dGgQ',
'CAACAgIAAxkBAALryV7fvHFaN8R069vc2OeSN_4Zt2CWAAJuAgAC8QSXE1uHZ4K1F_AWGgQ',
'CAACAgIAAxkBAALry17fvIgqkVvPpXRE5UWG2BJd1_MbAAJ3AgAC8QSXE-BntMxQcAyzGgQ',
'CAACAgIAAxkBAALrzV7fvJ4VzgPvlEmYuKdE-nJ8fCQpAAJVAgAC8QSXE8iuk9VIU6KWGgQ',
'CAACAgIAAxkBAALr3F7fznlsE8F7StUHjz_0WTmHkapfAAJnAgAC8QSXE21OmrwcOsfrGgQ',
'CAACAgIAAxkBAAL1z17uaODWTQYSfi3FueJDUtmgO3pSAAInAgAC8QSXE6Hq3A1zBpIPGgQ',
'CAACAgIAAxkBAAL-m1782rf5emngDVDe5FCwNPJUznx2AAIGAwACebI-BPrttgtywXMcGgQ',
'CAACAgIAAxkBAAL-nV782w7RDgGda041vQoWtjn8WiBiAAJoAQACebI-BHXQ81KPbYnsGgQ',
'CAACAgIAAxkBAAL-oV7820ejsvzvlEkCXBSxSBGBNWnRAAItAQACebI-BHTO6eipasQwGgQ',
'CAACAgIAAxkBAAL-o1783B8Te1f0AnHbVu3BRFGv_K7FAAJbAQACebI-BP6bJs7UysFTGgQ',
'CAACAgIAAxkBAAL-pV783DNY52bPNnLX_62I_dMXT_KIAAJdAQACebI-BD2jPp-5n9AIGgQ',
'CAACAgIAAxkBAAEBB91fCdEAARYcsBT0icsm7s0PW7_-AqcAAhUAA567YRKpmAABygABiT4ZGgQ',
'CAACAgIAAxkBAAEBB99fCdGTUCSqZ_GvIHz4LzOfauZTtwACBwADbjP4EUCSkEfkNiqnGgQ',]

def holidays_names():
    html_holidays = requests.get('https://calenday.org/uk/holidays/')
    html_days = requests.get('https://calenday.org/uk/names/')
    if html_days.status_code and html_holidays.status_code == 200:
        soup_n = BeautifulSoup(html_days.text, 'html.parser')
        soup_h = BeautifulSoup(html_holidays.text, 'html.parser')
        items_h = soup_h.find_all('h4', class_='media-heading')
        items_n = soup_n.find_all('tr', valign="top")
        holidays = []
        names = []
        for item in items_h:
            holidays.append(item.find('a').get_text())
        for item in items_n:
            names.append(item.find('a').get_text())
        return holidays, names
    else:
        return 'Error'

def get_db():
    try:
        connection = mysql.connector.connect(host='eu-cdbr-west-03.cleardb.net',database='heroku_827e33f01765a32',user='b9aaef9756aadc',password='4817bc17')
        sql_select_Query = "SELECT * FROM IDs"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        return records
    except Error as error:
        return f"Упс, помилка! {error}"

def weather_morning():
    records = get_db()
    ids = {}
    for x in records:
        ids.update({x[0]: x[1]})
    weather = Weather('Lviv').show_weather()
    result = holidays_names()
    count = 0
    total = len(ids.items())
    not_delivered = []
    for k, v in ids.items():
        try:
            bot.send_message(k, f"{tm()}, {v}!")
            bot.send_message(k, weather, parse_mode='Markdown')
            bot.send_message(k, f"*Сьогодні відзначають:*\n{result[0]}\n*Іменини:*\n{result[1]}", parse_mode='Markdown')
            count+=1
            time.sleep(1)
        except Exception:
            not_delivered.append(v)
    bot.send_message(454706315, f"*delivered:* {count}/{total}\n*not delivered:* {len(not_delivered)} {not_delivered}", parse_mode='Markdown')

def weather_evening():
    records = get_db()
    ids = {}
    for x in records:
        ids.update({x[0]: x[1]})
    forecast = Weather('Lviv').show_forecast()
    count = 0
    total = len(ids.items())
    not_delivered = []
    for k, v in ids.items():
        try:
            bot.send_message(k, f"{tm()}, {v}!\nПогода на завтра:")
            bot.send_message(k, forecast, parse_mode='Markdown')
            bot.send_sticker(k, random.choice(stickers))
            count+=1
            time.sleep(1)
        except Exception:
            not_delivered.append(v)
    bot.send_message(454706315, f"*delivered:* {count}/{total}\n*not delivered:* {len(not_delivered)} {not_delivered}", parse_mode='Markdown')

schedule.every().day.at('07:00').do(weather_morning)
schedule.every().day.at('17:00').do(weather_evening)

while True:
    schedule.run_pending()
    time.sleep(30)

bot.polling()
