from main_unit import Unit
from rpi_rf import RFDevice

class RfController(Unit):
    
    def __init__(self, unit_type, testing=False):
        super().__init__(unit_type, testing)
        
        self.PROTOCOL = 1
        self.PULSE_LENGTH = 200

        self.transmit_codes = {
            'ONCODE1': 2314284,
            'ONCODE2': 2314282,
            'ONCODE3': 2314281,
            'ONCODE4': 2314285,
            'ONCODE5': 2314283,
            'OFFCODE1': 2314276,
            'OFFCODE2': 2314274,
            'OFFCODE3': 2314273,
            'OFFCODE4': 2314277,
            'OFFCODE5': 2314275
        }

        self.rfcode_mapping = {
            "plug1": {"on": 2314284,
                    "off": 2314276},
            "plug2": {"on": 2314282,
                    "off": 2314274},
            "plug3": {"on": 2314281,
                    "off": 2314273},
            "plug4": {"on": 2314285,
                    "off": 2314277},
            "plug5": {"on": 2314283,
                    "off": 2314275}
        }

    def transmit(self, plug, on_or_off):
        code = self.rfcode_mapping[plug][on_or_off]
        print(f"Transmitting {code}")
        rfdevice = RFDevice(17)
        rfdevice.enable_tx()
        rfdevice.tx_code(code, self.PROTOCOL, self.PULSE_LENGTH)
        rfdevice.cleanup()
        return code
    
if __name__ == '__main__':
    rfcontroller = RfController("RF Controller")