'''
Integration Test for Power Supply.
Requires real hardware to be connected.
'''
import pytest
from time import sleep

from src.lab_assistant import LabAssistant
from src.enums.generic_enum import *
from src.enums.eload_enum import *
from src.enums.scope_enum import *


@pytest.fixture
def power_supply(resource, device):
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
    psu = LabAssistant.setup_psu(resource, Forced_Driver = device)  # Replace with actual initialization logic
    yield psu
    psu.cleanup()

@pytest.mark.dependency(name="set_get_voltage")         # When using parameterized inputs, name must be provided
@pytest.mark.parametrize("volt", ["0", "1.5", "4"])
def test_set_and_get_voltage(power_supply, volt):
    """
    Test setting and retrieving voltage on the power supply.

    Parameters:
        power_supply: The initialized power supply instance.
        volt: The target voltage value to set and verify (parameterized).

    Expected Behavior:
        - The retrieved voltage matches the set voltage (`volt`).
    """
    psu = power_supply
    for ch in psu.device_info.available_channels:
        psu.set_voltage(volt, ch)
        rd_volt = psu.get_voltage(ch)
        assert rd_volt == float(volt), f"Tried to set {volt}V but got {rd_volt}V."

@pytest.mark.dependency(name="set_get_current")
@pytest.mark.parametrize("curr", ["0", "0.1", "0.4"])
def test_set_and_get_current(power_supply, curr):
    """
    Test setting and retrieving current on the power supply.

    Parameters:
        power_supply: The initialized power supply instance.
        curr: The target current limit value to set and verify (parameterized).

    Expected Behavior:
        - The retrieved current matches the set current (`curr`).
    """
    psu = power_supply
    for ch in psu.device_info.available_channels:
        psu.set_current(curr, ch)
        assert psu.get_current(ch) == float(curr), f"Error: Configurating or reading voltage on {ch}."

@pytest.mark.dependency()
def test_toggle_output(power_supply):
    """
    Test toggling the output state of the power supply.

    Parameters:
        power_supply: The initialized power supply instance.

    Expected Behavior:
        - The output state matches the requested state (`ON` or `OFF`) for each channel.
    """
    psu = power_supply
    for ch in psu.device_info.available_channels:
        for state in [State.ON, State.OFF]:
            psu.set_output_state(state, ch)
            assert psu.get_output_state(ch) == state, f"Failed to set ouptut state to {state.value} on {ch}."

@pytest.mark.dependency(depends=["set_get_voltage", "set_get_current", "test_toggle_output"])
def test_device_reset(power_supply):
    """
    Test device reset functionality.

    Parameters:
        power_supply: The initialized power supply instance.

    Dependencies:
        - The `set_get_voltage` test must pass to ensure voltage setting works.
        - The `set_get_current` test must pass to ensure current limit configuration works.
        - The `test_toggle_output` test must pass to ensure output toggling is functional.
        
    Expected Behavior:
        - All outputs are disabled.
        - All channels have a voltage of 0V and a current limit of 0A.
    """

    psu = power_supply
    psu.reset_device()
    for ch in psu.device_info.available_channels:
        assert psu.get_voltage(ch) == 0, f"Voltage on {ch} was not reset correctly."
        assert psu.get_current(ch) == 0, f"Current on {ch} was not reset correctly."
        assert psu.get_output_state(ch) == State.OFF, f"Output state on {ch} was not reset correctly."

