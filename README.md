## About The Project    -_Work In Progress_-
  **General**<br /> 
  Quickly and easily interact with common lab instruments such as power supplies, multimeters, electronic loads, and oscilloscopes using SCPI and PyVisa. Write scripts that will work across multiple devices, without needing to rewrite any code. 

  **Why I Made This Tool**<br /> 
  I find myself working in a lab most days during the week, whether its a professional lab at work, or in my home lab on the weekend. I'm lucky enough to work with tools that can be programmed remotely. Though for the past 5 years, I seldom used the feature. Then one day I was exposed to LabView...

  Now I'm a hardware guy. Theoretically, LabView's circuit-esc programming style is supposedly tailored towards folk like me? But I always get the sense that labview is all GUI and no guts. So I started to design my own tool that could replace LabView for quick R&D style tests.

  A key value proposition for this tool was to be able to write scripts that will work both in the office and in my home lab. I need to be able to easily add new devices and have them work without needing to rewrite code. So if I design a tool on the weekend, I should be able to use it in the office too. The entirety of this module was built around this core idea: ease of use, adaptability, and seamless integration across different environments.

  **Alternatives** <br/>
  Around the time I started working on this project (mid 2024) Google also realeased an internal tool they've been using for some time. I learned this a little too late though.

## Example Usage
```python
# Dumb example script to show how to interact with devices
from src.lab_assistant import LabAssistant
from src.enum_types import *

print( LabAssistant.list_available_resources() )

# Connect to devices
my_DMM = LabAssistant.setup_dmm(resource="GPIB0::1::INSTR", EnableDebug = True)
my_PSU = LabAssistant.setup_psu(resource="USB0::0xF4EC::0x1201::SDM35HBQ802019::INSTR")
my_ELOAD = LabAssistant.setup_eload(resource="TCPIP::192.168.1.10::INSTR", Forced_Driver = "siglent_sdl1020xe")

# Setup
my_DMM.set_mode(MeasureType.VOLTAGE)
my_PSU.set_voltage(3.3, Channel.CH1)
my_PSU.set_current(2, Channel.CH1)
my_ELOAD.set_load(EloadMode.CC, 1.0)

# Start Test
my_PSU.enable_output(Channel.CH1)   # Note - If no CH provided. Default to CH1
my_ELOAD.enable_output()            # Like this...

# Measure stuff
my_DMM.measure(MeasureType.VOLTAGE)
my_PSU.measure(MeasureType.VOLTAGE)
my_PSU.measure(MeasureType.CURRENT)
my_ELOAD.measure(MeasureType.VOLTAGE)
my_ELOAD.measure(MeasureType.CURRENT)
my_ELOAD.measure(MeasureType.POWER)

# When script completes all connections are automatically closed
# and all devices are put into a powered down state
# but if you wanted to, you could call
my_DMM.cleanup()
my_PSU.cleanup()
my_ELOAD.cleanup()
```

## src.registry

This module manages the registration and retrieval of device information within the library. The primary goal of the DeviceRegistry class is to provide dynamic assignment of device classes.

In practice, this means you can write a generic test using `LabAssistant.setup_eload()` and `LabAssistant.setup_psu()`, and your code will work on ANY PSU and ANY ELOAD. In doing so we've made a **instrument agnostic** system. There's no free lunch though, the device we are trying to connect to must be defined by a class in the src.config file structure.

# ===== UNDER CONSTRUCTION =====
**=============Most of the notes below this point are out of date, and need to be revized=============**

#### Class - DeviceRegistry

- **Purpose:** 
    - Manages the registry of devices by providing functionalities to add new devices, retrieve the entire registry, list unique identification commands, and query specific device information based on manufacturer and model. It ensures efficient and organized handling of device data, facilitating device identification and management within the DriversPy ecosystem.
- **Class Attributes:**
    - `_registry`: A class-level variable that stores the registered device data.
- **Class Methods:**
    - `add`: Adds a new device to the registry.
    - `get_registry`: Retrieves the entire device registry.
    - `list_unique_id_cmds`: Lists all unique identification commands in the registry.
    - `get_registered_device`: Determines if a device is registered in the device registry.
    - `get_device_info`: Gets the device information for a specified device based on the manufacturer and model.

## DriversPy.EnumTypes

This module defines various enumeration types and data classes used throughout the DriversPy library for device management and interaction.
If the enumeration is used by multiple files, it is stored here.

#### Enums

