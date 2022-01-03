from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, ConversationHandler

from datetime import datetime
from decouple import config
import os
import socket
import sys
import threading
import time

import bot_db, reminders


updater = None
dispatcher = None

updater = Updater(config("HOMEBOT_BOTKEY"), use_context=True)

dispatcher = updater.dispatcher

users = []


def start_bot():
    global updater
    global dispatcher
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('ip', ip_check))
    dispatcher.add_handler(reminders.reminder_handler)
    dispatcher.add_handler(CommandHandler('showreminders', reminders.showreminders))
    
    updater.start_polling()
    updater.idle()
    
def start(update, context):
    global users
    users_name=update['message']['chat']['first_name']
    reply = "Hi " + users_name + ". I am Homebot. I will help you look after the house."
    update.message.reply_text(reply)
    
    chat_id = update['message']['chat']['id']
    bot_db.add_authorised_user(int(chat_id), users_name, "regular")
    
def ip_check(update, context):
    ip = os.popen('curl -4 icanhazip.com').read()
    update.message.reply_text(ip)
    return ip

def ip_monitor():
    while True:
        try:
            stored_ip = bot_db.get_latest_ip()
        except:
            stored_ip = 0
            
        print(f"[Homebot] IP Check: Retrieved IP from DB is {stored_ip}\n")
        
        ip = os.popen('curl -4 icanhazip.com').read()
        
        if ip != stored_ip:
            print(f"\n[Homebot] IP Change: \nOld: {stored_ip} \nNew: {ip}")
            bot_db.insert(datetime.now().strftime("%Y%m%d%H%M"), ip)
            time.sleep(0.5)
            print(f"\n[Homebot] Stored IP now updated to {bot_db.get_latest_ip()}\n")
            
            # ===SEND WARNING MESSAGE===
            for user in bot_db.get_all_users():
                try:
                    updater.bot.sendMessage(user[0], f"IP Address updated, old address:\n{stored_ip}\nNew address:\n{ip}", timeout=50)
                except Exception as e:
                    print(e)
            
        time.sleep(1800)
    
    
bot_thread = threading.Thread(name='bot', target=start_bot)
ip_monitor_thread = threading.Thread(name='ip_monitor', target=ip_monitor)
reminder_thread = threading.Thread(name='reminder_checker', target=reminders.remindchecker)

bot_thread.start()
ip_monitor_thread.start()
reminder_thread.start()
