# Delivery Trip Default Risk Analyzer

## Overview
This tool helps identify which stops in delivery trips are at risk of defaulting. It combines delivery trip data with default predictions to highlight potentially problematic stops.

## Web Application
Access the tool online at: [Your Streamlit URL]

### Security Features
- Password-protected access
- Secure credential management
- File size limits (100MB for CSV, 50MB for Excel)
- Input validation and sanitization
- Session management
- Secure data handling

### Features
- Easy-to-use web interface
- Real-time data processing
- Interactive visualizations
- Excel export with predictions
- No installation required

### How to Use the Web App
1. Open the web app in your browser
2. Log in with your credentials
3. Upload your `node.csv` file
4. Upload your `Default Predictions.xlsx` file
5. View the results and download the analysis

## Deployment Instructions

### 1. Local Development
```bash
git clone https://github.com/adityasshekhawat/delay-tracker.git
cd delay-tracker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Security
1. Create `.streamlit/secrets.toml`:
```toml
[credentials]
username = "your_username"
password = "your_password"
```

2. For Streamlit Cloud:
   - Go to your app's dashboard
   - Navigate to Settings > Secrets
   - Add the same credentials as above

### 3. Run Locally
```bash
streamlit run app.py
```

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

## Security Considerations
- All data is processed in-memory
- No data is stored on the server
- Secure password comparison using hmac
- Input validation for all file uploads
- File size restrictions to prevent abuse
- Required column validation
- Error handling and sanitization

## Support
For issues or questions, please contact [Your Contact Information] 