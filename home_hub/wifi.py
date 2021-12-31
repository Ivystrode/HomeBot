"""
This file will control the wifi scanning
"""

from datetime import datetime
import socket, shutil, subprocess
import threading, time
from tqdm import tqdm

label = "[" + socket.gethostname().upper() + "]"
scanning = False

        

def activate_monitor_mode(scan_time):
    global scanning
    subprocess.Popen(f"sudo airmon-ng start wlan1", shell=True)
    print(f"{label} Wifi monitor mode active")
    scanning = True
    time.sleep(5)
    threading.Thread(target=scan).start()
    if scan_time != "continuous":
        time.sleep(int(scan_time))
    scanning = False

def stop_scan():
    global scanning
    scanning=False
    print(f"{label} Terminating wifi scan...")

def scan():
    global scanning
    scanning_activated = False
    
    while True:
        if scanning:
            if not scanning_activated:
                filename = f"{datetime.now().strftime('%Y%m%d-%H%M')}_{socket.gethostname()}_wifi_scan"
                wifi_scanner = subprocess.Popen(f"sudo airodump-ng -w {filename} --output-format csv wlan1mon", shell=True, stdout=subprocess.PIPE)
                # wifi_scanner.sta
                scanning_activated = True
                print(f"{label} Wifi scanner active")
                # time.sleep(10)
                # wifi_scanner.terminate()
            else:
                pass
            
        if not scanning:
            wifi_scanner.terminate()
            subprocess.Popen("sudo airmon-ng stop wlan1mon", shell=True)
            print(f"{label} Wifi scanner deactivated")
            break

