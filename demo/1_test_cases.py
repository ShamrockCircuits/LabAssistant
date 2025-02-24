from src.lab_assistant import *
from src.enums.generic_enum import *
from src.errors import *

# My lab comms
USER_Scope_ip = "192.168.1.10"
USER_Eload_ip = "192.168.1.13"
USER_PSU_ip = "192.168.1.12"
USER_Func_ip = "192.168.1.11"

# Test 1 - Connecting to the wrong device typex
try:
    my_scope = LabAssistant.setup_scope(resource=USER_PSU_ip, connection_type=ConnectionType.ETHERNET, EnableDebug = True)
except DeviceInitializationError as e:
    print(f">>Exception Thrown<< {e.message}")


# Test 2 - Forced HW, but the HW is incorrect
try:
    my_psu = LabAssistant.setup_psu(resource=USER_PSU_ip, connection_type=ConnectionType.ETHERNET, Forced_Driver = "BK_9141")
except DeviceInitializationError as e:
    print(f">>Exception Thrown<< {e.message}")

# Test 3 - Correct HW, setting invalid channel
my_psu = LabAssistant.setup_psu(resource=USER_PSU_ip, connection_type=ConnectionType.ETHERNET)
try:
    my_psu.enable_output(Channel.CH8)
except DeviceChannelError as e:
    print(f">>Exception Thrown<< {e.message}")


print("here")