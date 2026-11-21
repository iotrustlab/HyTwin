from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder
import time
import random

# Connect to OpenPLC
client = ModbusTcpClient('localhost', port=502)  # Adjust the IP and port as needed

# Constants
TANK_VOLUME_ML = 900  # (32floz ~ 946mL) ~72s to fill @ 45000/3600=12.5mL/sec rate (not incl. dosing)
DOSE_VOLUME_ML = 5  # Adjust the dose volume as needed

# Mapping based on Modbus addressing
# Actuator mapping
ACT = {
    "red_doser": 6,  # QX0.6
    "blue_doser": 7,  # QX0.7
    "pump": 4,       # QX0.4
    "treatment_complete": 0  # QX0.0
}

# Sensor mapping
SENS = {
    "red_RGB": 0,       # IW0, Red channel
    "green_RGB": 1,     # IW1, Green channel (not used in this case)
    "blue_RGB": 2,      # IW2, Blue channel
    "range_sensor": 3,  # IW3, for distance measurement
}

# Additional variables to track state
dosing_complete = False
settling_timer = False
filling_stage = 0

# Initial state
water_volume_ml = 0
range_sensor = 100  # 100% range = empty container, min is 94% full (range sense = 6)
red_ml = 0
blue_ml = 0
red_concentration = 0
blue_concentration = 0
fill_rate_mlph = 45000  # Assuming an average fill rate of 45 Liters per Hour
step = 0

# Open file to save traces
with open("trace_output.txt", "w") as trace_file:
    trace_file.write("Timestamp,Water_Volume_ml,Red_Concentration,Blue_Concentration,Pump_State,Red_Doser,Blue_Doser,Range_Sensor,Treatment_Complete,Dosing_Complete,Settling_Timer,Filling_Stage\n")

    try:
        while True:
            # Simulate the filling of the tank
            step += 1
            range_sensor = 100 * (1 - water_volume_ml / TANK_VOLUME_ML)
            pump_result = client.read_coils(ACT['pump'])

            if not pump_result.isError() and pump_result.bits[0]:  # Pump is on
                water_volume_ml += fill_rate_mlph / 3600  # Increment the water volume

            # Read the state of the dosers, treatment complete, and stage from OpenPLC
            response = client.read_coils(ACT["red_doser"], 2)  # Get both red and blue doser states
            treatment_complete_result = client.read_coils(ACT["treatment_complete"])  # Read treatment_complete status
            stage_result = client.read_holding_registers(4, 1)  # Read the stage register (assuming QW4 corresponds to holding register 4)

            if not response.isError() and not treatment_complete_result.isError() and not stage_result.isError():
                red_dose, blue_dose = response.bits[0], response.bits[1]
                treatment_complete = treatment_complete_result.bits[0]  # Read as a boolean
                filling_stage = stage_result.registers[0]  # Extract the stage value

                # Determine if dosing is complete
                dosing_complete = not red_dose and not blue_dose

                # Determine if settling timer is active (depends on stage or external timer signal)
                settling_timer = filling_stage == 4  # Assuming stage 4 is the settling stage

                # Adjust red and blue concentrations and volumes
                if red_dose:
                    red_ml += DOSE_VOLUME_ML
                    water_volume_ml += DOSE_VOLUME_ML  # Account for dose volume
                if blue_dose:
                    blue_ml += DOSE_VOLUME_ML
                    water_volume_ml += DOSE_VOLUME_ML  # Account for dose volume

                # Overflow handling
                if water_volume_ml > TANK_VOLUME_ML:
                    overflow = water_volume_ml - TANK_VOLUME_ML
                    red_ml -= .5 * overflow * red_concentration
                    blue_ml -= .5 * overflow * blue_concentration
                    water_volume_ml = TANK_VOLUME_ML  # Cap the water volume at the tank capacity

                # Update concentrations
                if water_volume_ml > 0:
                    red_concentration = red_ml / water_volume_ml
                    blue_concentration = blue_ml / water_volume_ml

                # Write sensor values to OpenPLC
                client.write_registers(SENS["red_RGB"], [int(red_concentration * 255), 0, int(blue_concentration * 255)])
                client.write_registers(SENS["range_sensor"], int(range_sensor * 100))

                # Generate timestamp and write to trace file
                timestamp = time.time()
                pump_state = pump_result.bits[0]
                trace_file.write(f"{timestamp},{water_volume_ml:.2f},{red_concentration*255:.2f},{blue_concentration*255:.2f},{int(pump_state)},{int(red_dose)},{int(blue_dose)},{range_sensor:.2f},{int(treatment_complete)},{int(dosing_complete)},{int(settling_timer)},{filling_stage}\n")
                trace_file.flush()  # Ensure the trace is written to the file

                print(f'Water Vol: {water_volume_ml:.2f} ml, Red Level: {red_concentration*255:.2f}, Blue Conc: {blue_concentration*255:.2f}, Pump: {pump_state}, Red Dose: {red_dose}, Blue Dose: {blue_dose}, Range Sensor: {range_sensor:.2f}, Treatment Complete: {treatment_complete}, Dosing Complete: {dosing_complete}, Settling Timer: {settling_timer}, Filling Stage: {filling_stage}')
            else:
                print(f'Error reading from OpenPLC: {response}')

            time.sleep(1)  # Adjust the sleep time as needed

    except KeyboardInterrupt:
        pass  # Exit the loop on Ctrl-C

client.close()
