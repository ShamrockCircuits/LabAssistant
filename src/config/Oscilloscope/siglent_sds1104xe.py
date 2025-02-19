"""
SIGLENT SDS1104X-E Oscilloscope Driver
"""
from src.ABC.SCOPE import GenericScope, HDiv, VDiv, Stats, Union, Optional
from src.enums.generic_enum import Channel, DeviceInfo, ReadWrite, DeviceType
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

class SIGLENT_SDS1104XE(GenericScope):  # pylint: disable=invalid-name  
    """
    Class for the SIGLENT SDS1104X-E Oscilloscope.
    """
    device_info = DeviceInfo(
            device_type=DeviceType.SCOPE,
            manufacturer="SIGLENT",
            model="SDS1104XE",
            id_cmd="*IDN?",
            available_channels={Channel.CH1, Channel.CH2, Channel.CH3, Channel.CH4}
        )
    
    def __init__(self, deviceconnection: DeviceConnection):
        print("SIGLENT_SDS1104X-E.__init__()")
        super().__init__(deviceconnection)

    def _reset_device(self) -> None:
        self.send_command("*RST")
        return None

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
        channels = self._convert_channel_type(channel)
        for ch in channels:
            self.send_command(f"C{ch.value}:TRA OFF")
        if enable_unlisted:
            for ch in set(self.device_info.available_channels) - set(channels):
                self.send_command(f"C{ch.value}:TRA ON")
    
    # ================= Channel Setup =================
    def _set_vertical_offset(self, offset: float, channel: Union[list[Channel], Channel]) -> bool:
        channels = self._convert_channel_type(channel)
        for ch in channels:
            self.send_command(f"C{ch.value}:OFST {offset}")
        return True

    def _set_vertical_scale(self, scale: VDiv, channel: Union[list[Channel], Channel]) -> bool:
        channels = self._convert_channel_type(channel)
        for ch in channels:
            self.send_command(f"C{ch.value}:VDIV {scale.value}")
        return True

    def _set_horizontal_scale(self, scale: HDiv) -> bool:
        self.send_command(f"TDIV {scale.value}")
        return True

    # ================= Measure =================
    def _measure(self, stat: Stats, channel: Channel = Channel.CH1) -> float:
        response = self.send_command(f"C{channel.value}:PAVA? {stat.value}")
        return self._safe_string_to_float(response)[0]

    # ================== Misc. ==================
    def _print_screen(self, filename : Optional[str]) -> bool:
        response = self.send_command("SCDP", read_write = ReadWrite.READ).encode(encoding="utf-8") 
        
        with open(filename or "screenshot.png", "wb") as file:
            file.write(response)
        return True

DeviceRegistry.add_class(SIGLENT_SDS1104XE)
