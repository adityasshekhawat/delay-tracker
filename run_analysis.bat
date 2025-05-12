@echo off
echo ===================================
echo Delivery Trip Default Risk Analyzer
echo ===================================
echo.

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed on this system.
    echo Please install Python 3.7 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check if data folder exists
if not exist "data" (
    echo Creating data folder...
    mkdir data
    echo Please copy your node.csv and "Default Predictions.xlsx" files into the data folder.
    echo.
    pause
    exit /b 1
)

:: Check if required files exist
if not exist "data\node.csv" (
    echo ERROR: node.csv not found in the data folder!
    echo Please copy your node.csv file into the data folder.
    echo.
    pause
    exit /b 1
)

if not exist "data\Default Predictions.xlsx" (
    echo ERROR: "Default Predictions.xlsx" not found in the data folder!
    echo Please copy your Default Predictions.xlsx file into the data folder.
    echo.
    pause
    exit /b 1
)

:: Install required packages if not already installed
echo Checking and installing required packages...
pip install -r requirements.txt
echo.

:: Run the analysis
echo Running the analysis...
python process_defaults.py
echo.

echo Analysis complete! Check the data folder for your results.
echo The output file will be named like "at_risk_stops_[timestamp].xlsx"
echo.
pause 