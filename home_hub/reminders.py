import datetime, time, os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, ConversationHandler
from dateutil.parser import parse, parserinfo
from decouple import config

import bot_db

BOTKEY = config("HOMEBOT_BOTKEY")

updater = None
dispatcher = None

updater = Updater(BOTKEY, use_context=True)

dispatcher = updater.dispatcher

NEWREMINDERDETAILS, NEWREMINDERTIME = range(2)
reminderdetail = ''
remindertime = ''

class CustomParserInfo(parserinfo):
    DAYS = list(range(1, 31))
    MONTHS = [("Jan", "January"), ("Feb", "February"), ("Mar", "March"), ("Apr", "April"), ("May", "May"), ("Jun", "June"), ("Jul", "July"), ("Aug", "August"), ("Sep", "September"), ("Oct", "October"), ("Nov", "November"), ("Dec", "December"),]
    YEARS = list(range(2020, 2050))


def is_date(string, fuzzy=False):
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False
        
        
# ==========CONVERSATION HANDLER==========

def newreminder(update, context):
    print("newreminder function")
    update.message.reply_text("OK, what is the reminder about?")
    return NEWREMINDERDETAILS
def newreminderdetail(update, context):
    global reminderdetail
    new_reminder_details = update.message.text
    reminderdetail = update.message.text
    print(str(new_reminder_details))
    update.message.reply_text("OK. What time do you want to be reminded about that?")
    update.message.reply_text("I need to know the full date, and the time in 24 hour format please")
    return NEWREMINDERTIME
def newremindertime(update, context):
    global reminderdetail
    global remindertime
    user_name = update['message']['chat']['first_name']
    user_id = update['message']['chat']['id']
    new_reminder_time = update.message.text
    parsed_time = parse(new_reminder_time, parserinfo=CustomParserInfo())
    print(parsed_time)
    update.message.reply_text(str(parsed_time))

    try:
        if is_date(new_reminder_time):
            update.message.reply_text("OK. Reminder stored.")
            remindertime = parsed_time
            time.sleep(1)
            update.message.reply_text("I will send a reminder to " + str(user_name) +  " at " + str(parsed_time) +  " about the following: " + str(reminderdetail))
            addreminder(reminderdetail, remindertime, user_name, user_id)
            return ConversationHandler.END
        else:
            print("IS DATE IS FALSE")
            update.message.reply_text("Please use a date format I can understand - Year/Month/Day followed by Hour and Minute with nothing in between.")
    except Exception as e:
        print(f"Error: {e}")
        update.message.reply_text("Please use a date format I can understand - Year/Month/Day followed by Hour and Minute with nothing in between.")
        return NEWREMINDERTIME
    
# add TIMESTRING module to make reminders even better

def addreminder(detail, time, username, user_id):
    bot_db.add_reminder(user_id, username, detail, time)

def sendallreminders():
    bot_reply = 'All the reminders I am currently aware of:\n\n'
    i = 1
    reminders = bot_db.get_reminders()
    for reminder in reminders:
        # composed_time = reminder[3].strftime('%Y/%m/%d %H%M')
        bot_reply = bot_reply + str(i) + '.\nFor ' + reminder[1] + '\nDetails: ' + reminder[2] + '\nAt: ' + reminder[3] + '\n\n'
        i += 1
    return bot_reply

def deletereminder(details):
    bot_db.delete_reminder(details)
    reminders = bot_db.get_reminders()
    print(reminders)

def remindchecker():
    while True:
        reminders = bot_db.get_reminders()
        for reminder in reminders:
            remindertime = datetime.datetime.strptime(reminder[3], "%Y-%m-%d %H:%M:%S")
            #rem_time = parse(reminder['Time'], parserinfo=CustomParserInfo())
            if datetime.datetime.now().date() == remindertime.date():
                if datetime.datetime.now().time() > remindertime.time():
                    deletereminder(reminder[2])
                    remindermessage = "Reminder for " + reminder[1] + "! " + reminder[2]
                    updater.bot.send_message(chat_id=reminder[0], text=remindermessage)
        time.sleep(5)

def showreminders(update, context):
    update.message.reply_text(sendallreminders()) 

def cancel(update, context):
    update.message.reply_text("Cancelled - you either said cancel, quit or dont save. Watch out for those words if that was a mistake!")
    return ConversationHandler.END

reminder_handler = ConversationHandler(
    entry_points=[CommandHandler('addreminder', newreminder)],
    states={
        NEWREMINDERDETAILS: [MessageHandler(Filters.text, newreminderdetail)],
        NEWREMINDERTIME: [MessageHandler(Filters.text, newremindertime)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )