import telebot
import pyowm
import datetime
from pyowm import timeutils
import random
from bs4 import BeautifulSoup
import requests
import mysql.connector
from mysql.connector import Error
import time

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
            result = f"*{place_status.capitalize()} у місті {point_name}.*\nТемпература: {place_temp['temp']}℃\nВологість: {place_hum}%\nТиск: {place_pressure['press']} hPa\nШвидкість вітру: {place_wind['speed']} м/с"
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
            return f"*{rain} {sun}*\n9:00 - {temp9}℃\n12:00 - {temp12}℃\n18:00 - {temp18}℃\n21:00 - {temp21}℃"
        except Exception:
            return f"Вочевидь, такого міста немає :(\nСпробуйте ще раз!"
    
    def show_five_day_forecast(self):
        place = owm.three_hours_forecast(self.city)
        lw = place.get_forecast()
        s = []
        for x in lw:
            timestamp = x.get_reference_time()
            value = datetime.datetime.fromtimestamp(timestamp)
            s.append( f"{value.strftime('%A, %b %d, %H:%M')}:\n{x.get_detailed_status()}\nt: {x.get_temperature('celsius')['temp']}℃\n")
        return s

def parse_world():
    html = requests.get('https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FuVnJHZ0pWUVNnQVAB?hl=uk&gl=UA&ceid=UA%3Auk')
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all('h3', class_='ipQwMb ekueJc RD0gLb')
        news = {}
        for item in items:
            news.update({item.find('a', class_='DY5T1d').get_text(): item.find('a', class_='DY5T1d').get('href')})
        return news

def parse_ukraine():
    html = requests.get('https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FuVnJHZ0pWUVNnQVAB/sections/CAQiUENCQVNOZ29JTDIwdk1EVnFhR2NTQW5WckdnSlZRU0lPQ0FRYUNnb0lMMjB2TURkME1qRXFFZ29RRWc3UW85QzYwWURRc05HWDBMM1FzQ2dBKioIAComCAoiIENCQVNFZ29JTDIwdk1EVnFhR2NTQW5WckdnSlZRU2dBUAFQAQ?hl=uk&gl=UA&ceid=UA%3Auk')
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all('h3', class_='ipQwMb ekueJc RD0gLb')
        news = {}
        for item in items:
            news.update({item.find('a', class_='DY5T1d').get_text(): item.find('a', class_='DY5T1d').get('href')})
        return news

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

def insert_db(user_id, user_name):
    try:
        connection = mysql.connector.connect(host='eu-cdbr-west-03.cleardb.net',database='heroku_827e33f01765a32',user='b9aaef9756aadc',password='4817bc17')
        sql_select_Query = "SELECT * FROM IDs"
        sql_query = f"INSERT INTO Ids VALUES ({user_id}, '{user_name}', Null, Null, Null)"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        ids = [x[0] for x in records]
        if user_id in ids:
            return f"Ви вже підписані! Ви отримуватимете прогноз щодня (зранку та ввечері).\n\nЩоб відмовитись від розсилки, напишіть 'відписатись'."
        else:
            cursor.execute(sql_query)
            connection.commit()
            return "Вітаю! Щодня я повідомлятиму погоду і прогноз на завтра у нашому місті!\n\nЩоб відписатись, напишіть 'відписатись'.\n\nЩоб змінити місто, напишіть 'моя локація'."
    except Error as error:
        return f"Упс, помилка! {error}"

def delete_db(user_id):
    try:
        connection = mysql.connector.connect(host='eu-cdbr-west-03.cleardb.net',database='heroku_827e33f01765a32',user='b9aaef9756aadc',password='4817bc17')
        sql_query = f"DELETE FROM IDs WHERE UserID = {user_id}"
        cursor = connection.cursor()
        cursor.execute(sql_query)
        connection.commit()
        return 'Гаразд. Сподіваюсь, я Вас не підвів. \nВи можете підписатись на розсилку будь коли знову!'
    except Error as error:
        return f"Упс, помилка! {error}"

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

