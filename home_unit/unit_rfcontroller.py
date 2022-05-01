from main_unit import Unit
from rpi_rf import RFDevice
import json, time

class RfController(Unit):
         
    def __init__(self, unit_type, rfcodes, testing=False):
        super().__init__(unit_type, testing)
        
        self.transmit_codes = rfcodes['transmit_codes']
        self.rfcode_mapping = rfcodes['rfcode_mapping']
        self.PROTOCOL = 1
        self.PULSE_LENGTH = 200

    def transmit(self, plug, on_or_off):
        code = self.rfcode_mapping[plug][on_or_off]
        print(f"Transmitting {code}")
        rfdevice = RFDevice(17)
        rfdevice.enable_tx()
        rfdevice.tx_code(code, self.PROTOCOL, self.PULSE_LENGTH)
        rfdevice.cleanup()
        return code
    
    def activate_all(self):
        print("Activating all devices")
        
        for i in range(1, 6):
            self.transmit(f"plug{i}", "on")
            time.sleep(0.5)
            self.transmit(f"plug{i}", "on")
            time.sleep(0.5)
            
        self.signaller.message_to_hub("Activation message sent to all units", "sendtobot")
    
if __name__ == '__main__':
    with open("rfcodes.json", "r") as f:
        rfcodes1 = json.loads(f.read())
        
        rfcontroller = RfController("RF Controller", rfcodes=rfcodes1)
        
        print(rfcontroller)
