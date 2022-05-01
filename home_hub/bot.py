from shutil import which
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
is_testing = False

updater = Updater(config("HOMEBOT_BOTKEY"), use_context=True)

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
    dispatcher.add_handler(CommandHandler('ip', ip_check))
    dispatcher.add_handler(reminders.reminder_handler)
    dispatcher.add_handler(CommandHandler('showreminders', reminders.showreminders))
    
    dispatcher.add_handler(CommandHandler('detection', start_object_detection))
    dispatcher.add_handler(CommandHandler('stopdetection', stop_object_detection))
    
    dispatcher.add_handler(CommandHandler('wifiscan', start_wifi_scan))    
    dispatcher.add_handler(CommandHandler('stopwifiscan', stop_wifi_scan))  
      
    dispatcher.add_handler(CommandHandler('rf', plug))    
    dispatcher.add_handler(CommandHandler('activate', activate_all))    
    dispatcher.add_handler(CommandHandler('deactivate', deactivate_all))    
    
    dispatcher.add_handler(CommandHandler('sendpic', send_pic))
    
    dispatcher.add_handler(CommandHandler('reboot', reboot))
    
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

def plug(update, context):
    try:
        if len(context.args) < 1:
            update.message.reply_text("You need to tell me which plug")
        else:
            which_plug = context.args[0]
            on_or_off = context.args[1]
            
        for unit in bot_db.get_all_units():
            if unit[3] == "RF Controller":
                commands.send_command(unit[1], on_or_off, which_plug)
                
            update.message.reply_text(f"OK turned {on_or_off} {which_plug}")
    except Exception as e:
        update.message.reply_text(f"Something went wrong - {e}")
        
def activate_all(update, context):
    try:
        for unit in bot_db.get_all_units():
            if unit[3] == "RF Controller":
                commands.send_command(unit[1], "activate_all")
    except Exception as e:
        update.message.reply_text(f"Something went wrong - {e}")
        
def deactivate_all(update, context):
    try:
        for unit in bot_db.get_all_units():
            if unit[3] == "RF Controller":
                commands.send_command(unit[1], "deactivate_all")
    except Exception as e:
        update.message.reply_text(f"Something went wrong - {e}")
        

def start_object_detection(update, context):
    try:
        if len(context.args) == 0:
            for unit in bot_db.get_all_units():
                try:
                    commands.send_command(unit[1], "start_object_detection")
                    time.sleep(1)
                except Exception as e:
                    update.message.reply_text(f"Something went wrong sending to {unit[1]}: {e}")
            update.message.reply_text("Telling all units to start object detection")
    except Exception as e:
        update.message.reply_text("Something went wrong")
        update.message.reply_text(f"{e}")

def stop_object_detection(update, context):
    try:
        if len(context.args) == 0:
            for unit in bot_db.get_all_units():
                commands.send_command(unit[1], "stop_object_detection")
            update.message.reply_text("Telling all units to stop object detection")
    except Exception as e:
        update.message.reply_text("Something went wrong")
        update.message.reply_text(f"{e}")
        
def start_wifi_scan(update, context):
    update.message.reply_text("Starting the wifi scanner...")

def stop_wifi_scan(update, context):
    update.message.reply_text("Stopping the wifi scanner...")
        
def send_pic(update, context):
    try:
        if len(context.args) == 0:
            for unit in bot_db.get_all_units():
                commands.send_command(unit[1], "send_photo")
            update.message.reply_text("Getting picture from all units")
        else:
            for unit in context.args:
                commands.send_command(unit, "send_photo")
                update.message.reply_text(f"Getting picture from {unit}...")
    except Exception as e:
        update.message.reply_text("Something went wrong")
        update.message.reply_text(f"{e}")
 
def reboot(update, context):
    try:
        if len(context.args) == 0:
            for unit in bot_db.get_all_units():
                commands.send_command(unit[1], "reboot")
            update.message.reply_text("Rebooting all units")
        else:
            for unit in context.args:
                commands.send_command(unit, "reboot")
                update.message.reply_text(f"Rebooting {unit}...")
    except Exception as e:
        update.message.reply_text("Something went wrong")
        update.message.reply_text(f"{e}")

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
        
def send_message(message, unitname=None):
    if unitname is not None:
        message = unitname + ": " + message
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

def activate_bot(testing=False):
    # global is_testing
    # if testing:
    #     is_testing = True
    bot_thread.start()
    ip_monitor_thread.start()
    reminder_thread.start()
