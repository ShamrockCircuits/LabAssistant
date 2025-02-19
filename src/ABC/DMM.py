"""
TODO - Copy from readme.md
"""
from typing import final
from abc import ABC, abstractmethod
from src.generic_device import GenericDevice, DeviceConnection

from src.enums.generic_enum import MeasureType

print("Importing <== DMM.py")

class GenericDMM(GenericDevice, ABC):
    '''
    Base class for Digital Multimeter (DMM) devices.
    This class provides the basic interface and functionality for DMM devices,
    ensuring a consistent API across different models of DMMs.

    Attributes:
        _info (ConnectionInfo): Inherited. Connection info for this device. Some of this info is passed in during init.
        _visa_device_com (ConnectionProtocol): Inherited. Protocol interface supporting read and write.
        _visa_device (pyvisa.resources.MessageBasedResource | None): Inherited. True visa device if one exists. None if HW is simulated.
        _dmm_mode (MeasureType): The current mode of the DMM.
    '''

    def __init__(self, deviceconnection: DeviceConnection):
        """
        Initialize the DMM device.

        Parameters:
            deviceconnection (DeviceConnection): The connection object for the device.
        """
        print("Initializing DMM --> {self.device_info.manufacturer}_{self.device_info.model}")
        super().__init__(deviceconnection)

        # Stores the current state of the DMM
        self._dmm_mode : MeasureType = MeasureType.UNDEFINED

        # Check number of channels... only 1ch DMMs supported
        if len(self.device_info.available_channels) != 1:
            raise ValueError("Only 1 channel DMMs supported")

    @final
    def _cleanup(self):
        '''
        Cleanup method called by parent class.\n
        This method is not used by the DMM device type\n       
        '''
        return None

    @final
    def reset_device(self) -> None:
        '''
        Reset device back to factory default, typically calling *RST.\n
        Also does the following to all channels...
        1) Sets mode to Vdc
        '''
        self._reset_device()
        self.set_mode(MeasureType.VOLTAGE)
        return None

    @abstractmethod
    def _reset_device(self) -> None:
        '''
        Reset device back to factory default, typically calling *RST.\n
        Method called by GenericEload parent class reset_device(). \n
        '''
        
    # ====================== Measurement Method ====================== 
    @final
    def measure(self, measure_type: MeasureType) -> float:
        '''
        Measure the specified type. If needed method will set the mode of the DMM as well.

        Parameters:
            measure_type (MeasureType): The type of measurement (e.g., voltage, current).
        Returns:
            float: The measured value in the units specified by MeasureType
        '''
        
        # Ensure device configured properly
        if measure_type != self._dmm_mode:
            self._set_mode(measure_type)
            self._dmm_mode = measure_type

        return self._measure()

    @abstractmethod
    def _measure(self) -> float:
        '''
        Measure the currently configured parameter.\n
        For all DMMs I've seen, this is independent of the MeasurementType.\n
        If needed you can query the current mode of the DMM using self._dmm_mode.\n
        NOTE - self._dmm_mode is set by calling method.
        '''
        # Again you should NOT be calling self._set_mode in this method.
        # This is done by the caller measure().
        # Simimlarly, self._dmm_mode is updated by the caller.
        return 0.0

   # ====================== Config Method ======================    
    
    @final
    def set_mode(self, measure_type: MeasureType) -> None:
        '''
        Set the mode of the DMM to the specified type.

        Parameters:
            measure_type (MeasureType): The type of measurement (e.g., voltage, current).
        '''
        
        # Don't try to be smart here, just set mode regardless (user may change setting manually so self.__dmm_mode could be inaccurate)
        self._set_mode(measure_type)
        self._dmm_mode = measure_type

        return None
    
    @abstractmethod
    def _set_mode(self, measure_type: MeasureType) -> None:
        '''
        Set the mode of the DMM to the specified type.
        This method shall not access self._dmm_mode. Just set the mode.

        Parameters:
            measure_type (MeasureType): The type of measurement (e.g., voltage, current).
        '''
    
    @final
    def get_mode(self) -> MeasureType:
        '''
        Query the current mode of the device.\n

        Returns:
            MeasureType: The current measurement type the DMM is set to.
        '''
        return self._get_mode()
    
    @abstractmethod
    def _get_mode(self) -> MeasureType:
        '''
        Query the current mode of the device.\n

        Returns:
            MeasureType: The current measurement type the DMM is set to.
        '''