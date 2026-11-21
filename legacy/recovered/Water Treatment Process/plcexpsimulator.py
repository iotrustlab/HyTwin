from pymodbus.client.sync import ModbusTcpClient
import time

class PLCSim:
    def __init__(self, host='localhost', port=502):
        self.client = ModbusTcpClient(host, port)
        
        # Constants and initial values
        self.TANK_CAPACITY = 50
        self.FLOW_RATE = 2  # Units per second
        self.DESIRED_DISTANCE = 10  # Fixed as per ST program
        
        # Modbus register mapping
        self.REGISTERS = {
            "flow_sensor": 0,    # %IW0
            "range_sensor": 1,   # %IW1
            "pump": 0           # %QX0.0 (coil)
        }
        
        # Initialize state variables
        self.flow_sensor = 0
        self.range_sensor = self.TANK_CAPACITY  # Start with empty tank
        self.pump_state = False
        
        # Open trace file
        self.trace_file = open("trace_output.txt", "w")
        self.trace_file.write("Timestamp,FlowSensor,RangeSensor,Pump,DesiredDistance\n")
        
    def write_trace(self):
        """Write current state to trace file"""
        timestamp = time.time()
        self.trace_file.write(f"{timestamp},{self.flow_sensor},"
                            f"{self.range_sensor:.2f},{int(self.pump_state)},"
                            f"{self.DESIRED_DISTANCE}\n")
        self.trace_file.flush()
        
    def update_modbus_values(self):
        """Write current state to OpenPLC"""
        try:
            # Write sensor values
            self.client.write_registers(
                self.REGISTERS["flow_sensor"],
                [int(self.flow_sensor)]
            )
            self.client.write_registers(
                self.REGISTERS["range_sensor"],
                [int(self.range_sensor * 100)]  # Scale for better precision
            )
            
        except Exception as e:
            print(f"Error writing to OpenPLC: {e}")
            
    def read_plc_outputs(self):
        """Read pump state from OpenPLC"""
        try:
            # Read pump state
            pump_result = self.client.read_coils(self.REGISTERS["pump"], 1)
            if not pump_result.isError():
                self.pump_state = pump_result.bits[0]
                
        except Exception as e:
            print(f"Error reading from OpenPLC: {e}")
            
    def simulate_physics(self, dt):
        """Simulate physical system behavior"""
        # Update flow sensor based on pump state
        self.flow_sensor = 100 if self.pump_state else 0
        
        # Update range sensor based on pump action
        if self.pump_state:
            # Decrease range sensor value (filling up)
            self.range_sensor = max(0, 
                self.range_sensor - self.FLOW_RATE * dt)
        else:
            # Optional: Add slight leakage
            self.range_sensor = min(self.TANK_CAPACITY,
                self.range_sensor + 0.1 * dt)
                
        # Safety check: Ensure range sensor stays within bounds
        self.range_sensor = max(0, min(self.range_sensor, self.TANK_CAPACITY))
        
    def run(self, duration=None):
        """Run the simulation"""
        start_time = time.time()
        dt = 0.1  # 100ms cycle time
        
        try:
            while True:
                cycle_start = time.time()
                
                # Read PLC outputs
                self.read_plc_outputs()
                
                # Simulate physical system
                self.simulate_physics(dt)
                
                # Update Modbus values
                self.update_modbus_values()
                
                # Write trace
                self.write_trace()
                
                # Print current state
                print(f"Range: {self.range_sensor:.2f}, Flow: {self.flow_sensor}, "
                      f"Pump: {self.pump_state}, Desired Distance: {self.DESIRED_DISTANCE}")
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                    
                # Wait for next cycle
                elapsed = time.time() - cycle_start
                if elapsed < dt:
                    time.sleep(dt - elapsed)
                    
        except KeyboardInterrupt:
            print("\nSimulation stopped by user")
        finally:
            self.trace_file.close()
            self.client.close()
            
if __name__ == "__main__":
    simulator = PLCSim()
    print("Starting simulation. Press Ctrl+C to stop.")
    simulator.run()