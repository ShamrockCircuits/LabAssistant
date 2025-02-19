"""
Oscilloscope specific enum types.
"""
from enum import Enum

class VDiv(Enum):
    '''
    Voltage scales to be set on oscilloscope.
    '''
    _500uV = "500e-6"
    _1mV = "1e-3"
    _2mV = "2e-3"
    _5mV = "5e-3"
    _10mV = "10e-3"
    _20mV = "20e-3"
    _50mV = "50e-3"
    _100mV = "100e-3"
    _200mV = "200e-3"
    _500mV = "500e-3"
    _1V = "1"
    _2V = "2"
    _5V = "5"
    _10V = "10"

class HDiv(Enum):
    '''
    Time scales to be set to oscilloscope.
    '''
    _1ns = "1e-9"
    _2ns = "2e-9"
    _5ns = "5e-9"
    _10ns = "10e-9"
    _20ns = "20e-9"
    _50ns = "50e-9"
    _100ns = "100e-9"
    _200ns = "200e-9"
    _500ns = "500e-9"
    _1us = "1e-6"
    _2us = "2e-6"
    _5us = "5e-6"
    _10us = "10e-6"
    _20us = "20e-6"
    _50us = "50e-6"
    _100us = "100e-6"
    _200us = "200e-6"
    _500us = "500e-6"
    _1ms = "1e-3"
    _2ms = "2e-3"
    _5ms = "5e-3"
    _10ms = "10e-3"
    _20ms = "20e-3"
    _50ms = "50e-3"
    _100ms = "100e-3"
    _200ms = "200e-3"
    _500ms = "500e-3"
    _1S = "1"
    _2S = "2"
    _5S = "5"
    _10S = "10"
    _20S = "20"
    _50S = "50"

class Stats(Enum):
    '''
    Common statistics available on oscilloscopes.
    '''
    PKPK = "PKPK"
    MAX = "MAX"
    MIN = "MIN"
    AMPL = "AMPL"
    TOP = "TOP"
    BASE = "BASE"
    MEAN = "MEAN"
    RMS = "Rms"
    PER = "PER"
    FREQ = "FREQ"
    RISE = "RISE"
    FALL = "FALL"
    DUTY = "DUTY"
    WidthAtLevel = "WIDLV"
