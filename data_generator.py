import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import sys

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    sys.exit("FATAL: 'config.json' not found.")
except json.JSONDecodeError:
    sys.exit("FATAL: 'config.json' contains invalid JSON.")

num_shots = config['simulation']['num_shots']


# Generate mock data for metrics accounting for drift
pressure_bar = np.random.normal(
    config['targets']['pressure'], 
    config['variability']['pressure_std'], 
    num_shots
)
temp_celsius = np.random.normal(
    config['targets']['temperature'], 
    config['variability']['temp_std'], num_shots
)
extraction_sec = np.random.normal(
    config['targets']['extraction_time'], 
    config['variability']['extraction_std'], 
    num_shots
)

current_time = datetime.now()
times = []

min_gap = config['simulation']['time_gap_min']
max_gap = config['simulation']['time_gap_max']

# Shots pulled every 2-3 minutes
for i in range(num_shots):
    times.append(current_time)
    gap = np.random.randint(min_gap,max_gap)
    current_time = current_time + timedelta(minutes=gap)
    
def score_shot(row):
    # Target metrics
    target_p = config['targets']['pressure']
    target_e = config['targets']['extraction_time']
    target_temp = config['targets']['temperature']
    
    # Calculate penalties for distance from targets
    # Scaled by weight representing importance
    temp_penalty = abs(row['temp_celsius'] - target_temp) * config['scoring_weights']['temperature']
    p_penalty = abs(row['pressure_bar'] - target_p) * config['scoring_weights']['pressure']
    e_penalty = abs(row['extraction_sec'] - target_e) * config['scoring_weights']['extraction']
    
    score = 10.0 - (p_penalty + e_penalty + temp_penalty)
    return max(0, min(10, score))
    
df = pd.DataFrame({
    'timestamp': times,
    'machine_id': config['machine_info']['id'],
    'temp_celsius': temp_celsius,
    'pressure_bar': pressure_bar,
    'extraction_sec': extraction_sec
}) 

df['quality_score'] = df.apply(score_shot, axis=1)

output_file = config['machine_settings']['output_file']
df.to_csv(output_file, index=False)