"""
TODO - Copy from readme.md
"""
from typing import final
from abc import ABC, abstractmethod
from src.generic_device import GenericDevice, DeviceConnection
from src.enums.generic_enum import Channel, State, MeasureType

print("Importing <== PSU.py")

class GenericPSU(GenericDevice, ABC):
    '''
    Base class for power supply (PSU) devices.\n
    This class provides the basic interface and functionality for PSU devices,\n
    ensuring a consistent API across different models of PSUs.\n

    Attributes:
        _info (ConnectionInfo): Inherited. Connection info for this device. Some of this info is passed in during init.
        _visa_device_com (ConnectionProtocol): Inherited. Protocol interface supporting read and write.
        _visa_device (pyvisa.resources.MessageBasedResource | None): Inherited. True visa device if one exists. None if HW is simulated.
    '''

    def __init__(self, deviceconnection: DeviceConnection):
        """
        Initialize the PSU device.

        Parameters:
            deviceconnection (DeviceConnection): The connection object for the device.
        """
        print("GenericPSU.__init__()")
        print("Initializing PSU --> " + self.device_info.manufacturer + "_" + self.device_info.model)
        super().__init__(deviceconnection)
        print("PSU Initialized <-- " + self.device_info.manufacturer + "_" + self.device_info.model)

    @final
    def _cleanup(self):
        '''
        Cleanup method called by parent class.\n
        Disables all the power supply outputs. \n
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
        2) Sets OVP to 50V
        3) Sets OCP to 5A
        4) Sets V to 0V
        5) Sets I to 0A
        6) Disable remote sense
        '''
        self._reset_device()
        for ch in self.device_info.available_channels:
            self.disable_output(ch)
            self.set_ovp(50, ch)
            self.set_ocp(5, ch)
            self.set_voltage(0, ch)
            self.set_current(0, ch)
            self.set_remote_sense(ch, State.OFF)
        return None

    @abstractmethod
    def _reset_device(self) -> None:
        '''
        Send the RESET command to the device. Typically "*RST".\n
        What this does typically depeneds on the manufacturer. \n
        Method called by public method reset_device().
        '''

    # ================= Toggle Output Methods ================= 
    @final
    def enable_output(self, channel: Channel = Channel.CH1) -> None:
        '''
        Enable the output of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to enable. Defaults to Channel.CH1.
        '''
        self._check_channel_exists(channel)
        self._enable_output(channel)
        return None

    @abstractmethod
    def _enable_output(self, channel: Channel) -> None:
        '''
        Enable the output of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to enable. Defaults to Channel.CH1.
        Returns:
            none
        '''

    @final
    def disable_output(self, channel: Channel = Channel.CH1) -> None:
        '''
        Disable the output of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to disable. Defaults to Channel.CH1.
        '''
        self._check_channel_exists(channel)
        self._disable_output(channel)
        return None

    @abstractmethod
    def _disable_output(self, channel: Channel) -> None:
        '''
        Disable the output of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to disable. Defaults to Channel.CH1.
        '''

    @final
    def set_output_state(self, state: State, channel: Channel = Channel.CH1) -> None:
        '''
        Set the output state of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            state: OutputState - ON enables the output, OFF disables the output
        '''
        self._check_channel_exists(channel)
        if state.ON:
            self._enable_output(channel)
        else:
            self._disable_output(channel)
        
        return None

    @final
    def get_output_state(self, channel: Channel = Channel.CH1) -> State:
        '''
        Get the output state of the PSUJ on the specified channel.

        Parameters:
            channel: Channel - The channel to be read. Defaults to Channel.CH1.
        Returns:
            OutputState - ON if the output is enabled, OFF if the output is disabled
        '''
        self._check_channel_exists(channel)
        return self._get_output_state(channel)

    @abstractmethod
    def _get_output_state(self, channel: Channel) -> State:
        '''
        Get the output state of the PSUJ on the specified channel.

        Parameters:
            channel: Channel - The channel to be read. Defaults to Channel.CH1.
        Returns:
            OutputState - ON if the output is enabled, OFF if the output is disabled
        '''

    # ================= Output Setup Methods ================= 
    @final
    def set_current(self, current: float, channel: Channel = Channel.CH1) -> None:
        '''
        Set the current limit of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            current: float - The current to set in Amps
        '''
        self._check_channel_exists(channel)
        self._set_current(current, channel)
        return None

    @abstractmethod
    def _set_current(self, current: float, channel: Channel) -> None:
        '''
        Set the current limit of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            current: float - The current to set in Amps
        '''

    @final
    def get_current(self, channel: Channel = Channel.CH1) -> float:
        '''
        Get the current limit of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to be read. Defaults to Channel.CH1.
        Returns:
            float - The current in Amps
        '''
        self._check_channel_exists(channel)
        return self._get_current(channel)

    @abstractmethod
    def _get_current(self, channel: Channel) -> float:
        '''
        Get the current limit of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to be read. Defaults to Channel.CH1.
        Returns:
            float - The current in Amps
        '''

    @final
    def set_voltage(self, voltage: float, channel: Channel = Channel.CH1) -> None:
        '''
        Set the voltage of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            voltage: float - The voltage to set in Volts
        '''
        self._check_channel_exists(channel)
        self._set_voltage(voltage, channel)
        return None

    @abstractmethod
    def _set_voltage(self, voltage: float, channel: Channel) -> None:
        '''
        Set the voltage of the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            voltage: float - The voltage to set in Volts
        '''

    @final
    def get_voltage(self, channel: Channel = Channel.CH1) -> float:
        '''
        Get the voltage of the PSU on the specified channel.\n
        NOTE - This is NOT the measured voltage, just the desired setpoint.

        Parameters:
            channel: Channel - The channel to be read. Defaults to Channel.CH1.
        Returns:
            float - The voltage in Volts
        '''
        self._check_channel_exists(channel)
        return self._get_voltage(channel)

    @abstractmethod
    def _get_voltage(self, channel: Channel) -> float:
        '''
        Get the voltage of the PSU on the specified channel.\n
        NOTE - This is NOT the measured voltage, just the desired setpoint.

        Parameters:
            channel: Channel - The channel to be read. Defaults to Channel.CH1.
        Returns:
            float - The voltage in Volts
        '''
    
    @final
    def set_remote_sense(self, channel: Channel = Channel.CH1, state: State = State.ON) -> None:
        '''
        Enable or disable remote sensing on the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            state: OutputState - ON enables remote sensing, OFF disables remote sensing
        '''
        self._check_channel_exists(channel)
        self._set_remote_sense(channel, state)
        return None

    @abstractmethod
    def _set_remote_sense(self, channel: Channel, state: State) -> None:
        '''
        Enable or disable remote sensing on the PSU on the specified channel.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            state: OutputState - ON enables remote sensing, OFF disables remote sensing
        '''

    # ======================== Measure ======================== 
    @final
    def measure(self, measure_type: MeasureType, channel: Channel = Channel.CH1) -> float:
        '''
        Measure the voltage/current/power of the PSU on the specified channel.\n
        NOTE - If the device does not natively support POWER readings, than power\n
        will be calaculated based on I&V.

        Parameters:
            MeasureType: MeasureType - The type of measurement to be taken.
            channel: Channel - The channel to be read. Defaults to Channel.CH1.
        Returns:
            float - The measured value in the units specified by MeasureType
        '''
        self._check_channel_exists(channel)
        return self._measure(measure_type, channel)

    @abstractmethod
    def _measure(self, measure_type: MeasureType, channel: Channel) -> float:
        '''
        Measure the voltage/current/power of the PSU on the specified channel.\n
        NOTE - If the device does not natively support POWER readings, than power\n
        will be calaculated based on I&V.

        Parameters:
            MeasureType: MeasureType - The type of measurement to be taken.
            channel: Channel - The channel to be read. Defaults to Channel.CH1.
        Returns:
            float - The measured value in the units specified by MeasureType
        '''
    
    # ====================== Protection ====================== 
    @final
    def set_ovp(self, voltage: float, channel: Channel = Channel.CH1) -> None:
        '''
        Set the over voltage protection of the PSU on the specified channel.\n
        NOTE - Many devices do not support this method.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            voltage: float - The voltage to set in Volts
        '''
        self._check_channel_exists(channel)
        self._set_ovp(voltage, channel)
        return None

    @abstractmethod
    def _set_ovp(self, voltage: float, channel: Channel) -> None:
        '''
        Set the over voltage protection of the PSU on the specified channel.\n
        NOTE - Many devices do not support this method.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            voltage: float - The voltage to set in Volts
        '''

    @final
    def set_ocp(self, current: float, channel: Channel = Channel.CH1) -> None:
        '''
        Set the over current protection of the PSU on the specified channel.
        NOTE - Many devices do not support this method.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            current: float - The current to set in Amps
        '''
        self._check_channel_exists(channel)
        self._set_ocp(current, channel)
        return None

    @abstractmethod
    def _set_ocp(self, current: float, channel: Channel) -> None:
        '''
        Set the over current protection of the PSU on the specified channel.
        NOTE - Many devices do not support this method.

        Parameters:
            channel: Channel - The channel to be targeted. Defaults to Channel.CH1.
            current: float - The current to set in Amps
        '''
