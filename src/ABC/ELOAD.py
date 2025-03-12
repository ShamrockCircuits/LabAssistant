"""
TODO - Copy from readme.md
"""
from typing import final
from abc import ABC, abstractmethod
from src.generic_device import DeviceConnection, GenericDevice, Channel, warn
from src.enums.generic_enum import State, MeasureType
from src.enums.eload_enum import EloadMode, EloadSlewRate

class GenericEload(GenericDevice, ABC):
    '''
    Base class for Electronic Load (ELOAD) devices.
    This class provides the basic interface and functionality for ELOAD devices,
    ensuring a consistent API across different types of ELOADs.

    Attributes:
        _eload_mode (EloadMode): The current mode of the ELOAD.
        _info (ConnectionInfo): Inherited. Connection info for this device. Some of this info is passed in during init.
        _visa_device_com (ConnectionProtocol): Inherited. Protocol interface supporting read and write.
        _visa_device (pyvisa.resources.MessageBasedResource | None): Inherited. True visa device if one exists. None if HW is simulated.
    '''
   # ============================ Initialization ============================
    def __init__(self, deviceconnection: DeviceConnection):
        """
        Initialize the ELOAD device.\n
        If unable to read the current device state, init will set Eload\n
        to CR @10kOhm.

        Parameters:
            deviceconnection (DeviceConnection): The connection object for the device.
        """
        print("GenericELOAD.__init__()")
        print(f"Initializing ELOAD --> {self.device_info.manufacturer}_{self.device_info.model}")
        super().__init__(deviceconnection)
        print(f"ELOAD Initialized <-- {self.device_info.manufacturer}_{self.device_info.model}")

        # Get Current Device State
        self._eload_mode = self.get_mode()
        if self._eload_mode == State.UNDEFINED:
            raise TypeError(f"Unable to determine the mode of this ELOAD device - {self.device_info.manufacturer}_{self.device_info.model}")

        # Warning - To simplify this class I assumed only 1channel devices...
        # I don't know of any multi-channel ELOADs so this won't be an issue for 99% of users.
        # If we have a multichannel device we'd need to rethink how we store the current mode of the eload
        if len(self.device_info.available_channels) > 1:
            warn("Multi-channel ELOAD detected. This driver assumes all channels use the same mode.")
    
    @final
    def _cleanup(self) -> None:
        '''
        Automatically called by GenericDevice parent class.\n
        Purpose - to put the device into a safe state.\n
        All channels will be disabled.\n
        '''

        for ch in self.device_info.available_channels:
            self.disable_output(ch)
        
        return None

    @final
    def reset_device(self) -> None:
        '''
        Reset device back to factory default, typically calling *RST.\n
        Also does the following to all channels...
        1) Disables output
        2) Set mode to CR @10kOhm
        3) Disable remote sense
        '''
        self._reset_device()

        # Default state for eload [CR - 10kOhm], outputs disabled
        for ch in self.device_info.available_channels:
            self.disable_output(ch)
            self.set_load(EloadMode.CR, 10000, ch)
            self.set_remote_sense(State.OFF, ch)

        return None

    @abstractmethod
    def _reset_device(self) -> None:
        '''
        Reset device back to factory default, typically calling *RST.\n
        Method called by GenericEload parent class reset_device(). \n
        '''
        
   # ============================ Toggle Output =============================
    @final
    def enable_output(self, channel: Channel = Channel.CH1) -> None:
        """
        Enable the output of the ELOAD on the specified channel.

        Parameters:
            channel (Channel): The channel to enable. Defaults to Channel.CH1.
        """
        self._check_channel_exists(channel)
        self._enable_output(channel)
        return None

    @abstractmethod
    def _enable_output(self, channel: Channel) -> None:
        """
        Enable the output of the ELOAD on the specified channel.

        Parameters:
            channel (Channel): The channel to enable. Defaults to Channel.CH1.
        """

    @final
    def disable_output(self, channel: Channel = Channel.CH1) -> None:
        """
        Disable the output of the ELOAD on the specified channel.

        Parameters:
            channel (Channel): The channel to disable. Defaults to Channel.CH1.
        """
        self._check_channel_exists(channel)
        self._disable_output(channel)
        return None

    @abstractmethod
    def _disable_output(self, channel: Channel) -> None:
        """
        Disable the output of the ELOAD on the specified channel.

        Parameters:
            channel (Channel): The channel to disable. Defaults to Channel.CH1.
        """
        
    @final
    def set_output_state(self, state: State, channel: Channel = Channel.CH1) -> None:
        """
        Set the output state of the ELOAD on the specified channel.

        Parameters:
            channel (Channel): The channel to be targeted. Defaults to Channel.CH1.
            state (OutputState): ON enables the output, OFF disables the output.
        """
        self._check_channel_exists(channel)
        if state == State.ON:
            self.enable_output(channel)
        else:
            self.disable_output(channel)
        
        return None

    @final
    def get_output_state(self, channel: Channel = Channel.CH1) -> State:
        """
        Get the output state of the ELOAD on the specified channel.

        Parameters:
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            OutputState: ON if the output is enabled, OFF if the output is disabled.
        """
        self._check_channel_exists(channel)
        return self._get_output_state(channel)

    @abstractmethod
    def _get_output_state(self, channel: Channel) -> State:
        """
        Get the output state of the ELOAD on the specified channel.

        Parameters:
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            OutputState: ON if the output is enabled, OFF if the output is disabled.
        """
        
   # ============================ Output Setup =============================
    @final
    def set_load(self, mode: EloadMode, value: float, channel: Channel = Channel.CH1) -> None:
        """
        Set the load mode type and value (CC/CP/CR/CV) on the specified channel.

        Parameters:
            mode (EloadMode): The load mode to set.
            value (float): The load value to set.
            channel (Channel): The channel to set the mode and value on. Defaults to Channel.CH1.
        """
        self._check_channel_exists(channel)
        self._set_load(mode, value, channel)
        return None

    @abstractmethod
    def _set_load(self, mode: EloadMode, value: float, channel: Channel) -> None:
        """
        Set the load mode type and value (CC/CP/CR/CV) on the specified channel.

        Parameters:
            mode (EloadMode): The load mode to set.
            value (float): The load value to set.
            channel (Channel): The channel to set the mode and value on. Defaults to Channel.CH1.
        """
    
    @final
    def set_mode(self, mode: EloadMode, channel: Channel = Channel.CH1) -> None:   # pylint: disable=unused-argument
        """
        Set the mode of the <manufacturer> <model> (CC/CP/CR/CV) on the specified channel.\n
        NOTE - This method updates self._eload_mode

        Parameters:
            mode (EloadMode): The mode to set.
            channel (Channel): The channel to set the mode on. Defaults to Channel.CH1.
        """
        self._check_channel_exists(channel)
        self._set_mode(mode,channel)
        self._eload_mode = mode

        return None
    
    @abstractmethod
    def _set_mode(self, mode: EloadMode, channel: Channel = Channel.CH1) -> None:   # pylint: disable=unused-argument
        """
        Set the mode of the <manufacturer> <model> (CC/CP/CR/CV) on the specified channel.\n
        NOTE - Do not update _eload_mode in this method 

        Parameters:
            mode (EloadMode): The mode to set.
            channel (Channel): The channel to set the mode on. Defaults to Channel.CH1.
        """

    @final
    def get_mode(self, channel: Channel = Channel.CH1) -> EloadMode:
        """
        Get the current EloadMode of the device (CC/CP/CR/CV/UNDEFINED).

        Parameters:
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            EloadMode: The current mode of the eload.
        """
        self._check_channel_exists(channel)
        return self._get_mode(channel)

    @abstractmethod
    def _get_mode(self, channel: Channel) -> EloadMode:
        """
        Get the current EloadMode of the device (CC/CP/CR/CV/UNDEFINED).

        Parameters:
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            EloadMode: The current mode of the eload.
        """
        
    @final
    def get_load(self, channel: Channel = Channel.CH1) -> float:
        """
        Get the value currently set on the eload. Units depend on the mode (CC/CP/CR/CV).

        Parameters:
            channel (Channel): The channel to get the value from. Defaults to Channel.CH1.
        Returns:
            float: The value currently set on the device.
        """
        self._check_channel_exists(channel)
        return self._get_load(channel)

    @abstractmethod
    def _get_load(self, channel: Channel) -> float:
        """
        Get the value currently set on the eload. Units depend on the mode (CC/CP/CR/CV).

        Parameters:
            channel (Channel): The channel to get the value from. Defaults to Channel.CH1.
        Returns:
            float: The value currently set on the device.
        """
        
    @final
    def set_remote_sense(self, state: State, channel: Channel = Channel.CH1) -> None:
        """
        Enable or disable remote sense on the specified channel.

        Parameters:
            state (OutputState): The state to set (ON or OFF).
            channel (Channel): The channel to set the state on. Defaults to Channel.CH1.
        """
        self._check_channel_exists(channel)

        if state == State.UNDEFINED:
            raise ValueError("Unsupported state sent to Set_Remote_Sense()")

        if self.get_output_state(channel) == State.ON:
            warn("Remote sense cannot be set while the output is enabled.")

        self._set_remote_sense(state, channel)
        return None

    @abstractmethod
    def _set_remote_sense(self, state: State, channel: Channel) -> None:
        """
        Enable or disable remote sense on the specified channel.

        Parameters:
            state (OutputState): The state to set (ON or OFF).
            channel (Channel): The channel to set the state on. Defaults to Channel.CH1.
        """

    # Extra features
    @final
    def set_slew_rate(self, slew_rate: EloadSlewRate, slew_amps_per_ms: float = 1.0, channel: Channel = Channel.CH1) -> float:
        """
        Set the slew rate of the ELOAD on the specified channel. If custom slew rate is selected, driver will do its best to match the requested rate.
        This is incredibly device dependent. Some devices do not support this feature.

        Parameters:
            slew_rate (EloadSlewRate): The slew rate to set. (Fast, Slow, Custom)
            slew_Amps_per_ms (float): The custom slew rate to set in A/ms. Defaults to 1.0.
            channel (Channel): The channel to set the slew rate on. Defaults to Channel.CH1.
        Returns:
            float: The actual slew rate set on the device.
        """
        self._check_channel_exists(channel)
        return self._set_slew_rate(slew_rate, slew_amps_per_ms, channel)

    @abstractmethod
    def _set_slew_rate(self, slew_rate: EloadSlewRate, slew_amps_per_ms: float, channel: Channel) -> float:
        """
        Set the slew rate of the ELOAD on the specified channel. If custom slew rate is selected, driver will do its best to match the requested rate.
        This is incredibly device dependent. Some devices do not support this feature.

        Parameters:
            slew_rate (EloadSlewRate): The slew rate to set. (Fast, Slow, Custom)
            slew_Amps_per_ms (float): The custom slew rate to set in A/ms. Defaults to 1.0.
            channel (Channel): The channel to set the slew rate on. Defaults to Channel.CH1.
        Returns:
            float: The actual slew rate set on the device.
        """
        
   # ============================ Measurement =============================
    @final
    def measure(self, measure_type: MeasureType, channel: Channel = Channel.CH1) -> float:
        """
        Measure the voltage, current, or power of the ELOAD on the specified channel.\n
        NOTE - Depending on the device, POWER might be calculated based on I&V, or \n
        it may be directly reported by the device.

        Parameters:
            measure_type (MeasureType): The type of measurement to be taken.
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            float: The measured value in the units specified by MeasureType.
        """
        return self._measure(measure_type, channel)
    
    @abstractmethod
    def _measure(self, measure_type: MeasureType, channel: Channel = Channel.CH1) -> float:
        """
        Measure the voltage, current, or power of the ELOAD on the specified channel.\n
        NOTE - Depending on the device, POWER might be calculated based on I&V, or \n
        it may be directly reported by the device.

        Parameters:
            measure_type (MeasureType): The type of measurement to be taken.
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            float: The measured value in the units specified by MeasureType.
        """
        
   # ============================ Protection =============================
    # Add protection-related methods here if needed in the future.

   # ========================= Debugging Method ==========================
    @final
    def _test_all_methods(self) -> None:
        
        input("(1/5) - Device Reset           *enter*")
        self.reset_device()
        for ch in self.device_info.available_channels:
            if self.get_output_state(ch) != State.OFF:
                raise ValueError(">>> Error - Output not disabled after reset")
        if self.get_mode() != EloadMode.CR:
            print(">>> Error - Mode not set to CR after reset")        

        input("(2/5) - Set/Get Mode           *enter*")
        for mode in EloadMode:
            if mode == EloadMode.UNDEFINED:
                continue
            print(f"    Setting Mode: {mode} --> ", end="")
            try:
                self.set_mode(mode)
                rd_mode = self.get_mode()
                if rd_mode != mode:
                    print(f" Error: Expected mode does not match observed {rd_mode}")
                else:
                    print("PASS")
            except ValueError as e:
                print(f" Error: {e}")

        input("(3/5) - Measure              *enter*")
        for mmode in MeasureType:
            if mmode == MeasureType.UNDEFINED:
                continue
            print(f"    Measuring: {mmode} --> ", end="")
            try:
                result = self.measure(mmode)
                print(f"Observed {result}")
            except ValueError as e:
                print(f" Unsupported: {e}")
        
        input("(4/5) - Toggle Outputs       *enter*")
        for ch in self.device_info.available_channels:
            for state in {State.ON, State.OFF}:
                print(f"    Setting Output: {state} --> ", end="")
                self.set_output_state(state, ch)
                rd_state = self.get_output_state(ch)
                if rd_state != state:
                    print(f" Error: Expected state does not match observed {rd_state}")
                else:
                    print("PASS")
        input("(5/5) - Get ID                 *enter*")
        print(f"    Device ID: {self.get_id()}")