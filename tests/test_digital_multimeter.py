'''
Integration Test for DMM.
Requires real hardware to be connected.
'''
import pytest
from src.lab_assistant import LabAssistant
from src.enums.generic_enum import MeasureType

# pylint: disable=redefined-outer-name
unsupported_measurement_types = {MeasureType.UNDEFINED, MeasureType.POWER}

@pytest.fixture
def dmm_device(resource, device):
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
    dmm = LabAssistant.setup_dmm(resource, Forced_Driver = device)  # Replace with actual initialization logic
    yield dmm
    dmm.cleanup()

@pytest.mark.dependency(name="set_get_mode")
@pytest.mark.parametrize("mode", [m for m in MeasureType if m not in unsupported_measurement_types])
def test_set_get_mode(dmm_device, mode):
    """
    Test setting and retrieving the measurement mode on the DMM.

    Parameters:
        dmm_device: The initialized DMM instance.
        mode: The measurement mode to set and verify, parameterized over MeasureType.

    Expected Behavior:
        - The mode set by set_mode() matches the mode retrieved by get_mode().
        - XOR If the mode is invalid, a ValueError is raised.
    """
    dmm = dmm_device

    try:
        # Attempt to set the measurement mode
        dmm.set_mode(mode)

        # Retrieve and validate the mode
        observed_mode = dmm.get_mode()
        assert observed_mode == mode, f"Error: Expected mode {mode} but observed {observed_mode}."

    except ValueError as e:
        # We will mark this as a fail, since the device does not support this measure type. 
        assert mode not in MeasureType, f"Unexpected ValueError for valid mode {mode}. Error: {e}"

@pytest.mark.dependency(depends=["set_get_mode"])
@pytest.mark.parametrize("measure_type", [MeasureType.VOLTAGE, MeasureType.VOLTAGE_AC])
def test_measure_voltage(dmm_device, measure_type):
    """
    Test voltage measurement functionality for the DMM.\n

    Parameters:
        dmm_device: The initialized DMM instance.
        measure_type: The voltage measurement type to test (VOLTAGE or VOLTAGE_AC).

    Expected Behavior:
        - The measure() method returns a value less than 1V. (floating inputs)
    """
    dmm = dmm_device
    measured_value = dmm.measure(measure_type)

    # Validate the measured value is less than 1V, some devices this will be worse
    # Might need to short terminals, its just a sanity check really
    assert measured_value < 1.0, f"Error: Measured {measured_value}V, expected less than 1V for {measure_type}."

@pytest.mark.dependency(depends=["set_get_mode"])
@pytest.mark.parametrize("measure_type", [MeasureType.CURRENT, MeasureType.CURRENT_AC])
def test_measure_current(dmm_device, measure_type):
    """
    Test current measurement functionality for the DMM.

    Parameters:
        dmm_device: The initialized DMM instance.
        measure_type: The current measurement type to test (CURRENT or CURRENT_AC).

    Expected Behavior:
        - The measure() method returns a value less than 10mA.
    """
    dmm = dmm_device
    measured_value = dmm.measure(measure_type)

    # Validate the measured value is less than 10mA
    assert measured_value < 0.01, f"Error: Measured {measured_value}A, expected less than 10mA for {measure_type}."

@pytest.mark.dependency(depends=["set_get_mode"])
def test_measure_frequency(dmm_device):
    """
    Test frequency measurement functionality for the DMM.

    Parameters:
        dmm_device: The initialized DMM instance.

    Expected Behavior:
        - If the input is floating, the measured frequency should be less than 100Hz.
        - Likely observed values are around 50Hz or 60Hz depending on the location.
    """
    dmm = dmm_device
    measured_frequency = dmm.measure(MeasureType.FREQUENCY)

    # Validate that the frequency is less than 100Hz, likely 60/50Hz if floating
    assert measured_frequency < 100.0, f"Error: Measured {measured_frequency}Hz, expected less than 100Hz for floating input."

@pytest.mark.dependency(depends=["set_get_mode"])
def test_measure_capacitance(dmm_device):
    """
    Test capacitance measurement functionality for the DMM.

    Parameters:
        dmm_device: The initialized DMM instance.

    Expected Behavior:
        - If the input is floating, the measured capacitance should be less than 10nF.
    """
    dmm = dmm_device
    measured_capacitance = dmm.measure(MeasureType.CAPACITANCE)

    # Validate that the capacitance is less than 10nF
    assert measured_capacitance < 10e-9, f"Error: Measured {measured_capacitance}F, expected less than 10nF for floating input."

@pytest.mark.dependency(depends = ["set_get_mode"])
def test_reset(dmm_device):
    """
    Test resetting the DMM to its default state.

    Parameters:
        dmm_device: The initialized DMM instance.

    Expected Behavior:
        - The device is reset successfully.
        - The measurement mode is set to MeasureType.VOLTAGE after the reset.
    """
    dmm = dmm_device
    dmm.reset_device()
    assert dmm.get_mode() == MeasureType.VOLTAGE, "DMM mode after reset is not set to MeasureType.VOLTAGE."

if __name__ == "__main__":

    pytest.main(["tests/test_digital_multimeter.py", 
                 "--resource", "USB0::0xF4EC::0x1201::SDM35HBQ802019::INSTR",
                 "--device", "siglent_sdm3055",     # Specify device to make test faster
                 "-m", "not manual_test",           # Filter remove manual tests (change to "not manual_test")
                 "-v"])                             # verbose flag
