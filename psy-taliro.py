from staliro import staliro
from staliro.specifications import RTAMTSpecification
import numpy as np

class WaterSystemSpec:
    def __init__(self, HH, LL, H, L):
        self.HH = HH
        self.LL = LL
        self.H = H
        self.L = L
        
    def create_system_spec(self, duration):
        """
        Create integrated STL specification that captures:
        1. Control Logic: Relationship between x2, P1, and V1
        2. Physical Constraints: Flow dependencies
        3. Safety Properties: Level bounds
        """
        spec = RTAMTSpecification()
        
        # Declare all variables
        spec.declare_var('x1', 'float')  # Raw water tank level
        spec.declare_var('x2', 'float')  # Dosing tank level
        spec.declare_var('P1', 'float')  # Pump state (0 or 1)
        spec.declare_var('V1', 'float')  # Valve state (0 or 1)
        spec.declare_var('flow', 'float')  # Water flow between tanks
        
        # Build the complete specification
        
        # 1. Control Logic Property
        # When x2 < H, both P1 and V1 should be 1
        control_logic = f"""
        always[0,{duration}] (
            (x2 < {self.H} implies (P1 = 1 and V1 = 1)) and
            (x2 >= {self.H} implies (P1 = 0 or V1 = 0))
        )"""
        
        # 2. Physical Consistency Properties
        # Flow exists only when both P1 and V1 are on
        # x1 decreases and x2 increases with flow
        physical_consistency = f"""
        always[0,{duration}] (
            ((P1 = 1 and V1 = 1) implies flow > 0) and
            (flow > 0 implies (
                eventually[0,1](x1 < prev(x1)) and 
                eventually[0,1](x2 > prev(x2))
            )) and
            ((P1 = 0 or V1 = 0) implies flow = 0)
        )"""
        
        # 3. Safety Properties
        safety_bounds = f"""
        always[0,{duration}] (
            x1 > {self.LL} and x1 < {self.HH} and
            x2 > {self.LL} and x2 < {self.HH}
        )"""
        
        # 4. Pipe Safety Property
        # Pipe burst condition: P1 on but V1 closed
        pipe_safety = f"""
        always[0,{duration}] (
            not(P1 = 1 and V1 = 0)
        )"""
        
        # Combine all properties
        spec.spec = f"""
        {control_logic} and
        {physical_consistency} and
        {safety_bounds} and
        {pipe_safety}
        """
        
        return spec
    
    def check_attack_violation(self, time_series):
        """
        Evaluate system trace against specification.
        Returns robustness and identifies which properties were violated.
        """
        spec = self.create_system_spec(duration=len(time_series))
        robustness = spec.evaluate(time_series)
        
        violations = {
            'control_logic': False,
            'physical_consistency': False,
            'safety_bounds': False,
            'pipe_safety': False
        }
        
        # Example time series point
        t = time_series[0]
        
        # Check control logic violation
        if t['x2'] < self.H and (t['P1'] == 0 or t['V1'] == 0):
            violations['control_logic'] = True
            
        # Check physical consistency
        if t['P1'] == 1 and t['V1'] == 1 and t['flow'] <= 0:
            violations['physical_consistency'] = True
            
        # Check safety bounds
        if (t['x1'] <= self.LL or t['x1'] >= self.HH or 
            t['x2'] <= self.LL or t['x2'] >= self.HH):
            violations['safety_bounds'] = True
            
        # Check pipe safety
        if t['P1'] == 1 and t['V1'] == 0:
            violations['pipe_safety'] = True
            
        return robustness, violations

def main():
    # Initialize system specification
    system = WaterSystemSpec(
        HH=100,  # High-High limit
        LL=10,   # Low-Low limit
        H=90,    # High control limit
        L=20     # Low control limit
    )
    
    # Example attack scenario: Manipulate x2 sensor and V1 actuator
    time = np.linspace(0, 100, 1000)
    attack_trace = []
    
    for t in time:
        if t < 50:  # Normal operation
            state = {
                'time': t,
                'x1': 50,
                'x2': 40,
                'P1': 1,
                'V1': 1,
                'flow': 10
            }
        else:  # Attack phase
            # False x2 reading triggers control response
            # But V1 is forced closed while P1 runs
            state = {
                'time': t,
                'x1': 45,
                'x2': 95,  # False high reading
                'P1': 1,   # Pump keeps running
                'V1': 0,   # Valve forced closed
                'flow': 0  # No flow due to closed valve
            }
        attack_trace.append(state)
    
    # Evaluate attack
    robustness, violations = system.check_attack_violation(attack_trace)
    
    print("Attack Analysis Results:")
    print(f"Overall Robustness: {robustness}")
    print("\nViolated Properties:")
    for prop, violated in violations.items():
        if violated:
            print(f"- {prop}")

if __name__ == "__main__":
    main()