def insert_location_db(user, latitude, longitude):
    point = owm.weather_at_coords(latitude, longitude)
    p_n = point.get_location()
    point_name = p_n.get_name()
    try:
        record = get_db()
        ids = [x[0] for x in record]
        if user in ids:
            connection = mysql.connector.connect(host='eu-cdbr-west-03.cleardb.net',database='heroku_827e33f01765a32',user='b9aaef9756aadc',password='4817bc17')
            sql_query = f"UPDATE IDs SET City = '{point_name}', latitude = {latitude}, longitude = {longitude} WHERE UserID = {user}"
            cursor = connection.cursor()
            cursor.execute(sql_query)
            connection.commit()
            return f"Гаразд! Тепер я повідомлятиму погоду у місті {point_name}.\nЩоб повернутись до міста за замовчуванням, напишіть 'видалити локацію'."
        else:
            return "Ви ще не підписані на розсилку, тому не можете змінити локацію!\nБудь ласка, натисніть клавішу 'Щоденний прогноз' щоб підписатись."
    except Error as error:
        return f"Упс, помилка! {error}"

def del_location_db(user):
    try:
        connection = mysql.connector.connect(host='eu-cdbr-west-03.cleardb.net',database='heroku_827e33f01765a32',user='b9aaef9756aadc',password='4817bc17')
        sql_query = f"UPDATE IDs SET City = Null, latitude = Null, longitude = Null WHERE UserID = {user}"
        cursor = connection.cursor()
        cursor.execute(sql_query)
        connection.commit()
        return "Гаразд! Видалив.\nПогода за замовчуванням у місті Львів.\n\nЩоб відписатись від розсилки взагалі, напишіть 'відписатись'."
    except Error as error:
        return f"Упс, помилка! {error}"

jokes = ['- В яку погоду так і хочеться дивитись серіали?\n - В яку?\n - Та в будь яку!',
'Якщо після двох холодних дощових днів настав сонячний і теплий день, значить це понеділок.',
'Не хочу сказати що погода жахлива, але в мене під вікнами якийсь бородатий дядько будує корабель.',
'Наступило літо. Можна переодягатись в літню шапку, літнє пальто та літній шалик.',
'Всі скаржаться на погоду. Ніби крім погоди у вас все гаразд.',
'Ведучий прогнозу погоди після свят прийшовши на роботу показав не лише де знаходиться антициклон, але й де служив.',
'Синоптики заспокоюють: влітку снігу буде менше.',
'Весна – найкрасивіша пора року, якщо не бачити місця для вигулу собак!',
'Березень. Армія котів оголошує весняний призов.',
'-Яка погода на перше число?\n-Дощ\n-А на друге?\n-А на друге борщ.',
'І про погоду:\nзавтра очікується волога погода з рясними соплями, температура до 40 градусів, пориви кашлю можуть досягати 5-7 метрів.',
'Уже декілька днів іде дощ. У моєї жінки сильна депресія, вона стоїть і постійно дивиться у вікно. Якщо і далі буде йти дощ, доведеться впустити її в всередину.',]

keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Погода сьогодні', 'Погода завтра')
keyboard1.row('Погода на наступні 5 днів')
keyboard1.row('Пожартуй', 'Щоденний прогноз')
keyboard1.row('top-10 world news', 'top-10 news Ukraine')

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

@bot.message_handler(commands=['start', 'help'])
def commands(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, f"{tm()}, {message.from_user.first_name}", reply_markup=keyboard1)
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI_S16MgxSgpd99fPxFqp3MFLxxmuDxAAITAAPAY3ckIMwNpzrtVGcYBA')
    elif message.text == '/help':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton("Написати розробнику", url='telegram.me/stanlviv'))
        bot.send_message(message.chat.id,
        "*Q:* Чи можна дізнатись погоду в іншому місті?\n*A:* Звичайно! Просто напишіть боту назву Вашого міста!\n"+
        "*Q:* Розсилка лише з погодою у Львові?\n*A:* За замовчуванням, так. Але Ви можете це змінити, написавши команду 'моя локація'\n"+
        "*Q:* Як підписатись на розсилку?\n*A:* Виберіть клавішу 'Щоденний прогноз' на Вашій клавіатурі\n"+
        "*Q:* Чи ці новини актуальні?\n*A:* Так, це топ-10 актуальних новин.", 
        reply_markup=keyboard, parse_mode='Markdown')

