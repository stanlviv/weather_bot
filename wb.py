import telebot
import pyowm
import datetime
from pyowm import timeutils
import random
import pickle
from bs4 import BeautifulSoup
import requests

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

jokes = {
    1: '- В яку погоду так і хочеться дивитись серіали?\n - В яку?\n - Та в будь яку!',
    2: 'Якщо після двох холодних дощових днів настав сонячний і теплий день, значить це понеділок.',
    3: 'Не хочу сказати що погода жахлива, але в мене під вікнами якийсь бородатий дядько будує корабель.',
    4: 'Наступило літо. Можна переодягатись в літню шапку, літнє пальто та літній шалик.',
    5: 'Всі скаржаться на погоду. Ніби крім погоди у вас все гаразд.',
    6: 'Ведучий прогнозу погоди після свят прийшовши на роботу показав не лише де знаходиться антициклон, але й де служив.',
    7: 'Синоптики заспокоюють: влітку снігу буде менше.',
    8: 'Весна – найкрасивіша пора року, якщо не бачити місця для вигулу собак!',
    9: 'Березень. Армія котів оголошує весняний призов.',
    10: '-Яка погода на перше число?\n-Дощ\n-А на друге?\n-А на друге борщ.',
}

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
        key = random.choice(range(1,11))
        bot.send_message(message.chat.id, jokes[key])
    elif message.text == 'Щоденний прогноз':
        with open('ids.txt', 'rb') as i:
            ids = pickle.load(i)
        user_id = message.chat.id
        user_name = message.from_user.first_name
        ids.update({user_id: user_name})
        with open('ids.txt', 'wb') as i:
            pickle.dump(ids, i)
        bot.send_message(454706315, f"{message.chat.id}, {message.from_user.first_name} subscribed")
        bot.send_message(message.chat.id, 'Гаразд! Щодня я повідомлятиму  погоду і прогноз на завтра у нашому місті!\n\nЩоб відписатись, напишіть "відписатись"')
    elif message.text.lower() == 'відписатись':
        remove_user = message.chat.id
        with open('ids.txt', 'rb') as i:
            ids = pickle.load(i)
        ids.pop(remove_user)
        with open('ids.txt', 'wb') as i:
            pickle.dump(ids, i)
        bot.send_message(454706315, f"{message.chat.id}, {message.from_user.first_name} unsubscribed")
        bot.send_message(message.chat.id, 'Гаразд. Сподіваюсь, я Вас не підвів. \nВи можете підписатись на розсилку будь коли знову! :)')
    elif message.text.lower() == 'привіт':
        bot.send_message(message.chat.id, 'Привіт, друже!')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI7d16BzMSShyixww6APZD4KiOuTDwTAAIYAAPAY3cki65rroW9WfcYBA')
    elif message.text.lower() == 'бувай':
        bot.send_message(message.chat.id, 'See you later, aligator!')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI7e16Bza6XNPdRIPl5el6vcLh7fnT7AAI7AAPAY3cktopQHxzqzrEYBA')
    elif message.text == 'top-10 world news':
        n = parse_world()
        bot.send_message(message.chat.id, 'Новини світу:') 
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
        with open('ids.txt', 'rb') as i:
            ids = pickle.load(i)
        for k, v in ids.items():
            bot.send_message(message.chat.id, f"{v}: {k}")
    else:
        town = Weather(message.text)
        bot.send_message(message.chat.id, 'Сьогодні:')
        bot.send_message(message.chat.id, town.show_weather())
        bot.send_message(message.chat.id, 'Завтра:')
        bot.send_message(message.chat.id, town.show_forecast())

bot.polling()
