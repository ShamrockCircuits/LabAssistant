'''
Integration Test for ELOAD.
Requires real hardware to be connected.
'''

import pytest
from src.lab_assistant import LabAssistant
from src.enums.generic_enum import MeasureType, State
from src.enums.eload_enum import EloadMode

# Supported measurement types for the ELOAD 
supported_measurement_types = {MeasureType.VOLTAGE, MeasureType.VOLTAGE_AC, MeasureType.CURRENT, MeasureType.CURRENT_AC, MeasureType.POWER, MeasureType.POWER_AC}

@pytest.fixture
def electronic_load(resource, device):
    """
    Fixture to initialize and reset the power supply.

    Ensures the power supply is properly initialized with the given resource
    and device identifiers. Cleans up the instance after the test.
    
    Parameters:
        resource: The resource identifier for the power supply (e.g., ip address, COM port).
        device: The specific device driver to use. This must match a driver stored on the config directory (eg. siglent_spd1168x).

    Yields:
        An initialized power supply instance for use in tests.
    """
    if not resource or not device:
        pytest.fail("Resource and device identifier not provided. Use --resource and --device options.")
    eload = LabAssistant.setup_eload(resource, Forced_Driver = device)  # Replace with actual initialization logic
    yield eload
    eload.cleanup()

def test_multi_channel(electronic_load):
    """
    Eload class does not support multiple channels at this time....
    Tool may behave unexpectedly if using a multi channel device.

    Parameters:
        eload_device: The initialized ELOAD instance.

    Expected Behavior:
        - The ELOAD class should only support one channel.
    """
    eload = electronic_load
    assert len(eload.device_info.available_channels) == 1, "ELOAD class does not support multiple channels at this time"

@pytest.mark.dependency(name="toggle_output")
def test_toggle_output(electronic_load):
    """
    Test toggling the output state of the ELOAD.

    Parameters:
        electronic_load: The initialized ELOAD instance.

    Expected Behavior:
        - The output state alternates between ON and OFF when toggled.
    """
    eload = electronic_load

    # Toggle the output state to ON and verify
    eload.set_output_state(State.OFF)
    eload.set_output_state(State.ON)
    assert eload.get_output_state() == State.ON, "Output state not set to ON."

    # Toggle the output state to OFF and verify
    eload.set_output_state(State.OFF)
    assert eload.get_output_state() == State.OFF, "Output state not set to OFF."

@pytest.mark.dependency(name="set_get_mode")
def test_set_get_mode(electronic_load):
    """
    Test setting and getting the mode of the ELOAD.

    Parameters:
        electronic_load: The initialized ELOAD instance.

    Expected Behavior:
        - The ELOAD supports every mode defined in the EloadMode enum.
    """
    eload = electronic_load

    for mode in EloadMode:
        if mode == EloadMode.UNDEFINED:
            continue  # Skip undefined mode

        # Set the mode
        eload.set_mode(mode)

        # Get and verify the mode
        observed_mode = eload.get_mode()
        assert observed_mode == mode, f"Mode set to {mode} but observed {observed_mode}."

@pytest.mark.dependency(depends=["toggle_output", "set_get_mode"])
def test_device_reset(electronic_load):
    """
    Test resetting the ELOAD to its default state.
    NOTE - Beware ELOAD currently only supports single channel device

    Parameters:
        eload_device: The initialized ELOAD instance.

    Expected Behavior:
        - All outputs are disabled after the reset.
        - The mode is set to constant resistance (CR) with a value of 10kΩ.
    """
    eload = electronic_load

    # Reset the device
    eload.reset_device()

    # Verify all outputs are disabled, 10kohm, CR
    assert eload.get_output_state() == State.OFF, "Output is not disabled after reset."
    assert eload.get_mode() == EloadMode.CR, "Mode is not set to constant resistance (CR) after reset."
    assert eload.get_load() == 10000, "Load is not 10kohm after reset."

@pytest.mark.parametrize("measure_type", supported_measurement_types)
def test_measure(electronic_load, measure_type):
    """
    Test measurement functionality for the ELOAD.

    Parameters:
        electronic_load: The initialized ELOAD instance.

    Expected Behavior:
        - MeasureType.VOLTAGE and MeasureType.VOLTAGE_AC return valid measurements.
        - Unsupported types raise ValueError and fail the test.
    """
    eload = electronic_load
    try:
        result = eload.measure(measure_type)
        assert isinstance(result, float), f"Measurement for {measure_type} did not return a float."
    except ValueError:
        # pytest.fail(f"Measurement type {measure_type} unsupported: {e}")
        assert False, f"Measurement type {measure_type} unsupported"

if __name__ == "__main__":
    USER_Eload_ip = "TCPIP::192.168.1.13::INSTR"
    USER_device = "siglent_sdl1020xe"

    pytest.main(["tests/test_electronic_load.py", 
                 "--resource", USER_Eload_ip,
                 "--device", USER_device,       # Specify device to make test faster
                 "-m", "not manual_test",       # Filter remove manual tests
                 "-v"                           # verbose flag
                 ])
