import warnings

class LabAssistantError(Exception):
    """Base class for all exceptions in LabAssistant."""

class LabAssistantWarning(Warning):
    """Base class for all warnings in LabAssistant."""

# =================== Warning Classes ======================
class UnimplementedOptionalMethod(LabAssistantWarning):
    """Warning raised when an optional method is not implemented."""
    def __init__(self, method_name, message="Optional method {method_name} not supported"):
        self.method_name = method_name
        self.message = f"{message}: {method_name}"
        super().__init__(self.message)

# ==================== Error Classes =======================
class UnimplementedSafetyCriticalMethod(LabAssistantError):
    """Raised when a safety critical method is not supported."""
    # This is a bit tricky... the idea is if a class lacks a safety feature such as OVP
    # This error isn't necassarily raised unless OVP is called above some limit
    # Maybe I'm overcomplicating things though... I probably am.... yeah I'll just call it
    # On all unimplemented safety methods 

    def __init__(self, method_name, message="Safety critical method not supported"):
        self.method_name = method_name
        self.message = f"{message}: {method_name}"
        super().__init__(self.message)

# class DeviceNotFoundError(LabAssistantError):     # Wasn't using this error so I removed it... 
#     """Raised when a device cannot be found."""   # I've been using DeviceInitializationError instead
#     def __init__(self, resource, message="Device not found"):
#         self.resource = resource
#         self.message = message
#         super().__init__(self.message)

class DeviceConnectionError(LabAssistantError):
    """Raised when there is a connection error."""
    def __init__(self, message="Connection error"):
        self.message = message
        super().__init__(self.message)

class UnsupportedDeviceError(LabAssistantError):
    """Raised when an unsupported device is attempted to be used."""
    def __init__(self, model, message="Unsupported device"):
        self.model = model
        self.message = message
        super().__init__(self.message)

class DeviceInitializationError(LabAssistantError):
    """Raised when there is an error initializing a device."""
    def __init__(self, message="Device initialization error"):
        self.message = message
        super().__init__(self.message)

class InvalidCommandError(LabAssistantError):
    """Raised when an invalid SCPI command is issued."""
    def __init__(self, command, message="Invalid SCPI command"):
        self.command = command
        self.message = message
        super().__init__(self.message)

class DeviceChannelError(LabAssistantError):
    """Raised when an invalid channel is specified."""
    def __init__(self, message="Channel does not exist on this device"):
        self.message = message
        super().__init__(self.message)
    
class UnsupportedMeasurementType(LabAssistantError):
    """Raised when an unsupported measurement type is attempted."""
    def __init__(self, message="Unsupported measurement type"):
        self.message = message
        super().__init__(self.message)