- **MeasureType**
  - **Purpose:** Defines the types of measurements that can be taken (e.g., Voltage, Current, Power, Resistance, Capacitance).

- **OutputState**
  - **Purpose:** Represents the output state of a device (e.g., ON, OFF, UNDEFINED).

- **DeviceType**
  - **Purpose:** Specifies the type of the device (e.g., PSU, SCOPE, ELOAD, FGEN, DMM, UNDEFINED).

- **Channel**
  - **Purpose:** Lists the channels available on a device (e.g., CH1, CH2, CH3, CH4).

- **ConnectionType**
  - **Purpose:** Indicates the type of connection used for the device (e.g., Ethernet, RAW, UNDEFINED).

- **RdWr**
  - **Purpose:** Specifies the read/write mode for device commands (e.g., Read, Write, Auto).

#### Data Classes

- **ConnectionInfo**
  - **Purpose:** Stores connection-related information and configurations, including resource string, connection type, manufacturer and model, debug settings, and simulated hardware flag.
  - **Attributes:**
    - `resource`: Resource string for the device connection.
    - `connection_type`: Type of connection (e.g., Ethernet, RAW, UNDEFINED).
    - `manf_model`: Manufacturer and model information.
    - `EnableDebug`: Flag to enable or disable debug mode.
    - `SimulatedHW`: Flag to simulate hardware connection.
    - `ForcedDriver`: Specifies a forced driver for the connection.

- **DeviceInfo**
  - **Purpose:** Contains general information about a device, such as device type, manufacturer, model, identification command, and available channels.
  - **Attributes:**
    - `device_type`: Type of the device (e.g., PSU, DMM).
    - `manufacturer`: Manufacturer of the device.
    - `model`: Model name of the device.
    - `id_cmd`: Command to send to the device to get its ID.
    - `available_channels`: Set of available channels on the device.

## DriversPy.Device

This module manages device connections, identification, and communication within the DriversPy library.

#### **Class - DeviceConnection**
- **Purpose:** 
    - Establishes a connection with the device, identifies the device, and provides methods for communication and querying device information. It supports different connection types (e.g., Ethernet, RAW) and can simulate device connections for testing purposes.
- **Class Attributes:**
    - `_info`: Stores connection-related information and configurations.
    - `__VisaDevice_RdWr`: Object used for reading from or writing to the device.
    - `_VisaDevice`: Stores the actual device object (None if simulating hardware).
- **Private Methods:**
    - `__DefinePort`: Defines the port string for the device based on the connection type.
    - `__Connect`: Connects to the device using the VISA/PyVisa-py backend or simulates the connection if the device is not available.
    - `__Identify`: Identifies the device using all possible identification commands.
- **Public Methods:**
    - `SendCommand`: Sends a command to the device. Auto-detects whether to read or write.
    - `Get_Manf_Model`: Retrieves the manufacturer and model information of the connected device.
    
#### **Class - GenericDevice**
  - **Purpose:** 
    - Serves as a base class for all devices (e.g., PSU, DMM, FGEN, OSCILLOSCOPE) providing common functionalities and ensuring the device type matches the expected type.
  - **Class Attributes:**
    - `device_connection`: The device connection object for interacting with the VISA device.
    - `device_info`: General device information.
  - **Public Methods:**
    - `SendCommand`: Sends a command to the device. Auto-detects whether to read or write.
    - `Get_ID`: Queries the device ID, typically using *IDN?.
  - **Protected Methods:**
    - `_Warn_Unimplemented`: Warns the user that a method is not implemented.
    - `_Error_Unimplemented`: Raises an error if a critical method is not implemented.
    - `_Check_Channel_Exists`: Checks if the specified channel exists on the device.
    - `_Operation_Wait`: Waits for all pending operations to complete using the *OPC? command.
    - `_safe_string_to_float`: Converts a string response from the device to a list of floats.
  - **Static Methods:**
    - `_check_channel_exists`: A decorator that checks if the specified channel exists on the device before executing the method.

## DriversPy.PSU

This module manages the operations and configurations of Power Supply Units (PSU) within the DriversPy library.

#### **Class - GenericPSU**
- **Purpose:** 
    - Provides an interface for PSU operations, including toggling output, setting and getting current and voltage, enabling remote sensing, measuring parameters, and setting protection features. It ensures that the device is properly initialized and its type is correctly identified.
- **Class Attributes:**
    - None explicitly listed.
