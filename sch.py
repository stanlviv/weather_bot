import time
import datetime
import telebot
import pyowm
from pyowm import timeutils
import random
import schedule
import pickle

bot = telebot.TeleBot("1005149662:AAHV4mWgeo5qhHUxZXtxgI2L-hq4_yAMR7E")
owm = pyowm.OWM("3f152ae62a9f057cdb1a9851e3b676cd", language='ua')

class Weather:
    def __init__(self, city):
        self.city = city
    
    def show_weather(self):
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
            result = f"{place_status.capitalize()} у місті {point_name}.\nТемпература: {place_temp['temp']}℃\nВологість: {place_hum}%\nТиск: {place_pressure['press']} hPa\nШвидкість вітру: {place_wind['speed']} м/с"
            return result
        except Exception:
            return f"Вкажіть вірну назву!"

    def show_forecast(self):
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
            return f"{rain} {sun}\n9:00 - {temp9}℃\n12:00 - {temp12}℃\n18:00 - {temp18}℃\n21:00 - {temp21}℃"
        except Exception:
            return f"Вочевидь, такого міста немає :(\nСпробуйте ще раз!"

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
'CAACAgIAAxkBAAL1z17uaODWTQYSfi3FueJDUtmgO3pSAAInAgAC8QSXE6Hq3A1zBpIPGgQ',]

lviv = Weather('Lviv')

def weather_morning():
    with open('ids.txt', 'rb') as i:
        ids = pickle.load(i)
    weather = lviv.show_weather()
    for k, v in ids.items():
        bot.send_message(k, f"{tm()}, {v}!")
        bot.send_message(k, weather)
        bot.send_sticker(k, random.choice(stickers))
        time.sleep(2)

def weather_evening():
    with open('ids.txt', 'rb') as i:
        ids = pickle.load(i)
    forecast = lviv.show_forecast()
    for k, v in ids.items():
        bot.send_message(k, f"{tm()}, {v}!")
        bot.send_message(k, 'Погода на завтра:')
        bot.send_message(k, forecast)
        bot.send_sticker(k, random.choice(stickers))
        time.sleep(2)

schedule.every().day.at('08:00').do(weather_morning)
schedule.every().day.at('17:00').do(weather_evening)

while True:
    schedule.run_pending()
    time.sleep(20)

bot.polling()
