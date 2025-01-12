from telebot import types
import requests

API_KEY = 'b861c8561e83115483c6c064acbf4540'

def register_weather_handlers(bot):
    
    def get_main_keyboard():
        """
        Create the main keyboard for the bot's menu.

        Provides buttons for weather, notes, extra features, 
        and Instagram download. The keyboard resizes for mobile use.

        Returns:
            types.ReplyKeyboardMarkup: Main menu keyboard.
        """
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        gold_button = types.KeyboardButton('🌦️ مشاهده وضعیت آب و هوا')  
        notes_button = types.KeyboardButton('📓 یادداشت‌ها')
        af_button = types.KeyboardButton('🧩 امکانات جانبی')
        instadwomload = types.KeyboardButton('📥 دانلود از اینستاگرام')
        markup.add( gold_button, notes_button)
        markup.add(instadwomload, af_button)
        return markup
    
    @bot.message_handler(func=lambda message: message.text == '🌦️ مشاهده وضعیت آب و هوا')
    def send_weather_options(message):
        """
        Display weather input options to the user.

        Shows a keyboard for location sharing or manual city input.

        Args:
            message (types.Message): User message triggering the weather menu.
        """
        bot.send_message(
            message.chat.id, 
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
            reply_markup=weather_options_keyboard()
        )

    def weather_options_keyboard():
        """
        Generate a keyboard with weather retrieval options.

        Includes buttons for location sharing, city input, and returning.

        Returns:
            types.ReplyKeyboardMarkup: Keyboard with weather options.
        """
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_location = types.KeyboardButton(text="📍 ارسال لوکیشن", request_location=True)
        button_city = types.KeyboardButton(text="🏙️ وارد کردن نام شهر")
        button_back = types.KeyboardButton(text="🔙 بازگشت")
        keyboard.add(button_location, button_city)
        keyboard.add(button_back)
        return keyboard

    @bot.message_handler(content_types=['location'])
    def fetch_weather_by_location(message):
        """
        Fetch weather using user's shared location.

        Retrieves latitude and longitude from the message 
        and calls the weather API to get data.

        Args:
            message (types.Message): Message with location data.
        """
        lat = message.location.latitude # (Latitude)
        lon = message.location.longitude # (Longitude)
        fetch_weather(message, lat=lat, lon=lon) 

    @bot.message_handler(func=lambda message: message.text == '🏙️ وارد کردن نام شهر')
    def request_city_name(message):
        """
        Ask the user to input a city name.

        Prompts the user to enter the city name for weather retrieval.

        Args:
            message (types.Message): User request to enter a city name.
        """
        msg = bot.send_message(message.chat.id, "🏙️ لطفاً نام شهر را وارد کنید:")
        bot.register_next_step_handler(msg, fetch_weather_by_city)

    def fetch_weather_by_city(message):
        """
        Get weather data based on the city name.

        Called after the user types the city name. Sends the data to the API.

        Args:
            message (types.Message): Message containing the city name.
        """
        city_name = message.text
        fetch_weather(message, city=city_name)

    def fetch_weather(message, lat=None, lon=None, city=None):
        """
        Request weather data from the OpenWeather API.

        Fetches weather using either coordinates or city name. 
        Sends the weather details back to the user.

        Args:
            message (types.Message): User's message object.
            lat (float, optional): Latitude for location-based requests.
            lon (float, optional): Longitude for location-based requests.
            city (str, optional): City name for city-based requests.
        """
        if lat and lon:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=fa"
        elif city:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=fa"
        else:
            bot.send_message(message.chat.id, "❌ لطفاً لوکیشن یا نام شهر را ارسال کنید.")
            return

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            city_name = data['name']
            current_temp = data['main']['temp']
            description = data['weather'][0]['main']

            weather_translation = {
                'Clear': '☀️ آفتابی',
                'Clouds': '☁️ ابری',
                'Rain': '🌧 بارانی',
                'Snow': '❄️ برفی',
                'Drizzle': '🌦 نم‌نم باران',
                'Thunderstorm': '⛈ طوفانی',
                'Mist': '🌫 مه',
                'Fog': '🌫 مه غلیظ'
            }
            weather_status = weather_translation.get(description, '❓ نامشخص')

            text = (
                    f"🌤 وضعیت آب و هوای امروز در {city_name}:\n"
                    f"🔹 دمای فعلی: °{int(current_temp)}C\n"
                    f"🔹 وضعیت: {weather_status}"
                )
        else:
            text = "❌ شهر پیدا نشد یا مشکلی در دریافت اطلاعات وجود دارد."

        bot.send_message(message.chat.id, text)

    @bot.message_handler(func=lambda message: message.text == '🔙 بازگشت')
    def go_back_to_main_menu(message):
        """
        Return to the main menu.

        Displays the main keyboard when the back button is pressed.

        Args:
            message (types.Message): User's message requesting to go back.
        """
        bot.send_message(
            message.chat.id, 
            "✅ به منوی اصلی بازگشتید.", 
            reply_markup=get_main_keyboard()
        )
