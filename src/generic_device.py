"""
TODO - Copy from readme.md
"""
from typing import Optional, Set, cast, Union, Protocol, List, final
from abc import ABC, abstractmethod
from warnings import warn
import re # Used for str to float conversion
import atexit

from time import sleep, perf_counter
from random import random

# from src.util.logging import logger
import pyvisa
from src.util.errors import DeviceConnectionError, DeviceInitializationError, DeviceChannelError
from src.enums.generic_enum import DeviceInfo, ReadWrite, Channel, ConnectionType, ConnectionInfo
from src.registry import DeviceRegistry

print("Importing <== Device.py")

# Protocol Drivers
class ConnectionProtocol(Protocol):
    """
    Simple protocol to read and write to device. Created to support simulated hardware.
    """
    def write(self, command: str) -> None:
        """
        Send write command to device.
        """

    def query(self, command: str) -> str:
        """
        Send command then query response of device.
        """

class VisaDeviceConnection:
    """        Connection to device using VISA backend.        """
    def __init__(self, device: pyvisa.resources.MessageBasedResource):
        self.device = device

    def write(self, command: str) -> None:
        """        Send write command to device.        """
        self.device.write(command)

    def query(self, command: str) -> str:
        """        Send command then query response of device.        """
        return self.device.query(command)

class SimulatedDeviceConnection:
    """        Simulated connection to device.        """
    def write(self, command: str) -> None:
        """        Simulated Send write command to device.        """
        command = command + " "
        return None

    def query(self, command: str) -> str:
        """        Simulated Send write command to device.        """
        command = command + " "
        return str(random())

