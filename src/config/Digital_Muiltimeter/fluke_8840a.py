"""
Keithley 2380 Electronic Load Driver
"""
from src.ABC.DMM import GenericDMM
from src.enums.generic_enum import Channel, DeviceType, MeasureType, DeviceInfo, ReadWrite
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

class FLUKE_8840A(GenericDMM):  # pylint: disable=invalid-name
    """
    Oldie but a goodie... Fluke 8840A DMM.\n
    WARNING - Not all FLUKE_8840A's will respond to G8 identification command.\n
    In my case I had to store the name in the scratch register using P3.
    """
    device_info = DeviceInfo(
            device_type=DeviceType.DMM,
            manufacturer="fluke",
            model="8840a",
            id_cmd="G3",        # WARNING - Read above
            available_channels={Channel.CH1}
        )
    
    def __init__(self, deviceconnection: DeviceConnection):
        """
        General init method.
        
        Parameters:
            deviceconnection (DeviceConnection): Connection to the device.
        """
        super().__init__(deviceconnection)
    
    def _operation_wait(self):
        # TODO - This is a placeholder and may as well be sleep(x)... needs some sniffing
        self.send_command("G7", ReadWrite.READ, skip_opc=True)
        return None
    
    def _reset_device(self) -> None:
        '''
        Protected method to be implemented by child classes to reset the device to factory default.
        '''
        self.send_command("*")
        return None
    
    # ================= Measure =================
    def _measure(self) -> float:
        result = self.send_command("?")
        return self._safe_string_to_float(result)[0]
    
    def _set_mode(self, measure_type:MeasureType) -> None:
        # Voltage
        if measure_type == MeasureType.VOLTAGE_AC:
            self.send_command("F2")
        if measure_type == MeasureType.VOLTAGE:
            self.send_command("F1")

        # Current
        elif measure_type == MeasureType.CURRENT_AC:
            self.send_command("F6")
        elif measure_type == MeasureType.CURRENT:
            self.send_command("F5")

        # Other
        elif measure_type == MeasureType.RESISTANCE:
            self.send_command("F3")
        else:
            raise ValueError(f"Invalid measure type sent to {self.device_info.manufacturer} {self.device_info.model}  --> {measure_type}")

    def _get_mode(self) -> MeasureType:
        response = self.send_command("G0", ReadWrite.READ)
        mode = MeasureType.UNDEFINED
        
        # We expect a 4 bit reponse
        if len(response) != 4:
            raise ValueError("Unexpected response from {self.device_info.manufacturer}_{self.device_info.model} --> {response}")
        
        # Elem[0] - "F" Device Function (VDC, VAC, 2Wire, 4Wire, IDC, IAC)
        # Elem[1] - "R" Range, 0=Autorange (see datasheet for others)
        # Elem[2] - "S" Sample Rate, 0=Slow / 1=Medium / 2=Fast
        # Elem[3] - "T" Trigger Mode, See Datasheet

        if response[0] == "1":
            mode = MeasureType.VOLTAGE
        elif response[0] == "2":
            mode = MeasureType.VOLTAGE_AC
        elif response[0] == "3":
            mode = MeasureType.RESISTANCE
        elif response[0] == "4":
            mode = MeasureType.RESISTANCE_4W
        elif response[0] == "5":
            mode = MeasureType.CURRENT
        elif response[0] == "6":
            mode = MeasureType.CURRENT_AC

        return mode
    
DeviceRegistry.add_class(FLUKE_8840A)