@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
        res = insert_location_db(message.chat.id, latitude, longitude)
        bot.send_message(message.chat.id, res, reply_markup=keyboard1)
    else:
        bot.send_message(message.chat.id, "Ok",reply_markup=keyboard1)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == 'Погода сьогодні':
        bot.send_message(message.chat.id, Weather('Lviv').show_weather(), parse_mode='Markdown')
    elif message.text == 'Погода завтра':
        bot.send_message(message.chat.id, Weather('Lviv').show_forecast(), parse_mode='Markdown')
    elif message.text == 'Погода на наступні 5 днів':
        s = Weather('Lviv').show_five_day_forecast()
        for x in s:
            bot.send_message(message.chat.id, x)
    elif message.text == 'Пожартуй':
        bot.send_message(message.chat.id, random.choice(jokes))
    elif message.text == 'Щоденний прогноз':
        user_id = message.chat.id
        user_name = message.from_user.first_name
        report = insert_db(user_id, user_name)
        bot.send_message(454706315, f"{user_id}, {user_name} subscribed")
        bot.send_message(message.chat.id, report, reply_markup=keyboard1)
    elif message.text.lower() == 'відписатись':
        report = delete_db(message.chat.id)
        bot.send_message(454706315, f"{message.chat.id}, {message.from_user.first_name} unsubscribed")
        bot.send_message(message.chat.id, report, reply_markup=keyboard1)
    elif message.text.lower() == 'моя локація':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button_geo = telebot.types.KeyboardButton(text="Надіслати локацію", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(message.chat.id, "Надішліть мені Ваше місцерозташування", reply_markup=keyboard)
    elif message.text.lower() == 'видалити локацію':
        res = del_location_db(message.chat.id)
        bot.send_message(message.chat.id, res, reply_markup=keyboard1)
    elif message.text.lower() == 'привіт':
        bot.send_message(message.chat.id, 'Привіт, друже!')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI7d16BzMSShyixww6APZD4KiOuTDwTAAIYAAPAY3cki65rroW9WfcYBA')
    elif message.text.lower() == 'бувай':
        bot.send_message(message.chat.id, 'See you later, aligator!')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI7e16Bza6XNPdRIPl5el6vcLh7fnT7AAI7AAPAY3cktopQHxzqzrEYBA')
    elif message.text == 'top-10 world news':
        n = parse_world()
        bot.send_message(message.chat.id, 'Новини Світу:') 
        i=1
        for k, v in n.items():
            x = f"[{k}]({'https://news.google.com/' + v})"
            if i < 11:
                bot.send_message(message.chat.id, f"{i}. {x}", parse_mode = 'Markdown', disable_web_page_preview = True)
            i+=1
    elif message.text == 'top-10 news Ukraine':
        n = parse_ukraine()
        bot.send_message(message.chat.id, 'Новини України:') 
        i=1
        for k, v in n.items():
            x = f"[{k}]({'https://news.google.com/' + v})"
            if i < 11:
                bot.send_message(message.chat.id, f"{i}. {x}", parse_mode = 'Markdown', disable_web_page_preview = True)
            i+=1
    elif message.text.lower() == 'show list':
        record = get_db()
        for row1, row2, row3, row4, row5 in record:
            if row3 != None:
                bot.send_message(message.chat.id, f"{row1}: {row2} ({row3})")
            else:
                bot.send_message(message.chat.id, f"{row1}: {row2}")
        bot.send_message(message.chat.id, f"Total: {len(record)}")
    elif message.text.lower() == 'special days':
        try:
            holidays, names = holidays_names()
            if len(holidays) == 0:
                bot.send_message(message.chat.id, f"*Іменини:*\n{names}", parse_mode='Markdown')
            elif len(names) == 0:
                bot.send_message(message.chat.id, f"*Сьогодні відзначають:*\n{holidays}", parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, f"*Сьогодні відзначають:*\n{holidays}\n*Іменини:*\n{names}", parse_mode='Markdown')
        except Exception:
            bot.send_message(message.chat.id, "Error")
    elif message.text.lower() == 'send to all users':
        try:
            record = get_db()
            for x in record:
                bot.send_message(x[0], f"Привіт, {x[1]}!\nТепер я вмію робити розсилку погоди не лише у Львові!\nЯкщо Ви у іншому місті, напишіть 'моя локація' щоб я міг повідомляти погоду саме для Вас :)\nЗа додатковою інформацією виберіть команду '/help'\nГарного дня!")
        except Exception:
            bot.send_message(454706315, f"Smth went wrong ({x[1]})")
    else:
        town = Weather(message.text)
        bot.send_message(message.chat.id, 'Сьогодні:')
        bot.send_message(message.chat.id, town.show_weather(), parse_mode='Markdown')
        bot.send_message(message.chat.id, 'Завтра:')
        bot.send_message(message.chat.id, town.show_forecast(), parse_mode='Markdown')

bot.polling(none_stop=True ,interval=7)