from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

class EchoRouter:
    def __init__(self):
        self.handler = MessageHandler(Filters.text & ~Filters.command, self.echo_message)

    def echo_message(self, update: Update, context: CallbackContext):
        text = update.message.text
        reversed_text = ' '.join(reversed(text.split()))
        update.message.reply_text(reversed_text)
