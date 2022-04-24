"""
Checks for new MAC addresses (devices)
Is the same as wifi.py except outdated, but with
the additional functionality to store and check
MAC addresses. Will need to merge the files soon
"""

from datetime import datetime
from genericpath import exists
import os, socket, shutil, subprocess
import threading, time
import pandas as pd

import bot_db

class WifiScanner():
    
    def __init__(self, scanning=True):
        # self.scan_device = self.get_scan_device()
        self.scanning = scanning # set this to false to stop wifi scanner (via bot command...)
        self.scan_thread = threading.Thread(target=self.wifi_scan, daemon=True)

    def start(self):
        self.scan_thread.start()

    def add_trusted_device(self, mac):
        bot_db.add_device(mac, datetime.now(), 1) # 0 is false (not trusted)
        
    def get_scan_device(self):
        devices = os.listdir("/sys/class/net/")
        wifi_devices = [i for i in devices if i.startswith("w") and not i.startswith("wg")] # wg is wireguard vpn interface/s
        for device in wifi_devices:
            print(f"Trying to activate monitor mode on {device}...")
            try:
                subprocess.Popen(f"sudo airmon-ng start {device}", shell=True)
                time.sleep(1)
                if os.path.exists(f"/sys/class/net/{device}mon"):
                    print(f"Successfully activated monitor mode on {device}")
                    scan_device = f"{device}mon"
                    print(f"Scan interface is {device}mon")
                    return scan_device
                else:
                    print(f"Failed to activate monitor mode on {device}")
            except Exception as e:
                print(f"Failed to activate monitor mode on {device} - {e}")


    def wifi_scan(self, duration=10, interval=20):
        scan_device = self.get_scan_device()
        scanner_active = False
        while True:
            print("ree")
            if self.scanning:
                print("dee")
                if not scanner_active:
                    print("ddhh")
                    time.sleep(2)
                    filename = f"{datetime.now().strftime('%Y%m%d-%H%M')}_{socket.gethostname()}_wifi_scan"
                    wifi_scanner = subprocess.Popen(f"sudo airodump-ng -w {filename} --output-format csv {scan_device}", shell=True, stdout=subprocess.PIPE)
                    print("ok now")
                    scanner_active = True
                    print(f"Wifi scanner active")
                    
                    time.sleep(duration) # duration of the scan
                    wifi_scanner.terminate()
                    subprocess.Popen(f"sudo airmon-ng stop {scan_device}", shell=True)
                    print("Scan complete, sending file...")
                    scanner_active = False
                    self.check_report(f"{filename}-01.csv")
                    
                    # if new_device_detected:
                    # bot send message with details of new device
                    # bot.send_file("PINAS", filename, "Wifi scan")           
            
                time.sleep(interval) # interval between scans

    def check_report(self, file):
        # time.sleep(2)
        # print("READ")
        # print(os.listdir())
        
        print(file)
        # if exists(f"/home/main/Documents/Code/homebot/home_hub/{file}"):
        #     print("IT EXISTS")
        # else:
        #     print("CANT FIND IT")
        #     exit()
        print("reading scan file...")
        report = pd.read_csv(file)
        devices = [d for d in report['BSSID']]
        trusted_devices = [d[0] for d in bot_db.get_all_devices() if d[2] == 1]
        untrusted_devices = [d[0] for d in bot_db.get_all_devices() if d[2] == 0]


        for device in devices:
            try:
                if device not in trusted_devices:
                    print(f"UNTRUSTED DEVICE: {device}")
                if device not in trusted_devices and device not in untrusted_devices:
                    bot_db.add_device(device, datetime.now(), 0)
                    print(f"Added {device} to database as untrusted")
                if device in trusted_devices:
                    print(f"Detected {device} which is OK")
            except Exception as e:
                print(f"Error: {e}")
                bot_db.add_device(device, datetime.now(), 1)
                print("added to db as untrusted")
            print("===============")
        
s = WifiScanner()
# s.check_report("20220223-2128_LMT-Laptop-3_wifi_scan-01.csv")
s.wifi_scan()