@pytest.mark.dependency(depends=["set_get_voltage", "set_get_current","test_toggle_output"])
@pytest.mark.parametrize("volt", ["0.1", "1.5", "4"])
def test_measure_voltage(power_supply, volt):
    """
    Test voltage measurement functionality for the power supply.

    This test verifies that the power supply can measure the voltage correctly
    after setting the desired voltage on all available channels.

    Parameters:
        power_supply: A fixture that initializes the power supply for testing.
        volt: The target voltage value to be set and measured, provided via 
              parameterization.

    Test Steps (for each channel):
        1. Set the specified voltage (`volt`)
        2. Configure the current limit to 0.1 A
        3. Enable output
        4. Verify the measured voltage matches the set voltage within a tolerance.

    Dependencies:
        - The `set_get_voltage` test must pass to ensure voltage setting works.
        - The `set_get_current` test must pass to ensure current limit configuration works.
        - The `test_toggle_output` test must pass to ensure output toggling is functional.

    Expected Behavior:
        - The measured voltage should match the set voltage (`volt`) within a relative 
          tolerance of ±0.1V.
    """
    psu = power_supply
    for ch in psu.device_info.available_channels:
        psu.set_voltage(volt, ch)
        psu.set_current(0.1, ch)
        psu.enable_output(ch)

        # Difficult to define settling time of an unknown PSU
        # Give the PSU 5 seconds to settle, but end early if already settled
        for _ in range(5):
            sleep(1)
            if psu.measure(MeasureType.VOLTAGE, channel=ch) == pytest.approx(expected=float(volt), abs=0.1):
                break
        
        # Sample one last time, confirm previous wasn't just a lucky sample
        voltage = psu.measure(MeasureType.VOLTAGE, channel=ch)
        psu.disable_output(ch)
        assert voltage == pytest.approx(expected=float(volt), abs=0.1), f"Expected {volt}V measured {voltage}V."

@pytest.mark.manual_test
@pytest.mark.dependency(depends=["set_get_voltage", "set_get_current","test_toggle_output"])
@pytest.mark.parametrize("curr", ["0.1", "0.5", "1"])
def test_measure_current(power_supply, curr):
    """
    Test current measurement functionality for the power supply.

    This test verifies that the power supply can measure the current correctly
    after setting the desired current on all available channels.

    Parameters:
        power_supply: A fixture that initializes the power supply for testing.
        curr: The target current value to be set and measured, provided via 
              parameterization.

    Test Steps (for each channel):
        1. Set the specified current (`curr`)
        2. Configure the voltage limit to 0.5 V
        3. Enable output
        4. Verify the measured current matches the set current within a tolerance.

    Dependencies:
        - The `set_get_voltage` test must pass to ensure voltage setting works.
        - The `set_get_current` test must pass to ensure current limit configuration works.
        - The `test_toggle_output` test must pass to ensure output toggling is functional.

    Expected Behavior:
        - The measured current should match the set current (`curr`) within a relative 
          tolerance of ±0.1A.
    """
    psu = power_supply
    confirmation = input("Test..")
    for ch in psu.device_info.available_channels:
        psu.set_voltage(0.5, ch)
        psu.set_current(curr, ch)
        psu.enable_output(ch)
        sleep(1)
        voltage = psu.measure(MeasureType.CURRENT, channel=ch)
        psu.disable_output(ch)
        assert voltage == pytest.approx(expected=float(curr), abs=0.1), f"Expected {curr}A measured {curr}A."

# @pytest.mark.manual_test
# def test_remote_sense(power_supply):
#     """Test remote sense functionality."""
#     psu = power_supply
#     for ch in psu.device_info.available_channels:
#         for state in [State.ON, State.OFF]:
#             psu.set_remote_sense(ch, state)
#             input(f"Verify {ch} remote sense is {state}... Press Enter to continue.")

# @pytest.mark.user_input
# def test_ovp(power_supply):
#     """Test Over Voltage Protection."""
#     psu = power_supply
#     for ch in psu.device_info.available_channels:
#         psu.set_ovp(10.0, ch)
#         input(f"Verify {ch} OVP is set to 10V... Press Enter to continue.")

# def test_ocp(power_supply):
#     """Test Over Current Protection."""
#     psu = power_supply
#     for ch in psu.device_info.available_channels:
#         psu.set_ocp(1.0, ch)
#         input(f"Verify {ch} OCP is set to 1A... Press Enter to continue.")

# def test_get_id(power_supply):
#     """Test retrieving device ID."""
#     psu = power_supply
#     device_id = psu.get_id()
#     print(f"Device ID: {device_id}")
#     assert device_id is not None, "Error: Device ID is None."


if __name__ == "__main__":
    pytest.main(["tests/test_power_supply.py", 
                 "--resource", "TCPIP::192.168.1.12::INSTR",
                 "--device", "siglent_spd1168x", 
                 "-v"])
    
