"""
This file will control the wifi scanning
"""

from datetime import datetime
import os, socket, shutil, subprocess
import threading, time
from tqdm import tqdm

import bot

class WifiScanner():
    
    def __init__(self, scanning=True):
        self.scan_device = self.get_scan_device()
        self.scanning = scanning # set this to false to stop wifi scanner (via bot command...)
        self.scan_thread = threading.Thread(target=self.wifi_scan, daemon=True)
        
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


    def wifi_scan(self, duration=10, interval=300):
        scanner_active = False
        while True:
            if self.scanning:
                if not scanner_active:
                    filename = f"{datetime.now().strftime('%Y%m%d-%H%M')}_{socket.gethostname()}_wifi_scan"
                    wifi_scanner = subprocess.Popen(f"sudo airodump-ng -w {filename} --output-format csv {self.scan_device}", shell=True, stdout=subprocess.PIPE)
                    scanner_active = True
                    print(f"Wifi scanner active")
                    
                    time.sleep(duration) # duration of the scan
                    wifi_scanner.terminate()
                    subprocess.Popen(f"sudo airmon-ng stop {self.scan_device}", shell=True)
                    print("Scan complete, sending file...")
                    scanner_active = False
                    
                    # if new_device_detected:
                    # bot send message with details of new device
                    bot.send_file("PINAS", filename, "Wifi scan")           
            
                time.sleep(interval) # interval between scans

            
            
            
    def is_new_device():
        pass