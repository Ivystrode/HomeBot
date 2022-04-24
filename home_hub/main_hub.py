import os
from decouple import config
from datetime import datetime
from tqdm import tqdm

import ntpath, socket, subprocess, threading, time
import bot, bot_db, wifi, atlas_db, atlas_api

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

        # Wifi scanner - runs in additional thread
        self.wifi_scanner = wifi.WifiScanner(scanning=scanning)
        
        # Main thread - API
        # Instantiate the API object
        # Pass self as argument to allow api class
        # to call hub functions
        self.main_api = atlas_api.CentralAPI(self)
             
    def activate_hub(self):
        print("Activating hub")
        if not self.testing:
            bot.activate_bot()
            print("Bot active")
        else:
            bot.activate_bot(testing=True)
            print("Bot in test mode")
            
        # Start threads
        self.unit_listener_thread.start()
        self.file_listener_thread.start()
        self.remote_server_listener_thread.start()
        self.wifi_scanner.scan_thread.start()
        
        # Start API - runs in main thread
        self.main_api.run_api()
        
        print("Hub active")
        
    def api_command(self, command):
        print("RECEIVED COMMAND FROM API")
        print(command)
        
    def unit_listener(self):
        # while True:
        unit_sock = socket.socket()
        unit_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        unit_sock.bind(('0.0.0.0',self.local_recv_port))
        unit_sock.listen()
        
        try:
            sender_unit, unit_address = unit_sock.accept()
            raw_message = sender_unit.recv(self.BUFFER_SIZE).decode()
            cleaned_message = raw_message.split(self.SEPARATOR)

            unit_name = cleaned_message[0]
            message = cleaned_message[1]
            print(f"Message from {unit_name}: {message}")
            
            if message.lower() == "activated":
                print("add to db")
                bot_db.insert_unit(int(cleaned_message[2]), cleaned_message[0], unit_address[0], cleaned_message[3], message)
                try:
                    atlas_db.add_camera(int(cleaned_message[2]), cleaned_message[0], unit_address[0], cleaned_message[3], message)
                except Exception as e:
                    print(f"[HUB] Error adding unit to Atlas DB: {e}")
                    bot.send_message(f"[HUB] Error adding unit to Atlas DB: {e}")
            if cleaned_message[2] == "sendtobot":
                bot.send_message(message, unitname=unit_name)
            
        except Exception as e:
            print(f"Unit listener: Receive from local network error: {e}")
           
        print("[HUB] Restarting unit listener") 
        unit_sock.close()
        self.unit_listener()
            
    def remote_server_listener(self):
        # while True:
        remote_server_socket = socket.socket()
        remote_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        remote_server_socket.bind(('0.0.0.0', self.remote_recv_port))
        remote_server_socket.listen()
        
        try:
            remote_server, remote_address = remote_server_socket.accept()
            raw_message = remote_server.recv(self.BUFFER_SIZE).decode()
            cleaned_message = raw_message.split(self.SEPARATOR)

            remote_name = cleaned_message[0]
            message = cleaned_message[1]
            print(f"Message from {remote_name} at {remote_address}: {message}")
            
            if cleaned_message[2] == "sendtobot":
                bot.send_message(message)
            
        except Exception as e:
            print(f"Remote listener: Receive from remote error: {e}")
            
        print("[HUB] Restarting remote server listener")
        remote_server_socket.close()  
        self.remote_server_listener()
                   
    def file_listener(self):
        # while True:
        print("listening for files")
        file_socket = socket.socket()
        file_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        file_socket.bind(('0.0.0.0',self.file_recv_port))
        file_socket.listen()
        print("listening")
        
        try:
            sender_unit, unit_address = file_socket.accept() # did i close this??
            unit_name = bot_db.get_unit_name(unit_address[0])
            print(f"[HUB] Incoming file from {unit_name}")
            
            try:
                received = sender_unit.recv(self.BUFFER_SIZE).decode("utf-8")
            except:
                received = sender_unit.recv(self.BUFFER_SIZE).decode("iso-8859-1")
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
                    bytes_read = sender_unit.recv(self.BUFFER_SIZE)
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
            
            
        print("[HUB] Restarting file listener")
        file_socket.close()
        self.file_listener()
                


                
if __name__ == '__main__':
    hub = HomeHub(scanning=False)
    hub.activate_hub()