# Basic Device Connection
class DeviceConnection():
    '''
    The main goal of this class is to (1) establish a connection with the device, 
    and (2) to identify the device.

    Once we've identified the device, we can initialize the specific device class.

    Attributes:
        _info (ConnectionInfo): Connection info for this device. Some of this info is passed in during init.
        _visa_device_com (ConnectionProtocol): Protocol interface supporting read and write.
        _visa_device (pyvisa.resources.MessageBasedResource | None): True visa device if one exists. None if HW is simulated.
    '''

    def __init__(self, resource: str, connection_type : ConnectionType, **kwargs):
        '''
        Initialization for DeviceConnection. Note by default debug mode is disabled, and hardware is not simulated.

        Parameters:
            resource (str): The resource string for the device
            connection_type (ConnectionType): The type of connection (GPIB, USB, Ethernet, RS232)
        **kwargs
            EnableDebug : bool = False
            SimulatedHW : bool = False
            Forced_Driver : str = "none"        //Come hell or high water, we will use this driver, set if using simulated HW
        '''

        # Everything related to the device conneciton is stored in the self._info dataclass
        self._info = ConnectionInfo()
        self._info.connection_type = connection_type
        self._info.resource = self._define_port(resource, connection_type)

        # Pull Data from kwargs - Note we will not warn the user of typos or bad inputs
        self._info.enable_debug = cast( bool, kwargs.get('EnableDebug', False))
        self._info.simulated_hw = cast( bool, kwargs.get('SimulatedHW', False))
        self._info.forced_driver = cast(str, kwargs.get('Forced_Driver', self._info.forced_driver)).lower() # Force Lowercase

        # Variables - Device Connection
        # I had to do some wonky stuff here to support simulated HW.... in general you should only ever be talking to the __VisaDevice_RdWr object
        # The only time we will use _VisaDevice is when we want to set connection specific attributes such as timeouts ect
        self._visa_device_com : ConnectionProtocol = self._connect(self._info.resource)   # Object to be read to or written from
        self._visa_device : Union[pyvisa.resources.MessageBasedResource, None] = None        # The true device - None if simulating HW 

        if isinstance(self._visa_device_com, VisaDeviceConnection):
            self._visa_device = self._visa_device_com.device

    # Private Methods
    def _define_port(self, resource: str, connection_type: ConnectionType) -> str:
        """
        Defines the port string for the device based on the connection type.

        Parameters:
            resource (str): The resource string for the device.
            connection_type (ConnectionType): The type of connection (GPIB, USB, Ethernet, RS232).
        """

        # if connection_type == ConnectionType.GPIB:
        #     resource = f"GPIB0::{resource}::INSTR"  # Bad assumption
        # elif connection_type == ConnectionType.USB:
        #     resource = f"USB::{resource}::INSTR"
        if connection_type == ConnectionType.ETHERNET:
            resource = f"TCPIP::{resource}::INSTR"
        elif connection_type == ConnectionType.RAW:
            # do nothing, try to connect to whatever user sent
            pass
        else:
            raise ValueError("Unsupported connection type")
        return resource

    def _connect(self, resource: str, num_retry: int = 3) -> ConnectionProtocol:
        '''
        Connect to the device using the VISA/PyVisa-py backend, or simulate the connection if the 
        device is not available.

        Parameters:
            resource (str): The resource string for the device.
            num_retry (int): Number of times to retry connecting to the device. Default is 3.
        Returns:
            ConnectionProtocol: The connection object for the device.
        Raises:
            ConnectionError: Failed to connect after num_retry.
        '''
       
        if self._info.simulated_hw:
            return SimulatedDeviceConnection()

        for attempt_i in range(num_retry):
            try: 
                # Try to connect using default backend
                device = cast(pyvisa.resources.MessageBasedResource, pyvisa.ResourceManager().open_resource(resource))
                break
            except pyvisa.errors.VisaIOError:
                try: 
                    # If failed try using pyvisa-py backend
                    device = cast(pyvisa.resources.MessageBasedResource, pyvisa.ResourceManager('@py').open_resource(resource))
                    break
                except Exception as e:
                    # Log the error or handle it as needed
                    print(f"Attempt {attempt_i + 1} failed with error: {e}")
                    # Some devices just need multiple attempts to connect
                    if attempt_i == (num_retry - 1):
                        raise ConnectionError(f"Failed to connect to device after 3 attempts -> @{resource}") from e
                    
            sleep(1)
        
        return VisaDeviceConnection(device)

    def identify(self, id_cmd : Optional[str] = None) -> str:
        """
        Identify the device using all possible IDN commands. If a forced driver is set, that <IDN>
        command will be used. If the device is simulated, the forced driver MUST be set.
        
        Returns:
            str: The model number of the device "manufacturer_model". Empty string if not found.

        Raises:
            DeviceConnectionError: Failed to identify the device, or forced driver doesn't match found device
        """

        # There are three different ways to identify our device...
        # (1) We are using simulated HW - Return forced driver (if available), else raise error
        # (2) We are using a forced driver - Verify the endpoint device is the same class, then return the forced driver
        # (3) We are using a real device - Try all possible IDN commands to identify the device
        flag_hw_sim : bool = self._info.simulated_hw
        forced_driver : str = self._info.forced_driver
        manf_model : Union[None|str] = None

        # Case (1) - Simulated HW
        if flag_hw_sim is True:
            
            # In the future we could return default devices for simualted hardware
            if forced_driver == "none":
                raise ValueError("Simulated HW requires a forced driver to be set. What device should we simulate?")
            
            return forced_driver

        # Case (2) - Forced Driver
        elif forced_driver != "none":
            reg_info = DeviceRegistry.get_device_info(manufacturer = forced_driver.split("_")[0], model = forced_driver.split("_")[1])
            id_cmd = reg_info.id_cmd

        # Case (3) - Real Device, AutoDetect Driver
        if self._visa_device is not None:
            
            if id_cmd is None:
                unique_idn_commands = DeviceRegistry.list_unique_id_cmds()
            else:
                unique_idn_commands = [id_cmd]

            # Temporarily reduce the timeout
            old_timeout = self._visa_device.timeout
            self._visa_device.timeout = 1500    

            for idn_command in unique_idn_commands:
                print("Sending command <" + idn_command + ">", end = " ")
                
                try:
                    response = cast( str, self._visa_device_com.query(idn_command))
                    
                    # Some devices give bad responses on first query
                    # If the repsonse is supicously short, best to just query again
                    if len(response) <  8:
                        response = cast( str, self._visa_device_com.query(idn_command))
                    print( str(" <--- " + response).strip("\n\r") )
                    
                    # TODO - Check that response isn't entirely numeric
                    # Some devices will respond with a reading for ANY query

                    if response:
                        manf_model = DeviceRegistry.get_registered_device(response )
                        
                        if manf_model != '':
                            break
                        
                # This will cause driver timeouts as we guess what IDN is valid
                except pyvisa.errors.VisaIOError:
                    print(" <--- Timeout")
                    continue

            self._visa_device.timeout = old_timeout

        # Did we find a device?        
        if manf_model is None or manf_model == '':
            if forced_driver != "none":
                if input(f"Warning - Unable to verify that the device connected at <{self._info.resource}> port matches the forced driver. Continue anyway? (y/n)") == "y":
                    return forced_driver
            raise DeviceConnectionError("Failed to identify model using available 'IDN' commands.")
        
        # Sanity check that (2) forced driver, matches the detected device
        if forced_driver != "none" and (forced_driver.lower() != manf_model.lower()):
            raise DeviceInitializationError(message = f"Forced driver {forced_driver} does not match detected device {manf_model}")
    
        return manf_model
    
    def _reconnect(self) -> None:
        '''
        WARNING - This method is pretty untested... may be removed shortly
        This method should only be called when an already established connection raises some unkown error.
        This method will close the device then attempt to re-establish the connection.
        NOTE - Testing w/ Ethernet, GPIB, 
        ISSUE - Currently this method isn't able to fully reestablish connection. Work to be done at home.

        Parameters:
            NONE, however class attributes are accessed
            self.__VisaDevice_RdWr
            self.VisaDevice
        '''

        # This is a simulated device no sense reconnecting
        if self._visa_device is None:
            return None

        # Try to close the device - TODO - lots of testing to ensure reconnect works good
        try:
            self._visa_device.close()  # close the device
            pyvisa.ResourceManager().close() # GPIB needs to have the resource mangager closed
            self._visa_device.open()
        except Exception as e:
            print(f"Error occured while trying to close device... Continuing anyway {e}")

        self._visa_device_com = self._connect(self._info.resource, num_retry=15)

        if isinstance( self._visa_device_com, VisaDeviceConnection):
            self._visa_device = self._visa_device_com.device

        return None

    def send_command(self, command: str, read_write : ReadWrite = ReadWrite.AUTO) -> str:
        """
        Send a command to the device. Read or Write is auto detected by default.

        Parameters:
            command (str): The command to send to the device.
            RW (RdWr): Read or Write. Default is auto detected.
        Returns:
            str: The response from the device. ( This is "" for write commands )
        """

        start_time = perf_counter()
        send_str : str = "" # Debug string - Sent command
        rcvd_str : str = "" # Debug string - Received from device
        
        # Auto Detect Read or Write
        if read_write == ReadWrite.AUTO:
            if command.find("?") != -1:
                read_write = ReadWrite.READ
            else:
                read_write = ReadWrite.WRITE

        # Send Command - Write
        if read_write == ReadWrite.WRITE:
            send_str = "Send Command -> " + command
            self._visa_device_com.write(command)
            sleep(0.001)

        # Send Command - Read
        elif read_write == ReadWrite.READ:
            send_str = "Send Query -> " + command
            rcvd_str = self._visa_device_com.query(command)
    
        if self._info.simulated_hw:
            send_str += " (Simulated)"

        # Debug Prints
        end_time = perf_counter()
        if self._info.enable_debug:
            if read_write == ReadWrite.READ:
                print("\n============ DEBUG ============\n" +
                        send_str + "\n" +
                        "==DELAY== "+str( round(end_time-start_time, 3) ) + "\n" +
                        "SCPI Rcvd <- " + repr(rcvd_str) + "\n"
                        "============ DEBUG ============")
            else:
                print("\n============ DEBUG ============\n" +
                        send_str + "\n" +
                        "============ DEBUG ============")
        
        return rcvd_str.strip("\n\r")
    
    @staticmethod
    def available_devices() -> Set[str]:
        """
        Returns a set of available devices. 
        Useful to identify the resource string for the device.
        """
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        return set(resources)

