import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sample_input(output_file="data/sample_input.xlsx"):
    """Generate a sample input file for testing the delay tracker."""
    print("Generating sample input file...")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Generate nodes data
    hubs = ['HUB001', 'HUB002', 'HUB003']
    trip_refs = [f'TR{i:03d}' for i in range(1, 11)]
    trip_ids = [f'TID{i:04d}' for i in range(1, 21)]
    
    # Create node data with multiple stops per trip
    nodes_data = []
    for hub in hubs:
        for trip_ref in trip_refs[:5]:  # Each hub has 5 trip refs
            for trip_id in trip_ids[:2]:  # Each trip ref has 2 trip ids
                num_stops = np.random.randint(5, 15)  # Random number of stops between 5 and 15
                for seq in range(1, num_stops + 1):
                    nodes_data.append({
                        'hub': hub,
                        'trip_trip_ref_number': trip_ref,
                        'trip_trip_id': trip_id,
                        'visit_sequence': seq,
                        'customer_name': f'Customer_{np.random.randint(1, 100)}',
                        'order_id': f'ORD{np.random.randint(10000, 99999)}',
                        'delivery_date': (datetime.now() + timedelta(days=np.random.randint(1, 10))).strftime('%Y-%m-%d'),
                        'slots_start_time': (datetime.now() + timedelta(hours=np.random.randint(1, 24))).strftime('%H:%M:%S'),
                        'slots_end_time': (datetime.now() + timedelta(hours=np.random.randint(1, 24))).strftime('%H:%M:%S'),
                    })
    
    nodes_df = pd.DataFrame(nodes_data)
    
    # Generate predictions data
    predictions_data = []
    for hub in hubs:
        for trip_ref in trip_refs[:5]:  # Each hub has 5 trip refs
            for trip_id in trip_ids[:2]:  # Each trip ref has 2 trip ids
                # Only include some trips in predictions (80% chance)
                if np.random.random() < 0.8:
                    # Get count of nodes for this trip
                    node_count = len(nodes_df[(nodes_df['hub'] == hub) & 
                                              (nodes_df['trip_trip_ref_number'] == trip_ref) & 
                                              (nodes_df['trip_trip_id'] == trip_id)])
                    
                    # Create prediction with defaults (30% chance of having defaults)
                    if np.random.random() < 0.3 and node_count > 0:
                        defaults = np.random.randint(1, max(2, node_count))
                    else:
                        defaults = 0
                        
                    predictions_data.append({
                        'Hub': hub,
                        'trip_trip_ref_number': trip_ref,
                        'trip_trip_id': trip_id,
                        'Defaults': defaults,
                        'avg DRR': np.random.uniform(0.01, 0.2),
                        'Max DRR': np.random.uniform(0.05, 0.4),
                        'Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
    
    predictions_df = pd.DataFrame(predictions_data)
    
    # Save to Excel with two sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        nodes_df.to_excel(writer, sheet_name='Nodes', index=False)
        predictions_df.to_excel(writer, sheet_name='Predictions', index=False)
    
    print(f"Sample input file generated at: {output_file}")
    print(f"Generated {len(nodes_df)} node records across {nodes_df['trip_trip_id'].nunique()} unique trips")
    print(f"Generated {len(predictions_df)} prediction records with {len(predictions_df[predictions_df['Defaults'] > 0])} having defaults")

if __name__ == "__main__":
    generate_sample_input()
    print("Done!") 