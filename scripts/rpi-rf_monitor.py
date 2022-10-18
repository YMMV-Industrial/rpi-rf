#!/usr/bin/env python3
#
#  YMMV Industrial  -- Basic RF sniffer with logging
#  Original recieve script only writes to standard out, modified log collection to include time stamp
#  and write to a file.  The use case is tracking RF disruptions happening after hours or when someone 
#  isn't watching a screen. Compare events with CCTV to support an investigation.
#  Using the rc switch RPI module but this presumably could be ported to use any protocol and frequency.
#
#  2022-09-16 Original modifications to deal with demo
#



import argparse
import signal
import sys
import time
import logging

# Using Existing RFI module from Micha LaQua (Note,  Raspian needs root unless you mess with perms)
from rpi_rf import RFDevice

# Define location for logging output,  using /var/tmp by default since anyone can write there. Assuming single user system
rfevents_log = '/var/tmp/rfevents.log'


rfdevice = None

# pylint: disable=unused-argument
def exithandler(signal, frame):
    rfdevice.cleanup()
    sys.exit(0)

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s',
                    handlers=[logging.FileHandler(rfevents_log),
                              logging.StreamHandler(sys.stdout)])


parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='gpio', type=int, default=27,
                    help="GPIO pin (Default: 27)")
args = parser.parse_args()

signal.signal(signal.SIGINT, exithandler)
rfdevice = RFDevice(args.gpio)
rfdevice.enable_rx()
timestamp = None
logging.info("Listening for codes on GPIO " + str(args.gpio))
while True:
    if rfdevice.rx_code_timestamp != timestamp:
        timestamp = rfdevice.rx_code_timestamp
        logging.info(str(rfdevice.rx_code) +
                     " [pulselength " + str(rfdevice.rx_pulselength) +
                     ", protocol " + str(rfdevice.rx_proto) + "]")
    time.sleep(0.01)
rfdevice.cleanup()
