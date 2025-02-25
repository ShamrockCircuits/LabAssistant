from src.lab_assistant import *
from src.enums.eload_enum import *
from src.enums.generic_enum import *
from src.enums.scope_enum import *

# from DriversPy.SCOPE import 
from src.ABC.ELOAD import EloadMode
from typing import List
from time import sleep

# Vin_TPs = range(90,400,10)
Vin_TPs = range(150, 700, 10)
Pout_TPs = range(2000,10100,200)

# Convert from mW to W
Pout_TPs = [x / 1000 for x in Pout_TPs]

class datapoint():

    def __init__(self, Vin, Po, PulseAVG, PulseMAX, PulseMIN, Observed_Runt_SR):
        self.Vin = Vin
        self.Po = Po
        self.PulseAVG = PulseAVG
        self.PulseMAX = PulseMAX
        self.PulseMIN = PulseMIN
        self.RuntFLAG = str(Observed_Runt_SR)

    def get(self):
        return [self.Vin, self.Po, self.PulseAVG, self.PulseMAX, self.PulseMIN, self.RuntFLAG]

class DataBase():

    database : List[datapoint] = []

    @classmethod
    def add(cls, Vin, Po, PulseAVG, PulseMAX, PulseMIN, Observed_Runt_SR):
        cls.database.append(datapoint(Vin, Po, PulseAVG, PulseMAX, PulseMIN, Observed_Runt_SR))

    @classmethod
    def get(cls):
        result = []
        for elem in cls.database:
            result.append(elem.get())
        return result
    
    @classmethod
    def get_str(cls):

        result : str = "Vin, Po, PulseAVG, PulseMAX, PulseMIN, SR_RUNT_FLAG \n"

        for elem in cls.database:
            result += (str(elem.get()).strip("[]") + "\n")

        return result

print(LabAssistant.list_available_resources())

Keithley_Eload = LabAssistant.setup_eload(resource="GPIB0::5::INSTR", connection_type= ConnectionType.RAW, EnableDebug = False)
Magna_PSU = LabAssistant.setup_psu(resource="GPIB0::1::INSTR", connection_type=ConnectionType.RAW, EnableDebug = False)
Lecroy_Scope = LabAssistant.setup_scope(resource="USB0::0x05FF::0x1023::3557N06935::INSTR", connection_type=ConnectionType.RAW, EnableDebug = False, Forced_Driver = "lecroy_HDO6104")

# LabAssistant.CreateEload()
Magna_PSU.set_voltage(154)
Magna_PSU.set_current(0.3)
Magna_PSU.set_ovp(700)
Magna_PSU.set_ocp(0.5)
Magna_PSU.enable_output()

# Eload test
Keithley_Eload.set_load(EloadMode.CP, value=0.01)
Keithley_Eload.enable_output()

# MAIN Test LOOP
input("Start Test? *Enter*")

for Vin in Vin_TPs:
    # Update Voltage
    print(">>>> New Voltage")
    Magna_PSU.set_voltage(Vin)

    for Po in Pout_TPs:
        # Update Current
        print(f"Test: {Vin}Vin, {Po}W", end ="")
        Keithley_Eload.set_load(EloadMode.CP, Po)
        # Clear Stats
        sleep(0.1)
        Lecroy_Scope.send_command("CLSW")

        # sleep(1)
        # if Keithley_Eload.Measure(MeasureType.VOLTAGE) < 11:
        #     print("RAIL COLLAPSED")
        #     Keithley_Eload.Set_Load(EloadMode.CP, 0.01)
        #     sleep(2)
        #     break

        # PulseWidth = Lecroy_Scope._safe_string_to_float(Lecroy_Scope.SendCommand("PAST? CUST,P1"))
        # # SR_Pulse = Lecroy_Scope._safe_string_to_float(Lecroy_Scope.SendCommand("PAST? CUST,P2"))
        
        # if len(PulseWidth) < 3:
        #     print("Skip Sweep Missed Trigger")
        #     break
        
        # try:
        #     SR_Pulse_MIN = SR_Pulse[3]
        #     SR_RUNT_FLAG = (SR_Pulse_MIN < 1/(1000*1000)) #Flag anything less than 1us as a run pulse
        # except:
        #     SR_Pulse_MIN = 0 # At very light load no SR pulse is provided... odd
        #     SR_RUNT_FLAG = "MISSED SR PULSE"

        # if( SR_RUNT_FLAG == True ):
        #     print(" << RUNT >> ", end="")
        # if( SR_RUNT_FLAG == "MISSED SR PULSE"):
        #     print(" << MISSED SR PULSE >> ", end="")

        # DataBase.add(Vin=Vin, Po=Po, PulseAVG=PulseWidth[0], PulseMAX=PulseWidth[1], 
        #              PulseMIN=PulseWidth[3], Observed_Runt_SR=SR_RUNT_FLAG)

        # print(f" ---- Pulse Width ---> {PulseWidth[0]}")
        print("")

Magna_PSU.disable_output()
Keithley_Eload.disable_output()

with open('Outputs\\results.txt', 'w') as output:
    output.write(DataBase.get_str())
print("HERE")

