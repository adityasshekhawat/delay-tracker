import pandas as pd
import os
import logging
from datetime import datetime
import sys
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import your existing delay tracker logic here
# Adjust the path to point to your actual delay-tracker directory
sys.path.append('/Users/jumbotail/Desktop/delay-tracker')

try:
    # Try importing directly if the module is in the Python path
    from processor import process_data
    logger.info("Successfully imported delay-tracker modules")
except ImportError as e:
    logger.warning(f"Could not import delay-tracker modules directly: {str(e)}")
    logger.warning("Using dummy implementation.")
    # Fallback to dummy implementation if imports fail

# Real implementation using actual delay tracker logic
def delay_tracker_function(df):
    """Process the delay tracking using the actual processor"""
    try:
        # Process the dataframe using the core delay tracker logic
        # Since process_data expects nodes_df and predictions_df, we need to split our input
        # Our function expects DataFrames directly, not file paths
        
        # Check if this is a combined DataFrame that needs to be split
        if 'Nodes' in df and 'Predictions' in df:
            nodes_df = df['Nodes']
            predictions_df = df['Predictions']
        else:
            # Assume it's already a single DataFrame with the right structure
            # We'll create a temporary file to use with process_file
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_input:
                temp_input_path = temp_input.name
            
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            # Write the DataFrame to the temporary file with two sheets
            with pd.ExcelWriter(temp_input_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Nodes', index=False)
                df.to_excel(writer, sheet_name='Predictions', index=False)
            
            # Process using the file-based interface
            from processor import process_file
            success = process_file(temp_input_path, temp_output_path)
            
            if success:
                # Read the output
                result_df = pd.read_excel(temp_output_path)
                
                # Clean up temporary files
                os.unlink(temp_input_path)
                os.unlink(temp_output_path)
                
                return result_df
            else:
                raise Exception("Processor failed to process the data")
        
        # If we get here, we're using the DataFrame-based interface
        result_df, _ = process_data(nodes_df, predictions_df)
        
        return result_df
    except Exception as e:
        logger.error(f"Error in delay_tracker_function: {str(e)}")
        # Return original dataframe with error note
        error_df = df.copy()
        error_df['error'] = str(e)
        error_df['processed'] = False
        return error_df

# Example dummy implementation (fallback if imports fail)
def dummy_delay_tracker_function(df):
    """Example function - used as fallback if actual imports fail"""
    required_cols = ['allocation_id', 'planned_date', 'status']
    if all(col in df.columns for col in required_cols):
        # Convert planned_date to datetime
        df['planned_date'] = pd.to_datetime(df['planned_date'])
        
        # Calculate days from planned date
        today = pd.Timestamp.now().normalize()
        df['days_from_planned'] = (today - df['planned_date']).dt.days
        
        # Identify delayed allocations
        df['is_delayed'] = (df['days_from_planned'] > 0) & (df['status'] != 'completed')
        
        # Add delay metrics
        df['delay_status'] = df.apply(
            lambda row: 'delayed' if row['is_delayed'] else row['status'], axis=1
        )
        
        # Add processing metadata
        df['tracked_date'] = datetime.now()
    else:
        df['processing_note'] = "Could not process delay tracking: missing required columns"
    
    return df

def process_file(input_file_path, output_file_path):
    """
    Process the input Excel file for tracking allocation delays.
    
    Args:
        input_file_path (str): Path to the input Excel file
        output_file_path (str): Path where the output Excel file will be saved
    
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        logger.info(f"Processing file {input_file_path} with Delay Tracker tool")
        
        # Read the input Excel file
        df = pd.read_excel(input_file_path)
        
        # Log the data shape
        logger.info(f"Input data shape: {df.shape}")
        
        # Validate required columns
        required_columns = ['allocation_id', 'planned_date', 'product_id', 'location', 'quantity', 'status']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' is missing from input file")
        
        # Validate status values
        valid_statuses = ['scheduled', 'in_progress', 'completed', 'delayed']
        invalid_statuses = df[~df['status'].isin(valid_statuses)]['status'].unique()
        if len(invalid_statuses) > 0:
            raise ValueError(f"Invalid status values found: {invalid_statuses}. Valid values are: {valid_statuses}")
        
        # Execute your existing delay tracker logic here
        try:
            # Try to use the real implementation
            result_df = delay_tracker_function(df)
            logger.info("Used actual delay tracker logic for processing")
        except (NameError, ImportError) as e:
            # Fall back to dummy implementation if actual logic fails to import
            logger.warning(f"Could not use actual delay tracker logic: {str(e)}")
            logger.warning("Falling back to dummy implementation")
            result_df = dummy_delay_tracker_function(df)
        
        # Save the result to the output path
        result_df.to_excel(output_file_path, index=False)
        
        logger.info(f"Successfully processed file. Output saved to {output_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        
        # Create an error report if the processing fails
        error_df = pd.DataFrame({
            'error': [str(e)],
            'input_file': [input_file_path],
            'timestamp': [datetime.now()]
        })
        
        error_df.to_excel(output_file_path, index=False)
        return False

if __name__ == "__main__":
    # This allows for standalone testing
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python standardized_wrapper.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
        
    result = process_file(input_file, output_file)
    sys.exit(0 if result else 1) 