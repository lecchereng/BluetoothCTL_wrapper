#!/usr/bin/env python 

import sys
import re
import logging
import bluetoothctl #import Bluetoothctl
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
def main(dev_macs:list[str]):
    ''' This main remove intersted devices form connected and re-pairing and re-connect them for reset '''
    for dev_mac in dev_macs:
        # I search if my device is paired
        bluetoothctl.force_reconnect_device(dev_mac,logging.DEBUG)
    

if __name__ == "__main__":
    dev_mac=[] #"E4:D7:00:02:73:8C"
    mac_ex="[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}"
    # First I check if all arguments are ok
    for arg in sys.argv:
        if(re.match(mac_ex,arg)):
            print(f"{arg} is ok!")
            dev_mac.append(arg)
        else:
            print(f"{arg} is ko!")
    main(dev_mac)