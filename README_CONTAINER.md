# Delay Tracker - Containerized Implementation

This version of the Delay Tracker has been adapted to work within a containerized platform that integrates multiple warehouse allocation tools.

## Overview

The Delay Tracker processes delivery trip data to identify stops at risk of defaulting. This containerized version provides a standardized interface while preserving the core functionality of the original application.

## Usage

### Input File Format

The input Excel file must contain two sheets:

1. **Nodes**: Delivery trip data with these required columns:
   - `hub`: The hub identifier
   - `trip_trip_ref_number`: Reference number for the trip
   - `trip_trip_id`: Unique identifier for the trip
   - `visit_sequence`: Order of stops within the trip
   - (Other columns will be preserved in the output)

2. **Predictions**: Default predictions with these required columns:
   - `Hub`: The hub identifier (must match values in Nodes sheet)
   - `trip_trip_ref_number`: Reference number for the trip
   - `trip_trip_id`: Unique identifier for the trip
   - `Defaults`: Number of predicted defaults
   - `avg DRR`: Average Delivery Rejection Rate
   - `Max DRR`: Maximum Delivery Rejection Rate
   - `Time`: Timestamp of the prediction

### Output File Format

The output Excel file will contain all original columns from the Nodes sheet plus these additional columns:
- `predicted_defaults`: Number of defaults predicted for the trip
- `actual_defaults_marked`: Number of stops marked as at-risk
- `avg_drr`: Average Delivery Rejection Rate
- `max_drr`: Maximum Delivery Rejection Rate
- `prediction_time`: Timestamp of the prediction

### Command Line Usage

```bash
python processor.py <input_file> <output_file>
```

Example:
```bash
python processor.py data/input.xlsx data/output.xlsx
```

### Programmatic Usage

```python
from processor import process_file

result = process_file("data/input.xlsx", "data/output.xlsx")
if result:
    print("Processing successful")
else:
    print("Processing failed")
```

## Dependencies

All required packages are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

## Error Handling

If an error occurs during processing, the application will:
1. Log the error message
2. Create an error report Excel file at the specified output path
3. Return `False` from the `process_file` function

## Business Logic

The processor identifies at-risk stops using this logic:
1. For each trip with predicted defaults, find all stops (nodes) matching the hub, trip reference number, and trip ID
2. Sort stops by visit sequence
3. Mark the last N stops as at-risk, where N = number of predicted defaults
4. If predicted defaults exceed the number of stops, mark all stops as at-risk

## Integration Notes

This version has been specifically designed to work within containerized platforms by:
- Providing a standardized interface with the `process_file` function
- Implementing proper logging
- Handling errors gracefully
- Supporting standalone execution for testing 