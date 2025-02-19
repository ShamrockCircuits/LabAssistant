"""
Lecroy HDO6104 Oscilloscope Driver
"""
from src.ABC.SCOPE import GenericScope, HDiv, VDiv, Stats, Union, Optional
from src.enums.generic_enum import Channel, DeviceInfo, DeviceType, ReadWrite
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

class LECROY_HDO6104(GenericScope): # pylint: disable=invalid-name
    """
    Class for the Lecroy HDO6104 Oscilloscope.
    """
    device_info = DeviceInfo(
        device_type = DeviceType.SCOPE,
        manufacturer = "Lecroy",   # SAME AS ABOVE!!!
        model = "HDO6104",               # SAME AS ABOVE!!!
        id_cmd = "*IDN?",           # SAME AS ABOVE!!!
        available_channels = {Channel.CH1, Channel.CH2, Channel.CH3, Channel.CH4}  # Please list the valid channels for this instrument
        )
   
   # =================== Initialization ===================
    def __init__(self, deviceconnection: DeviceConnection):
        print("LECROY_HDO6104.__init__()")
        super().__init__(deviceconnection)

    def _reset_device(self) -> None:
        self.send_command("*RST")

    def _operation_wait(self) -> None:
        self.send_command("*OPC?", ReadWrite.READ, skip_opc=True)
        return None

    # ================= Toggle Output Methods =================
    def _enable_channels(self, channel: Union[list[Channel], Channel], disable_unlisted :bool) -> None:
        channels = self._convert_channel_type(channel)

        for ch in channels:
            self.send_command(f"C{ch.value}:TRA ON")
        if disable_unlisted:
            for ch in set(self.device_info.available_channels) - set(channels):
                self.send_command(f"C{ch.value}:TRA OFF")
    
    def _disable_channels(self, channel : Union[list[Channel], Channel], enable_unlisted :bool) -> None:
        channels = [channel] if isinstance(channel, Channel) else channel
        for ch in channels:
            self.send_command(f"C{ch}:TRA OFF")
        if enable_unlisted:
            for ch in set(self.device_info.available_channels) - set(channels):
                self.send_command(f"C{ch}:TRA ON")
    
    # ================= Channel Setup =================
    def _set_vertical_offset(self, offset: float, channel: Union[list[Channel], Channel]) -> bool:
        channels = [channel] if isinstance(channel, Channel) else channel
        for ch in channels:
            self.send_command(f"C{ch}:OFST {offset}")
        return True

    def _set_vertical_scale(self, scale: VDiv, channel: Union[list[Channel], Channel]) -> bool:
        channels = [channel] if isinstance(channel, Channel) else channel
        for ch in channels:
            self.send_command(f"C{ch}:VDIV {scale}")
        return True

    def _set_horizontal_scale(self, scale: HDiv) -> bool:
        self.send_command(f"TDIV {scale}")
        return True

    # ================= Measure =================
    def _measure(self, stat: Stats, channel: Channel = Channel.CH1) -> float:
        response = self.send_command(f"C{channel}:PAVA? {stat}")
        return float(response)

    # ================== Misc. ==================
    def _print_screen(self, filename : Optional[str]) -> bool:
        response = self.send_command("SCDP", read_write = ReadWrite.READ).encode()
        
        with open(filename or "screenshot.png", "wb") as file:
            file.write(response)
        return True
    
DeviceRegistry.add_class(LECROY_HDO6104)