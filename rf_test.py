#!/usr/bin/env python3

import argparse
import logging
import time

from rpi_rf import RFDevice

# PLUG 1 ON: CODE: 2314284 PULSELENGTH: 200 PROTOCOL: 1
# PLUG 1 OFF: CODE: 2314276 PULSELENGTH: 200 PROTOCOL: 1

#PLUG 2
# 2314282 [pulselength 200, protocol 1]
# 2314274 [pulselength 202, protocol 1]

#PLUG 3
#  2314281 [pulselength 200, protocol 1]
# 2314273 [pulselength 201, protocol 1]

# PLUG 4
# 2314285 [pulselength 201, protocol 1]
# 2314277 [pulselength 200, protocol 1]

# PLUG 5
# 2314283 [pulselength 200, protocol 1]
# 2314275 [pulselength 202, protocol 1]

# rfdevice = RFDevice(17)
# rfdevice.enable_tx()

PROTOCOL = 1
PULSE_LENGTH = 200
ONCODE1 = 2314284
ONCODE2 = 2314282
ONCODE3 = 2314281
ONCODE4 = 2314285
ONCODE5 = 2314283

OFFCODE1 = 2314276
OFFCODE2 = 2314274
OFFCODE3 = 2314273
OFFCODE4 = 2314277
OFFCODE5 = 2314275

def transmit(code):
    rfdevice = RFDevice(17)
    rfdevice.enable_tx()
    rfdevice.tx_code(code, PROTOCOL, PULSE_LENGTH)
    rfdevice.cleanup()

def test_all_sockets():
    time.sleep(3)
    transmit(ONCODE1)
    time.sleep(1)
    transmit(ONCODE2)
    time.sleep(1)
    transmit(ONCODE3)
    time.sleep(1)
    transmit(ONCODE4)
    time.sleep(1)
    transmit(ONCODE5)
    time.sleep(1)
    transmit(OFFCODE1)
    time.sleep(1)
    transmit(OFFCODE2)
    time.sleep(1)
    transmit(OFFCODE3)
    time.sleep(1)
    transmit(OFFCODE4)
    time.sleep(1)
    transmit(OFFCODE5)
    time.sleep(1)
    
    
test_all_sockets()