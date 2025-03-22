"""
SIGLENT SPD1168X Power Supply Driver
"""
from src.ABC.PSU import GenericPSU
from src.enums.generic_enum import Channel, DeviceInfo, DeviceType, State, MeasureType, ReadWrite
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection


class SIGLENT_SPD1168X(GenericPSU): # pylint: disable=invalid-name
    """
    Class for SIGLENT SPD1168X high volt power supply.
    """
    # Note - Every instance of this class will have same device info
    device_info = DeviceInfo(
        device_type=DeviceType.PSU,
        manufacturer="siglent",
        model="spd1168x",
        id_cmd="*IDN?",
        available_channels={Channel.CH1}
    )
   
   # =================== Initialization ===================
    def __init__(self, deviceconnection : DeviceConnection):
        super().__init__(deviceconnection)
   
    def _reset_device(self) -> None:
        # There is no reset command for this device, so I'll make one
        for channel in self.device_info.available_channels:
            self.enable_output(channel)
            self.set_voltage(0.0, channel)
            self.set_current(0.0, channel)
        
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
        cmd_str = f"OUTP CH{channel.value},ON"
        self.send_command(cmd_str, ReadWrite.WRITE)
        return None

    def _disable_output(self, channel: Channel = Channel.CH1) -> None:
        cmd_str = f"OUTP CH{channel.value},OFF"
        self.send_command(cmd_str, ReadWrite.WRITE)
        return None

    def _get_output_state(self, channel: Channel = Channel.CH1) -> State:
        str_cmd = "SYST:STAT?"
        bin_response = format(int(self.send_command(str_cmd, ReadWrite.READ), 16), 'b').zfill(8)

        # Bit 4 is the output state, LSB first so [3]
        if bin_response[3] == '1':
            return State.ON
        else:
            return State.OFF
        
   # ================= Output Setup Methods =================
    def _set_current(self, current: float, channel: Channel = Channel.CH1) -> None:
        str_cmd = f"CH{channel.value}:CURR {current}"
        self.send_command(str_cmd, ReadWrite.WRITE)
        return None

    def _get_current(self, channel: Channel= Channel.CH1) -> float:
        str_cmd = f"CH{channel.value}:CURR?"
        response = self.send_command(str_cmd, ReadWrite.READ)
        return self._safe_string_to_float(response)[0]

    def _set_voltage(self, voltage: float, channel: Channel = Channel.CH1) -> None:
        str_cmd = f"CH{channel.value}:VOLT {voltage}"
        self.send_command(str_cmd, ReadWrite.WRITE)
        return None

    def _get_voltage(self, channel: Channel = Channel.CH1) -> float:
        str_cmd = f"CH{channel.value}:VOLT?"
        response = self.send_command(str_cmd, ReadWrite.READ)
        return self._safe_string_to_float(response)[0]
   
   # ================= Measure Methods =================
    def _measure(self, measure_type: MeasureType, channel: Channel = Channel.CH1) -> float:
        '''
        Measure the voltage and current of the PSU on the specified channel.

        Parameters:
            MeasureType: MeasureType - The type of measurement to be taken.
            channel: Channel - The channel to be read. Defaults to Channel.CH1.
        Returns:
            float - The measured value in the units specified by MeasureType
        '''
        str_volt = f"MEAS:VOLT? CH{channel.value}"
        str_curr = f"MEAS:CURR? CH{channel.value}"
        str_pow = f"MEAS:POWE? CH{channel.value}"
        str_sent = ""

        # Select command
        if measure_type == MeasureType.VOLTAGE:
            str_sent = str_volt
        elif measure_type == MeasureType.CURRENT:
            str_sent = str_curr
        elif measure_type == MeasureType.POWER:
            str_sent = str_pow
        else:
            raise ValueError("Unsupported MeasureType")
        
        # Send command
        response = self.send_command(str_sent, ReadWrite.READ)
        
        # Attempt to convert response
        return self._safe_string_to_float(response)[0]
    
   # =================== Protection ====================
   # Neither OCP or OVP is supported by this device
   # Do not modify default implementations

# DeviceRegistry.add(SIGLENT_SPD1168X.device_info)
DeviceRegistry.add_class(SIGLENT_SPD1168X)
