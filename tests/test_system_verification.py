import pytest
from src.lab_assistant import LabAssistant
from src.enums.generic_enum import Channel
from src.util.errors import DeviceInitializationError, DeviceChannelError

# Lab communications
USER_Scope_ip = "TCPIP::192.168.1.10::INSTR"
USER_Eload_ip = "TCPIP::192.168.1.13::INSTR"
USER_PSU_ip = "TCPIP::192.168.1.12::INSTR"
USER_Func_ip = "TCPIP::192.168.1.11::INSTR"
USER_Dmm_usb = "USB0::0xF4EC::0x1201::SDM35HBQ802019::INSTR"
USER_Dmm_gpib = "GPIB0::1::INSTR"

def test_wrong_device_type():
    """
    Test connecting to the wrong device type.
    
    Expected Behavior:
        - Raises a DeviceInitializationError.
    """
    with pytest.raises(DeviceInitializationError):
        LabAssistant.setup_scope(resource=USER_PSU_ip)

def test_forced_hw_incorrect():
    """
    Test forcing hardware with an incorrect driver.

    Expected Behavior:
        - Raises a DeviceInitializationError.
    """
    with pytest.raises(DeviceInitializationError):
        LabAssistant.setup_psu(resource=USER_PSU_ip, Forced_Driver="BK_9141")

def test_invalid_channel():
    """
    Test setting an invalid channel on the correct hardware.

    Expected Behavior:
        - Raises a DeviceChannelError.
    """
    my_psu = LabAssistant.setup_psu(resource=USER_PSU_ip)
    with pytest.raises(DeviceChannelError):
        my_psu.enable_output(Channel.CH8)

if __name__ == "__main__":

    pytest.main(["tests/test_system_verification.py", "-v"])