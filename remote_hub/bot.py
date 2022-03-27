"""
Bot that runs on the remote hub
Can communicate with me via Telegram, atm primarily if home hub is down for some reason
e.g. camera units can send signals to remote hub if they are getting no response from home hub
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, ConversationHandler

from datetime import datetime
from decouple import config
import time, threading

import bot_db

updater = None
dispatcher = None
is_testing = False

updater = Updater(config("VBOT_BOTKEY"), use_context=True)

dispatcher = updater.dispatcher

users = []


def start_bot():
    global updater
    global dispatcher
    global is_testing
    # if is_testing:
    #     updater = Updater(config("TESTING_BOTKEY"), use_context=True)
    # else:
    #     updater = Updater(config("HOMEBOT_BOTKEY"), use_context=True)
    
    dispatcher.add_handler(CommandHandler('start', start))
    
    updater.start_polling()
    updater.idle()
    
def start(update, context):
    global users
    users_name=update['message']['chat']['first_name']
    reply = "Hi " + users_name + ". I am VBot. I exist on a virtual machine in the cloud and will watch over HomeBot."
    update.message.reply_text(reply)
    
    chat_id = update['message']['chat']['id']
    bot_db.add_authorised_user(int(chat_id), users_name, "regular")

def send_message(message, unitname=None):
    if unitname is not None:
        message = unitname + ": " + message
    for user in bot_db.get_all_users():
        updater.bot.send_message(user[0], message)
        

bot_thread = threading.Thread(name='bot', target=start_bot)

def activate_bot(testing=False):
    # global is_testing
    # if testing:
    #     is_testing = True
    bot_thread.start()
