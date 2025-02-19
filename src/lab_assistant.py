"""
TODO - Copy from readme.md
"""
import os
import importlib
from typing import cast, Set
from src.errors import DeviceInitializationError
from src.enums.generic_enum import ConnectionType, DeviceType
from src.generic_device import DeviceConnection, GenericDevice
from src.ABC.PSU import GenericPSU
from src.ABC.ELOAD import GenericEload
from src.ABC.SCOPE import GenericScope
from src.ABC.DMM import GenericDMM
from src.registry import DeviceRegistry

class LabAssistant():
    '''
    The Lab assistant class can help you...\n
    Find available com ports -> ListAvailableResources()\n
    Setup your devices -> setup_psu(), setup_eload(), setup_dmm()\n
    Once setup you can use the devices methods to create your tests.\n
    '''
    
    @classmethod
    def setup_psu(cls, resource: str, **kwargs) -> GenericPSU:
        '''
        Initialization for a power suppoly. Returned calss will belong specific device found at provided resource.

        Parameters:
            resource (str): The resource string for the device.
            connection_type (ConnectionType): The type of connection (GPIB, USB, Ethernet, RS232)
        **kwargs:
            EnableDebug (bool): Enable or disable debug mode. Defaults to False.
            SimulatedHW (bool): Simulate hardware if set to True. Defaults to False
            Forced_Driver (str): Example: "Siglent_SPD1168X"
        '''
        return cast(GenericPSU, cls._create_device(resource, DeviceType.PSU, **kwargs))

    @classmethod
    def setup_eload(cls,resource: str, **kwargs) -> GenericEload:
        '''
        Initialization for an Electronic load. Returned class will belong specific device found at provided resource.

        Parameters:
            resource (str): The resource string for the device.
            connection_type (ConnectionType): The type of connection (GPIB, USB, Ethernet, RS232)
        **kwargs:
            EnableDebug (bool): Enable or disable debug mode. Defaults to False.
            SimulatedHW (bool): Simulate hardware if set to True. Defaults to False
            Forced_Driver (str): Example: "Siglent_SPD1168X"
        '''
        return cast(GenericEload, cls._create_device(resource, DeviceType.ELOAD, **kwargs))

    @classmethod
    def setup_scope(cls,resource: str, **kwargs) -> GenericScope:
        '''
        Initialization for an Electronic load. Returned class will belong specific device found at provided resource.

        Parameters:
            resource (str): The resource string for the device.
            connection_type (ConnectionType): The type of connection (GPIB, USB, Ethernet, RS232)
        **kwargs:
            EnableDebug (bool): Enable or disable debug mode. Defaults to False.
            SimulatedHW (bool): Simulate hardware if set to True. Defaults to False
            Forced_Driver (str): Example: "Siglent_SPD1168X"
        '''
        return cast(GenericScope, cls._create_device(resource, DeviceType.SCOPE, **kwargs))

    @classmethod
    def setup_dmm(cls, resource: str, **kwargs) -> GenericDMM:
        '''
        Initialization for a Digital Multimeter. Returned class will belong specific device found at provided resource.

        Parameters:
            resource (str): The resource string for the device.
            connection_type (ConnectionType): The type of connection (GPIB, USB, Ethernet, RS232)
        **kwargs:
            EnableDebug (bool): Enable or disable debug mode. Defaults to False.
            SimulatedHW (bool): Simulate hardware if set to True. Defaults to False
            Forced_Driver (str): Example: "Siglent_SPD1168X"
        '''
        return cast(GenericDMM, cls._create_device(resource, DeviceType.DMM, **kwargs))

    @classmethod
    def _create_device(cls, resource: str, device_type:DeviceType, **kwargs) -> GenericDevice:
        '''
        Generic create device method called by more specific create_psu/create_scope/ect methods.
        Performs type checking to confirm resulting GenericDevice matches desired device_type

        Parameters:
            resource (str): The resource string for the device.
            connection_type (ConnectionType): The type of connection (GPIB, USB, Ethernet, RS232)
            device_type (DeviceType): The type of device we are about to create.

        **kwargs:
            EnableDebug : bool = False
            SimulatedHW : bool = False
            Forced_Driver : str = "Siglent_SPD1168X"

        Raises:
            DeviceInitializationError - If the resource doesn't match our expected device type
        '''
        # Create a basic connection to the device
        device_connection = DeviceConnection(resource = resource, connection_type = ConnectionType.RAW, **kwargs)

        # Determine what class this device is
        class_name = device_connection.identify()

        # Lets create the device
        new_device = cls._dynamic_class_instantiate(class_name, device_connection)

        # Check device matches our intended type
        if new_device.device_info.device_type != device_type:
            raise DeviceInitializationError(message=f"Incorrect device type, {new_device.device_info.model} is a {new_device.device_info.device_type.value}, not an {device_type.value}")
        
        # Returned device should be safe to cast to the desired generic class
        return new_device
    
    @staticmethod
    def list_available_resources() -> Set[str]:
        '''
        List all available resources where devices may be located using Pyvisa ResourceManager.
        Use this to copy com ports to pass to CreateXXX methods.

        Returns:
            Set[str]: A list of available devices.
        '''
        return DeviceConnection.available_devices()

    @staticmethod
    def _dynamic_class_instantiate(class_name: str, *args, **kwargs) -> GenericDevice:
        '''
        Dynamically instantiate a class based on the provided class name.
        TODO - This method needs cleanup

        Parameters:
            class_name (str): The name of the class to instantiate.
            *args: Arguments to pass to the class constructor
        '''

        registered_class = DeviceRegistry.get_class_from_registry(class_name)

        if registered_class is None:
            raise NameError(f"Error in DeviceRegistry, unable to find class with name {class_name}")

        return registered_class(*args, **kwargs)

    @staticmethod
    def _import_all_classes_from_directory(root_directory: str = 'src/config'):
        """
        Import all classes from the specified directory and its subdirectories.
        TODO - This method needs cleanup
        """
        print("import_all_classes_from_directory()")
        imported_classes = {}
        # package = root_directory.replace('/', '.')
        
        for dirpath, dirnames, filenames in os.walk(root_directory):
            for file in filenames:
                if file.endswith('.py') and not file.startswith('__'):
                    module_name = file[:-3]
                    full_package = dirpath.replace('/', '.').replace('\\', '.')  # Handles OS-specific path separators
                    try:
                        module = importlib.import_module(f"{full_package}.{module_name}")
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if isinstance(attr, type):
                                globals()[attr_name] = attr
                                imported_classes[attr_name] = attr
                    except Exception as e:
                        print(f"Error during config import. Driver <{module_name}> was not imported properly. Error: {e}. *Enter* to continue anyway.")
                        input()
                        
        return imported_classes