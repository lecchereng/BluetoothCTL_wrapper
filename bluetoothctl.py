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
    
    def __init__(self,clean_output:bool=True,log_level=logging.WARNING):
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

    def __add_output(self,out:str)->None:
        if(self.__clean_outout):
            clean_out=self.clean_output(out)
            self.__logger.debug(f"Adding to output:[{clean_out.encode("raw_unicode_escape")}]")
            self.__output.append(clean_out)
        else:
            self.__logger.debug(f"Adding to output:[{out}]")
            self.__output.append(out)

    def getLogger(self)->logging.Logger:
        return self.__logger

    def send(self, command:str, expected:list[str]=[], pause:int=3)->None:
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
            
    def get_output(self, *args, **kwargs)->str:
        """ Runs a command in bluetoothctl prompt, return output as a list of lines."""
        try:
            self.send(*args, **kwargs)
        except Exception as e:
            raise e   
        return self.read_last_output() #self.read_last_output()
    
    def get_last_match(self)->str:
        """ Gets last string matched the expected output """
        return self.__expected_matched
    
    def set_clean_output(self,clean:bool)->None:
        """ Sets if outut is cleaned from now or not """
        self.__clean_output=clean

    def clean_output(self,output:str)->str:
        """ Cleans output from "dirty characters" used by console to embellish the output """
        # crude but effective
        # remove "blue part"
        output=re.compile("\\x1b\\[\\?[0-9a-zA-Z;]+\\x1b\\[[0-9a-zA-Z;]+[^\\]]+\\]\\x1b\\[[0-9a-zA-Z;]+").sub("",output)
        # And this remove some other unuseful unicode character
        output=re.compile("\\[?\\x1b\\[\\??[\\?0-9a-zA-Z;\r\n]+\\]?").sub("",output)
        # Then trim the string and remove \r chars
        # Should remain just \n,this should not be a problem
        return output.strip().replace("\r","")
         
    def read_last_output(self)->str:
        return self.__output[-1]

    def read_full_output(self)->list[str]:
        """ Returns all output product """
        return self.__output

    def command_help(self)->str:
        """ Gives back help command. Using explained command will guide to write other features wrapped."""
        return self.get_output("help")

    def command_list(self)->str:
        """ Gives back list of connector availables."""
        return self.get_output("list")
        
    def command_devices_connected(self)->str:
        """ Gives sback devices connected."""
        return self.get_output("devices Connected")

    def command_devices_paired(self)->str:
        """ Gives sback devices paired."""
        return self.get_output("devices Paired")

    def command_pair_device(self,dev_mac:str)->str:
        """ Unpairs device with specific mac address. Returning true if device is paired, false if not"""
        expected=["Pairing successful","Device %s not available" % dev_mac]
        out=self.get_output("pair %s" % dev_mac,expected)
        if re.search(expected[0],out):
            return True
        else:
            return False

    def command_trust_device(self,dev_mac:str)->str:
        """ Trusts device with specific mac address. Returning true if device is trusted, false if not"""
        expected=["Device has been removed","Device %s not available" % dev_mac]
        out=self.get_output("remove %s" % dev_mac,expected)
        if re.search(expected[0],out):
            return True
        else:
            return False    
            
    def command_connect_device(self,dev_mac:str)->str:
        """ Connects device with specific mac address. Returning true if device is connected, false if not"""
        expected=["Connection successful","Device %s not available" % dev_mac]
        out=self.get_output("connect %s" % dev_mac,expected)
        if re.search(expected[0],out):
            return True
        else:
            return False
            
    def command_disconnect_device(self,dev_mac:str)->str:
        """ Removes device with specific mac address from list of connected, trusted and paired devices. Returning true if device was disconnected, false if not"""
        expected=["Device has been removed","Device %s not available" % dev_mac]
        out=self.get_output("remove %s" % dev_mac,expected)
        if re.search(expected[0],out):
            return True
        else:
            return False

    def command_scan_on(self,dev_mac:str)->str:
        """ Start scanning and searching for specific mac address"""
        expected=[dev_mac,"Discovery started"]
        out=self.get_output("scan on",expected,5)
        if(re.search(expected[0],out) or re.search(expected[1],out)):
            return True
        else:
            return False
    
    def command_scan_off(self)->None:
        """ Stop scanning """
        out=self.get_output("scan off",["Discovery stopped"])


def parse_device_info(info_string:str):
    """Parse a string corresponding to a device."""
    print(info_string.encode("raw_unicode_escape"))
    device = {}
    block_list = ["[\x1b[0;", "removed"]
    string_valid = not any(keyword in info_string for keyword in block_list)

    if string_valid:
        try:
            device_position = info_string.index("Device")
        except ValueError:
            pass
        else:
            if device_position > -1:
                attribute_list = info_string[device_position:].split(" ", 2)
                device = {
                    "mac_address": attribute_list[1],
                    "name": attribute_list[2]
                }

    return device

def force_reconnect_device(dev_mac:str,log_level=logging.WARNING)->None:
    # I search if my device is paired
    bt=Bluetoothctl(True,log_level)
    dc=bt.command_devices_paired()
    dev_paired=re.search(dev_mac,dc)
    # If someone needs info about devices...
    #if dev_paired:
    #    lines=dc.split("\n")
    #    dev_info={'mac_address':dev_mac,'name':''}
    #    for line in lines:
    #        if re.search(dev_mac,line):
    #            dev_info=parse_device_info(line)
    #    
    if dev_paired:
        bt.command_disconnect_device(dev_mac)
    res=input(f"Would you like to reconnect the {dev_mac} device?\nPress y when device {dev_mac} is pairing ...")
    if(not (res=="y" or res=="Y")):
        print("Stop connecting %s!" % dev_mac)
        return
    # start scanning
    bt.command_scan_on(dev_mac)
    # Pairing devices
    bt.command_pair_device(dev_mac)
    # Connecting devices
    bt.command_connect_device(dev_mac)
    # Stop scanning
    bt.command_scan_off()
