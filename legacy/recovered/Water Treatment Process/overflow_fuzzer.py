from pymodbus.client.sync import ModbusTcpClient
import time
import random
from dataclasses import dataclass
from typing import List
import datetime

@dataclass
class SafetyViolation:
    timestamp: float
    range_sensor: float
    pump_state: bool
    description: str

class SafetyFuzzer:
    def __init__(self, host='localhost', port=502):
        self.client = ModbusTcpClient(host, port)
        
        # Constants from ST program
        self.DESIRED_DISTANCE = 10
        
        # Modbus register mapping
        self.REGISTERS = {
            "flow_sensor": 0,    # %IW0
            "range_sensor": 1,   # %IW1
            "pump": 0           # %QX0.0 (coil)
        }
        
        # Create timestamp for file names
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Open files for logging
        self.trace_file = open(f"fuzzing_trace_{self.timestamp}.txt", "w")
        self.violation_file = open(f"violations_{self.timestamp}.txt", "w")
        self.summary_file = open(f"fuzzing_summary_{self.timestamp}.txt", "w")
        
        # Write headers
        self.trace_file.write("Timestamp,Event,RangeSensor,PumpState,Description\n")
        self.violation_file.write("Timestamp,RangeSensor,PumpState,Description\n")

    def write_range_sensor(self, value: float) -> bool:
        """Safely write range sensor value to PLC"""
        try:
            register_value = int(value * 100)
            self.client.write_registers(self.REGISTERS["range_sensor"], [register_value])
            self.log_trace("WRITE", value)
            return True
        except Exception as e:
            self.log_trace("ERROR", value, str(e))
            return False

    def log_trace(self, event: str, range_sensor: float, extra: str = ""):
        """Log to trace file"""
        timestamp = time.time()
        pump_result = self.client.read_coils(self.REGISTERS["pump"], 1)
        pump_state = pump_result.bits[0] if not pump_result.isError() else "ERROR"
        
        self.trace_file.write(f"{timestamp},{event},{range_sensor:.2f},{pump_state},{extra}\n")
        self.trace_file.flush()

    def log_violation(self, violation: SafetyViolation):
        """Log to violations file"""
        self.violation_file.write(
            f"{violation.timestamp},{violation.range_sensor:.2f},"
            f"{violation.pump_state},{violation.description}\n"
        )
        self.violation_file.flush()

    def check_safety_violation(self, range_sensor: float, pump_state: bool) -> SafetyViolation:
        """Check for safety violation based on ST program logic"""
        if range_sensor > self.DESIRED_DISTANCE and pump_state:
            violation = SafetyViolation(
                timestamp=time.time(),
                range_sensor=range_sensor,
                pump_state=pump_state,
                description=f"VIOLATION: Pump ON when range_sensor ({range_sensor:.2f}) > DESIRED_DISTANCE ({self.DESIRED_DISTANCE})"
            )
            self.log_violation(violation)
            return violation
        return None

    def test_sequence(self, duration: float = 5.0) -> List[SafetyViolation]:
        """Run test sequence"""
        violations = []
        start_time = time.time()
        
        test_sequences = [
            # Around threshold
            [9, 10, 11, 12, 13],
            # Above threshold
            [15, 20, 25, 30],
            # Oscillating
            [9.5, 10.5, 9.8, 10.2, 10.8],
            # Rapid changes
            [5, 15, 8, 12, 7, 11]
        ]
        
        for seq_num, sequence in enumerate(test_sequences):
            self.log_trace("START_SEQUENCE", 0, f"Sequence {seq_num + 1}: {sequence}")
            
            for value in sequence:
                if time.time() - start_time > duration:
                    break
                    
                if self.write_range_sensor(value):
                    time.sleep(0.2)
                    
                    pump_result = self.client.read_coils(self.REGISTERS["pump"], 1)
                    if not pump_result.isError():
                        pump_state = pump_result.bits[0]
                        
                        violation = self.check_safety_violation(value, pump_state)
                        if violation:
                            violations.append(violation)
                    
                time.sleep(0.1)
            
            self.log_trace("END_SEQUENCE", 0, f"Sequence {seq_num + 1} complete")
        
        return violations

    def run_campaign(self, iterations: int = 3):
        """Run fuzzing campaign"""
        try:
            print(f"Starting fuzzing campaign... (logs: fuzzing_*_{self.timestamp}.txt)")
            total_violations = []
            
            self.summary_file.write("Fuzzing Campaign Summary\n")
            self.summary_file.write("======================\n")
            self.summary_file.write(f"Start Time: {datetime.datetime.now()}\n\n")
            
            for i in range(iterations):
                print(f"\nIteration {i+1}/{iterations}")
                violations = self.test_sequence()
                total_violations.extend(violations)
                
                # Log iteration summary
                summary = f"\nIteration {i+1} Results:\n"
                summary += f"Violations found: {len(violations)}\n"
                self.summary_file.write(summary)
                self.summary_file.flush()
                
                time.sleep(1)
            
            # Write final summary
            final_summary = f"\nFinal Campaign Results\n"
            final_summary += f"=====================\n"
            final_summary += f"Total iterations: {iterations}\n"
            final_summary += f"Total violations: {len(total_violations)}\n\n"
            final_summary += "Violation Details:\n"
            
            for v in total_violations:
                final_summary += f"Time: {v.timestamp}, Range: {v.range_sensor:.2f}, "
                final_summary += f"Pump: {v.pump_state}, {v.description}\n"
            
            self.summary_file.write(final_summary)
            print("\nFuzzing complete. Check output files for results.")
            
        except Exception as e:
            error_msg = f"\nError during fuzzing: {str(e)}"
            self.summary_file.write(error_msg)
            print(error_msg)
            
        finally:
            self.trace_file.close()
            self.violation_file.close()
            self.summary_file.close()
            self.client.close()

if __name__ == "__main__":
    fuzzer = SafetyFuzzer()
    fuzzer.run_campaign(iterations=5)