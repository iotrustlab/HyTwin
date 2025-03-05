
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class SWaTMonitor:
    def __init__(self, error_margin: float = 5.0):
        self.error_margin = error_margin
        
        # Define tank physical limits from SWaT paper
        self.TANK_LIMITS = {
            'LIT101': {'min': 250, 'max': 1100},
            'LIT301': {'min': 250, 'max': 1100},
            'LIT401': {'min': 250, 'max': 1000}
        }
        
        # Define actuator-sensor relationships based on SWaT architecture
        self.FLOW_DEPENDENCIES = {
            'FIT101': ['MV101', 'P101', 'P102'],
            'FIT201': ['P201', 'P202', 'P203', 'P204', 'P205', 'P206'],
            'FIT301': ['P301', 'P302', 'MV301', 'MV302', 'MV303', 'MV304'],
            'FIT401': ['P401', 'P402']
        }

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load and preprocess the SWaT dataset."""
        # Read excel file, skipping the first row which contains process stage info
        df = pd.read_excel(file_path, header=1)
        
        # Clean column names - remove leading/trailing spaces
        df.columns = df.columns.str.strip()
        
        # Convert timestamp string to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'].str.strip())
        
        return df

    def calculate_expected_flow(self, current_flow: float, row: pd.Series, 
                              flow_sensor: str) -> float:
        """Calculate expected flow based on actuator states."""
        expected_flow = current_flow
        for actuator in self.FLOW_DEPENDENCIES[flow_sensor]:
            expected_flow *= float(row[actuator])
        return expected_flow

    def estimate_tank_level(self, prev_level: float, inflow: float, outflow: float, 
                          time_delta: float) -> float:
        """Estimate tank level based on SCADMAN's physical model."""
        return prev_level + (inflow - outflow) * time_delta

    def check_flow_consistency(self, row: pd.Series) -> List[str]:
        """Check if flow measurements are consistent with actuator states."""
        anomalies = []
        
        for flow_sensor in self.FLOW_DEPENDENCIES.keys():
            if flow_sensor in row.index:
                expected_flow = self.calculate_expected_flow(
                    float(row[flow_sensor]), row, flow_sensor
                )
                
                if expected_flow == 0 and float(row[flow_sensor]) > self.error_margin:
                    anomalies.append(
                        f"Flow anomaly in {flow_sensor} at {row['Timestamp']}: "
                        f"Flow detected when actuators indicate no flow"
                    )
                elif expected_flow > 0 and float(row[flow_sensor]) == 0:
                    anomalies.append(
                        f"Flow anomaly in {flow_sensor} at {row['Timestamp']}: "
                        f"No flow detected when actuators indicate flow"
                    )
        
        return anomalies

    def check_tank_levels(self, current_row: pd.Series, prev_row: pd.Series) -> List[str]:
        """Check if tank level changes are consistent with flows."""
        anomalies = []
        time_delta = (current_row['Timestamp'] - prev_row['Timestamp']).total_seconds()
        
        # Check LIT101 (Raw water tank)
        expected_lit101 = self.estimate_tank_level(
            float(prev_row['LIT101']),
            float(current_row['FIT101']) if float(current_row['MV101']) == 1 else 0,
            float(current_row['FIT201']) if float(current_row['P101']) == 1 or float(current_row['P102']) == 1 else 0,
            time_delta
        )
        
        if abs(float(current_row['LIT101']) - expected_lit101) > self.error_margin:
            anomalies.append(
                f"Tank level anomaly in LIT101 at {current_row['Timestamp']}: "
                f"Expected {expected_lit101:.2f}, Got {float(current_row['LIT101']):.2f}"
            )
        
        return anomalies

    def check_control_logic(self, row: pd.Series) -> List[str]:
        """Check if control logic constraints are satisfied."""
        anomalies = []
        
        # Check tank levels against limits
        for tank, limits in self.TANK_LIMITS.items():
            current_level = float(row[tank])
            if current_level < limits['min']:
                anomalies.append(
                    f"Tank {tank} below minimum level at {row['Timestamp']}: {current_level:.2f}"
                )
            elif current_level > limits['max']:
                anomalies.append(
                    f"Tank {tank} above maximum level at {row['Timestamp']}: {current_level:.2f}"
                )
        
        # Check pump logic
        if float(row['P101']) == 1 and float(row['P102']) == 1:
            anomalies.append(f"Invalid pump state at {row['Timestamp']}: P101 and P102 on simultaneously")
        
        if float(row['P301']) == 1 and float(row['P302']) == 1:
            anomalies.append(f"Invalid pump state at {row['Timestamp']}: P301 and P302 on simultaneously")
        
        return anomalies

    def analyze_data(self, df: pd.DataFrame) -> List[Dict]:
        """Analyze the dataset for anomalies using SCADMAN approach."""
        all_anomalies = []
        
        # Initialize with first row
        prev_row = df.iloc[0]
        
        # Process each row
        for idx in range(1, len(df)):
            current_row = df.iloc[idx]
            
            # Check all three aspects as per SCADMAN
            flow_anomalies = self.check_flow_consistency(current_row)
            tank_anomalies = self.check_tank_levels(current_row, prev_row)
            logic_anomalies = self.check_control_logic(current_row)
            
            # Combine any detected anomalies
            if flow_anomalies or tank_anomalies or logic_anomalies:
                all_anomalies.append({
                    'timestamp': current_row['Timestamp'],
                    'flow_anomalies': flow_anomalies,
                    'tank_anomalies': tank_anomalies,
                    'logic_anomalies': logic_anomalies
                })
            
            prev_row = current_row
        
        return all_anomalies

def main():
    # Initialize monitor
    monitor = SWaTMonitor(error_margin=5.0)
    
    print("Loading data...")
    # Load data
    df = monitor.load_data('/home/jp/Desktop/Swat Datasets/D1/SWaT_Dataset_Normal_v1.xlsx')
    print(f"Loaded {len(df)} rows of data")
    
    print("\nAnalyzing data...")
    # Analyze for anomalies
    anomalies = monitor.analyze_data(df)
    
    # Print results
    print(f"\nAnalysis complete. Found {len(anomalies)} anomalies.")
    for anomaly in anomalies:
        print(f"\nTimestamp: {anomaly['timestamp']}")
        
        if anomaly['flow_anomalies']:
            print("Flow anomalies:")
            for fa in anomaly['flow_anomalies']:
                print(f"  - {fa}")
        
        if anomaly['tank_anomalies']:
            print("Tank anomalies:")
            for ta in anomaly['tank_anomalies']:
                print(f"  - {ta}")
        
        if anomaly['logic_anomalies']:
            print("Logic anomalies:")
            for la in anomaly['logic_anomalies']:
                print(f"  - {la}")

if __name__ == "__main__":
    main()
