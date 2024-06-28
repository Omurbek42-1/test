from telegram import Update
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext
import aiosqlite
from database import Database

class SurveyRouter:
    def __init__(self):
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_survey)],
            states={
                'NAME': [MessageHandler(Filters.text & ~Filters.command, self.get_name)],
                'AGE': [MessageHandler(Filters.text & ~Filters.command, self.get_age)],
                'OCCUPATION': [MessageHandler(Filters.text & ~Filters.command, self.get_occupation)],
                'SALARY': [MessageHandler(Filters.text & ~Filters.command, self.get_salary)]
            },
            fallbacks=[]
        )
        self.db = Database()

    async def create_survey_table(self):
        async with aiosqlite.connect(self.db.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS survey (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    occupation TEXT,
                    salary INTEGER
                )
            ''')
            await db.commit()

    async def start_survey(self, update: Update, context: CallbackContext) -> str:
        await self.create_survey_table()
        update.message.reply_text("Давайте начнем опрос. Как вас зовут?")
        return 'NAME'

    async def get_name(self, update: Update, context: CallbackContext) -> str:
        context.user_data['name'] = update.message.text
        update.message.reply_text("Сколько вам лет?")
        return 'AGE'

    async def get_age(self, update: Update, context: CallbackContext) -> str:
        try:
            age = int(update.message.text)
            if age < 17:
                update.message.reply_text("Извините, но опрос доступен только для пользователей старше 16 лет.")
                return ConversationHandler.END
            context.user_data['age'] = age
            update.message.reply_text("Какая у вас профессия или род занятий?")
            return 'OCCUPATION'
        except ValueError:
            update.message.reply_text("Пожалуйста, введите возраст цифрами.")
            return 'AGE'

    async def get_occupation(self, update: Update, context: CallbackContext) -> str:
        context.user_data['occupation'] = update.message.text
        update.message.reply_text("Каков ваш месячный доход в USD?")
        return 'SALARY'

    async def get_salary(self, update: Update, context: CallbackContext) -> str:
        try:
            salary = int(update.message.text)
            context.user_data['salary'] = salary
            await self.db.insert_survey_data(context.user_data['name'], context.user_data['age'],
                                             context.user_data['occupation'], context.user_data['salary'])
            update.message.reply_text("Спасибо за участие в опросе! Ваши данные сохранены.")
            return ConversationHandler.END
        except ValueError:
            update.message.reply_text("Пожалуйста, введите сумму в виде числа.")
            return 'SALARY'
