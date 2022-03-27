import os
from decouple import config
from datetime import datetime
from tqdm import tqdm

import ntpath, socket, subprocess, threading, time
import bot, bot_db, wifi, rfcon

class HomeHub():
    """
    The instance of the home hub
    Runs the bot, wifi scanner, and other things
    """
    def __init__(self, testing=False, scanning=True) -> None:
        
        # setup
        self.BUFFER_SIZE = 1024
        self.SEPARATOR = "<SEPARATOR>"
        self.testing = testing
        
        # Wifi scanner
        self.wifi_scanner = wifi.WifiScanner(scanning=scanning)
        
        # Remote server
        self.remote_recv_port = int(config("LOCAL_SERVER_RECV_PORT")) # listen on this
        self.remote_send_port = int(config("REMOTE_SERVER_RECV_PORT")) # send on this
        
        # Local network comms
        self.local_recv_port = int(config("LOCAL_HUB_RECV_PORT")) # listen on this
        self.unit_send_port = int(config("LOCAL_UNIT_RECV_PORT")) # send on this
        self.file_recv_port = int(config("LOCAL_HUB_FILE_RECV_PORT")) # listen on this
        
        # Socket listeners
        self.unit_listener_thread = threading.Thread(target=self.unit_listener, daemon=True)
        self.remote_server_listener_thread = threading.Thread(target=self.remote_server_listener, daemon=True)
        self.file_listener_thread = threading.Thread(target=self.file_listener, daemon=True)
        
        # Electrical socket turn off (save electricity!)
        self.power_saver_thread = threading.Thread(target=self.power_saver, daemon=True)
        

        
    def activate_hub(self):
        print("Activating hub")
        if not self.testing:
            bot.activate_bot()
            print("Bot active")
        else:
            bot.activate_bot(testing=True)
            print("Bot in test mode")
        self.unit_listener_thread.start()
        self.file_listener_thread.start()
        self.remote_server_listener_thread.start()
        
        self.wifi_scanner.scan_thread.start()
        
        self.power_saver_thread.start()
        
        print("Hub active")
        
    def unit_listener(self):
        while True:
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0',self.local_recv_port))
            s.listen(5)
            try:
                unit_socket, unit_address = s.accept()
                raw_message = unit_socket.recv(self.BUFFER_SIZE).decode()
                cleaned_message = raw_message.split(self.SEPARATOR)

                unit_name = cleaned_message[0]
                message = cleaned_message[1]
                print(f"Message from {unit_name}: {message}")
                
                s.close()
                
                if message.lower() == "activated":
                    print("add to db")
                    bot_db.insert_unit(int(cleaned_message[2]), cleaned_message[0], unit_address[0], cleaned_message[3], message)
                    
                if cleaned_message[2] == "sendtobot":
                    bot.send_message(message, unitname=unit_name)
                
            except Exception as e:
                print(f"Unit listener: Receive from local network error: {e}")
            
    def remote_server_listener(self):
        while True:
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', self.remote_recv_port))
            s.listen(5)
            try:
                remote_socket, remote_address = s.accept()
                raw_message = remote_socket.recv(self.BUFFER_SIZE).decode()
                cleaned_message = raw_message.split(self.SEPARATOR)

                remote_name = cleaned_message[0]
                message = cleaned_message[1]
                print(f"Message from {remote_name} at {remote_address}: {message}")
                
                if cleaned_message[2] == "sendtobot":
                    bot.send_message(message)

                s.close()
                
            except Exception as e:
                print(f"Remote listener: Receive from remote error: {e}")
                
        
    def file_listener(self):
        while True:
            print("listening for files")
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0',self.file_recv_port))
            s.listen(5)
            print("listening")
            try:
                file_socket, unit_address = s.accept() # did i close this??
                unit_name = bot_db.get_unit_name(unit_address[0])
                print(f"[HUB] Incoming file from {unit_name}")
                
                try:
                    received = file_socket.recv(self.BUFFER_SIZE).decode("utf-8")
                except:
                    received = file_socket.recv(self.BUFFER_SIZE).decode("iso-8859-1")
                print(received)
                # if unit_name is not None:
                    
                print(f"[HUB] Receiving file from {unit_name}")
                # time.sleep(1)
                print(received.split(self.SEPARATOR))
                file, filesize, file_description, file_type = received.split(self.SEPARATOR)
                filesize = int(filesize)
                print(filesize)
                filename = ntpath.basename(file)
                print(filename)
                print("got here")
                progress = tqdm(range(filesize), f"[HUB] Progress {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                with open(filename, "wb") as f: 
                    for _ in progress:
                        bytes_read = file_socket.recv(self.BUFFER_SIZE)
                        if not bytes_read:

                            break
                        f.write(bytes_read)
                        progress.update(len(bytes_read))
                print("ok now received now send to bot")
                # send to bot to send to users
                try:
                    bot.send_message(f"{file_type} incoming from {unit_name}...")
                    bot.send_file(unit_name, filename, file_description)
                except Exception as e:
                    bot.send_message(f"File send attempt failed: {e}")
                
                # s.close()
                # print("SOCKET CLOSED")
                
                
            except Exception as e:
                print(f"File listener: Receive from local network error: {e}")
                # s.close()
                
    def power_saver(self):
        """
        Sends an RF signal that turns off all RF enabled power sockets to save power if they are
        left on late at night
        """
        sent_1 = False
        sent_2 = False
        sent_3 = False
        while True:
            timenow = datetime.now().strftime("%H%M%S")
            if (int(timenow) > 235900) and (int(timenow) < 235910) and not sent_1:
                rfcon.transmit(5, "off") # initially we'll make sure this is the heater...
                time.sleep(2)
                rfcon.transmit(5, "off") # send twice to make sure
                
                print("[HUB] Sent power saver signal 1")
                bot.send_message("Power saver signal 1 sent")
                sent_1 = True
                
            # checking an int value on a number that starts with 0 seems to cause issues, so do it as a string
            if datetime.now().strftime("%H%M") == "0100" and not sent_2:
                rfcon.transmit(5, "off")
                time.sleep(2)
                rfcon.transmit(5, "off")
                
                print("[HUB] Sent power saver signal 2")
                bot.send_message("Power saver signal 2 sent")
                sent_2 = True
                
            if datetime.now().strftime("%H%M") == "0200" and not sent_3:
                rfcon.transmit(5, "off")
                time.sleep(2)
                rfcon.transmit(5, "off")
                
                print("[HUB] Sent power saver signal 3")
                bot.send_message("Power saver signal 3 sent")
                sent_3 = True
                
                
            if datetime.now().strftime("%H%M") == "0600" and sent_1:
                # reset signals
                sent_1 = False
                sent_2 = False
                sent_3 = False
                print("[HUB] Reset power saver booleans")
                
            
                

        

        
        
                
if __name__ == '__main__':
    hub = HomeHub(scanning=False)
    hub.activate_hub()