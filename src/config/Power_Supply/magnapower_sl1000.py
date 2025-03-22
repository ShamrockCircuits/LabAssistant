"""
MAGNAPOWER SL1000 Power Supply Driver
"""
from src.ABC.PSU import GenericPSU
from src.enums.generic_enum import Channel, DeviceInfo, DeviceType, State, MeasureType, ReadWrite
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

# ============================= PSU - Example Device Class =============================
# Your device class should inherit from the PSU class and implement the abstract methods.
# Example methods are provided below. Please note, the device driver Manufacturer_Model.py, 
# device class Munufacturer_model and the device's registry object all must match, and are 
# (currently) case sensitive.
# 
# Errors & Warnings
# Any unimplemented methods should raise a NotImplementedError if it is a safety concern.
# Else it should print a warning to the console using the _Warn_Unimplemented method.
# If you neglect to add support for any of the abstract methods, hit a keyerror in _dynamic_class_instantiate()
# =======================================================================================

class MAGNAPOWER_SL1000(GenericPSU): # pylint: disable=invalid-name
    """
    Class for MAGNAPOWER SL1000 high volt power supply.
    """
    # Note - Every instance of this class will have same device info
    device_info = DeviceInfo(
        device_type = DeviceType.PSU,
        manufacturer = "MagnaPower",   # SAME AS ABOVE!!!
        model = "SL1000",               # SAME AS ABOVE!!!
        id_cmd = "*IDN?",           # SAME AS ABOVE!!!
        available_channels = {Channel.CH1}  # Please list the valid channels for this instrument
        )
   
   # =================== Initialization ===================
    def __init__(self, deviceconnection : DeviceConnection):
        super().__init__(deviceconnection)
        # ============================
        # (optional) Your Code here!!!
        # ============================
        self.send_command("CONF:SETPT 3") #Enable remote control
    
    def _reset_device(self) -> None:
        # Set everything to a safe level
        self.disable_output()
        self.set_voltage(0.0)
        self.set_current(0.0)
        self.set_ovp(50)

        # Disable auto sequence mode
        self.send_command("OUTP:ARM 0")

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

        self.send_command("OUTP:START", ReadWrite.WRITE)
        return None

    def _disable_output(self, channel: Channel = Channel.CH1) -> None:
        self.send_command("OUTP:STOP", ReadWrite.WRITE)
        return None

    def _get_output_state(self, channel: Channel) -> State:
        response = self.send_command("OUTP?", ReadWrite.READ).strip()

        # check if rsponse includes "ON"
        if response == "1":
            return State.ON
        elif response == "0":
            return State.OFF
        else:
            return State.UNDEFINED

   # ================= Output Setup Methods ================= 
    def _set_current(self, current: float, channel: Channel = Channel.CH1) -> None:
        self.send_command(f"CURR {current}", ReadWrite.WRITE)
        return None

    def _get_current(self, channel: Channel) -> float:
        response = self.send_command("CURR?", ReadWrite.READ)
        return self._safe_string_to_float(response)[0]

    def _set_voltage(self, voltage: float, channel: Channel = Channel.CH1) -> None:
        self.send_command(f"VOLT {voltage}", ReadWrite.WRITE)
        return None

    def _get_voltage(self, channel: Channel = Channel.CH1) -> float:
        response = self.send_command("VOLT?", ReadWrite.READ)
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
        # Select command
        if measure_type == MeasureType.VOLTAGE:
            response = self.send_command("MEAS:VOLT?", ReadWrite.READ)
            response_fp = self._safe_string_to_float(response)[0]
        elif measure_type == MeasureType.CURRENT:
            response = self.send_command("MEAS:CURR?", ReadWrite.READ)
            response_fp = self._safe_string_to_float(response)[0]
        elif measure_type == MeasureType.POWER:
            print("Warning - The power formula is calculated using voltage and current measurements.")
            volt_str = self.send_command("MEAS:VOLT?", ReadWrite.READ)
            curr_str = self.send_command("MEAS:curr?", ReadWrite.READ)
            volt_fp = self._safe_string_to_float(volt_str)[0]
            curr_fp = self._safe_string_to_float(curr_str)[0]
            response_fp = volt_fp*curr_fp
        else:
            raise ValueError("Unsupported MeasureType")
        
        # Attempt to convert response
        return response_fp
    
   # =================== Protection ====================
    def _set_ovp(self, voltage: float, channel: Channel) -> None:
        self.send_command(f"VOLT:PROT {voltage}")
        return 

    def _set_ocp(self, current: float, channel: Channel) -> None:
        self.send_command(f"CURR:PROT {current}")
        return None

DeviceRegistry.add_class(MAGNAPOWER_SL1000)
