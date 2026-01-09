from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
import asyncio
import requests
import datetime

TOKEN = '8365065421:AAEFCnr3SwqAStJqyW3oHeICCo_Fc8YcSh0'
bot = Bot(TOKEN)
dp = Dispatcher()

ALERT_HOUR = 8
ALERT_MINUTE = 0
TARGET_CHAT_ID = 8365065421


def fetch_weather(city: str) -> dict:
    try:
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid=f580fdcd8a4f4a6893a51d23fd0b49c2&units=metric'
        weather_data = requests.get(url).json()
        return weather_data
    except Exception:
        return None


def format_weather(city: str, data: dict) -> str:
    try:
        temperature = data['main']['temp']
        temperature_feels = data['main']['feels_like']
        wind_speed = data['wind']['speed']
        cloud_cover = data['weather'][0]['description']
        humidity = data['main']['humidity']
        return (f'Сейчас температура в городе {city}: {temperature}°C\n'
                f'Ощущается как {temperature_feels}°C\n'
                f'Ветер: {wind_speed} м/с\n'
                f'Облачность: {cloud_cover}\n'
                f'Влажность: {humidity}%')
    except KeyError:
        return f'Не удалось определить погоду для города: {city}.'


async def send_weather_for_city(city: str, chat_id: int):
    data = fetch_weather(city)
    if data is None:
        text = f'Не удалось получить данные погоды для {city}.'
    else:
        text = format_weather(city, data)
    await bot.send_message(chat_id=chat_id, text=text)


async def daily_weather_loop(city: str, chat_id: int):
    """
    Фоновый цикл: каждый день в заданное время отправляет прогноз.
    """
    while True:
        now = datetime.datetime.now()
        # время следующего выполнения
        next_time = now.replace(hour=ALERT_HOUR, minute=ALERT_MINUTE, second=0, microsecond=0)
        if next_time <= now:
            next_time = next_time + datetime.timedelta(days=1)
        wait_seconds = (next_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        # отправка прогноза
        await send_weather_for_city(city, chat_id)


@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer('Привет! Пришли город, чтобы узнать погоду. Также можно настроить рассылку ежедневной погоды.')


@dp.message(F.text)
async def get_weather(message: types.Message):
    city = message.text
    data = fetch_weather(city)
    if data:
        text = format_weather(city, data)
        await message.answer(text)
    else:
        await message.answer(f'Не удалось определить город: {city}.')



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    if TARGET_CHAT_ID is not None and isinstance(TARGET_CHAT_ID, int):
        city = "Вологда"
        asyncio.create_task(daily_weather_loop(city, TARGET_CHAT_ID))
        await dp.start_polling(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
