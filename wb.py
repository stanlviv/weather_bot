import telebot
import pyowm
import datetime
from pyowm import timeutils
import random

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
            t9 = place.get_weather_at(tomorrow9)
            t12 = place.get_weather_at(tomorrow12)
            t18 = place.get_weather_at(tomorrow18)
            temp9 = t9.get_temperature('celsius')['temp']
            temp12 = t12.get_temperature('celsius')['temp']
            temp18 = t18.get_temperature('celsius')['temp']
            if place.will_be_rainy_at(tomorrow12):
                rain = 'Дощитиме'
            else: rain = 'Буде сухо'
            if place.will_be_sunny_at(tomorrow12):
                sun = 'та сонячно.'
            else: sun = 'та хмарно.'
            return f"{rain} {sun}\n9:00 - {temp9}℃\n12:00 - {temp12}℃\n18:00 - {temp18}℃"
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

def remove_doubles():
    lst = []
    f = open('ids.txt', 'r')
    for x in f:
        lst.append(int(x))
    f.close()
    f = open('ids.txt', 'w')
    ids = list(set(lst))
    for x in ids:
        f.write(f"{x}\n")
    f.close()

def remove_id(user_id):
    lst = []
    f = open('ids.txt', 'r')
    for x in f:
        lst.append(int(x))
    f.close()
    for x in lst:
        if x == user_id:
            lst.remove(x)
    f = open('ids.txt', 'w')
    for x in lst:
        f.write(f"{x}\n")
    f.close()

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

def tm():
    global greeting
    now = datetime.datetime.now()
    hour = now.hour+3
    if hour >= 6 and hour <12:
        daytime = 'Добрий ранок!'
    elif hour >=12 and hour <18:
        daytime = 'Добрий день!'
    elif hour >=18 and hour <20:
        daytime = 'Добрий вечір!'
    else:
        daytime = 'Доброї ночі!'
    greeting = f'{daytime}'
    return greeting

lviv = Weather('Lviv')

@bot.message_handler(commands=['start'])
def start_message(message):
    tm()
    bot.send_message(message.chat.id, greeting, reply_markup=keyboard1)
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI_S16MgxSgpd99fPxFqp3MFLxxmuDxAAITAAPAY3ckIMwNpzrtVGcYBA')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == 'Погода сьогодні':
        bot.send_message(message.chat.id, lviv.show_weather())
    elif message.text == 'Погода завтра':
        bot.send_message(message.chat.id, lviv.show_forecast())
    elif message.text == 'Погода на наступні 5 днів':
        s = lviv.show_five_day_forecast()
        for x in s:
            bot.send_message(message.chat.id, x)
    elif message.text == 'Пожартуй':
        key = random.choice(range(1,11))
        bot.send_message(message.chat.id, jokes[key])
    elif message.text == 'Щоденний прогноз':
        f = open('ids.txt', 'a+')
        i = str(message.chat.id)
        f.write(f"{i}\n")
        f.close()
        bot.send_message(454706315, f"{i}, {message.from_user.first_name} subscribed")
        bot.send_message(message.chat.id, 'Гаразд! Щодня я повідомлятиму  погоду і прогноз на завтра у нашому місті!\n\nЩоб відписатись, напишіть "відписатись"')
        remove_doubles()
    elif message.text.lower() == 'відписатись':
        remove_id(message.chat.id)
        bot.send_message(454706315, f"{message.chat.id}, {message.from_user.first_name} unsubscribed")
        bot.send_message(message.chat.id, 'Гаразд. Сподіваюсь, я Вас не підвів. \nВи можете підписатись на розсилку будь коли знову! :)')
    elif message.text.lower() == 'привіт':
        bot.send_message(message.chat.id, 'Привіт, друже!')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI7d16BzMSShyixww6APZD4KiOuTDwTAAIYAAPAY3cki65rroW9WfcYBA')
    elif message.text.lower() == 'бувай':
        bot.send_message(message.chat.id, 'See you later, aligator!')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI7e16Bza6XNPdRIPl5el6vcLh7fnT7AAI7AAPAY3cktopQHxzqzrEYBA')
    elif message.text.lower() == 'котра година?':
        bot.send_message(message.chat.id, f"{datetime.datetime.now().hour}:{datetime.datetime.now().minute}")
    elif message.text.lower() == 'show list':
        f = open('ids.txt', 'r')
        for x in f:
            bot.send_message(message.chat.id, f"{x}")
        f.close()
    else: 
        town = Weather(message.text)
        bot.send_message(message.chat.id, 'Сьогодні:')
        bot.send_message(message.chat.id, town.show_weather())
        bot.send_message(message.chat.id, 'Завтра:')
        bot.send_message(message.chat.id, town.show_forecast())


bot.polling()
