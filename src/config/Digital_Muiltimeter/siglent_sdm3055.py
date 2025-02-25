"""
Keithley 2380 Electronic Load Driver
"""
from src.ABC.DMM import GenericDMM
from src.enums.generic_enum import Channel, DeviceType, MeasureType, DeviceInfo, ReadWrite
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

class SIGLENT_SDM3055(GenericDMM):  # pylint: disable=invalid-name
    """
    SIGLENT SDM3055 Digital Multimeter Driver
    """
    device_info = DeviceInfo(
            device_type=DeviceType.DMM,
            manufacturer="siglent",
            model="sdm3055",
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
        self.send_command("SAMP:COUN 1")  # Set sample count to 1
    
    def _operation_wait(self):
        '''
        Many devices support an *OPC? command that returns 1 when all pending operations are complete.
        Calling this following some write command dramatically increases the overall stability of the system.
        
        Returns:
            None
        '''
        # On this device just querying the status bit is enough to delay execution
        response = self.send_command("*STB?", ReadWrite.READ, skip_opc=True)

        # # Execution Error - In my testing this is a reliable replacement for *OPC? on this device
        # if response == "16":
        #     self._operation_wait()

        return None
    
    def _reset_device(self) -> None:
        '''
        Protected method to be implemented by child classes to reset the device to factory default.
        '''
        self.send_command("SYST:PRES")      # Nicer then *RST since it saves user configurations!
        return None
    
    # ================= Measure =================
    def _measure(self) -> float:
        result = self.send_command("READ?")
        return self._safe_string_to_float(result)[0]
    
    # ================= Config =================
    def _set_mode(self, measure_type: MeasureType) -> None:
        # Voltage
        if measure_type == MeasureType.VOLTAGE_AC:
            self.send_command("CONF:VOLT:AC AUTO")
        elif measure_type == MeasureType.VOLTAGE:
            self.send_command("CONF:VOLT:DC AUTO")

        # Current
        elif measure_type == MeasureType.CURRENT_AC:
            self.send_command("CONF:CURR:AC AUTO")
        elif measure_type == MeasureType.CURRENT:
            self.send_command("CONF:CURR:DC AUTO")

        # Other
        elif measure_type == MeasureType.RESISTANCE:
            self.send_command("CONF:RES AUTO")
        elif measure_type == MeasureType.FREQUENCY:
            self.send_command("CONF:FREQ")
        elif measure_type == MeasureType.CAPACITANCE:
            self.send_command("CONF:CAP AUTO")
        else:
            raise ValueError(f"Invalid measure type sent to {self.device_info.manufacturer} {self.device_info.model}  --> {measure_type}")
    
    def _get_mode(self) -> MeasureType:
        response = self.send_command("CONF?")
        mode = MeasureType.UNDEFINED
        
        # Check Voltage
        if "VOLT" in response:
            if "VOLT:AC" in response:
                mode = MeasureType.VOLTAGE_AC
            else:
                mode = MeasureType.VOLTAGE
        
        # Check Current
        elif "CURR" in response:
            if "CURR:AC" in response:
                mode = MeasureType.CURRENT_AC
            else:
                mode = MeasureType.CURRENT

        # Check Misc
        elif "FREQ" in response:
            mode = MeasureType.FREQUENCY
        elif "RES" in response:
            mode = MeasureType.RESISTANCE
        elif "CAP" in response:
            mode = MeasureType.CAPACITANCE
        
        return mode
        

DeviceRegistry.add_class(SIGLENT_SDM3055)
