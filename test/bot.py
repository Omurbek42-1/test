import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import aiosqlite


NAME, AGE, OCCUPATION, SALARY = range(4)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Привет! Давай начнем опрос.\n"
        "Как тебя зовут?"
    )
    return NAME


def get_name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text(
        f"Отлично, {context.user_data['name']}! Сколько тебе лет?"
    )
    return AGE

def get_age(update: Update, context: CallbackContext) -> int:
    try:
        age = int(update.message.text)
        if age < 17:
            update.message.reply_text(
                "Извини, но этот опрос предназначен для людей старше 16 лет. До свидания!"
            )
            return ConversationHandler.END
        context.user_data['age'] = age
        update.message.reply_text(
            "Какая у тебя профессия или род занятий?"
        )
        return OCCUPATION
    except ValueError:
        update.message.reply_text(
            "Пожалуйста, введи возраст цифрами."
        )
        return AGE


def get_occupation(update: Update, context: CallbackContext) -> int:
    context.user_data['occupation'] = update.message.text
    update.message.reply_text(
        "Какой у тебя доход в месяц (в USD)?"
    )
    return SALARY


async def get_salary(update: Update, context: CallbackContext) -> int:
    try:
        salary = int(update.message.text)
        context.user_data['salary'] = salary
        
       
        async with aiosqlite.connect('survey_data.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS survey (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    occupation TEXT,
                    salary INTEGER
                )
            ''')
            await db.execute('''
                INSERT INTO survey (name, age, occupation, salary)
                VALUES (?, ?, ?, ?)
            ''', (context.user_data['name'], context.user_data['age'], context.user_data['occupation'], context.user_data['salary']))
            await db.commit()
        
        update.message.reply_text(
            "Спасибо за участие в опросе! Данные сохранены."
        )
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text(
            "Пожалуйста, введи заработную плату числом."
        )
        return SALARY


def main():
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

  
    dispatcher = updater.dispatcher

   
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, get_age)],
            OCCUPATION: [MessageHandler(Filters.text & ~Filters.command, get_occupation)],
            SALARY: [MessageHandler(Filters.text & ~Filters.command, get_salary)],
        },
        fallbacks=[],
    )

   
    dispatcher.add_handler(conv_handler)

  
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
