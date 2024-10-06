#!/usr/bin/env python
# BluetoothCTL Wrapper
import time
import pexpect
import subprocess
import re
import logging
from logging import StreamHandler
from rich.logging import RichHandler

#logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler(),StreamHandler()],format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
#handler = StreamHandler()
#formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)
#logger.addHandler(handler)
logger = logging.getLogger("Bluettooth_module")

class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""
    
    
    def __init__(self,log_level=logging.WARNING,clean_output:bool=False):
        self.__expected_matched=None
        self.__output=[]
        self.__logger = logging.getLogger("Bluetoothctl")
        self.__expected_common=["Invalid argument","Invalid command","#",pexpect.EOF]
        self.__clean_outout=clean_output
        self.__logger.setLevel(log_level)
        subprocess.check_output("rfkill unblock bluetooth", shell=True)
        self.__process = pexpect.spawnu("bluetoothctl", echo=False)
        self.__logger.info("Process bluetoothctl created")
        expected=["Agent registered"]+self.__expected_common
        expected_index=self.__process.expect(expected)
        self.__logger.debug(f"expected_index={expected_index}")
        if expected_index<0:
            self.__logger.warning(f"Failed after initializing bluetoothctl")
            #raise Exception(f"failed after {command}")
        else:
            self.__expected_matched=expected[expected_index]
            self.__logger.debug(f"expected_matched={self.__expected_matched}")
            self.__add_output(self.__process.before)

    def __add_output(self,out:str):
        if(self.__clean_outout):
            clean_out=self.clean_output(out)
            self.__logger.debug(f"Adding to output:[{clean_out}]")
            self.__output.append(clean_out)
        else:
            self.__logger.debug(f"Adding to output:[{out}]")
            self.__output.append(out)

    def getLogger(self):
        return self.__logger

    def send(self, command, expected:list[str]=[], pause=3):
        """ This method is the core of the class. It sends command to the bluetoothctl process and undetand when an answer arrived """
        self.__expected_matched=None
        self.__process.send(f"{command}\n")
        time.sleep(pause)
        # Default expected in output, I don't want repetetion
        for common_ex in self.__expected_common:
            if common_ex not in expected:
                expected.append(common_ex)
        self.__logger.info(f"Sending command [{command}] with expected=[{expected}] and pause=[{pause}]")
        expected_index=self.__process.expect(expected)
        self.__logger.debug(f"expected_index={expected_index}")
        if expected_index<0:
            self.__logger.warning(f"Failed after {command}",e)
            raise Exception(f"failed after {command}")
        else:
            self.__expected_matched=expected[expected_index]
            self.__logger.debug(f"expected_matched={self.__expected_matched}")
            self.__add_output(self.__process.before)
            
    def get_output(self, *args, **kwargs):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        try:
            self.send(*args, **kwargs)
        except Exception as e:
            raise e   
        return self.__process.before #self.read_last_output()
    
    def get_last_match(self):
        return self.__expected_matched
    
    def set_clean_output(self,clean:bool):
        self.__clean_output=clean


    def clean_output(self,output:str):
        """ clean output from "dirty characters" used by console to embellish the output """
        # crude but effective
        # remove "blue part"
        output=re.compile("\r\n\\x1b\\[\\?2004h\\x1b\\[0;94m\\[[^\\]]+\\]\\x1b\\[0m").sub("",output)
        output=re.compile("\\s\\x1b\\[\\??[0-9a-zA-z;]+\\s*").sub("",output)
        return output
         
    def read_last_output(self):
        return self.__output[-1]

    def read_full_output(self):
        return self.__output

    def get_last_expected(self):
        return self.__last_expected

    def command_help(self):
        """Give back help command. Using explained command will guide to write other features wrapped."""
        return self.get_output("help")

    def command_list(self):
        """Give back list of connector availables."""
        return self.get_output("list")
        
    def command_devices_connected(self):
        """Give back devices connected."""
        return self.get_output("devices Connected")

    def command_devices_paired(self):
        """Give back devices paireded."""
        return self.get_output("devices Paired")

    def command_pair_device(self,dev_mac:str):
        """Unpair device with specific mac address. Returning true if device was paired, false if device was unpaired"""
        expected=["Pairing successful","Device %s not available" % dev_mac]
        out=self.get_output("pair %s" % dev_mac,expected)
        if re.search(expected[0],out):
            return True
        else:
            return False

    def command_trust_device(self,dev_mac:str):
        """Unpair device with specific mac address. Returning true if device was paired, false if device was unpaired"""
        expected=["Device has been removed","Device %s not available" % dev_mac]
        out=self.get_output("remove %s" % dev_mac,expected)
        if re.search(expected[0],out):
            return True
        else:
            return False    
            
    def command_connect_device(self,dev_mac:str):
        """Unpair device with specific mac address. Returning true if device was paired, false if device was unpaired"""
        expected=["Connection successful","Device %s not available" % dev_mac]
        out=self.get_output("connect %s" % dev_mac,expected)
        if re.search(expected[0],out):
            return True
        else:
            return False
            
    def command_disconnect_device(self,dev_mac:str):
        """Unpair device with specific mac address. Returning true if device was paired, false if device was unpaired"""
        expected=["Device has been removed","Device %s not available" % dev_mac]
        out=self.get_output("remove %s" % dev_mac,expected)
        if re.search(expected[0],out):
            return True
        else:
            return False

    def command_scan_on(self,dev_mac:str):
        """ Start scanning """
        expected=[dev_mac,"Discovery started"]
        out=self.get_output("scan on",expected,5)
        if(re.search(expected[0],out) or re.search(expected[1],out)):
            return True
        else:
            return False
    
    def command_scan_off(self):
        """ Stop scanning """
        out=self.get_output("scan off",["Discovery stopped"])


def force_reconnect_device(dev_mac:str,log_level=logging.WARNING):
    # I search if my device is paired
    bt=Bluetoothctl(log_level)
    dc=bt.command_devices_paired()
    dev_paired=re.search(dev_mac,dc)
    if dev_paired:
        bt.command_disconnect_device(dev_mac)
    res=input("Press enter when device %s is pairing ..." % dev_mac)
    # start scanning
    bt.command_scan_on(dev_mac)
    # Pairing devices
    bt.command_pair_device(dev_mac)
    # Connecting devices
    bt.command_connect_device(dev_mac)
    # Stop scanning
    bt.command_scan_off()