# from rpi_rf import RFDevice
from home_hub.rfcon import Transmitter

# import time

# PROTOCOL = 1
# PULSE_LENGTH = 200
# ONCODE1 = 2314284
# ONCODE2 = 2314282
# ONCODE3 = 2314281
# ONCODE4 = 2314285
# ONCODE5 = 2314283

# OFFCODE1 = 2314276
# OFFCODE2 = 2314274
# OFFCODE3 = 2314273
# OFFCODE4 = 2314277
# OFFCODE5 = 2314275

# def transmit(code):
#     rfdevice = RFDevice(17)
#     rfdevice.enable_tx()
#     rfdevice.tx_code(code, PROTOCOL, PULSE_LENGTH)
#     rfdevice.cleanup()

# def test_all_sockets():
#     time.sleep(3)
#     transmit(ONCODE1)
#     time.sleep(1)
#     transmit(ONCODE2)
#     time.sleep(1)
#     transmit(ONCODE3)
#     time.sleep(1)
#     transmit(ONCODE4)
#     time.sleep(1)
#     transmit(ONCODE5)
#     time.sleep(1)
#     transmit(OFFCODE1)
#     time.sleep(1)
#     transmit(OFFCODE2)
#     time.sleep(1)
#     transmit(OFFCODE3)
#     time.sleep(1)
#     transmit(OFFCODE4)
#     time.sleep(1)
#     transmit(OFFCODE5)
#     time.sleep(1)
    
    
# # test_all_sockets()


t = Transmitter()
t.transmit(t.transmit_codes['ONCODE4'])