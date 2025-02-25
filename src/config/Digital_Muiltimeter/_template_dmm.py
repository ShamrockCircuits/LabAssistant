"""
Example template for a Digital Multimeter driver.
"""
from src.ABC.DMM import GenericDMM
from src.enums.generic_enum import Channel, DeviceType, MeasureType, DeviceInfo, ReadWrite
from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

# ============================= DMM - Example Device Class =============================
    # Your device class should inherit from the DMM class (found in the ABC folder) and 
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

class TEMPLATE_DMM(GenericDMM):  # pylint: disable=invalid-name
    """
    <manufacturer> <model> Digital Multimeter Driver
    """
    device_info = DeviceInfo(
        # ========================= TODO =========================
        # Update this dataclass, everthing except device_type
        # manufacture - NOTE, must match the name of the class MFN_MODEL
        # model - NOTE, must match the name of the class MFN_MODEL
        # If you don't follow the above notes an error will be raised
        # ========================================================
            device_type=DeviceType.DMM,
            manufacturer="template",           
            model="dmm",                      
            id_cmd="*IDN?",                    
            available_channels={Channel.CH1}
        )
    
   # ============================ Initialization ============================
    def __init__(self, deviceconnection: DeviceConnection):
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
    
    def _operation_wait(self):
        # ========================= TODO =========================
        # You must provide some mechanism to control the code execution.
        # See the inherited docstring for details... 
        # =======================================================
        #self._warn_unimplemented("Warning -> Missing OPC on this device!!! Beware of stability issues.")
        self.send_command("<Paste Command Here>", ReadWrite.READ, skip_opc=True) # ======== TODO ========
        return None
    
   # ================= Measure =================
    def _measure(self) -> float:
        # ========================= TODO =========================
        # Add the command to measure the value from the device
        # =======================================================
        result = self.send_command("<Paste Command Here>")  # ======== TODO ======== 
        return self._safe_string_to_float(result)[0]
    
   # ================= Config =================
    def _set_mode(self, measure_type: MeasureType) -> None:
        # Voltage
        if measure_type == MeasureType.VOLTAGE_AC:
            self.send_command("<Paste Command Here>")   # ======== TODO ======== 
        if measure_type == MeasureType.VOLTAGE:
            self.send_command("<Paste Command Here>")   # ======== TODO ======== 

        # Current
        elif measure_type == MeasureType.CURRENT_AC:    
            self.send_command("<Paste Command Here>")   # ======== TODO ======== 
        elif measure_type == MeasureType.CURRENT:
            self.send_command("<Paste Command Here>")   # ======== TODO ========

        # Other
        elif measure_type == MeasureType.RESISTANCE:
            self.send_command("<Paste Command Here>")   # ======== TODO ========
        elif measure_type == MeasureType.FREQUENCY:
            self.send_command("<Paste Command Here>")   # ======== TODO ========
        elif measure_type == MeasureType.CAPACITANCE:
            self.send_command("<Paste Command Here>")   # ======== TODO ========
        else:
            raise ValueError("Unsupported measure type")
        
    def _get_mode(self)-> MeasureType:

        # Query the device state
        response = self.send_command("<Paste Command Here>")   # ======== TODO ========

        # ========================= TODO =========================
        # Parse the reponse and return the MeasureType
        # =======================================================
        
        return MeasureType.UNDEFINED

DeviceRegistry.add_class(TEMPLATE_DMM)
