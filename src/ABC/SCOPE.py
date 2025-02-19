"""
TODO - Copy from readme.md
"""
from typing import final, Union, Optional
from abc import ABC, abstractmethod
from src.generic_device import DeviceConnection, GenericDevice, Channel
from src.enums.scope_enum import HDiv, VDiv, Stats

class GenericScope(GenericDevice, ABC):
    '''
    Base class for oscilloscope (SCOPE) devices.
    This class provides the basic interface and functionality for SCOPE devices,
    ensuring a consistent API across different models of PSUs.

    Attributes:
        _info (ConnectionInfo): Inherited. Connection info for this device. Some of this info is passed in during init.
        _visa_device_com (ConnectionProtocol): Inherited. Protocol interface supporting read and write.
        _visa_device (pyvisa.resources.MessageBasedResource | None): Inherited. True visa device if one exists. None if HW is simulated.
    '''

    def __init__(self, deviceconnection: DeviceConnection):
        """
        Adds SCOPE device_type to self.device_info, and passes along to GenericDevice constructor.
        """
        print("Initializing SCOPE --> " + self.device_info.manufacturer + "_" + self.device_info.model)
        super().__init__(deviceconnection)

    def _cleanup(self):
        '''
        Cleanup method called by parent class.\n
        This method is not used by the oscilloscope device type\n       
        '''
        return None
    
    @final
    def reset_device(self) -> None:
        """
        Reset device back to factory default. What exactly this means depends on the device.
        """
        self._reset_device()
        return None

    @abstractmethod
    def _reset_device(self) -> None:
        """
        Protected method to be implemented by child classes to reset the device to factory default.
        """

    # ================= Toggle Output Methods =================
    # Stuff related to enable / disable channel
    @final
    def enable_channels(self, channel : Union[list[Channel], Channel], disable_unlisted :bool = False) -> None:
        '''
        Enables the specified channels on the oscilloscope. Channels not included will be disabled.

        Parameters:
            channel (List[Channel] | Channel): List of channel to be turned on. Else single channel to be turned on. Default is CH1.
            disable_unlisted (bool): If True, all unlisted channel will be disabled. Default is False (no change to unlisted channels).
        '''
        self._check_channel_exists(channel)
        self._enable_channels(channel, disable_unlisted)

    @abstractmethod
    def _enable_channels(self, channel: Union[list[Channel], Channel], disable_unlisted :bool) -> None:
        '''
        Protected method to be implemented by child class.
        '''
    
    @final
    def disable_channels(self, channel : Union[list[Channel], Channel], enable_unlisted :bool = False) -> None:
        '''
        Enables the specified channels on the oscilloscope. Channels not included will be disabled.

        Parameters:
            channel (List[Channel] | Channel): List of channel to be turned on. Else single channel to be turned on.
            enable_unlisted (bool): If true, all unlisted channel will be enabled. Default is False (no change to unlisted channels).
        '''
        self._check_channel_exists(channel)
        self._disable_channels(channel, enable_unlisted)

    @abstractmethod
    def _disable_channels(self, channel : Union[list[Channel], Channel], enable_unlisted :bool) -> None:
        '''
        Protected method to be implemented by child class.
        '''
    
    # ================= Channel Setup =================
    @final
    def set_vertical_offset(self, offset:float, channel : Union[list[Channel], Channel]) -> bool:
        '''
        Set the vertical offset on desired channels.

        Parameters:
            value (float) : Offset value to be set on channel.

        Returns:
            bool: True if successful. 

        '''
        self._check_channel_exists(channel)
        return self._set_vertical_offset(offset, channel)

    @abstractmethod
    def _set_vertical_offset(self, offset:float, channel : Union[list[Channel], Channel]) -> bool:
        '''
        Protected method to be implemented by child class.
        '''

    @final
    def set_vertical_scale(self, scale:VDiv, channel : Union[list[Channel], Channel]) -> bool:
        '''
        Set the vertical scale on the desired channels.

        Parameters:
            scale (VDiv): The voltage scale you'd like to set.
            channels ( list[Channel] | Channel ): The channels you'd like it applied to.
        
        Returns:
            bool: True if successful.
        '''
        self._check_channel_exists(channel)
        return self._set_vertical_scale(scale, channel)
      
    @abstractmethod
    def _set_vertical_scale(self, scale:VDiv, channel : Union[list[Channel], Channel]) -> bool:
        '''
        Protected method to be implemented by child class.
        '''
    
    @final
    def set_horizontal_scale(self, scale:HDiv) -> bool:
        '''
        Set the horizontal scale on the scope.

        Parameters:
            scale (HDiv): The timebase to be used.
        
        Returns:
            bool: True if successful.
        '''
        return self._set_horizontal_scale(scale)

    @abstractmethod
    def _set_horizontal_scale(self, scale:HDiv) -> bool:
        '''
        Protected method to be implemented by child class.
        '''

    # ================= Measure =================
    @final
    def measure(self, stat: Stats, channel: Channel = Channel.CH1) -> float:
        """
        Returns the measurement of one specific STAT from the specified channel.

        Parameters:
            measure_type (MeasureType): The type of measurement to be taken.
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            float: The measured value in the units specified by MeasureType.
        """
        self._check_channel_exists(channel)
        return self._measure(stat, channel)
    
    @abstractmethod
    def _measure(self, stat: Stats, channel: Channel = Channel.CH1) -> float:
        """
        Protected method to be implemented by child class.
        """
    
    # ================== Misc. ==================
    @final
    def print_screen(self, filename : Optional[str] = None) -> bool:
        '''
        Saves current screen to the Outputs folder, with the specified filename. Default filename based on date.time is used.
        Beware, method overwrites the file at the location.

        Parameters:
            filename (str): Filename inside outputs directory. If None, default filename used based on date.time.
        
        Returns:
            bool: True if successful, else false.
        '''
        return self._print_screen(filename)

    @abstractmethod
    def _print_screen(self, filename : Optional[str]) -> bool:
        """
        Protected method to be implemented by child class.
        """

    # ================= Protection =================
    # Add protection-related methods here if needed in the future.

    # ================ Future Work =================
    # Cursors
    # BWL
    # trigger setup
    # labels
    # coupling
    # Export_to_CSV (or similar) 