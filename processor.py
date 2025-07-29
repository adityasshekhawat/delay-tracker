import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_file(input_file_path, output_file_path):
    """
    Process the input Excel file and write results to the output file.
    
    Args:
        input_file_path (str): Path to the input Excel file containing both the node data and default predictions
                              Expected to have two sheets:
                              - 'Nodes': Delivery trip data with columns hub, trip_trip_ref_number, trip_trip_id, visit_sequence, etc.
                              - 'Predictions': Default predictions with columns Hub, trip_trip_ref_number, trip_trip_id, Defaults, avg DRR, Max DRR, Time
        output_file_path (str): Path where the output Excel file will be saved
    
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        logger.info(f"Starting to process file: {input_file_path}")
        
        # 1. Read the input Excel file
        logger.info("Reading input file...")
        try:
            # Read from sheets in the same file
            nodes_df = pd.read_excel(input_file_path, sheet_name='Nodes', na_values=['', ' '], thousands=',')
            predictions_df = pd.read_excel(input_file_path, sheet_name='Predictions')
            logger.info(f"Successfully loaded data: {len(nodes_df)} nodes and {len(predictions_df)} predictions")
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise ValueError(f"Error reading Excel file: {str(e)}")
        
        # Validate required columns
        required_node_columns = ['hub', 'trip_trip_ref_number', 'trip_trip_id', 'visit_sequence']
        required_pred_columns = ['Hub', 'trip_trip_ref_number', 'trip_trip_id', 'Defaults', 'avg DRR', 'Max DRR', 'Time']
        
        missing_node_cols = [col for col in required_node_columns if col not in nodes_df.columns]
        missing_pred_cols = [col for col in required_pred_columns if col not in predictions_df.columns]
        
        if missing_node_cols:
            error_msg = f"Missing required columns in Nodes sheet: {', '.join(missing_node_cols)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if missing_pred_cols:
            error_msg = f"Missing required columns in Predictions sheet: {', '.join(missing_pred_cols)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 2. Process the data (using the core logic from app.py)
        logger.info("Processing data...")
        final_df, output_columns = process_data(nodes_df, predictions_df)
        
        if final_df is None or len(final_df) == 0:
            logger.warning("No at-risk stops found in the data")
            # Create an empty report with structure information
            empty_df = pd.DataFrame(columns=['hub', 'trip_trip_ref_number', 'trip_trip_id', 'visit_sequence', 
                                           'predicted_defaults', 'actual_defaults_marked', 'avg_drr', 'max_drr', 
                                           'prediction_time', 'process_status'])
            empty_df.loc[0] = ['', '', '', 0, 0, 0, 0, 0, datetime.now(), 'No at-risk stops found']
            empty_df.to_excel(output_file_path, index=False)
            logger.info(f"Empty result file created at: {output_file_path}")
            return True
        
        # 3. Write results to the output file
        logger.info(f"Writing {len(final_df)} at-risk stops to {output_file_path}")
        final_df.to_excel(output_file_path, index=False)
        logger.info(f"Processing complete. Results saved to: {output_file_path}")
        
        return True
    
    except Exception as e:
        # Log the error
        logger.error(f"Error processing file: {str(e)}")
        
        # Create an error report if processing fails
        error_df = pd.DataFrame({
            'error': [str(e)],
            'input_file': [input_file_path],
            'timestamp': [pd.Timestamp.now()]
        })
        
        error_df.to_excel(output_file_path, index=False)
        return False

def process_data(nodes_df, predictions_df):
    """Process the data and return the results DataFrame."""
    try:
        # Store original columns order
        original_columns = nodes_df.columns.tolist()
        prediction_columns = ['predicted_defaults', 'actual_defaults_marked', 'avg_drr', 'max_drr', 'prediction_time']
        
        # Process each Hub, trip_ref, and trip_trip_id combination that has defaults
        results = []
        
        # First, get all trips with defaults
        default_predictions = predictions_df[predictions_df['Defaults'] > 0].copy()
        logger.info(f"Found {len(default_predictions)} trips with predicted defaults")
        
        matched_trips = 0
        
        for _, row in default_predictions.iterrows():
            hub = row['Hub']
            trip_ref = row['trip_trip_ref_number']
            trip_trip_id = row['trip_trip_id']
            num_defaults = int(row['Defaults'])
            
            logger.info(f"Processing Hub: {hub}, Trip Ref: {trip_ref}, Trip ID: {trip_trip_id}")
            
            # Get all nodes for this hub, trip reference, and trip_trip_id
            trip_nodes = nodes_df[
                (nodes_df['hub'] == hub) & 
                (nodes_df['trip_trip_ref_number'] == trip_ref) &
                (nodes_df['trip_trip_id'] == trip_trip_id)
            ].copy()
            
            if len(trip_nodes) > 0:
                matched_trips += 1
                logger.info(f"Found {len(trip_nodes)} nodes for this trip")
                
                # Get all sequence numbers and sort them
                sequences = sorted(trip_nodes['visit_sequence'].unique())
                
                # If defaults are equal to or greater than number of stops, mark all stops
                if num_defaults >= len(sequences):
                    logger.info(f"Predicted defaults ({num_defaults}) equal to or exceed number of stops ({len(sequences)})")
                    at_risk_sequences = sequences  # Mark all sequences
                    actual_defaults_to_mark = len(sequences)
                else:
                    # Get the last n sequences where n = number of defaults
                    at_risk_sequences = sequences[-num_defaults:]
                    actual_defaults_to_mark = num_defaults
                
                logger.info(f"At risk sequences: {at_risk_sequences}")
                
                # Filter nodes to get only the at-risk ones
                at_risk_nodes = trip_nodes[
                    trip_nodes['visit_sequence'].isin(at_risk_sequences)
                ].copy()
                
                logger.info(f"Found {len(at_risk_nodes)} at-risk nodes")
                
                # Add prediction info to these nodes
                at_risk_nodes = at_risk_nodes.assign(
                    predicted_defaults=num_defaults,
                    actual_defaults_marked=actual_defaults_to_mark,
                    avg_drr=row['avg DRR'],
                    max_drr=row['Max DRR'],
                    prediction_time=row['Time']
                )
                
                results.append(at_risk_nodes)
            else:
                logger.warning(f"No matching nodes found for Hub: {hub}, Trip Ref: {trip_ref}, Trip ID: {trip_trip_id}")

        logger.info(f"Matched {matched_trips} trips out of {len(default_predictions)} trips with defaults")
        
        if results:
            final_df = pd.concat(results, ignore_index=True)
            return final_df, original_columns + prediction_columns
        else:
            logger.warning("No at-risk stops could be identified")
            return None, None
            
    except Exception as e:
        logger.error(f"Error in data processing: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python processor.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
        
    result = process_file(input_file, output_file)
    sys.exit(0 if result else 1) 