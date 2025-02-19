"""
Example template for a Digital Multimeter driver.
"""
from src.ABC.DMM import GenericDMM
from src.enums.generic_enum import Channel, DeviceType, MeasureType, DeviceInfo, ReadWrite
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection, sleep

class HP_3458A(GenericDMM):  # pylint: disable=invalid-name 
    """
    HP 3458A Digital Multimeter Driver
    """
    device_info = DeviceInfo(
            device_type=DeviceType.DMM,
            manufacturer="HP",
            model="3458A",                       
            id_cmd="ID?",            
            available_channels={Channel.CH1}  
        )
    
    def __init__(self, deviceconnection: DeviceConnection):
        """
        Initialize the HP 3458A device.
        
        Parameters:
            deviceconnection (DeviceConnection): Connection to the device.
        """
        # Must send "END ALWAYS" to device to ensure it response after each query we send
        # Else you will get a wall of samples when you try to send "ID?" or other queries
        super().__init__(deviceconnection)
        self.send_command("END ALWAYS", ReadWrite.WRITE, skip_opc=True)
        #TODO (3) Add any specific initialization commands here (OPTIONAL)
    
    def _operation_wait(self):
        # If the device does not support OPC, we will likey need to add a sleep() at some point to imporve reliability.
        # Where you'll start missing *OPC? is when you quickly send consecutive commands to the device. 
        # If done too quickly the device won't be able to complete the previous command before the next one arrives (chaos ensues)

        # Check status register
        sleep(0.1)
        # for i in range(100):
        #     status = self.send_command("STB?", ReadWrite.READ, skip_opc=True)
        #     status = bin(int(status))   #TODO - do this better!!!
        #     status = status[::-1]       # Flip it so status[0] is the lowest significant bit
            
        #     # If bit 0 is 1, execution is complete
        #     if status[0] == '1':
        #         break
        #     sleep(0.01)

        return None
    
    def _reset_device(self) -> None:
        self.send_command("RESET")
        self.send_command("END ALWAYS", ReadWrite.WRITE, skip_opc=True)
        return None
    
    # ================= Measure =================
    def _measure(self) -> float:
        #TODO (6) Add the command to measure the value from the device
        result = self.send_command("", read_write=ReadWrite.READ)
        return self._safe_string_to_float(result)[0]
    
    # ================= Config =================
    def _set_mode(self, measure_type: MeasureType) -> None:
        # Voltage
        if measure_type == MeasureType.VOLTAGE_AC:
            self.send_command("ACV")
        if measure_type == MeasureType.VOLTAGE:
            self.send_command("DCV")

        # Current
        elif measure_type == MeasureType.CURRENT_AC:    
            self.send_command("ACI")
        elif measure_type == MeasureType.CURRENT:
            self.send_command("DCI")

        # Other
        elif measure_type == MeasureType.RESISTANCE:
            self.send_command("OHM")
        elif measure_type == MeasureType.FREQUENCY:
            self.send_command("FREQ")
        else:
            
            #TODO (8) If any of the above measurements aren't valid for your device remove them from the if/else case
            raise ValueError(f"Invalid measure type sent to {self.device_info.manufacturer} {self.device_info.model}  --> {measure_type}")
    
    def _get_mode(self) -> MeasureType:
        raise NotImplementedError("_get_mode() not yet implemented")
    
DeviceRegistry.add_class(HP_3458A)
