import telebot
import pyowm
import datetime
from pyowm import timeutils
import random
from bs4 import BeautifulSoup
import requests
import mysql.connector
from mysql.connector import Error


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
        items = soup.find_all('h3', class_='ipQwMb ekueJc gEATFF RD0gLb')
        news = {}
        for item in items:
            news.update({item.find('a', class_='DY5T1d').get_text(): item.find('a', class_='DY5T1d').get('href')})
        return news

def parse_ukraine():
    html = requests.get('https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FuVnJHZ0pWUVNnQVAB/sections/CAQiUENCQVNOZ29JTDIwdk1EVnFhR2NTQW5WckdnSlZRU0lPQ0FRYUNnb0lMMjB2TURkME1qRXFFZ29RRWc3UW85QzYwWURRc05HWDBMM1FzQ2dBKioIAComCAoiIENCQVNFZ29JTDIwdk1EVnFhR2NTQW5WckdnSlZRU2dBUAFQAQ?hl=uk&gl=UA&ceid=UA%3Auk')
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all('h3', class_='ipQwMb ekueJc gEATFF RD0gLb')
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
        sql_query = "INSERT INTO Ids VALUES (%s, %s)"
        values = (user_id, user_name)
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        ids = []
        for x in records:
            ids.append(x[0])
        if user_id in ids:
            return f"Ви вже підписані! Ви отримуватимете прогноз щодня (зранку та ввечері).\nЯкщо ви все ж не отримуєте повідомлень, напишіть про це @stanlviv"
        else:
            cursor.execute(sql_query, values)
            connection.commit()
            return 'Гаразд! Щодня я повідомлятиму  погоду і прогноз на завтра у нашому місті!\n\nЩоб відписатись, напишіть "відписатись"'
    except Error as error:
        return f"Упс, помилка! {error}"

def delete_db(user_id):
    try:
        connection = mysql.connector.connect(host='eu-cdbr-west-03.cleardb.net',database='heroku_827e33f01765a32',user='b9aaef9756aadc',password='4817bc17')
        sql_query = f"DELETE FROM IDs WHERE UserID = {user_id}"
        cursor = connection.cursor()
        cursor.execute(sql_query)
        connection.commit()
        return 'Гаразд. Сподіваюсь, я Вас не підвів. \nВи можете підписатись на розсилку будь коли знову! :)'
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

@bot.message_handler(commands=['start'])
def start_message(message):
    tm()
    bot.send_message(message.chat.id, f"{tm()}, {message.from_user.first_name}", reply_markup=keyboard1)
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI_S16MgxSgpd99fPxFqp3MFLxxmuDxAAITAAPAY3ckIMwNpzrtVGcYBA')

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == 'Погода сьогодні':
        bot.send_message(message.chat.id, Weather('Lviv').show_weather())
    elif message.text == 'Погода завтра':
        bot.send_message(message.chat.id, Weather('Lviv').show_forecast())
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
        bot.send_message(message.chat.id, report)
    elif message.text.lower() == 'відписатись':
        user_id = message.chat.id
        report = delete_db(user_id)
        bot.send_message(454706315, f"{message.chat.id}, {message.from_user.first_name} unsubscribed")
        bot.send_message(message.chat.id, report)
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
        for row in record:
            bot.send_message(message.chat.id, f"{row[0]}: {row[1]}")
        bot.send_message(message.chat.id, f"Total: {len(record)}")
    else:
        town = Weather(message.text)
        bot.send_message(message.chat.id, 'Сьогодні:')
        bot.send_message(message.chat.id, town.show_weather())
        bot.send_message(message.chat.id, 'Завтра:')
        bot.send_message(message.chat.id, town.show_forecast())

bot.polling()