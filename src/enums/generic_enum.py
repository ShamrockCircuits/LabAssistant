"""
Generic enums used by most devices.
"""
from enum import Enum
from dataclasses import dataclass, field

# ================== Generic ==================
class MeasureType(Enum):
    '''
    Measurement types for a variety of instruments.
    
    Attributes:
        VOLTAGE (str): Voltage measurement, represented by "V".
        CURRENT (str): Current measurement, represented by "A".
        POWER (str): Power measurement, represented by "W".
        RESISTANCE (str): Resistance measurement, represented by "OHM".
        CAPACITANCE (str): Capacitance measurement, represented by "F".
    '''
    # DC measurment types
    VOLTAGE = "V"
    CURRENT = "A"
    POWER = "W"

    # Ac measurement types
    VOLTAGE_AC = "Vrms"
    CURRENT_AC = "Arms"
    POWER_AC = "W"

    # General
    RESISTANCE = "OHM"
    RESISTANCE_4W = "OHM"
    CAPACITANCE = "F"
    FREQUENCY = "Hz"

    # Undefined
    UNDEFINED = "Undefined"

class State(Enum):
    '''
    State of device output. 

    Attributes:
        ON (str): Device output is on, "ON"
        OFF (str): Device output is off, "OFF"
        UNDEFINED (str): State couldn't be resolved, or unkonwn.
    '''

    ON = "ON"
    OFF = "OFF"
    UNDEFINED = "UNDEFINED"

class DeviceType(Enum):
    """
    Enumeration of different types of devices used in electronic testing and measurement.

    Attributes:
        PSU (str): Power Supply unit, generally assumed DC PSU.
        SCOPE (str): Oscilloscope, used for observing the change of an electrical signal over time.
        ELOAD (str): Electronic Load, used for testing power supplies by simulating real-world loads.
        FGEN (str): Function Generator, used for generating electrical waveforms.
        DMM (str): Digital Multimeter, used for measuring voltage, current, and resistance.
        UNDEFINED (str): Undefined device type, default value.
    """
    
    PSU = "Power Supply"           
    SCOPE = "Oscilloscope"         
    ELOAD = "Electronic Load"      
    FGEN = "Function Generator"    
    DMM = "Digital Multimeter"     
    UNDEFINED = "Undefined"        # Undefined device type

class Channel(Enum):
    """
    Device Channels, first channel is CH1.

    Attributes:
        CH1 (str): "1"
        CH2 (str): "2"
        CH3 (str): "3"
        CH4 (str): "4"
        CH5 (str): "5"
        CH6 (str): "6"
        CH7 (str): "7"
        CH8 (str): "8"
    """

    CH1 = "1"
    CH2 = "2"
    CH3 = "3"
    CH4 = "4"
    CH5 = "5"
    CH6 = "6"
    CH7 = "7"
    CH8 = "8"
    # Add more channels as needed

class ConnectionType(Enum):
    """
    Type of connection used by this device.
    
    Attributes:
        GPIB (str): "GPIB"
        USB (str): "USB"
        ETHERNET (str): "ETHERNET"
        RS232 (str): "RS232"
        RAW (str): "RAW"
        UNDEFINED (str): "UNDEFINED"
    """

    GPIB = "GPIB"
    USB = "USB"
    ETHERNET = "ETHERNET"
    RS232 = "RS232"
    RAW = "RAW"
    UNDEFINED = "UNDEFINED"

class ReadWrite(Enum):
    """
    Used to define a command as either read, write or auto.

    Attributes:
        Read (str): "Read"
        Write (str): "Write"
        Auto (str): "Auto" - System will auto recognize command as read or write.
    """

    READ = "READ"
    WRITE = "WRITE"
    AUTO = "AUTO"

# ================== Probably Shouldn't be here ==================
@dataclass
class ConnectionInfo:
    """
    Generic Connection info for this device.

    Attributes:
        resource (str): The resource identifier, default is "Undefined".
        connection_type (ConnectionType): The type of connection, default is ConnectionType.UNDEFINED.
        manf_model (str): the devices make and model. Formatted as "Maker_Model". default is "Undefined".
        enable_debug (bool): Flag to enable debugging, default is False.
        simulated_hw (bool): Flag to indicate simulated hardware, default is False.
        forced_driver (str): The name of the forced driver. Default is "None".
    """

    resource : str = "Undefined"
    connection_type : ConnectionType = ConnectionType.UNDEFINED
    manf_model : str = "Undefined"      # based on 

    enable_debug : bool = False
    simulated_hw : bool = False
    forced_driver : str = "None"        # Must match python driver file, TODO - This won't really work since the DeviceConneciton doesn't know what DeviceType it is, needs work 

@dataclass
class DeviceInfo:
    '''
    Generic device info not linked to device connection.

    Attributes:
        device_type (DeviceType): The type of device. PSU, ELOAD, SCOPE, ect. Default is "Undefined".
        manufacturer (str): The manufacturer of the device. Default "Undefined". 
        model (str): The model name of this device. Default "Undefined". 
        id_cmd (str): Command send to recieve device info. Typically "*IDN?". Default "Undefined".
        available_channels (set[Channel]): Channels available on this device. Ex: {Channel.CH1, Channel.CH2}
    '''
    device_type: DeviceType = DeviceType.UNDEFINED      # The type of the device (e.g., PSU, DMM)
    manufacturer: str = "Undefined"         # The manufacturer of the device
    model: str = "Undefined"                # The model name of the device
    id_cmd: str = "Undefined"               # The command to send to the device to get its ID
    available_channels : set[Channel] = field(default_factory=set)   # The channels available on the device

    # I think the below code isn't really staying true to "Device Info", its unrelated to the device
    # # Connection Info
    # connection_type: ConnectionType = ConnectionType.UNDEFINED   # The type of connection to the device
    # resource: str = "Undefined"             # The resource string used to connect to the device

    # # debugging
    # enable_debug: bool = False   # All SCPI commands will be printed to the console
    # simulate_hw: bool = False   # If true, responses will be simulated, no connection to hardware