"""
TODO - Copy from readme.md
"""
from typing import List, Optional, Type, TYPE_CHECKING
from src.enums.generic_enum import DeviceInfo

if TYPE_CHECKING:
    from src.generic_device import GenericDevice    # This causes circular import sadness

print("Importing <== Registry.py")

class DeviceRegistry:
    """
    Manages the registry of devices by providing functionalities to add new devices, 
    retrieve the entire registry, list unique identification commands, and query 
    specific device information based on manufacturer and model. It ensures efficient 
    and organized handling of device data, facilitating device identification and management 
    within the DriversPy ecosystem.

    Class Attributes:
        _registry (List[DeviceInfo]): Old registry used to store device info. Needs to be removed TODO
        _class_registry (List[GenericDevice]): Stores device specific class in list.
    """
    _class_registry : List[Type['GenericDevice']]= []   # This is a list of GenericDevice classes, I would have type hinted, but it causes a circular import

    @classmethod
    def add_class(cls, device_class : Type['GenericDevice']) -> None:
        '''
        Adds the class to the class registry.

        Args:
            device_class (GenericDevice) : Child class of GenericDevice to be added.
        '''
        # flagged_input = False
        
        # Check if class already added...
        # TODO - this check
        
        # Check Some common errors, class name must be lower case
        # manf_model = str(device_class.__name__.split("_"))
        # for temp_str in manf_model:
        #     for char in temp_str:
        #         if char.isnumeric() or char.islower():
        #             pass
        #         else:
        #             flagged_input = True
        #             break
        
        # We do this in GenericDevice init now... leaving just incase
        # # When we add a new device we want to make sure its device_info has been overwritten
        # if device_class.device_info.device_type == DeviceType.UNDEFINED:
        #     raise ValueError("Some fun error message")        

        # verify user set device_info correclty...
        # We do not check that the user correctly assigned the device type, but this will raise other errors
        info : DeviceInfo = device_class.device_info
        if info.manufacturer.lower() != device_class.__name__.split("_")[0].lower():
            raise ValueError(f"Manufacturer in device_info must match in class {device_class.__name__}.")
        if info.model.lower() != device_class.__name__.split("_")[1].lower():
            raise ValueError(f"Model in device_info must match in class {device_class.__name__}.")
        
        

        cls._class_registry.append(device_class)
        return None

    @classmethod
    def list_unique_id_cmds(cls) -> List[str]:
        """
        List all unique identification commands (ID_CMD) in the registry.

        Returns:
            List[str]: A list of unique ID_CMD values from all registered devices.

        Example:
            unique_id_cmds = DeviceRegistry.list_unique_id_cmds()
        """

        id_list : list = [device.device_info.id_cmd for device in cls._class_registry]
        
        # Create a dictionary to count the frequency of each id command
        frequency_counter : dict[str, int]= {}
        for id_command in id_list:
            if id_command in frequency_counter:
                frequency_counter[id_command] += 1
            else:
                frequency_counter[id_command] = 1
        
        # Sort the items by frequency in descending order
        sorted_items = sorted(frequency_counter.items(), key=lambda x: x[1], reverse=True)
        
        # Extract the sorted ID commands
        sorted_id_list = [item[0] for item in sorted_items]
        
        return sorted_id_list

    @classmethod
    def get_registered_device(cls, device_string: str) -> str:
        '''
        Determine if a device is registered in the device registry. 
        Note - This is a simple string match. Ideally the response will match the driver 
        class in the config folder.

        Args:
            device_string (str): Raw string returned from device.
        
        Returns:
            str: A string containing the manufacturer and model of the device. Formatting is 
            "manufacturer_model". If no match is found, an empty string is returned [""].
        '''
        
        # Remove invalid characters, and change to lower
        device_string = device_string.replace("-","").strip("\n").lower()

        matched_devices : List[str] = []
        for device in cls._class_registry:
            if device.device_info.manufacturer.lower() in device_string and device.device_info.model.lower() in device_string:
                matched_devices.append(f'{device.device_info.manufacturer}_{device.device_info.model}')

        # Reminder def
        if len(matched_devices) == 0:
            device_string = device_string.strip("\r\n")
            print(f"\n Warning - Failed to match <{device_string}> to registered device.\n"
                  "Ensure the device driver exists in the config folder, and has the correct spelling.\n"
                  "============REGISTRY============\n"
                  f"{cls._class_registry}\n"
                  "================================")
            matched_devices = ['']
        # This will occur when we have two similar products made by the same manufacturer
        # For example say i have two devices "Siglent,SDS1204X-E" and "Siglent,SDS1204X"
        # Both would match with 'Siglent Technologies,SDS1204X-E,SDL13GCQ6R1247,1.1.1.22\n'
        # to avoid this error we will always assume the LONGEST model number is correct.
        # (seems like a good assumption to me)
        return max(matched_devices, key=len)
    
    @classmethod
    def get_device_info(cls, manufacturer: str, model: str) -> DeviceInfo:
        """
        Get the DeviceInfo for a specified device based on the manufacturer and model.

        Args:
            manufacturer (str): The manufacturer of the device.
            model (str): The model name of the device.

        Returns:
            Optional[DeviceInfo]: The DeviceInfo of the specified device if found, otherwise None.

        Example:
            device_info = DeviceRegistry.get_device_info("Siglent", "SPD1168X")
        """

        found_class = cls.get_class_from_registry(class_name = manufacturer + "_" + model)
        if found_class is None:
            raise KeyError("Unable to find device {manufacturer}_{model} in device registry. \n"
                           "Device registry includes TODO")
        
        return found_class.device_info
    
    @classmethod
    def get_class_from_registry(cls, class_name : str) -> Optional[Type['GenericDevice']]:
        '''
        Returns the specified class from the class registry. If class DNE returns none.

        args:
            class_name (str) : name of class. Not case sensitive. 

        Returns:
            GenericDevice|None : Device class.
        '''

        for elem in cls._class_registry:

            if elem.__name__.lower() == class_name.lower():
                return elem

        print(f"Unable to find {class_name} in registry")
        return None
    
    # =================== Private Methods ===================
    @classmethod
    def _check_class_exists(cls, class_name : str) -> bool:
        '''
        Checks if the class exists in _class_registry. Not case sensitive.

        args:
            class_name (str) : name of the class. Not case sensitive. 

        Return:
            (bool) : True if found, else false
        '''
        if cls.get_class_from_registry(class_name) is None:
            return False
        
        return True
    