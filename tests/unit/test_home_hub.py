import sys, time, pytest, socket
from decouple import config

sys.path.append("/home/main/Documents/Main/Code/Projects/homebot/home_hub")
import main_hub, bot_db, rfcon

def test_add_unit_over_socket():
    """
    Test to see if the hub adds a new unit to the database properly
    when it receives an activation message through the socket.
    The sleep statements stop the test going too quickly.
    """
    
    local_recv_port = int(config("LOCAL_HUB_RECV_PORT"))
    hub_addr = "192.168.1.79"
    sep = "<SEPARATOR>"
    
    hub = main_hub.HomeHub(testing=True)
    hub.activate_hub()
    time.sleep(2)
    
    message = f"testname{sep}Activated{sep}4321431{sep}testunit"
    s = socket.socket()
    s.connect((hub_addr, local_recv_port))
    s.send(message.encode())
    s.close()
    time.sleep(1)
    
    assert bot_db.get_unit_name("192.168.1.79") == "testname"
    assert bot_db.get_unit_address("testname") == "192.168.1.79"
    
def test_bot_rf_comd(plug, cmd):
    """
    Test to see if commands go through properly to correct rf code
    """
    rfcon.transmit(plug, cmd)
    
    assert type(rfcon.transmit(plug, cmd)) == int
    
# test_bot_rf_comd("plug2", "off")