- **Public Methods:**
    - `Reset_Device`: Resets the device back to factory default.
    - `Set_Output_Enable`: Enables the output of the PSU on the specified channel.
    - `Set_Output_Disable`: Disables the output of the PSU on the specified channel.
    - `Set_Output_State`: Sets the output state of the PSU on the specified channel.
    - `Get_Output_State`: Gets the output state of the PSU on the specified channel.
    - `Set_Current`: Sets the current of the PSU on the specified channel.
    - `Get_Current`: Gets the current of the PSU on the specified channel.
    - `Set_Voltage`: Sets the voltage of the PSU on the specified channel.
    - `Get_Voltage`: Gets the voltage of the PSU on the specified channel.
    - `Set_Remote_Sense`: Enables or disables remote sensing on the specified channel.
    - `Measure`: Measures the voltage and current of the PSU on the specified channel.
    - `Set_OVP`: Sets the over voltage protection of the PSU on the specified channel.
    - `Set_OCP`: Sets the over current protection of the PSU on the specified channel.
- **Protected Methods:**
    - `_Reset_Device`: Protected method to be implemented by child class
    - `_Set_Output_Enable`: Protected method to be implemented by child class
    - `_Set_Output_Disable`: Protected method to be implemented by child class
    - `_Get_Output_State`: Protected method to be implemented by child class
    - `_Set_Current`: Protected method to be implemented by child class
    - `_Get_Current`: Protected method to be implemented by child class
    - `_Set_Voltage`: Protected method to be implemented by child class
    - `_Get_Voltage`: Protected method to be implemented by child class
    - `_Set_Remote_Sense`: Protected method to be implemented by child class
    - `_Measure`: Protected method to be implemented by child class
    - `_Set_OVP`: Protected method to be implemented by child class
    - `_Set_OCP`: Protected method to be implemented by child class

## DriversPy.Eload

This module manages the operations and configurations of Electronic Loads (ELOAD) within the DriversPy library.

#### **Class - GenericEload**
- **Purpose:** 
    - Provides an interface for ELOAD operations, including toggling output, setting and getting load parameters, enabling remote sensing, measuring parameters, and setting slew rates. It ensures that the device is properly initialized and its type is correctly identified.
- **Class Attributes:**
    - None explicitly listed.
- **Public Methods:**
    - `Reset_Device`: Resets the device back to factory default.
    - `Enable_Output`: Enables the output of the ELOAD on the specified channel.
    - `Disable_Output`: Disables the output of the ELOAD on the specified channel.
    - `Set_Output_State`: Sets the output state of the ELOAD on the specified channel.
    - `Get_Output_State`: Gets the output state of the ELOAD on the specified channel.
    - `Set_Load`: Sets the load mode type and value on the specified channel.
    - `Get_Mode`: Gets the current mode of the ELOAD.
    - `Get_Load`: Gets the value currently set on the ELOAD.
    - `Set_Remote_Sense`: Enables or disables remote sense on the specified channel.
    - `Set_Slew_Rate`: Sets the slew rate of the ELOAD on the specified channel.
    - `Measure`: Measures the voltage, current, or power of the ELOAD on the specified channel.
- **Protected Methods:**
    - `_Reset_Device`: Protected method to be implemented by child class
    - `_Enable_Output`: Protected method to be implemented by child class
    - `_Disable_Output`: Protected method to be implemented by child class
    - `_Get_Output_State`: Protected method to be implemented by child class
    - `_Set_Load`: Protected method to be implemented by child class
    - `_Get_Mode`: Protected method to be implemented by child class
    - `_Get_Load`: Protected method to be implemented by child class
    - `_Set_Remote_Sense`: Protected method to be implemented by child class
    - `_Set_Slew_Rate`: Protected method to be implemented by child class
    - `_Measure`: Protected method to be implemented by child class

## DriversPy.LabAssistant

This module provides a utility class for creating and managing power supply units (PSUs) and electronic loads (ELOADs) within the DriversPy library.

#### **Class - LabAssistant**
- **Purpose:** 
    - Provides static methods for creating PSU and ELOAD instances, listing available resources, and dynamically instantiating classes. It facilitates the initialization and management of lab equipment by providing a simplified interface for users.
- **Class Methods:**
    - `CreatePSU`: Initializes and returns a specific PSU instance found at the provided resource.
    - `CreateEload`: Initializes and returns a specific ELOAD instance found at the provided resource.
    - `ListAvailableResources`: Lists all available resources where devices may be located using PyVISA's ResourceManager.
    - `_dynamic_class_instantiate`: Dynamically instantiates a class based on the provided class name and arguments.
