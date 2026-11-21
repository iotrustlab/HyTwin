import numpy as np
import rtamt


def format_trace_for_rtamt(trace_data):
    """Convert trace data into RTAMT format"""
    num_samples = len(trace_data['x2'])
    
    # Initialize lists for each variable
    x2_data = []
    P1_data = []
    V1_data = []
    
    # Extract time and values
    for i in range(num_samples):
        time = trace_data['x2'][i][0]
        x2_data.append(trace_data['x2'][i][1])
        P1_data.append(trace_data['P1'][i][1])
        V1_data.append(trace_data['V1'][i][1])
    
    # Create proper RTAMT format
    rtamt_data = {
        'time': [float(t) for t in trace_data['x2'][:][0]],
        'x2': x2_data,
        'P1': P1_data,
        'V1': V1_data
    }
    
    return rtamt_data


class WaterSystemAttacks:
    def __init__(self, H, HH, LL):
        self.H = H    # Control threshold
        self.HH = HH  # Safety upper limit
        self.LL = LL  # Safety lower limit
        
    def create_safety_spec(self):
        spec = rtamt.STLSpecification()
        
        spec.declare_var('x2', 'float')
        spec.declare_var('P1', 'float')
        spec.declare_var('V1', 'float')
        
        # Define safe behavior (to be negated)
        safe_behavior = f"""(
            (x2 <= {self.HH} and x2 >= {self.LL}) and
            ((x2 < {self.H}) implies (P1 >= 0.9 and V1 >= 0.9))
        )"""
        
        spec.spec = f"not(always[0,100]({safe_behavior}))"
        
        spec.parse()
        return spec
    

    def evaluate_attack(self, trace, HH=100, LL=0, penalty_factor=10):
        """
        Evaluate the attack based on:
        1. Duration of the attack
        2. Distance to safety bounds (last timestep only)
        
        Parameters:
            trace: Dictionary of time-series data (e.g., {'x2': [(time, value), ...]})
            HH: Safety upper limit
            LL: Safety lower limit
            penalty_factor: Extra penalty for x2 > HH
            
        Returns:
            Dictionary with duration score, safety violation score, and robustness.
        """
        num_samples = len(trace['x2'])
        attack_duration = 0
        last_attack_timestep = None

        # Track attack duration
        for t, x2_value in trace['x2']:
            if x2_value != 0:  # Assuming manipulation or non-zero value indicates an attack
                attack_duration += 1
                last_attack_timestep = x2_value

        # Distance to safety bounds (last timestep only)
        if last_attack_timestep is not None:
            if last_attack_timestep < HH:
                distance = HH - last_attack_timestep
            else:
                distance = (last_attack_timestep - HH) + penalty_factor
        else:
            distance = 0  # No attack occurred

        # Compute scores
        duration_score = attack_duration / num_samples
        safety_violation_score = distance / (HH - LL)

        robustness = -(duration_score * safety_violation_score)

        return {
            'duration_score': duration_score,
            'safety_violation_score': safety_violation_score,
            'robustness': robustness
        }


    


# Generate traces for each attack
def generate_actuator_compromise_trace(duration=100, threshold=10, compromised_duration=20):
    time = np.linspace(0, duration, 1000)
    traces = {}

    traces['actuator_compromise'] = {
        'x2': [(t, threshold if t < compromised_duration else threshold + 5.0) for t in time],  # Water level stays near H initially
        'P1': [(t, 1.0) for t in time],  # P1 remains on
        'V1': [(t, 1.0) for t in time],  # V1 remains open
    }

    return traces


def generate_valve_attack_trace(duration=100):
    time = np.linspace(0, duration, 1000)
    traces = {}

    traces['valve_attack'] = {
        'x2': [(t, 5.0) for t in time],  # x2 stays constant at 5.0
        'P1': [(t, 1.0) for t in time],  # P1 remains on
        'V1': [(t, 0.0) for t in time],  # V1 remains closed
    }

    return traces


def generate_sensor_attack_trace(duration=100):
    time = np.linspace(0, duration, 1000)
    traces = {}

    traces['sensor_attack'] = {
        'x2': [(t, max(5.0 + 0.1 * max(0, t - duration * 0.3), 5.0) - 0.1) for t in time],  # x2 is subtly reduced
        'P1': [(t, 1.0) for t in time],  # P1 remains on
        'V1': [(t, 0.0) for t in time],  # V1 remains closed
    }

    return traces


def main():
    system = WaterSystemAttacks(H=10, HH=100, LL=0)
    
    # Generate traces for each attack
    traces = {}
    traces.update(generate_actuator_compromise_trace())
    traces.update(generate_valve_attack_trace())
    traces.update(generate_sensor_attack_trace())

    # Evaluate each attack
    for attack_name, trace in traces.items():
        print(f"\nEvaluating attack: {attack_name}")
        
        # Evaluate robustness (duration and safety violation)
        metrics = system.evaluate_attack(trace)

        print(f"Duration Score: {metrics['duration_score']:.3f}")
        print(f"Safety Violation Score: {metrics['safety_violation_score']:.3f}")
        print(f"Robustness Score: {metrics['robustness']:.3f}")


if __name__ == "__main__":
    main()
