'''
TODO - All functionality checks are currently manual. Need to add checks to this code later.
'''
from src.lab_assistant import LabAssistant
from src.enums.generic_enum import *
from src.enums.eload_enum import *
from src.enums.scope_enum import *

# My lab comms
print( LabAssistant.list_available_resources())
USER_Scope_ip = "192.168.1.10"
USER_Eload_ip = "192.168.1.13"
USER_PSU_ip = "192.168.1.12"
USER_Func_ip = "192.168.1.11"
USER_Dmm_usb = "USB0::0xF4EC::0x1201::SDM35HBQ802019::INSTR"
USER_Dmm_gpib = "GPIB0::1::INSTR"

TestDevice = {DeviceType.PSU}

# ============================= Oscilloscope =============================
if DeviceType.SCOPE in TestDevice:
    print("\n\n============== Oscilloscope TEST ==============")
    my_scope = LabAssistant.setup_scope(resource=f"TCPIP::{USER_Scope_ip}::INSTR")

    # Test Channel Toggles
    my_scope.enable_channels([Channel.CH1, Channel.CH2], disable_unlisted = False)
    my_scope.enable_channels(Channel.CH1, disable_unlisted = True) # This should remove CH2-4
    my_scope.disable_channels(Channel.CH1, enable_unlisted = True) # CH2-4 should be on
    my_scope.enable_channels([Channel.CH1, Channel.CH2, Channel.CH3, Channel.CH4])

    # Test offset
    my_scope.set_vertical_scale(VDiv._1V, [Channel.CH1, Channel.CH2])
    my_scope.set_vertical_offset(offset = 1, channel = [Channel.CH1, Channel.CH2])
    my_scope.set_horizontal_scale(HDiv._100ms)

    # Measure something simple
    print(f"Stat measurement => {my_scope.measure(Stats.PKPK)}V")
    
    # Screenshot
    # my_scope.Print_Screen()
    print("here")

if DeviceType.PSU in TestDevice:
    print("\n\n============== POWER SUPPLY TEST ==============")
    my_PSU = LabAssistant.setup_psu(resource=f"TCPIP::{USER_PSU_ip}::INSTR", EnableDebug = False)
    my_PSU.cleanup()
    my_PSU.cleanup()

    # my_PSU.test_all_methods()
    # my_PSU.set_voltage(1.0, Channel.CH1)
    # my_PSU.set_current(1.0, Channel.CH1)
    # my_PSU.enable_output(Channel.CH1)  
    # my_PSU.disable_output(Channel.CH1)

    # print("here")

if DeviceType.ELOAD in TestDevice:
    print("\n\n============== ELOAD TEST ==============")
    my_ELOAD = LabAssistant.setup_eload(resource=f"TCPIP::{USER_Eload_ip}::INSTR", EnableDebug = False)

    my_ELOAD.test_all_methods()
    # Test different modes
    my_ELOAD.set_load(EloadMode.CC, 1)
    my_ELOAD.set_load(EloadMode.CV, 1)
    my_ELOAD.set_load(EloadMode.CR, 1)
    my_ELOAD.set_load(EloadMode.CP, 1)

    # Test output state
    my_ELOAD.set_output_state(State.ON)
    my_ELOAD.set_output_state(State.OFF)
    my_ELOAD.set_output_state(State.ON)

    # Test remote sense
    my_ELOAD.set_remote_sense(State.ON)
    my_ELOAD.set_remote_sense(State.OFF)

    # Test slew rate
    my_ELOAD.set_slew_rate(EloadSlewRate.FASTEST)
    my_ELOAD.set_slew_rate(EloadSlewRate.SLOWEST)
    my_ELOAD.set_slew_rate(EloadSlewRate.CUSTOM, 100)

    print("here")

if DeviceType.DMM in TestDevice:
    print("\n\n============== DMM TEST ==============")
    # my_DMM_usb = LabAssistant.setup_dmm(resource=USER_Dmm_usb, connection_type = ConnectionType.RAW, EnableDebug = True)
    # my_DMM = LabAssistant.setup_dmm(resource=USER_Dmm_gpib, EnableDebug = False)
    my_other_DMM = LabAssistant.setup_dmm(resource=USER_Dmm_usb, EnableDebug = False)
    my_other_DMM.test_all_methods()
    # print("Reset Device")
    # my_DMM.reset_device()

    # print("USB DMM...")
    # my_DMM.set_mode(MeasureType.VOLTAGE)
    # observed = my_DMM.get_mode()
    # print("\nSet Mode - Voltage DC", end="")
    # print(f" ---> Observed {observed}")
    # print( f"DC Votlage --> {my_DMM.measure(MeasureType.VOLTAGE)}" )

    # my_DMM.set_mode(MeasureType.CURRENT)
    # observed = my_DMM.get_mode()
    # print("\nSet Mode - Current DC", end="")
    # print(f" ---> Observed {observed}")
    # print( f"DC Current --> {my_DMM.measure(MeasureType.CURRENT)}" )

    # my_DMM.set_mode(MeasureType.RESISTANCE)
    # observed = my_DMM.get_mode()
    # print("\nSet Mode - Resistance", end="")
    # print(f" ---> Observed {observed}")
    # print( f"Resistance --> {my_DMM.measure(MeasureType.RESISTANCE)}" )

    # my_DMM.set_mode(MeasureType.FREQUENCY)
    # observed = my_DMM.get_mode()
    # print("\nSet Mode - Frequency", end="")
    # print(f" ---> Observed {observed}")
    # print( f"Frequency ---> {my_DMM.measure(MeasureType.FREQUENCY)}" )
