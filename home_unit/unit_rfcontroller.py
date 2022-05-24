from main_unit import Unit
from rpi_rf import RFDevice
import json, time, logging

class RfController(Unit):
         
    def __init__(self, unit_type, rfcodes, testing=False):
        super().__init__(unit_type, testing)
        
        self.transmit_codes = rfcodes['transmit_codes']
        self.rfcode_mapping = rfcodes['rfcode_mapping']
        self.PROTOCOL = 1
        self.PULSE_LENGTH = 200

    def transmit(self, plug, on_or_off):
        logger.info(f"Transmitting {on_or_off} to {plug}")
        code = self.rfcode_mapping[plug][on_or_off]
        logger.info(f"Transmit code: {code}")
        rfdevice = RFDevice(17)
        rfdevice.enable_tx()
        rfdevice.tx_code(code, self.PROTOCOL, self.PULSE_LENGTH)
        rfdevice.cleanup()
        logger.info("Transmit complete")
        return code
    
    def activate_all(self):
        logger.info("Activating all devices")
        
        for i in range(1, 6):
            self.transmit(f"plug{str(i)}", "on")
            time.sleep(0.5)
            self.transmit(f"plug{str(i)}", "on")
            time.sleep(0.5)
            
        self.signaller.message_to_hub("Activation signal transmitted to all units", "sendtobot")
        
    def deactivate_all(self):
        logger.info("Deactivating all devices")
        
        for i in range(1, 6):
            self.transmit(f"plug{str(i)}", "off")
            time.sleep(0.5)
            self.transmit(f"plug{str(i)}", "off")
            time.sleep(0.5)
            
        self.signaller.message_to_hub("Deactivation signal transmitted to all units", "sendtobot")
        
    def on(self, plug):
        self.transmit(f"plug{str(plug)}", "on")
        self.signaller.message_to_hub(f"Transmitted on signal to plug {str(plug)}", "sendtobot")
        
    def off(self, plug):
        self.transmit(f"plug{str(plug)}", "off")
        self.signaller.message_to_hub(f"Transmitted off signal to plug {str(plug)}", "sendtobot")
    
if __name__ == '__main__':
    with open("/home/pi/Code/HomeBot/home_unit/rfcodes.json", "r") as f:
        rfcodes1 = json.loads(f.read())
        
    rfcontroller = RfController("RF Controller", rfcodes=rfcodes1)
    
    print(rfcontroller)
    logging.basicConfig(filename="cam_unit.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
