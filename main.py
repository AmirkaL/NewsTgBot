from aiogram import Bot, Dispatcher, executor, types
from dBase import Database
from news_parser.lenta import get_lenta_economic_news
from news_parser.ria import get_ria_economic_news
from news_parser.rbk import get_rbk_economic_news
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

API_TOKEN = '6887740905:AAG-GfF1a0MqMXFPOFvMjQDuyA4w5PcToNQ'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
db = Database('bot.db')

async def check_for_new_news_periodically():
    while True:
        await asyncio.sleep(5)  # Проверка каждые 5 минут

        # lenta.ru
        lenta_news = get_lenta_economic_news()
        if lenta_news:
            for item in lenta_news:
                if not db.news_exists(item['title']):
                    db.add_news(item['title'], item['link'])
                    subscribers = db.get_all_subscribers()
                    news_text = f"<a href='{item['link']}'>{item['title']}</a>"
                    for subscriber in subscribers:
                        keyboard = InlineKeyboardMarkup()
                        keyboard.add(InlineKeyboardButton(text="Посмотреть", url=item['link']))
                        await bot.send_message(subscriber, news_text, reply_markup=keyboard, parse_mode='HTML')

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    start_message = (
        "Привет! Я бот для получения новостей. Вот мои команды:\n\n"
        "/get - Получить актуальные новости\n"
        "/get_news - Получить новости из выбранного источника\n"
        "/update_n - Обновить количество новостей\n"
        "/default - Показать/Сменить текущий источник новостей\n"
        "/subscribe - Подписаться на рассылку новостей\n"
        "/unsubscribe - Отписаться от рассылки новостей\n"
    )
    if not db.get_user_default_source(chat_id):
        db.set_user_default_source(chat_id, "Лента.ру")
    db.log_user_action(chat_id, "/start")
    await message.answer(start_message)


# Обработчик команды /subscribe
@dp.message_handler(commands=['subscribe'])
async def cmd_subscribe(message: types.Message):
    chat_id = message.chat.id
    if not db.is_subscriber(chat_id):
        db.add_subscriber(chat_id)
        await message.reply("Вы успешно подписались на рассылку новостей!")
    else:
        await message.reply("Вы уже подписаны на рассылку новостей.")


# Обработчик команды /unsubscribe
@dp.message_handler(commands=['unsubscribe'])
async def cmd_unsubscribe(message: types.Message):
    chat_id = message.chat.id
    if db.is_subscriber(chat_id):
        db.remove_subscriber(chat_id)
        await message.reply("Вы успешно отписались от рассылки новостей.")
    else:
        await message.reply("Вы не подписаны на рассылку новостей.")


# Обработчик команды /update_n
@dp.message_handler(commands=['update_n'])
async def cmd_update_n(message: types.Message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) >= 2:
        try:
            n = int(args[1])
            if 1 <= n <= 10:
                db.set_user_news_count(chat_id, n)
                await message.reply(f"Количество новостей, отображаемых за раз, установлено на {n}.")
                db.log_user_action(chat_id, f"/update_n {n}")
            else:
                await message.reply("Пожалуйста, укажите число от 1 до 10.")
        except ValueError:
            await message.reply("Пожалуйста, укажите число.")
    else:
        await message.reply("Пожалуйста, укажите количество новостей после команды /update_n.")


# Обработчик команды /get_news
@dp.message_handler(commands=['get_news'])
async def cmd_get_news(message: types.Message):
    chat_id = message.chat.id
    default_source = db.get_user_default_source(chat_id)
    news_count = db.get_user_news_count(chat_id) or 5
    if default_source == "Лента.ру":
        news = get_lenta_economic_news()
    elif default_source == "РИА":
        news = get_ria_economic_news()
    elif default_source == "РБК":
        news = get_rbk_economic_news()
    else:
        await message.reply("Пожалуйста, выберите один из доступных источников новостей: 'Лента.ру', 'РИА' или 'РБК'.")
        return

    if news:
        for item in news[:news_count]:
            news_text = f"<a href='{item['link']}'>{item['title']}</a>"
            keyboard = InlineKeyboardMarkup()
            if default_source == "Лента.ру":
                keyboard.add(InlineKeyboardButton(text="Посмотреть", url=item['link']))
            await message.answer(news_text, parse_mode="HTML", reply_markup=keyboard)
        db.log_user_action(chat_id, f"/get_news {default_source}")
    else:
        await message.reply(f"Произошла ошибка при получении новостей с {default_source}.")

import random

# Обработчик команды /get
@dp.message_handler(commands=['get'])
async def cmd_get(message: types.Message):
    chat_id = message.chat.id
    news_count = db.get_user_news_count(chat_id) or 5
    random_source = random.choice(["Лента.ру", "РИА", "РБК"])

    if random_source == "Лента.ру":
        news = get_lenta_economic_news()
    elif random_source == "РИА":
        news = get_ria_economic_news()
    elif random_source == "РБК":
        news = get_rbk_economic_news()

    if news:
        random.shuffle(news)
        for item in news[:news_count]:
            news_text = f"<a href='{item['link']}'>{item['title']}</a>"
            keyboard = None
            if random_source == "Лента.ру":
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton(text="Посмотреть", url=item['link']))
            await message.reply(news_text, parse_mode="HTML", reply_markup=keyboard)
        db.log_user_action(chat_id, f"/get {random_source}")
    else:
        await message.reply(f"Произошла ошибка при получении новостей с {random_source}.")


# Обработчик команды /default
@dp.message_handler(commands=['default'])
async def cmd_default(message: types.Message):
    chat_id = message.chat.id
    default_source = db.get_user_default_source(chat_id)
    if default_source:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text=default_source, callback_data="current_source"))
        available_sources = ["Лента.ру", "РИА", "РБК"]
        for source in available_sources:
            if source != default_source:
                keyboard.add(InlineKeyboardButton(text=source, callback_data=source))
        await message.reply(f"Ваш выбранный источник новостей: {default_source}.", reply_markup=keyboard)
        db.log_user_action(chat_id, f"/default {default_source}")
    else:
        await message.reply("Вы еще не выбрали источник новостей. Пожалуйста, установите его с помощью команды /default.")

# Обработчик нажатий на инлайн кнопки
@dp.callback_query_handler(lambda query: query.data in ["current_source", "Лента.ру", "РИА", "РБК"])
async def process_callback_button(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    source = callback_query.data
    if source != "current_source":
        db.set_user_default_source(chat_id, source)
        await bot.edit_message_text(chat_id=chat_id, message_id=callback_query.message.message_id, text=f"Ваш выбранный источник новостей: {source}.")
        db.log_user_action(chat_id, f"InlineButton: {source}")
    else:
        current_source = db.get_user_default_source(chat_id)
        await bot.answer_callback_query(callback_query.id, text=f"Ваш текущий выбранный источник новостей: {current_source}", show_alert=True)
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback_query.message.message_id, reply_markup=None)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_for_new_news_periodically())
    executor.start_polling(dp, skip_updates=True)