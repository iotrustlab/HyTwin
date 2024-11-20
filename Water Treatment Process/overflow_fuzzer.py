import random
from pymodbus.client import ModbusTcpClient
import time
from dataclasses import dataclass
from typing import List, Dict
import numpy as np

@dataclass
class OverflowTrace:
    water_volume: List[float]
    pump_states: List[bool]
    timestamps: List[float]
    overflow_detected: bool

class TankOverflowFuzzer:
    def __init__(self, host='localhost', port=502):
        self.client = ModbusTcpClient(host, port)
        self.TANK_VOLUME_ML = 900  # From simulator constants

    def generate_fuzz_scenario(self) -> Dict:
        return {
            'pump_duration': random.uniform(5, 15),  # seconds
            'initial_volume': random.uniform(800, 900),  # ml
            'pump_on_off_sequence': [
                random.choice([True, False]) 
                for _ in range(10)
            ]
        }

    def execute_scenario(self, scenario: Dict) -> OverflowTrace:
        water_volumes = []
        pump_states = []
        timestamps = []
        overflow_detected = False
        
        # Set initial conditions
        start_time = time.time()
        current_volume = scenario['initial_volume']
        
        for pump_state in scenario['pump_on_off_sequence']:
            # Write pump state
            self.client.write_coil(4, pump_state)
            
            # Let system run for a bit
            time.sleep(scenario['pump_duration'] / len(scenario['pump_on_off_sequence']))
            
            # Read results
            range_sensor = self.client.read_holding_registers(3, 1).registers[0] / 100.0
            current_volume = self.TANK_VOLUME_ML * (1 - range_sensor/100)
            
            current_time = time.time() - start_time
            water_volumes.append(current_volume)
            pump_states.append(pump_state)
            timestamps.append(current_time)
            
            # Check for overflow
            if current_volume > self.TANK_VOLUME_ML:
                overflow_detected = True
                break

        return OverflowTrace(
            water_volume=water_volumes,
            pump_states=pump_states,
            timestamps=timestamps,
            overflow_detected=overflow_detected
        )

    def run_fuzzing_campaign(self, num_tests: int = 100) -> List[OverflowTrace]:
        overflow_traces = []
        
        for _ in range(num_tests):
            scenario = self.generate_fuzz_scenario()
            trace = self.execute_scenario(scenario)
            
            if trace.overflow_detected:
                overflow_traces.append(trace)
                print(f"Overflow detected! Initial volume: {scenario['initial_volume']}")
                print(f"Pump sequence: {scenario['pump_on_off_sequence']}")
        
        return overflow_traces

    def save_traces(self, traces: List[OverflowTrace], filename: str):
        with open(filename, 'w') as f:
            f.write("Timestamp,Water_Volume,Pump_State\n")
            for trace in traces:
                for t, v, p in zip(trace.timestamps, trace.water_volume, trace.pump_states):
                    f.write(f"{t},{v},{int(p)}\n")

if __name__ == "__main__":
    fuzzer = TankOverflowFuzzer()
    overflow_traces = fuzzer.run_fuzzing_campaign(100)
    if overflow_traces:
        fuzzer.save_traces(overflow_traces, "overflow_traces.txt")
        print(f"Found {len(overflow_traces)} traces with overflow violations")
    else:
        print("No overflow violations detected")