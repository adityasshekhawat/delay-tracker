# Delivery Trip Default Risk Analyzer

## Overview
This tool helps identify which stops in delivery trips are at risk of defaulting. It combines delivery trip data with default predictions to highlight potentially problematic stops.

## Web Application
Access the tool online at: [Your Streamlit URL]

### Features
- Easy-to-use web interface
- Real-time data processing
- Interactive visualizations
- Excel export with predictions
- No installation required

### How to Use the Web App
1. Open the web app in your browser
2. Upload your `node.csv` file
3. Upload your `Default Predictions.xlsx` file
4. View the results and download the analysis

## Local Installation (For Developers)

### Requirements
- Python 3.7 or higher
- pip (Python package installer)

### Setup
1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd delay-tracker
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally
1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Open your browser to `http://localhost:8501`

## File Requirements

### node.csv
Must contain these columns:
- hub
- trip_trip_ref_number
- visit_sequence
(Plus any other columns you normally have)

### Default Predictions.xlsx
Must contain these columns:
- Hub
- trip_trip_ref_number
- Defaults
- avg DRR
- Max DRR
- Time

## Features
- Identifies at-risk stops based on prediction data
- Handles cases where predicted defaults exceed stop count
- Maintains all original data columns
- Adds prediction columns for analysis
- Provides visual breakdown of results
- Exports results in Excel format

## Support
For issues or questions, please contact [Your Contact Information] 