import telebot
from telebot import types


from models import User
from todo_bot import register_todo_handlers
from weather_bot import register_weather_handlers
from additional_features_bot import register_af_handlers
from instagram_downloader_bot import register_instadownloader_handlers


TOKEN = '7200499579:AAEyMOqSnT52dFHZbiFtC0Qw1t8jfBgvd3w'
bot = telebot.TeleBot(TOKEN)


# --- HANDLER FOR START ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    gold_button = types.KeyboardButton('🌦️ مشاهده وضعیت آب و هوا')  
    notes_button = types.KeyboardButton('📓 یادداشت‌ها')
    af_button = types.KeyboardButton('🧩 امکانات جانبی')
    instadwomload = types.KeyboardButton('📥 دانلود از اینستاگرام')
    markup.add( gold_button, notes_button) 
    markup.add(instadwomload, af_button)
    

    # Extracting user information
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username if message.from_user.username else None

    # Checking whether the user is already registered in the database or not
    user = User.filter(user_id=user_id)
    
    if not user:
        # If the user does not exist in the database, we store their information.
        User.insert(user_id=user_id, first_name=first_name, username=username)
        
    
    welcome_text = (
        f'سلام {first_name} عزیز به ربات من خوش آمدید. 👋\n\n'
        'امکانات ربات:\n'
        '- 📓 یادداشت‌ها\n\n'
        '- 🌦️ مشاهده وضعیت آب و هوا\n\n'
        '- 📥 دانلود از اینستاگرام\n\n'
        '- 🧩 امکانات جانبی\n\n\n'

        
        'برای شروع، یکی از گزینه‌ها را انتخاب کنید.'
    )
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


register_todo_handlers(bot)
register_weather_handlers(bot)
register_af_handlers(bot)
register_instadownloader_handlers(bot)


bot.polling(none_stop=True)
