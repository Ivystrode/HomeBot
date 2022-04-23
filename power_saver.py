# from home_hub import rfcon
from datetime import datetime 
import time

"""
Moved 433mhz module to separate RPI
This file will no longer run on PINAS
"""

def power_saver():
    """
    Sends an RF signal that turns off all RF enabled power sockets to save power if they are
    left on late at night
    For some reason this works when I do it with a lone python file or manually in the python shell
    but not from this file. Why?
    """
    while True:
        time.sleep(20)
        timenow = datetime.now().strftime("%H%M")
        if timenow == "2300":
            from home_hub import rfcon
            rfcon.transmit("plug5", "off") # initially we'll make sure this is the heater...
            time.sleep(2)
            rfcon.transmit("plug5", "off") # send twice to make sure

            print("[HUB] Sent power saver signal 1")
            # bot.send_message("Power saver signal 1 sent")

        # checking an int value on a number that starts with 0 seems to cause issues, so do it as a string
        if timenow == "0001":
            from home_hub import rfcon
            rfcon.transmit("plug5", "off")
            time.sleep(2)
            rfcon.transmit("plug5", "off")

            print("[HUB] Sent power saver signal 2")
            # bot.send_message("Power saver signal 2 sent")

        if timenow == "0100":
            from home_hub import rfcon
            rfcon.transmit("plug5", "off")
            time.sleep(2)
            rfcon.transmit("plug5", "off")

            print("[HUB] Sent power saver signal 3")
            # bot.send_message("Power saver signal 3 sent")


power_saver()
