import pytest

def pytest_addoption(parser):
    """Add a custom command-line option for specifying the resource."""
    parser.addoption(
        "--resource", 
        action="store", 
        default=None, 
        help="Resource identifier for the power supply (e.g., VISA address)"
    )
    parser.addoption(
        "--device",
        action="store",
        default=None,
        help="Exact device name as it appears in the config directory."
    )
    parser.addoption(
        "--run_manual", action="store_true", default=False, help="run tests requiring user interaction" # Example short two terminals
    )

def pytest_configure(config):
    config.addinivalue_line("markers", "manual_test: mark test as requiring user intervention")

def pytest_collection_modifyitems(config, items):
    if config.getoption("--run_manual"):
        # --run_manual given in cli: do not skip manual tests
        return
    skip_manual = pytest.mark.skip(reason="need --run_manual -s option to run")
    for item in items:
        if "manual_test" in item.keywords:
            item.add_marker(skip_manual)

@pytest.fixture
def resource(request):
    """Fixture to access the resource argument."""
    return request.config.getoption("--resource")

@pytest.fixture
def device(request):
    """Fixture to access the device argument."""
    return request.config.getoption("--device")