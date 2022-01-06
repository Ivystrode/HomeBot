import sys, time, pytest, socket, threading
from decouple import config

sys.path.append("/home/main/Documents/Main/Code/Projects/homebot/home_hub")
import main_hub, bot_db, commands

sys.path.append("/home/main/Documents/Main/Code/Projects/homebot/home_unit")
import main_unit

"""
Run with pytest -rP to see internal test/console output
"""

def test_activate_object_detection():
    """
    Test the process of sending a command to start object detection
    """
    
    hub = main_hub.HomeHub(testing=True)
    hub.activate_hub()
    print("hub active")
    time.sleep(1)
    
    unit = main_unit.HomeUnit("camera", testing=True)
    unit.activate()
    print("unit active")
    time.sleep(1)
    
    commands.send_command("testname", "start_object_detection")
    print("command sent")
    time.sleep(1)
    print(f"RESULT: {unit.camera.object_detection_active}")
    
    assert unit.camera.object_detection_active == True
