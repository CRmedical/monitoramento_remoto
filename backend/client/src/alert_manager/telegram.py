import telebot
from dotenv import load_dotenv
import os
from .interfaces import Handle
from .entities import Fault, Connection
from src.manage_telegram import get_chat_id

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN', '')

bot = telebot.TeleBot(API_TOKEN)


class Telegram:

    def __init__(self, handles: Handle) -> None:
        self.handles = handles

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

    def send_connection_alert(self, connection: Connection):
        body = self.handles.create_connection_message(connection)
        try: 
            chat_id = get_chat_id(connection.hospital)
            self.send_message(chat_id, body)
        except:
            self.send_message(1538185358, body)



    def send_fault(self, fault: Fault, recover: bool = False) -> None:
        if recover:
            body = self.handles.create_recover_message(fault)
        else:
            body = self.handles.create_message(fault)

        try: 
            chat_id = get_chat_id(fault.hospital)
            self.send_message(chat_id, body)
        except:
            self.send_message(1538185358, body)

    

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