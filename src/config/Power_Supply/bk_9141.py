"""
BK 9141 Power Supply Driver
"""
from src.ABC.PSU import GenericPSU
from src.enums.generic_enum import Channel, DeviceInfo, DeviceType, State, MeasureType, ReadWrite
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

class BK_9141(GenericPSU): # pylint: disable=invalid-name
    """
    Class for BK 9141 power supply.
    """
    # Device information
    device_info = DeviceInfo(
        device_type=DeviceType.PSU,
        manufacturer="bk",
        model="9141",
        id_cmd="*IDN?",
        available_channels={Channel.CH1, Channel.CH2, Channel.CH3}
    )

    # =================== Initialization ===================
    def __init__(self, deviceconnection: DeviceConnection):
        """
        Initialize the BK_9141 device.
        
        Parameters:
            deviceconnection (DeviceConnection): Connection to the device.
        """
        super().__init__(deviceconnection)
   
    def _reset_device(self) -> None:
        """
        Reset the device to its default state.
        """
        self.send_command("*RST", ReadWrite.WRITE)
        return None

    def _operation_wait(self) -> None:
        '''
        Many devices support an *OPC? command that returns 1 when all pending operations are complete.
        Calling this following some write command dramatically increases the overall stability of the system.
        
        Returns:
            None
        '''
        self.send_command("*OPC?", ReadWrite.READ, skip_opc=True)
        return None

    # ================= Toggle Output Methods =================
    def _enable_output(self, channel: Channel = Channel.CH1) -> None:
        """
        Enable the output for the specified channel.
        
        Parameters:
            channel (Channel): The channel to enable.
        """
        self._select_channel(channel)
        self.send_command("OUTP:STAT ON", ReadWrite.WRITE)
        return None

    def _disable_output(self, channel: Channel = Channel.CH1) -> None:
        """
        Disable the output for the specified channel.
        
        Parameters:
            channel (Channel): The channel to disable.
        """
        self._select_channel(channel)
        self.send_command("OUTP:STAT OFF", ReadWrite.WRITE)
        return None

    def _get_output_state(self, channel: Channel = Channel.CH1) -> State:
        str_cmd = f"OUTP? CH{channel.value}"
        response = self.send_command(str_cmd, ReadWrite.READ)

        # check if rsponse includes "ON"
        state = State.UNDEFINED
        if State.ON.value in response:
            state = State.ON
        elif State.OFF.value in response:
            state= State.OFF
        
        # It could be a safety concern if we incorrectly parse this
        if state == State.UNDEFINED:
            raise ValueError(f"Failed to parse response from get_output_state(). Response <{response}>.")
        
        return state
        
    # ================= Output Setup Methods =================
    def _set_voltage(self, voltage: float, channel: Channel = Channel.CH1) -> None:
        """
        Set the voltage for the specified channel.
        
        Parameters:
            voltage (float): The desired voltage.
            channel (Channel): The channel to set the voltage for.
        """
        self._select_channel(channel)
        self.send_command(f"VOLT {voltage}", ReadWrite.WRITE)
        return None

    def _get_voltage(self, channel: Channel = Channel.CH1) -> float:
        """
        Get the voltage for the specified channel.
        
        Parameters:
            channel (Channel): The channel to query.
        
        Returns:
            float: The voltage of the specified channel.
        """
        self._select_channel(channel)
        response = self.send_command("VOLT?", ReadWrite.READ)
        return self._safe_string_to_float(response)[0]

    def _set_current(self, current: float, channel: Channel = Channel.CH1) -> None:
        """
        Set the current for the specified channel.
        
        Parameters:
            current (float): The desired current.
            channel (Channel): The channel to set the current for.
        """
        self._select_channel(channel)
        self.send_command(f"CURR {current}", ReadWrite.WRITE)
        return None

    def _get_current(self, channel: Channel = Channel.CH1) -> float:
        """
        Get the current for the specified channel.
        
        Parameters:
            channel (Channel): The channel to query.
        
        Returns:
            float: The current of the specified channel.
        """
        self._select_channel(channel)
        response = self.send_command("CURR?", ReadWrite.READ)
        return self._safe_string_to_float(response)[0]

    def _set_remote_sense(self, channel: Channel = Channel.CH1, state: State = State.ON) -> None:
        """
        Set the remote sense state for the specified channel.
        
        Parameters:
            channel (Channel): The channel to set.
            state (OutputState): The desired state.
        """
        self._select_channel(channel)
        self.send_command(f"VOLT:SENS {state.value}", ReadWrite.WRITE)
        return None
   
    # ================= Measure Methods =================
    def _measure(self, measure_type: MeasureType, channel: Channel = Channel.CH1) -> float:
        """
        Measure the voltage, current, or power of the PSU on the specified channel.

        Parameters:
            measure_type (MeasureType): The type of measurement to be taken.
            channel (Channel): The channel to be read. Defaults to Channel.CH1.

        Returns:
            float: The measured value in the units specified by MeasureType.
        """
        self._select_channel(channel)
        str_sent = ""

        # Select command
        if measure_type == MeasureType.VOLTAGE:
            str_sent = "MEAS:VOLT:DC?"
        elif measure_type == MeasureType.CURRENT:
            str_sent = "MEAS:CURR:DC?"
        elif measure_type == MeasureType.POWER:
            str_sent = "MEAS:POW:DC?"
        else:
            raise ValueError("Unsupported MeasureType")
        
        # Send command
        response = self.send_command(str_sent, ReadWrite.READ)
        
        # Attempt to convert response
        return self._safe_string_to_float(response)[0]

   # =================== Protection ====================
    # Neither ocp or ovp are supported by this device

   # ================= New Class Specific Private Methods =================
    def _select_channel(self, channel: Channel = Channel.CH1) -> None:
        """
        Convert the channel enum to the corresponding B&K channel number and select the channel.
        
        Parameters:
            channel (Channel): The channel to be selected (CH1, CH2, CH3)
        """

        # BK is a special snowflake, it starts at index zero
        bk_channel = int(channel.value) - 1
        self.send_command(f"INST:SEL {bk_channel}", ReadWrite.WRITE)
        return None

DeviceRegistry.add_class(BK_9141)