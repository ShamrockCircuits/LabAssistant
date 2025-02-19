"""
Siglent SDL1020 Electronic Load Driver
"""
from src.ABC.ELOAD import GenericEload, EloadMode, EloadSlewRate
from src.enums.generic_enum import Channel, DeviceType, MeasureType, State, ReadWrite, DeviceInfo
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

class SIGLENT_SDL1020XE(GenericEload):  # pylint: disable=invalid-name
    """
    Class for the Siglent Eload Electronic Load.
    """
    device_info = DeviceInfo(
            device_type=DeviceType.ELOAD,
            manufacturer="siglent",
            model="sdl1020xe",
            id_cmd="*IDN?",
            available_channels={Channel.CH1}
        )
    
    def __init__(self, deviceconnection: DeviceConnection):
        """
        Initialize the Siglent Eload.
        
        Parameters:
            deviceconnection (DeviceConnection): Connection to the device.
        """
        super().__init__(deviceconnection)

    def _reset_device(self) -> None:
        """
        Reset device back to factory default.
        According to siglent datasheet "Rstore the equipment state to be initial state".
        """
        self.send_command("*RST", ReadWrite.WRITE)
        return None
    
    def _operation_wait(self):
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
        Enable the output of the Siglent Eload on the specified channel.

        Parameters:
            channel (Channel): The channel to enable. Defaults to Channel.CH1.
        Returns:
            None
        """
        self.send_command(":INP ON", ReadWrite.WRITE)
        return None

    def _disable_output(self, channel: Channel = Channel.CH1) -> None:
        """
        Disable the output of the Siglent Eload on the specified channel.

        Parameters:
            channel (Channel): The channel to disable. Defaults to Channel.CH1.
        Returns:
            None
        """
        self.send_command(":INP OFF", ReadWrite.WRITE)
        return None

    def _get_output_state(self, channel: Channel = Channel.CH1) -> State:
        """
        Get the output state of the Siglent Eload on the specified channel.

        Parameters:
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            OutputState: ON if the output is enabled, OFF if the output is disabled.
        """
        response = self.send_command(":INP?", ReadWrite.READ)
        
        if "1" in response:
            result = State.ON
        elif "0" in response:
            result = State.OFF 
        else:
            result = State.UNDEFINED

        return result

    # ================= Output Setup Methods =================
    def _set_load(self, mode: EloadMode, value: float, channel: Channel = Channel.CH1) -> None:
        """
        Set the load mode type and value (CC/CP/CR/CV) on the specified channel.

        Parameters:
            mode (EloadMode): The load mode to set.
            value (float): The load value to set.
            channel (Channel): The channel to set the mode and value on. Defaults to Channel.CH1.
        """
        if self._eload_mode == mode:
            pass
        else:
            self._set_mode(mode, channel)
            
        if mode == EloadMode.CC:
            self.send_command(f"CURR {value}", ReadWrite.WRITE)
        elif mode == EloadMode.CP:
            self.send_command(f"POW {value}", ReadWrite.WRITE)
        elif mode == EloadMode.CR:
            self.send_command(f"RES {value}", ReadWrite.WRITE)
        elif mode == EloadMode.CV:
            self.send_command(f"VOLT {value}", ReadWrite.WRITE)
        else:
            raise ValueError("Unsupported load mode")
        
        return None

    def _set_mode(self, mode: EloadMode, channel: Channel = Channel.CH1) -> None:   # pylint: disable=unused-argument
        """
        Set the mode of the Siglent Eload (CC/CP/CR/CV) on the specified channel.

        Parameters:
            mode (EloadMode): The mode to set.
            channel (Channel): The channel to set the mode on. Defaults to Channel.CH1.
        """
        if mode == EloadMode.CC:
            self.send_command("FUNC CURR", ReadWrite.WRITE)
        elif mode == EloadMode.CP:
            self.send_command("FUNC POW", ReadWrite.WRITE)
        elif mode == EloadMode.CR:
            self.send_command("FUNC RES", ReadWrite.WRITE)
        elif mode == EloadMode.CV:
            self.send_command("FUNC VOLT", ReadWrite.WRITE)
        else:
            raise ValueError("Unsupported load mode")
        
        # Update class variable
        self._eload_mode = mode
        return None

    def _get_mode(self, channel: Channel = Channel.CH1) -> EloadMode:
        """
        Get the current EloadMode of the Siglent Eload (CC/CP/CR/CV/UNDEFINED).

        Parameters:
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            EloadMode: The current mode of the eload. If failed to parse, return EloadMode.UNDEFINED.
        """
        response = self.send_command("FUNC?", ReadWrite.READ)
        mode = EloadMode.UNDEFINED

        if "CUR" in response:
            mode = EloadMode.CC
        elif "POW" in response:
            mode = EloadMode.CP
        elif "RES" in response:
            mode = EloadMode.CR
        elif "VOLT" in response:
            mode = EloadMode.CV
        else:
            mode = EloadMode.UNDEFINED

        return mode

    def _get_load(self, channel: Channel = Channel.CH1) -> float:
        """
        Get the value currently set on the Siglent Eload. Units depend on the mode (CC/CP/CR/CV).

        Parameters:
            channel (Channel): The channel to get the value from. Defaults to Channel.CH1.
        Returns:
            float: The value currently set on the device.
        """
        if self._eload_mode == EloadMode.CC:
            response = self.send_command("CURR?", ReadWrite.READ)
        elif self._eload_mode == EloadMode.CP:
            response = self.send_command("POW?", ReadWrite.READ)
        elif self._eload_mode == EloadMode.CR:
            response = self.send_command("RES?", ReadWrite.READ)
        elif self._eload_mode == EloadMode.CV:
            response = self.send_command("VOLT?", ReadWrite.READ)
        else:
            raise ValueError("Unsupported load mode")
        
        return self._safe_string_to_float(response)[0]

    def _set_remote_sense(self, state: State, channel: Channel = Channel.CH1) -> None:
        """
        Enable or disable remote sense on the specified channel.

        Parameters:
            state (OutputState): The state to set (ON or OFF).
            channel (Channel): The channel to set the state on. Defaults to Channel.CH1.
        """
        if state == State.UNDEFINED:
            raise ValueError("Unsupported state sent to Set_Remote_Sense()")

        self.send_command(f"SYST:SENS {state.value}")
        return None

    def _set_slew_rate(self, slew_rate: EloadSlewRate, slew_amps_per_ms: float = 1.0, channel: Channel = Channel.CH1) -> float:
        """
        Set the slew rate of the Siglent Eload on the specified channel.

        Parameters:
            slew_rate (EloadSlewRate): The slew rate to set. (Fast, Slow, Custom)
            slew_Amps_per_ms (float): The custom slew rate to set in A/ms. Defaults to 1.0.
            channel (Channel): The channel to set the slew rate on. Defaults to Channel.CH1.
        Returns:
            float: The actual slew rate set on the device.
        Raises:
            ValueError: If an unsupported slew rate is given.
        """

        # Set fastest possible slewrate on this device
        if slew_rate == EloadSlewRate.FASTEST:
            self.send_command("CURR:SLEW MAX")
            # response = self.send_command("CURR:SLEW?")

        # Set slowest possible slewrate on this device
        elif slew_rate == EloadSlewRate.SLOWEST:
            self.send_command("CURR:SLEW MIN", ReadWrite.WRITE)
            # response = self.send_command("CURR:SLEW?", ReadWrite.READ)

        # Attempt to set custom slew rate "slew_Amps_per_ms" to the device
        elif slew_rate == EloadSlewRate.CUSTOM:
            
            # Units used by Siglent are in A/us, we must convert to support A/ms
            # 1 A/ms = 1000 A/us            
            self.send_command(f"CURR:SLEW {slew_amps_per_ms*1000}")
            # response = self.send_command("CURR:SLEW?", ReadWrite.READ)

        else:
            raise ValueError("Unsupported slew rate type")
        
        # Device does not support reading the slew rate :(, returning zero
        return 0.0

    # ================= Measure =================
    def _measure(self, measure_type: MeasureType, channel: Channel = Channel.CH1) -> float:
        """
        Measure the voltage, current, or power of the Siglent Eload on the specified channel.

        Parameters:
            measure_type (MeasureType): The type of measurement to be taken.
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            float: The measured value in the units specified by MeasureType.
        """
        if measure_type == MeasureType.VOLTAGE:
            response = self.send_command("MEAS:VOLT?", ReadWrite.READ)
        elif measure_type == MeasureType.CURRENT:
            response = self.send_command("MEAS:CURR?", ReadWrite.READ)
        elif measure_type == MeasureType.POWER:
            response = self.send_command("MEAS:POW?", ReadWrite.READ)
        else:
            raise ValueError("Unsupported measurement type")
        return self._safe_string_to_float(response)[0]
    
DeviceRegistry.add_class(SIGLENT_SDL1020XE)
