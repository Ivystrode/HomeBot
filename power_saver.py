from home_hub import rfcon
from datetime import datetime 
import time

def power_saver(self):
    """
    Sends an RF signal that turns off all RF enabled power sockets to save power if they are
    left on late at night
    For some reason this works when I do it with a lone python file or manually in the python shell
    but not from this file. Why?
    """
    sent_1 = False
    sent_2 = False
    sent_3 = False
    while True:
        time.sleep(30)
        timenow = datetime.now().strftime("%H%M%S")
        if (int(timenow) > 235900) and (int(timenow) < 235910) and not sent_1:
            rfcon.transmit("plug5", "off") # initially we'll make sure this is the heater...
            time.sleep(2)
            rfcon.transmit("plug5", "off") # send twice to make sure
            
            print("[HUB] Sent power saver signal 1")
            # bot.send_message("Power saver signal 1 sent")
            sent_1 = True
            
        # checking an int value on a number that starts with 0 seems to cause issues, so do it as a string
        if datetime.now().strftime("%H%M") == "1711" and not sent_2:
            rfcon.transmit("plug5", "off")
            time.sleep(2)
            rfcon.transmit("plug5", "off")
            
            print("[HUB] Sent power saver signal 2")
            # bot.send_message("Power saver signal 2 sent")
            sent_2 = True
            
        if datetime.now().strftime("%H%M") == "0200" and not sent_3:
            rfcon.transmit("plug5", "off")
            time.sleep(2)
            rfcon.transmit("plug5", "off")
            
            print("[HUB] Sent power saver signal 3")
            # bot.send_message("Power saver signal 3 sent")
            sent_3 = True
            
            
        if datetime.now().strftime("%H%M") == "0600" and sent_1:
            # reset signals
            sent_1 = False
            sent_2 = False
            sent_3 = False
            print("[HUB] Reset power saver booleans")