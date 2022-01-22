# from rpi_rf import RFDevice

# class Transmitter():

PROTOCOL = 1
PULSE_LENGTH = 200

transmit_codes = {
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

rfcode_mapping = {
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

def transmit(plug, on_or_off):
    code = rfcode_mapping[plug][on_or_off]
    print(f"Transmitting {code}")
    rfdevice = RFDevice(17)
    rfdevice.enable_tx()
    rfdevice.tx_code(code, PROTOCOL, PULSE_LENGTH)
    rfdevice.cleanup()
    return code
        
