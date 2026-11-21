import sys
import rtamt

# Monitor for STL traces
# Registers Description:
# Register 1: Range Sensor (represents water level)
# Register 2: Pump State
# Register 3: Red Doser State
# Register 4: Blue Doser State

desiredDistanceFill = 7.0  # Desired distance from the sensor when the tank is full (example value)

def monitor():
    # Read the traces
    with open('trace_output.txt', 'r') as file:
        traces = [list(map(float, line.strip().split(','))) for line in file]

    # Split the traces into timestamps and register values
    timestamps = [trace[0] for trace in traces]
    range_values = [[timestamps[i], traces[7]] for i in range(len(timestamps))]  # Range sensor (column 7)
    pump_values = [[timestamps[i], traces[4]] for i in range(len(timestamps))]   # Pump state (column 4)

    spec = rtamt.StlDenseTimeSpecification()
    spec.name = 'Initialization Phase Monitoring'
    spec.declare_var('range_sensor', 'float')
    spec.declare_var('pump_state', 'float')
    spec.set_var_io_type('range_sensor', 'input')
    spec.set_var_io_type('pump_state', 'output')

    # Spec #1: If the water level is below the desired level, the pump should be on
    spec.spec = f'always((range_sensor > {desiredDistanceFill}) implies (pump_state == 1))'

    try:
        spec.parse()
    except rtamt.RTAMTException as err:
        print('RTAMT Exception: {}'.format(err))
        sys.exit()

    # Evaluate the STL spec for the given traces
    rob = spec.evaluate(['range_sensor', range_values], ['pump_state', pump_values])

    print('Robustness: {}'.format(rob))

if __name__ == '__main__':
    monitor()
