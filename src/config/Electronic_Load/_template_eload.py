"""
Example template for an Electronic Load driver.
"""
from src.ABC.ELOAD import GenericEload, EloadMode, EloadSlewRate
from src.enums.generic_enum import Channel, DeviceType, MeasureType, State, ReadWrite, DeviceInfo

from src.registry import DeviceRegistry
from src.generic_device import DeviceConnection

# ============================= ELOAD - Example Device Class =============================
    # Your device class should inherit from the ELOAD class (found in the ABC folder) and 
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

class TEMPLATE_ELOAD(GenericEload):  # pylint: disable=invalid-name
    """
    <manufacturer> <model> Electronic Load Driver
    """
    device_info = DeviceInfo(
        # ========================= TODO =========================
        # Update this dataclass, everthing except device_type
        # manufacture - NOTE, must match the name of the class MFN_MODEL
        # model - NOTE, must match the name of the class MFN_MODEL
        # If you don't follow the above notes an error will be raised
        # ========================================================
            device_type=DeviceType.ELOAD,
            manufacturer="template",           
            model="eload",                      
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
        self.send_command("<Paste Command Here>", ReadWrite.READ, skip_opc=True)
        return None
    
   # ============================ Toggle Output =============================
    def _enable_output(self, channel: Channel = Channel.CH1) -> None:
        self.send_command("<Paste Command Here>")       # ======== TODO ========
        return None

    def _disable_output(self, channel: Channel = Channel.CH1) -> None:
        self.send_command("<Paste Command Here>")       # ======== TODO ========
        return None

    def _get_output_state(self, channel: Channel = Channel.CH1) -> State:
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
    def _set_load(self, mode: EloadMode, value: float, channel: Channel = Channel.CH1) -> None:
        
        if self._eload_mode != mode:
            self._set_mode(mode, channel)
            self._eload_mode = mode
            
        if mode == EloadMode.CC:
            self.send_command(f"<Paste Command Here> {value}") # ======== TODO ========
        elif mode == EloadMode.CP:
            self.send_command(f"<Paste Command Here> {value}") # ======== TODO ========
        elif mode == EloadMode.CR:
            self.send_command(f"<Paste Command Here> {value}") # ======== TODO ========
        elif mode == EloadMode.CV:
            self.send_command(f"<Paste Command Here> {value}") # ======== TODO ========
        else:
            raise ValueError("Unsupported load mode")
        return None

    def _set_mode(self, mode: EloadMode, channel: Channel = Channel.CH1) -> None:   # pylint: disable=unused-argument
        if mode == EloadMode.CC:
            self.send_command("<Paste Command Here>") # ======== TODO ========
        elif mode == EloadMode.CP:
            self.send_command("<Paste Command Here>") # ======== TODO ========
        elif mode == EloadMode.CR:
            self.send_command("<Paste Command Here>") # ======== TODO ========
        elif mode == EloadMode.CV:
            self.send_command("<Paste Command Here>") # ======== TODO ========
        else:
            raise ValueError("Unsupported load mode")
        
        return None

    def _get_mode(self, channel: Channel = Channel.CH1) -> EloadMode:
        response = self.send_command("<Paste Command Here>", ReadWrite.READ) # ======== TODO ========
        mode = EloadMode.UNDEFINED

        if "<Paste Response Here>" in response: # ======== TODO ========
            mode = EloadMode.CC
        elif "<Paste Response Here>" in response: # ======== TODO ========
            mode = EloadMode.CP
        elif "<Paste Response Here>" in response: # ======== TODO ========
            mode = EloadMode.CR
        elif "<Paste Response Here>" in response: # ======== TODO ========
            mode = EloadMode.CV
        else:
            mode = EloadMode.UNDEFINED

        return mode
    
    def _get_load(self, channel: Channel = Channel.CH1) -> float:
        if self._eload_mode == EloadMode.CC:
            response = self.send_command("<Paste Command Here>") # ======== TODO ========
        elif self._eload_mode == EloadMode.CP:
            response = self.send_command("<Paste Command Here>") # ======== TODO ========
        elif self._eload_mode == EloadMode.CR:
            response = self.send_command("<Paste Command Here>") # ======== TODO ========
        elif self._eload_mode == EloadMode.CV:
            response = self.send_command("<Paste Command Here>") # ======== TODO ========
        else:
            raise ValueError("Unsupported load mode")
        
        return self._safe_string_to_float(response)[0]

    def _set_remote_sense(self, state: State, channel: Channel = Channel.CH1) -> None:
        self.send_command(f"<Paste Command Here> {state.value}") # ======== TODO ========
        return None

    def _set_slew_rate(self, slew_rate: EloadSlewRate, slew_amps_per_ms: float = 1.0, channel: Channel = Channel.CH1) -> float:
        # Set fastest possible slewrate on this device
        if slew_rate == EloadSlewRate.FASTEST:
            self.send_command("<Paste Command Here>")               # ======== TODO ========
            response = self.send_command("<Paste Command Here>")    # ======== TODO ========
        
        # Set slowest possible slewrate on this device
        elif slew_rate == EloadSlewRate.SLOWEST:
            self.send_command("<Paste Command Here>")               # ======== TODO ========
            response = self.send_command("<Paste Command Here>")    # ======== TODO ========

        # Set custom slew rate
        elif slew_rate == EloadSlewRate.CUSTOM:
            self.send_command("<Paste Command Here>")               # ======== TODO ========
            response = self.send_command("<Paste Command Here>")    # ======== TODO ========

        # Unsupported
        else:
            raise ValueError("Unsupported slew rate type")
        
        return self._safe_string_to_float(response)[0]

   # ============================ Measurement =============================
    def _measure(self, measure_type: MeasureType, channel: Channel = Channel.CH1) -> float:
        if measure_type == MeasureType.VOLTAGE:
            response = self.send_command("<Paste Command Here>", ReadWrite.READ)    # ======== TODO ========
        elif measure_type == MeasureType.CURRENT:
            response = self.send_command("<Paste Command Here>", ReadWrite.READ)    # ======== TODO ========
        elif measure_type == MeasureType.POWER:
            response = self.send_command("<Paste Command Here>", ReadWrite.READ)    # ======== TODO ========
        else:
            raise ValueError("Unsupported measurement type")
        
        return self._safe_string_to_float(response)[0]
    
DeviceRegistry.add_class(TEMPLATE_ELOAD) # TODO - Do not forget this!!!
