'''
Module initialization.\n
Required to import child device classes which populates the device registry.\n
'''
# # Things the user will need to import
# from src.enums.generic_enum import ConnectionType, DeviceType, MeasureType, State, Channel, ReadWrite
# from src.ABC.PSU import GenericPSU
# from src.ABC.SCOPE import GenericScope, HDiv, VDiv, Stats
# from src.ABC.ELOAD import GenericEload, EloadMode, EloadSlewRate

from src.lab_assistant import LabAssistant

# We must call this method when the user first imports the class
# It adds all the device drivers from the config folder to the registry
LabAssistant._import_all_classes_from_directory()