import pandas as pd
import numpy as np
from datetime import datetime
import os

def main():
    # File paths
    predictions_file = 'data/Default Predictions.xlsx'
    nodes_file = 'data/node.csv'
    
    # Verify files exist
    for file in [predictions_file, nodes_file]:
        if not os.path.exists(file):
            print(f"Error: File not found: {file}")
            return

    print("Reading input files...")
    
    # Read the files
    predictions_df = pd.read_excel(predictions_file)
    nodes_df = pd.read_csv(nodes_file,
                          na_values=['', ' '],
                          thousands=',',
                          low_memory=False)
    
    # Store original columns order
    original_columns = nodes_df.columns.tolist()
    prediction_columns = ['predicted_defaults', 'actual_defaults_marked', 'avg_drr', 'max_drr', 'prediction_time']
    
    print(f"\nData Overview:")
    print(f"Predictions file: {len(predictions_df)} records")
    print(f"Nodes file: {len(nodes_df)} records")
    
    # Check hub overlap
    pred_hubs = set(predictions_df['Hub'])
    node_hubs = set(nodes_df['hub'])
    common_hubs = pred_hubs.intersection(node_hubs)
    
    print(f"\nHub Analysis:")
    print(f"Hubs in predictions: {len(pred_hubs)}")
    print(f"Hubs in nodes: {len(node_hubs)}")
    print(f"Common hubs: {len(common_hubs)}")
    print("Common hub names:", sorted(common_hubs))
    
    # Analyze trip reference numbers
    pred_refs = set(predictions_df['trip_trip_ref_number'])
    node_refs = set(nodes_df['trip_trip_ref_number'])
    common_refs = pred_refs.intersection(node_refs)
    
    print(f"\nTrip Reference Number Analysis:")
    print(f"Reference numbers in predictions: {len(pred_refs)}")
    print(f"Reference numbers in nodes: {len(node_refs)}")
    print(f"Common reference numbers: {len(common_refs)}")
    if common_refs:
        print("Common reference numbers:", sorted(common_refs))
    
    # Process each Hub and trip_ref combination that has defaults
    results = []
    processed_trips = 0
    matched_trips = 0
    
    print("\nProcessing predictions...")

    # First, get all trips with defaults
    default_predictions = predictions_df[predictions_df['Defaults'] > 0].copy()
    print(f"Found {len(default_predictions)} trips with predicted defaults")
    
    for _, row in default_predictions.iterrows():
        hub = row['Hub']
        trip_ref = row['trip_trip_ref_number']
        num_defaults = int(row['Defaults'])
        
        # Get all nodes for this hub and trip reference
        trip_nodes = nodes_df[
            (nodes_df['hub'] == hub) & 
            (nodes_df['trip_trip_ref_number'] == trip_ref)
        ].copy()
        
        if len(trip_nodes) > 0:
            matched_trips += 1
            print(f"\nProcessing Hub: {hub}, Trip Ref: {trip_ref}")
            print(f"Found {len(trip_nodes)} nodes for this trip")
            
            # Get all sequence numbers and sort them
            sequences = sorted(trip_nodes['visit_sequence'].unique())
            print(f"All sequences: {sequences}")
            
            # If defaults are equal to or greater than number of stops, mark all stops
            if num_defaults >= len(sequences):
                print(f"Predicted defaults ({num_defaults}) equal to or exceed number of stops ({len(sequences)})")
                print(f"Marking all {len(sequences)} stops as at-risk")
                at_risk_sequences = sequences  # Mark all sequences
                actual_defaults_to_mark = len(sequences)
            else:
                # Get the last n sequences where n = number of defaults
                at_risk_sequences = sequences[-num_defaults:]
                actual_defaults_to_mark = num_defaults
            
            print(f"At risk sequences: {at_risk_sequences}")
            
            # Filter nodes to get only the at-risk ones
            at_risk_nodes = trip_nodes[
                trip_nodes['visit_sequence'].isin(at_risk_sequences)
            ].copy()
            
            print(f"Found {len(at_risk_nodes)} at-risk nodes with sequences: {sorted(at_risk_nodes['visit_sequence'].unique())}")
            
            # Add prediction info to these nodes
            at_risk_nodes = at_risk_nodes.assign(
                predicted_defaults=num_defaults,
                actual_defaults_marked=actual_defaults_to_mark,
                avg_drr=row['avg DRR'],
                max_drr=row['Max DRR'],
                prediction_time=row['Time']
            )
            
            results.append(at_risk_nodes)
            processed_trips += 1
        else:
            print(f"No matching nodes found for Hub: {hub}, Trip Ref: {trip_ref}")

    print(f"\nMatching Statistics:")
    print(f"Trips with defaults in predictions: {len(default_predictions)}")
    print(f"Trips matched with nodes: {matched_trips}")

    # Combine all results
    if results:
        print("\nGenerating final output...")
        final_df = pd.concat(results, ignore_index=True)
        
        # Ensure columns are in the right order (original + prediction columns)
        output_columns = original_columns + prediction_columns
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'data/at_risk_stops_{timestamp}.xlsx'
        
        # Save to Excel with original column order plus prediction columns
        final_df[output_columns].to_excel(output_file, index=False)
        print(f"\nAnalysis complete!")
        print(f"Found {len(final_df)} at-risk stops across {final_df['trip_trip_ref_number'].nunique()} trips")
        print(f"Output saved to: {output_file}")
        
        # Print detailed breakdown
        print("\nDetailed breakdown of at-risk stops per trip:")
        breakdown = final_df.groupby(['hub', 'trip_trip_ref_number']).agg({
            'visit_sequence': ['count', lambda x: sorted(x.unique())],
            'predicted_defaults': 'first',
            'actual_defaults_marked': 'first'
        }).round(2)
        breakdown.columns = ['Stops Found', 'Sequences', 'Defaults Predicted', 'Defaults Marked']
        print(breakdown.to_string())
        
        # Print sample row to verify format
        print("\nSample row format:")
        print("Original columns:", original_columns)
        print("Added prediction columns:", prediction_columns)
    else:
        print("\nNo at-risk stops found in the data.")
        print("This might be because:")
        print("1. No matching reference numbers between the files")
        print("2. No defaults predicted")
        print("3. Hub names don't match between files")

if __name__ == "__main__":
    main() 