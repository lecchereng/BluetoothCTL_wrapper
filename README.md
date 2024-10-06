# BluetoothCTL_wrapper
A Bluetoothctl wrapper in Python

This wrapper is inspired by the wrapper I saw based on ReachView from @egorf Egor Fedorov and also @dmeulen Danny van der Meulen  modification. I focused this version on functionality analysing the outuput of any commands: for each command sent, the output that came out is parsed to understand what happened. This work is inspired by

[https://gist.github.com/egorf/66d88056a9d703928f93](https://gist.github.com/egorf/66d88056a9d703928f93)

[https://gist.github.com/dmeulen/02591532170ce3b5734946452cea38a1](https://gist.github.com/dmeulen/02591532170ce3b5734946452cea38a1)

[https://forums.raspberrypi.com/viewtopic.php?t=170680](https://forums.raspberrypi.com/viewtopic.php?t=170680)

## BluettothCTL module
Inside the python file, there is a class that wraps the bluetoothctl command for a few of its features. I implemented it to resolve an issue I implemented in the other feature the module also provides.
## How to use Bluetootctl class
The bluetoothctl constructor lets you chose the debug level and also if the output brought from bluetoothctl tool is cleared from trappings of colours and so on. It controls the program through the [pexpect](https://pexpect.readthedocs.io/en/stable/) module.
However, the core fature of the class is the call method. All the other ones are based on it, passing command with its params, expected output array strings and specifying a reasonable time to wait between the command and the output it produces.
I suggest for example, as you find in command_scan_on metod to wait a few seconds the bluetoothctl tool to search your device before searching expected string in output.
You have to refer to the device with its mac address.
## All features implemented
Bluetoothctl methods
- constructor(log_level=logging.WARNING,clean_output:bool=False) : create Bluetoothctl object with specific log level and cleaning output or not
- getLogger() : to get logger and modify it
- send(command:str, expected:list[str]=[], pause:int=3) : sends command to bluetoothctl, expecting output string array and waiting 3 seconds before anlysing the output. It sets last expeted_inde, last expected_string, last output
- get_output((self, *args, **kwargs) : call send() and reeturn the output
- get_last_match() : return the last expected string matched by last command
- set_clean_output(bool) : set if the output coming from bluetoothctl is cleaned by trapping
- read_last_output() : return output of last command
- read_full_output() : return the array of all output produced since now
- command_help() : gives back help command. Using the explained command will guide to write other features wrapped.
- command_list() : gives back a list of connector available.
- command_devices_connected() : gives sback devices connected.
- command_devices_paired() : gives back devices paired.
- command_pair_device(mac:str) : unpairs device with specific mac address. Returning true if device was paired, false if not
- command_trust_device(mac:str) : trusts device with specific mac address. Returning true if device was trusted, false if not
- command_connect_device(mac:str) : connects device with specific mac address. Returning true if device was paired, false if not
- command_disconnect_device(mac:str) : removes device with specific mac address from list of connected, trusted and paired devices. Returning true if device was disconnected, false if not
- command_scan_on(mac:str) : start scanning for the specific device. Return true if device is found,false if not
- command_scan_off() : stop scanning

Core feature:
- force_reconnect_device(dev_mac:str,log_level=logging.WARNING) : removes device, than pairs, trusts and connects it
## Test the core feature
You need the mac address (as A1:B2:C3:D4:E5:F6) of your device and test it just run the main.py passing it. It use the class to search into paired devices, remove it and then, when your device is in paring mode, going on pressing the enter key to scan for it, pair it and connect it before stoppiing scan.
To test it try:
```
./main.py A1:B2:C3:D4:E5:F6 A2:B6:C7:D8:E9:F0 ...
```
using the mac_address of your devices. You can see it using the command_device_paired method which shows precisely the list of connected deivces.
## Improve the features
Improve the other features of bluetoothctl shall be quite simple. You just need to keep the example of the implemented methods. You can also change something using the name of device istead of the mac_address in searching mode but as for bluetoothctl tool you need the mac_address to connect to.
