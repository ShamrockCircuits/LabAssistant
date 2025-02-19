"""
Keithley 2380 Electronic Load Driver
"""
from src.ABC.ELOAD import GenericEload, EloadMode, EloadSlewRate
from src.enums.generic_enum import Channel, DeviceType, MeasureType, State, ReadWrite, DeviceInfo
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

class KEITHLEY_2380(GenericEload): # pylint: disable=invalid-name
    """
    Class for the Keithley 2380 Electronic Load.
    """
    device_info = DeviceInfo(
            device_type=DeviceType.ELOAD,
            manufacturer="Keithley",
            model="2380",
            id_cmd="*IDN?",
            available_channels={Channel.CH1}
        )
    
    def __init__(self, deviceconnection: DeviceConnection):
        """
        Initialize the Keithley 2380 device.
        
        Parameters:
        
            deviceconnection (DeviceConnection): Connection to the device.
        """
        super().__init__(deviceconnection)

    def _reset_device(self) -> None:
        """
        Reset device back to factory default.
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
        Enable the output of the Keithley 2380 on the specified channel.

        Parameters:
            channel (Channel): The channel to enable. Defaults to Channel.CH1.
        Returns:
            None
        """
        self.send_command("INP ON", ReadWrite.WRITE)
        return None

    def _disable_output(self, channel: Channel = Channel.CH1) -> None:
        """
        Disable the output of the Keithley 2380 on the specified channel.

        Parameters:
            channel (Channel): The channel to disable. Defaults to Channel.CH1.
        Returns:
            None
        """
        self.send_command("INP OFF", ReadWrite.WRITE)
        return None

    def _get_output_state(self, channel: Channel = Channel.CH1) -> State:
        """
        Get the output state of the Keithley 2380 on the specified channel.

        Parameters:
            channel (Channel): The channel to be read. Defaults to Channel.CH1.
        Returns:
            OutputState: ON if the output is enabled, OFF if the output is disabled.
        """
        response = self.send_command("INP?", ReadWrite.READ)
        return State.ON if "1" in response else State.OFF

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
        Set the mode of the Keithley 2380 (CC/CP/CR/CV) on the specified channel.

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
        Get the current EloadMode of the Keithley 2380 (CC/CP/CR/CV/UNDEFINED).

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
        Get the value currently set on the Keithley 2380. Units depend on the mode (CC/CP/CR/CV).

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
        Set the slew rate of the Keithley 2380 on the specified channel.

        Parameters:
            slew_rate (EloadSlewRate): The slew rate to set. (Fast, Slow, Custom)
            slew_Amps_per_ms (float): The custom slew rate to set in A/ms. Defaults to 1.0.
            channel (Channel): The channel to set the slew rate on. Defaults to Channel.CH1.
        Returns:
            float: The actual slew rate set on the device.
        """
        print("Set_Slew_Rate() makes alot of assumptions about the devices response... we need to verify the behaviour of the device")

        # Set fastest possible slewrate on this device
        if slew_rate == EloadSlewRate.FASTEST:
            
            # For fastest slew rate, we need to set ELOAD to "Quick mode"
            # TODO - This might actually be unnecessary, I think the device might assume "Quick mode"
            # When you set slew to maximum (like I'm about to do)
            self.send_command("CURR:SLOW 0", ReadWrite.WRITE)

            # Now that we're in quick mode the
            # We get the maximum slew rate when use use the max current range for the device
            self.send_command("CURR:SLEW MAX", ReadWrite.WRITE)

            # Read the slew rate we set
            # TODO - unclear if we can query this... pos/neg slew may not be the same
            response = self.send_command("CURR:SLEW?", ReadWrite.READ)

        # Set slowest possible slewrate on this device
        elif slew_rate == EloadSlewRate.SLOWEST:
            
            # Do the inverse of above, same comments apply
            self.send_command("CURR:SLOW 1", ReadWrite.WRITE)
            self.send_command("CURR:SLEW MAX", ReadWrite.WRITE)
            response = self.send_command("CURR:SLEW?", ReadWrite.READ)

        # Attempt to set custom slew rate "slew_Amps_per_ms" to the device
        elif slew_rate == EloadSlewRate.CUSTOM:
            
            # Units sent to device depends on the mode we're in
            # If "quick mode" units are A/us, if "slow mode" units are A/m
            if self.send_command("CURR:SLOW:STAT?", ReadWrite.READ).find("1") != -1:
                # Couldn't find a "1" in response, we're in fast mode. Units are A/us.
                slew_amps_per_ms = slew_amps_per_ms * 1000
            
            self.send_command(f"CURR:SLEW {slew_amps_per_ms}", ReadWrite.WRITE)

            # This may or may not work... don't know if I can query CURR:SLEW?
            # TODO - confirm if this works
            response = self.send_command("CURR:SLEW?", ReadWrite.READ)

        else:
            raise ValueError("Unsupported slew rate type")
        
        return self._safe_string_to_float(response)[0]

    # ================= Measure =================
    def _measure(self, measure_type: MeasureType, channel: Channel = Channel.CH1) -> float:
        """
        Measure the voltage, current, or power of the Keithley 2380 on the specified channel.

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
    
DeviceRegistry.add_class(KEITHLEY_2380)
