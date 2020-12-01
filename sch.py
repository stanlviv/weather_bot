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
    def __init__(self, city=None, latitude=None, longitude=None):
        self.city = city
        self.latitude = latitude
        self.longitude = longitude

    def show_weather(self):
        i = 0
        while i<=2:
            if self.latitude != None:
                try:
                    point = owm.weather_at_coords(self.latitude, self.longitude)
                    p_n = point.get_location()
                    point_name = p_n.get_name()
                    place = point.get_weather()
                    place_temp = place.get_temperature('celsius')
                    place_hum = place.get_humidity()
                    place_wind = place.get_wind()
                    place_status = place.get_detailed_status()
                    place_pressure = place.get_pressure()
                    return f"*{place_status.capitalize()} у місті {point_name}.*\nТемпература: {place_temp['temp']:.1f}℃\nВологість: {place_hum}%\nТиск: {place_pressure['press']} hPa\nШвидкість вітру: {place_wind['speed']} м/с"
                except Exception:
                    i+=1
                    time.sleep(2)
                    continue
            else:
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
                    return f"*{place_status.capitalize()} у місті {point_name}.*\nТемпература: {place_temp['temp']:.1f}℃\nВологість: {place_hum}%\nТиск: {place_pressure['press']} hPa\nШвидкість вітру: {place_wind['speed']} м/с"
                except Exception:
                    i+=1
                    time.sleep(2)
                    continue

    def show_forecast(self):
        i = 0
        while i<=2:
            if self.latitude != None:
                try:
                    place = owm.three_hours_forecast_at_coords(self.latitude, self.longitude)
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
                    return f"*{rain} {sun}*\n9:00 - {temp9:.1f}℃\n12:00 - {temp12:.1f}℃\n18:00 - {temp18:.1f}℃\n21:00 - {temp21:.1f}℃"
                except Exception:
                    i+=1
                    time.sleep(2)
                    continue
            else:
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
                    return f"*{rain} {sun}*\n9:00 - {temp9:.1f}℃\n12:00 - {temp12:.1f}℃\n18:00 - {temp18:.1f}℃\n21:00 - {temp21:.1f}℃"
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

podia_stickers = [
    'CAACAgIAAxkBAAEBCzlfDC_6peLigfCi7-AJPi-6z2V4cAACKQIAAvEElxMIApYlP1BZzxoE',
    'CAACAgIAAxkBAAEBCztfDDAQhe6KHd_oN2p1iZODqQse1AACJwIAAvEElxOh6twNcwaSDxoE',
    'CAACAgIAAxkBAAEBCz1fDDAm2PYzTfGfKIFvZlEz5gYEeAACKwIAAvEElxODPc5pV0h-nRoE',
    'CAACAgIAAxkBAAEBCz9fDDBCj716QBUnTKlicB0NukcuoQACOQIAAvEElxO5NS4brF5hzxoE',
    'CAACAgIAAxkBAAEBC0FfDDCJB_4uNdPNyWbldL0oFXu2EAACTwIAAvEElxPODTH-cRpgWRoE',
    'CAACAgIAAxkBAAEBC0NfDDC3fzfu0mDmUmnP6I9u3H5shQACaAIAAvEElxNVGzs6SPKFLhoE',
    'CAACAgIAAxkBAAEBC0VfDDDDC63NgG3PUMORtd0WygxKawACagIAAvEElxO_DQMuctHXshoE',
    'CAACAgIAAxkBAAEBC0dfDDDTUUWjZR_nT7XFd1z0NBQLSQACbgIAAvEElxNbh2eCtRfwFhoE',
    'CAACAgIAAxkBAAEBC0lfDDDif8x7Nvlj-C8LCV87uFtxBgACbAIAAvEElxNXLEnhoFDVXBoE',
    'CAACAgIAAxkBAAEBC0tfDDEEHstO0sx3bv1kHjAKdE7BxQACggIAAvEElxPP3beJhPM_3BoE',
]

