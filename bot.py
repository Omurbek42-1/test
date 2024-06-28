import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from database import Database
from queries import create_survey_table

TOKEN = 'YOUR_BOT_TOKEN'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
db = Database()


# States
class SurveyStates(StatesGroup):
    ask_name = State()
    ask_age = State()
    ask_occupation = State()
    ask_salary = State()


# Handlers
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await SurveyStates.ask_name.set()
    await message.reply("Давайте начнём опрос. Введите ваше имя:")


@dp.message_handler(state=SurveyStates.ask_name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await SurveyStates.next()
    await message.reply("Введите ваш возраст:")


@dp.message_handler(state=SurveyStates.ask_age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Введите число.")
        return
    age = int(message.text)
    if age < 17:
        await message.reply("Извините, опрос доступен только для лиц старше 16 лет. Прекращаем опрос.")
        await state.finish()
        return
    async with state.proxy() as data:
        data['age'] = age
    await SurveyStates.next()
    await message.reply("Введите вашу профессию:")


@dp.message_handler(state=SurveyStates.ask_occupation)
async def process_occupation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['occupation'] = message.text
    await SurveyStates.next()
    await message.reply("Введите вашу заработную плату:")


@dp.message_handler(state=SurveyStates.ask_salary)
async def process_salary(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Введите число.")
        return
    salary = int(message.text)
    async with state.proxy() as data:
        data['salary'] = salary
        await db.create_survey_entry(data['name'], data['age'], data['occupation'], data['salary'])
    await message.reply("Спасибо за участие в опросе! Данные сохранены.")
    await state.finish()


@dp.message_handler()
async def echo_message(message: types.Message):
    words = message.text.split()
    reversed_words = ' '.join(reversed(words))
    await message.reply(f'{" ".join(words)} -> {reversed_words}')


async def on_startup(dp):
    await db.create_table(create_survey_table)


if __name__ == '__main__':
    dp.middleware.setup(LoggingMiddleware())
    dp.loop.run_until_complete(on_startup(dp))
    try:
        dp.start_polling()
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        dp.stop_polling()
        asyncio.get_event_loop().close()
