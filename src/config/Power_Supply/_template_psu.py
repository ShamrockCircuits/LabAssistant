"""
<manufacturer> <model> Power Supply Driver
"""
from src.ABC.PSU import GenericPSU
from src.enums.generic_enum import Channel, DeviceType, MeasureType, State, ReadWrite, DeviceInfo
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

# ============================= PSU - Example Device Class =============================
    # Your device class should inherit from the PSU class (found in the ABC folder) and 
    # implement the abstract methods. A skeleton is provided below.
    #
    # Errors & Warnings
    # Any unimplemented methods should raise a NotImplementedError if it is a safety concern.
    # Raise value errors when user tries to access unsupported features. (example invalid measure type)
    # If you neglect to add support for any of the abstract methods, you will hit a keyerror in _dynamic_class_instantiate()
    #
    # Customizing This Driver
    # I've added notes throughout this class telling you where things need to be added
    # If you have more questions you can always checkout another class of this device type
    # For cross compatibility avoid adding custom public methods
# =======================================================================================

class TEMPLATE_PSU(GenericPSU): # pylint: disable=invalid-name
    """
    <manufacturer> <model> PSU Driver
    """
    # ========================= TODO =========================
    # Update this dataclass, everthing except device_type
    # manufacture - NOTE, must match the name of the class MFN_MODEL
    # model - NOTE, must match the name of the class MFN_MODEL
    # If you don't follow the above notes an error will be raised
    # ========================================================
    device_info = DeviceInfo(
        device_type = DeviceType.PSU,
        manufacturer = "template",
        model = "psu",
        id_cmd = "*IDN?",
        available_channels = {Channel.CH1} 
        )
   
   # ============================ Initialization ============================
    def __init__(self, deviceconnection : DeviceConnection):
        super().__init__(deviceconnection)
        # ============================
        # (optional) Your Code here!!!
        # ============================
    
    def _reset_device(self) -> None:
        # ============================
        # (optional) Your Code here!!!
        # ============================
        self.send_command("<Paste Command Here>")
        return None
        
    def _operation_wait(self) -> None:
        # ========================= TODO =========================
        # You must provide some mechanism to control the code execution.
        # See the inherited docstring for details... 
        # =======================================================
        #self._warn_unimplemented("Warning -> Missing OPC on this device!!! Beware of stability issues.")
        self.send_command("<Paste Command Here>", ReadWrite.READ, skip_opc=True)
        return None        

   # ============================ Toggle Output =============================
    def _enable_output(self, channel: Channel = Channel.CH1) -> None:
        self.send_command("<Paste Command Here>")       # ======== TODO ========
        return None

    def _disable_output(self, channel: Channel = Channel.CH1) -> None:
        self.send_command("<Paste Command Here>")       # ======== TODO ========
        return None

    def _get_output_state(self, channel: Channel) -> State:
        state = State.UNDEFINED
        response = self.send_command("<Paste Command Here>", ReadWrite.READ)    # ======== TODO ========

        # check if response is "ON" or "OFF"
        # ========================= TODO =========================
        # What this logic looks like is somewhat device dependend.
        # Check with the programming manual for your device
        # =======================================================
        
        # Error Handling
        if state == State.UNDEFINED:
            raise ValueError(f"Failed to parse response from get_output_state(). Response <{response}>.")
        
        return state
        
   # ============================ Output Setup =============================
    def _set_current(self, current: float, channel: Channel = Channel.CH1) -> None:
        self.send_command("<Paste Command Here>")               # ======== TODO ========
        return None

    def _get_current(self, channel: Channel) -> float:
        response = self.send_command("<Paste Command Here>")    # ======== TODO ========
        return self._safe_string_to_float(response)[0]

    def _set_voltage(self, voltage: float, channel: Channel = Channel.CH1) -> None:
        self.send_command("<Paste Command Here>")               # ======== TODO ========
        return None

    def _get_voltage(self, channel: Channel = Channel.CH1) -> float:
        response = self.send_command("<Paste Command Here>")    # ======== TODO ========
        return self._safe_string_to_float(response)[0]

    def _set_remote_sense(self, channel: Channel = Channel.CH1, state: State = State.ON) -> None:
        self._warn_unimplemented("Set_Remote_Sense()")          # ======== TODO ========
        return None
   
   # ============================ Measurement =============================
    def _measure(self, measure_type: MeasureType, channel: Channel = Channel.CH1) -> float:

        # Select command
        if MeasureType == MeasureType.VOLTAGE:
            str_sent = "<Paste Command Here>"                   # ======== TODO ======== 
        elif MeasureType == MeasureType.CURRENT:
            str_sent = "<Paste Command Here>"                   # ======== TODO ========
        elif MeasureType == MeasureType.POWER:
            str_sent = "<Paste Command Here>"                   # ======== TODO ========
        else:
            raise ValueError("Unsupported MeasureType")
        
        # Send command
        response = self.send_command(str_sent, ReadWrite.READ)
        return self._safe_string_to_float(response)[0]
    
   # ============================ Protection =============================
    def _set_ovp(self, voltage: float, channel: Channel) -> None:
        self._warn_unimplemented("<Paste warning Here>")    # ======== TODO ========
        return 

    def _set_ocp(self, current: float, channel: Channel) -> None:
        self._warn_unimplemented("<Paste warning Here>")    # ======== TODO ========

DeviceRegistry.add_class(TEMPLATE_PSU) # TODO - Do not forget this!!!
