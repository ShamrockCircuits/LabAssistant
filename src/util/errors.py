class LabAssistantError(Exception):
    """Base class for all exceptions in LabAssistant."""
    pass

class DeviceNotFoundError(LabAssistantError):
    """Raised when a device cannot be found."""
    def __init__(self, resource, message="Device not found"):
        self.resource = resource
        self.message = message
        super().__init__(self.message)

class DeviceConnectionError(LabAssistantError):
    """Raised when there is a connection error."""
    def __init__(self, connection_type, message="Connection error"):
        self.connection_type = connection_type
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