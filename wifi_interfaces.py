import os, subprocess, time

interfaces = os.listdir("/sys/class/net/")

print(interfaces)


# subprocess.Popen("sudo airmon-ng start enp6s0", shell=True)

def get_scan_device(interfaces):
    wifi_devices = [i for i in interfaces if i.startswith("w") and not i.startswith("wg")]
    for device in wifi_devices:
        print(f"Trying to activate monitor mode on {device}...")
        try:
            subprocess.Popen(f"sudo airmon-ng start {device}", shell=True)
            time.sleep(1)
            if os.path.exists(f"/sys/class/net/{device}mon"):
                print("GREAT SUCCESS!!!")
                return device
            else:
                print("nayh didnt work")
        except Exception as e:
            print(f"Failed to activate monitor mode on {device} - {e}")
            
get_scan_device(interfaces)