# Base Class -> class Custom_Driver(PSU(GenericDevice)):
class GenericDevice(ABC):
    '''
    This is an extremely generic device. Base class for all devices (PSU, DMM, FGEN, ect).

    Attributes:
        device_info (DeviceInfo): Device information.
        device_connection (DeviceConnection): Connection to the device.
    '''
    # This will be quickly overwritten by the child data
    device_info = DeviceInfo()

    def __init__(self, deviceconnection : DeviceConnection):
        '''
        Adds device_connection to class attributes. 

        Parameters:
            deviceconnection (DeviceConnection): Connection to the device.

        Raises:
            ValueError: If the device type does not match the expected device
        '''
        self.device_connection = deviceconnection   # Visa device we will interact with
        atexit.register(self.cleanup)               # Effectively makes cleanup a destructor
        
        print(f"GenericDevice.__init__() --> {self.device_info.manufacturer} {self.device_info.model}")

        # Sanity check device is the type we expect...
        # This should only be possible if we Force the driver, but even then I think it would cause an errror
        if self.device_info.device_type != DeviceRegistry.get_device_info(self.device_info.manufacturer, self.device_info.model).device_type:
            raise ValueError("Device type does not match the expected device type.")
    
    @final
    def cleanup(self) -> None:
        '''
        Closes visa device connection if it exists.
        Class child class _cleanup method to ensure it ends in a safe sta
        TODO - add atexit to method
        '''
        print(f"Cleanup Device --> {self.device_info.manufacturer} {self.device_info.model}")

        # First cleanup device
        self._cleanup()

        # Then close the connection
        if self.device_connection._visa_device is not None:
            self.device_connection._visa_device.close()

    @abstractmethod
    def _cleanup(self) -> None:
        '''
        Device specifc cleanup method... must be implemented by child
        Example - disable all the outputs on a PSU.
        '''
        return None
    
    # Public Methods
    def send_command(self, command: str, read_write : ReadWrite = ReadWrite.AUTO, skip_opc : bool = False) -> str:
        """
        Send a command to the device. Read or Write is auto detected by default.
        Warning - If your defining _Operation_Wait() be sure to set skipOPC to True else you will have a deadlock.
        Will reattempt to send command 5 times before raising an error.

        Parameters:
            command (str): The command to send to the device.
            RW (RdWr): Read or Write. Default is auto detected.
            SkipOPC (bool): Skip the previous Operation Complete check. Default is False.

        Returns:
            str: The response from the device. ( This is "" for write commands )
        """
        com_error = 0

        # Ensure the previous command completed
        # Some devices really benefit from this, others seem to manage regardless
        if not skip_opc:
            self._operation_wait()

        # Attempt to send command
        while com_error < 5:
            try:
                response = self.device_connection.send_command(command, read_write)
                break
            except pyvisa.VisaIOError as e:
                print(f"\nERROR {com_error+1} Occured during visa command <{command}>"
                      f" @{self.device_info.device_type.value} -> {self.device_info.manufacturer}_{self.device_info.model}\n{e}\n\n")
                
                # If this is a VI_ERROR_CONN_LOST error, try to reconnect
                if e.error_code == -1073807194:
                    print("\nERROR - Attempting to reconnect to device... This method doesn't really work yet"
                          "needs much more testing, maybe not possible in certain scenarios\n"
                          "Anyway in we go!!!!")
                    self.device_connection._reconnect()

                sleep(1)
            
            # On 5th attempt let error propogate
            com_error += 1
            if com_error == 5:
                response = self.device_connection.send_command(command, read_write)
        
        return response

    def get_id(self) -> str:
        '''
        Query device ID. Tyipcally using *IDN?, but depends on device.

        Returns
            str : Raw, unparsed response from device.
        '''
        str_cmd = self.device_info.id_cmd
        return self.send_command(str_cmd, ReadWrite.READ)

    # Protected Methods
    def _warn_unimplemented(self, method_name: str):
        """
        Warn the user that a method is not implemented.

        Parameters:
            method_name (str): The name of the unimplemented method.
        """
        print(f">>> Warning: The method '{method_name}' is not implemented for the device -> {self.device_info.manufacturer} {self.device_info.model}")
    
    def _error_unimplemented(self, method_name: str, comment : str):
        """
        Warn the user that a method is not implemented. Call this if the missing implemenation is deamed safety critical.

        Parameters:
            method_name (str): The name of the unimplemented method.
            comment (str): Extra comment added to error printout. Best to leave breadcrumbs.

        Raises:
            NotImplementedError
        """
        print("ERROR!!! Critical method not implemented", end="")

        # Print some dots to make it look like we're doing something
        for i in range(5):
            print(".", end="")
            sleep(1)
        print("\n")

        raise NotImplementedError(f"The method '{method_name}' is not implemented for the device -> " + self.device_info.manufacturer + self.device_info.model + 
                                  f"\n{comment}")

    def _check_channel_exists(self, channel : Union[list[Channel], Channel]) -> bool:
        '''
        Check if the channel exists on the specified device.
        
        Parameters:
            channel (list[Channel] | Channel ): Either list of channels or single channel

        Returns:
            bool: True if the channel(s) exist(s), otherwise raises an exception.
        
        Raises:
            DeviceChannelError: If any channel in the list or the single channel does not exist on the device.
        '''
        channel = self._convert_channel_type(channel)

        for ch in channel:
            if ch not in self.device_info.available_channels:
                raise DeviceChannelError(f"Channel {channel} does not exist on this device. {self.device_info.model}")
        
        return True

    def _convert_channel_type(self, channel: Union[List[Channel], Channel]) -> list[Channel]:
        '''
        Helper fnction that ensures the type is always uniform in other class methods.\n
        If the input is of isinstance of Channel, then it converts it to be a list[Channel] of size 1.

        Parameters:
            channel (list[Channel] | Channel ): Either list of channels or single channel
        
        returns:
            list[Channel]: list of channels.
        '''
        channel_list = [channel] if isinstance(channel, Channel) else channel
        return channel_list

    def _check_device_type(self):
        return None

    @abstractmethod
    def _operation_wait(self) -> None:
        '''
        Many devices support an *OPC? command that returns 1 when all pending operations are complete.
        Calling this following some write command dramatically increases the overall stability of the system.
        
        WARNING - Ensure skipOPC is set to True in all send_command() calls within this method!!!
        Else you WILL introduce an infinite loop!

        TODO - I think make one version of Operation_Wait that is private to GenericDevice and NOT overwritten
        And make another then gets overwritten... the private one can just take the str and pass it to send_command with the SkipOPC flag set
        This doesn't rely on the user to remember to set the flag, and it's less code to write.
        '''
        return None

    @final
    def test_all_methods(self) ->None:
        '''
        This method calls every method in the device class and automatically.\n
        checks that it works when possible. User must verify the printouts to determine pass/fail.\n
        '''
        print("\n======================== Test Mode ========================\n"
               f" {self.device_info.device_type.name} --> {self.device_info.manufacturer} {self.device_info.model}\n"
                " NOTE - There are two likely causes for issues\n"
                " 1) The commands are being sent too quickly. In this\n"
                "    case you need to tweak the _operation_wait() method\n"
                " 2) You are sending the wrong commands to the device.\n"
                "    Verify the strings being sent to the device by enabling debug.\n"
                "    Try using the send_command() method directly, or use NI MAX.\n"
                "===============================================================\n"
                " Disconnect all devices from DUT before starting test\n"
                "===============================================================\n")
        input("Press Enter to continue...")
        self._test_all_methods()
        print("\n======================== Test Complete ========================\n")

    @abstractmethod
    def _test_all_methods(self) -> None:
        '''
        This method calls every method in the device class and automatically.\n
        checks that it works when possible. User must verify the printouts to determine pass/fail.\n
        '''
        return None      


    @staticmethod
    def _safe_string_to_float(input_str:str) -> list[float]:
        '''
        Returns a list of numeric values parsed out of a string.\n
        Formatting responses can be tricky, due to the variety of instrument formatting.\n
        This method tries to find the following formatted substrings within main string \n
        (1) Scientific Notation -> +-x.xxxE+-x \n
        (2) Floating Poitn ------> +-x.xxxx \n
        (3) Integer -------------> +-x \n

        Parameters:
            input_str: (str) - Raw response from device.
        
        Returns:
            list[float] - All elements that match the above formats. Only 1 format will be used, priority as shown.
        
        Raises:
            warning : warn - Warns the user if unable to parse string. Returns [0.0]
        '''
        float_vals : list[float] = []
        # print(input_str + " --> ", end="")

        # First just to to convert to float
        # If this works its much faster than parsing the string
        try:
            temp_float = float(input_str)
            return [temp_float]
        except ValueError:
            pass

        # Scientific Notation
        # [\s|+-]? --> First character is +|-|<whitespace>|Nothing
        # \d+ ------> Next character is a 0-9, followed by 'n' more digits
        # \. -------> Followed by one decimal point
        # \d+ ------> Next character is a 0-9, followed by 'n' more digits
        # [Ee] -----> Upper or lower case E 
        pattern_sci = r"[\s|+-]?\d+\.\d+[Ee][-+]\d+"

        # Regular Float
        # [\s|+-] --> First character is +|-|<whitespace>
        # \d+ ------> Next character is a 0-9, followed by 'n' more digits
        # \. -------> Followed by one decimal point
        # \d+ ------> Next character is a 0-9, followed by 'n' more digits
        pattern_float = r"[\s|+-]\d+\.\d+"

        # Integer
        # [\s|+-] --> First character is +|-|<whitespace>
        # \d+ ------> Next character is a 0-9, followed by 'n' more digits
        pattern_int = r"[\s|+-]\d+"

        # Attempt Scientic Notation
        matches = re.findall(pattern_sci, input_str)
        if len(matches) == 0:
            # Attempt Float
            matches = re.findall(pattern_float, input_str)
        if len(matches) == 0:
            # Attempt Int
            matches = re.findall(pattern_int, input_str)
        if len(matches) == 0:
            warn("Failed to convert instrument response <" + input_str + "> to float. Returning [0.0]")
        
        # Convert matches to float
        for match in matches:
            try:
                float_vals.append(float(match))
            except ValueError:
                warn("Failed to convert instrument response <" + input_str + "-->" + match + " to float.")
                float_vals.append(0.0)

        return float_vals or [0.0]