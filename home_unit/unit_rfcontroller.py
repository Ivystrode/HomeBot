from main_unit import Unit
from rpi_rf import RFDevice
import json

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
    
if __name__ == '__main__':
    with open("rfcodes.json", "r") as f:
        rfcodes1 = json.loads(f.read())
        
        rfcontroller = RfController("RF Controller", rfcodes=rfcodes1)
        
        print(rfcontroller)

