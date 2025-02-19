"""
Eload specific enum types.
"""
from enum import Enum

class EloadMode(Enum):
    '''
    Electronic load type.

    Attributes:
        CR (str) - "Constant Resistance"
        CP (str) - "Constant Power"
        CV (str) - "Constant Voltage"
        CC (str) - "Constant Current"
        UNDEFINED (str) - "Undefined"
    '''
    CR = "Constant Resistance"
    CP = "Constant Power"
    CV = "Constant Voltage"
    CC = "Constant Current"
    UNDEFINED = "Undefined"

class EloadSlewRate(Enum):
    '''
    Slew rate enumeration class.

    Attributes:
        FASTEST (str) - "Fast". Used to define the fastest possible slew rate on this device.
        SLOWEST (str) - "Slow". Used to define the slowest possible slew rate on this device.
        CUSTOM (str) - "Custom". User defined slew rate.
        UNDEFINED (str) - "Undefined". Default value.
    '''
    FASTEST = "Fast"
    SLOWEST = "Slow"
    CUSTOM = "Custom"
    UNDEFINED = "Undefined"