quarantine_stickers = [
    'CAACAgIAAxkBAAEBCydfDC4deg2Tf11qClLbx75g0JRlpgACOcgBAAFji0YMW3WeIv3odJ4aBA',
    'CAACAgIAAxkBAAEBCylfDC4qgvDm-HKQuLzVAhMfwqTw2QACOMgBAAFji0YMf6ZMpnzkjYQaBA',
    'CAACAgIAAxkBAAEBCytfDC401umtYaBX8ICARKNVtTrh0wACOsgBAAFji0YM4exOQQQSl-UaBA',
    'CAACAgIAAxkBAAEBCy1fDC4_TrK-pK7NzDvQ8cIwsesglwACO8gBAAFji0YMEPTtxb57y78aBA',
    'CAACAgIAAxkBAAEBCy9fDC5JAAGON0o1iVRsk16EjqJvDb8AAjzIAQABY4tGDJJzkl4yLbX6GgQ',
    'CAACAgIAAxkBAAEBCzFfDC5U4aAcXTd3gUa4PuDDYLBGBwACPcgBAAFji0YMhQeI14kvLYEaBA',
    'CAACAgIAAxkBAAEBCzNfDC5ebp-ST6dESKv8XOvRiuhe3gACPsgBAAFji0YM_uBo6puFRSAaBA',
    'CAACAgIAAxkBAAEBCzVfDC5qGwOovAFv0kwlq7t_xvQUOgACP8gBAAFji0YMqaNPAAExW8mvGgQ',
    'CAACAgIAAxkBAAEBCzdfDC52tIb4u3xdI3YbxP-ktYuDjQACQMgBAAFji0YMlFFEKc01eigaBA',
]

halizia_stickers = [
    'CAACAgIAAxkBAAEBC2tfDDecZWKUAk2kI6desgjdBsNnlQACBgMAAnmyPgT67bYLcsFzHBoE',
    'CAACAgIAAxkBAAEBC21fDDemszECtY8MhaGsUy0EFz7HMQACigEAAnmyPgQNuOQ2QmWbCRoE',
    'CAACAgIAAxkBAAEBC29fDDe6sxES51QMoJTceKVSdxcf6gACFwEAAnmyPgQhHGwEVeOOgxoE',
    'CAACAgIAAxkBAAEBC3FfDDfStHtVZh3PVPD3V89K6wbj3gACLQEAAnmyPgR0zunoqWrEMBoE',
    'CAACAgIAAxkBAAEBC3NfDDfzkgKhBY7Nc2L99MIqEUacAgACUwEAAnmyPgSSskf8dum_sBoE',
    'CAACAgIAAxkBAAEBC3dfDDgRFhPcXFVvaKeylWHlNS4m3AACaAEAAnmyPgR10PNSj22J7BoE',
    'CAACAgIAAxkBAAEBC3lfDDgo72vL0igGHwyM8tTLl5HHzAACowIAAnmyPgR-5A1GpChlFhoE',
    'CAACAgIAAxkBAAEBC3tfDDh1fF1dYPKCGgz22fUrpYvNNQACgAEAAnmyPgRM2CuTXZ9rSxoE',
]

gus_stickers = [
    'CAACAgIAAxkBAAEBC5pfDD2uY4A-BzMt3S8Q0K7tPTRZkwACnQEAAo5EEQKtOHcKhhglVBoE',
    'CAACAgIAAxkBAAEBC5xfDD3uNM8oUvu3X5JtZxsbRu7mswACvwEAAo5EEQLHhmdDoeGHShoE',
    'CAACAgIAAxkBAAEBC55fDD4HA-QsEXbwVtdZxJhjE6KUUAACwgEAAo5EEQICdywoQU29nhoE',
    'CAACAgIAAxkBAAEBC6BfDD4XCwM1PfdojrSDE7odr-KvSQACxwEAAo5EEQIMNBoYMPR1FBoE',
    'CAACAgIAAxkBAAEBC6JfDD498CH05B3YECKgY3PexGSo1AACiQEAAo5EEQIXqSWJ-YM9WxoE',
    'CAACAgIAAxkBAAEBC6RfDD5J6D7S-OPHq9iqWGSxFO4T7gACyQEAAo5EEQJ2RbK33NffGxoE',
    'CAACAgIAAxkBAAEBC6ZfDD5fktlFENWCwzkAAV9ePaRUo6MAAo4BAAKORBECB1RQ2ATBUukaBA',
    'CAACAgIAAxkBAAEBC6hfDD6WUjyy7CaR8cSXOYGUnLkqLQACygEAAo5EEQIAARL5eXp_ZacaBA',
    'CAACAgIAAxkBAAEBC6pfDD6lTiHe8nQccSxy1ejFN8HxdwACmAEAAo5EEQLLRGx16pXt2BoE'
]

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

