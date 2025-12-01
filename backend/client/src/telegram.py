import telebot
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN', '')

bot = telebot.TeleBot(API_TOKEN)


class Telegram:

    @staticmethod
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Olá! Eu sou o bot.")


    @staticmethod
    @bot.message_handler(commands=['getId'])
    def get_chat_id(message):
        bot.reply_to(message, message.chat.id)


    @staticmethod
    def send_message(chat_id, text):
        bot.send_message(chat_id, text)

    @staticmethod
    def run_bot():
        bot.infinity_polling()


if __name__ == "__main__":
    # Telegram.run_bot()


    hospitais = {
        'Hospital da Crianca': -5043458545,
        'Hospital das Clinicas': 1538185358,
        'Joao Machado - Natal/RN': -1002197592567,
    }

    print(hospitais.get('Hospital da Crianca'))