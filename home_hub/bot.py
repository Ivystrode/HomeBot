from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, ConversationHandler

from datetime import datetime
from decouple import config
import os
import socket
import sys
import threading
import time

import bot_db, reminders, commands


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
    dispatcher.add_handler(CommandHandler('detection', start_object_detection))
    dispatcher.add_handler(CommandHandler('stopdetection', stop_object_detection))
    
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

def start_object_detection(update, context):
    try:
        if len(context.args) == 0:
            for unit in bot_db.get_all_units():
                commands.send_command()
                update.message.reply_text()
    except:
        pass

def stop_object_detection(update, context):
    update.message.reply_text()

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
        
def send_message(message):
    for user in bot_db.get_all_users():
        updater.bot.send_message(user[0], message)
        
def send_file(unitname, filename, file_description):
        users = bot_db.get_all_users()
        print(f"[HUB] BOT: FILE SEND, users: {users}")
        try:
            for user in users:
                sent = False
                try:
                    updater.bot.sendPhoto(user[0], photo=open(filename, "rb"), timeout=50, caption=f"{unitname}: {file_description}")
                    print("[HUB] BOT: Sent photo")
                    sent = True
                except Exception as e:
                    print(f"[HUB] BOT: Not a photo...send as file?")
                    try:
                        if not sent:
                            updater.bot.sendDocument(user[0], document=open(filename, "rb"), timeout=50, caption=f"{unitname}: {file_description}")
                            print("[HUB] BOT: Sent as document")
                        sent = True
                    except Exception as e:
                        print(f"[HUB] BOT: Unable to send file (neither a photo or a document recognised) {filename} - {e}")
                if sent == True:
                    print(f"[HUB] BOT: File sent: {filename} to {user}")
                else:
                    print(f"[HUB] BOT: Unable to send {filename} to user: {user}")
                    
        except Exception as e:
            print(f"[HUB] BOT: Unable to send file {filename} - {e}")
    
    
bot_thread = threading.Thread(name='bot', target=start_bot)
ip_monitor_thread = threading.Thread(name='ip_monitor', target=ip_monitor)
reminder_thread = threading.Thread(name='reminder_checker', target=reminders.remindchecker)

def activate_bot():
    pass
    # bot_thread.start()
    # ip_monitor_thread.start()
    # reminder_thread.start()