def delete_db(user_id, username):
    try:
        connection = mysql.connector.connect(host='eu-cdbr-west-03.cleardb.net',database='heroku_827e33f01765a32',user='b9aaef9756aadc',password='4817bc17')
        sql_query = f"DELETE FROM IDs WHERE UserID = {user_id}"
        cursor = connection.cursor()
        cursor.execute(sql_query)
        connection.commit()
        bot.send_message(454706315, f"{username} *deleted from DB*", parse_mode='Markdown')
    except Error as error:
        bot.send_message(454706315, f"DB deletion error: {error}")

#users not delivered
unsubs = []

def weather_morning():
    records = get_db()
    holidays, names = holidays_names()
    weather = Weather(city='Lviv').show_weather()
    greet = tm()
    count = 0
    not_delivered = []
    for userid, username, city, latitude, longitude in records:
        if userid in unsubs:
            delete_db(userid, username)
            unsubs.remove(userid)
            continue
        try:
            if city != None:
                weather1 = Weather(latitude=latitude, longitude=longitude).show_weather()
                bot.send_message(userid, f"{greet}, {username}!\n{weather1}", parse_mode='Markdown')
                if len(holidays) == 0:
                    bot.send_message(userid, f"*Іменини:*\n{names}", parse_mode='Markdown')
                elif len(names) == 0:
                    bot.send_message(userid, f"*Сьогодні відзначають:*\n{holidays}", parse_mode='Markdown')
                else:
                    bot.send_message(userid, f"*Сьогодні відзначають:*\n{holidays}\n*Іменини:*\n{names}", parse_mode='Markdown')
                count+=1
            else:
                bot.send_message(userid, f"{greet}, {username}!\n{weather}", parse_mode='Markdown')
                if len(holidays) == 0:
                    bot.send_message(userid, f"*Іменини:*\n{names}", parse_mode='Markdown')
                elif len(names) == 0:
                    bot.send_message(userid, f"*Сьогодні відзначають:*\n{holidays}", parse_mode='Markdown')
                else:
                    bot.send_message(userid, f"*Сьогодні відзначають:*\n{holidays}\n*Іменини:*\n{names}", parse_mode='Markdown')
                count+=1
            time.sleep(1)
        except Exception:
            unsubs.append(userid)
            not_delivered.append(username)
    bot.send_message(454706315, f"*delivered:* {count}/{len(records)}\n*not delivered:* {len(not_delivered)} {not_delivered}", parse_mode='Markdown')

def weather_evening():
    records = get_db()
    forecast = Weather(city='Lviv').show_forecast()
    greet = tm()
    count = 0
    not_delivered = []
    wkday = datetime.datetime.today().weekday()
    if wkday == 0 or wkday == 1:
        stiker = quarantine_stickers
    elif wkday == 4 or wkday == 5:
        stiker = podia_stickers
    elif wkday == 2:
        stiker = halizia_stickers
    else:
        stiker = gus_stickers
    for userid, username, city, latitude, longitude in records:
        if userid in unsubs:
            delete_db(userid, username)
            unsubs.remove(userid)
            continue
        try:
            if city != None:
                forecast1 = Weather(latitude=latitude, longitude=longitude).show_forecast()
                bot.send_message(userid, f"{greet}, {username}!\nПогода на завтра у місті {city}:\n{forecast1}", parse_mode='Markdown')
                bot.send_sticker(userid, random.choice(stiker))
                count+=1
            else:
                bot.send_message(userid, f"{greet}, {username}!\nПогода на завтра:\n{forecast}", parse_mode='Markdown')
                bot.send_sticker(userid, random.choice(stiker))
                count+=1
            time.sleep(1)
        except Exception:
            unsubs.append(userid)
            not_delivered.append(username)
    bot.send_message(454706315, f"*delivered:* {count}/{len(records)}\n*not delivered:* {len(not_delivered)} {not_delivered}", parse_mode='Markdown')

schedule.every().day.at('07:00').do(weather_morning)
schedule.every().day.at('18:00').do(weather_evening)

while True:
    schedule.run_pending()
    time.sleep(30)