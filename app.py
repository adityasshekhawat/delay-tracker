import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import os
import hmac
import hashlib

# Set page config
st.set_page_config(
    page_title="Delivery Trip Default Risk Analyzer",
    page_icon="🚚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    .css-1d391kg {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["username"], st.secrets.credentials.username) and \
           hmac.compare_digest(st.session_state["password"], st.secrets.credentials.password):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
            del st.session_state["username"]  # Don't store the username.
        else:
            st.session_state["password_correct"] = False

    # First run or already authenticated
    if "password_correct" not in st.session_state:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    
    # Password incorrect
    elif not st.session_state["password_correct"]:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        st.error("😕 User not known or password incorrect")
        return False
    
    # Password correct
    else:
        return True

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
        
        for _, row in default_predictions.iterrows():
            hub = row['Hub']
            trip_ref = row['trip_trip_ref_number']
            trip_trip_id = row['trip_trip_id']
            num_defaults = int(row['Defaults'])
            
            # Get all nodes for this hub, trip reference, and trip_trip_id
            trip_nodes = nodes_df[
                (nodes_df['hub'] == hub) & 
                (nodes_df['trip_trip_ref_number'] == trip_ref) &
                (nodes_df['trip_trip_id'] == trip_trip_id)
            ].copy()
            
            if len(trip_nodes) > 0:
                # Get all sequence numbers and sort them
                sequences = sorted(trip_nodes['visit_sequence'].unique())
                
                # If defaults are equal to or greater than number of stops, mark all stops
                if num_defaults >= len(sequences):
                    at_risk_sequences = sequences
                    actual_defaults_to_mark = len(sequences)
                else:
                    # Get the last n sequences where n = number of defaults
                    at_risk_sequences = sequences[-num_defaults:]
                    actual_defaults_to_mark = num_defaults
                
                # Filter nodes to get only the at-risk ones
                at_risk_nodes = trip_nodes[
                    trip_nodes['visit_sequence'].isin(at_risk_sequences)
                ].copy()
                
                # Add prediction info to these nodes
                at_risk_nodes = at_risk_nodes.assign(
                    predicted_defaults=num_defaults,
                    actual_defaults_marked=actual_defaults_to_mark,
                    avg_drr=row['avg DRR'],
                    max_drr=row['Max DRR'],
                    prediction_time=row['Time']
                )
                
                results.append(at_risk_nodes)
        
        if results:
            final_df = pd.concat(results, ignore_index=True)
            return final_df, original_columns + prediction_columns
        else:
            return None, None
            
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None, None

def main():
    if not check_password():
        st.stop()  # Do not continue if check_password is not True.
    
    # Add logout button
    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.experimental_rerun()
    
    st.title("🚚 Delivery Trip Default Risk Analyzer")
    
    # Add session info
    st.sidebar.markdown("### Session Info")
    st.sidebar.info(f"Last activity: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("""
    This tool helps identify which stops in delivery trips are at risk of defaulting.
    Upload your delivery trip data and default predictions to get started.
    """)
    
    # File upload section with additional security checks
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Upload Delivery Trip Data")
        nodes_file = st.file_uploader("Upload node.csv", type=['csv'])
        if nodes_file:
            if nodes_file.size > 100 * 1024 * 1024:  # 100MB limit
                st.error("File size too large. Please upload a file smaller than 100MB.")
                st.stop()
        
    with col2:
        st.subheader("2. Upload Predictions")
        predictions_file = st.file_uploader("Upload Default Predictions.xlsx", type=['xlsx'])
        if predictions_file:
            if predictions_file.size > 50 * 1024 * 1024:  # 50MB limit
                st.error("File size too large. Please upload a file smaller than 50MB.")
                st.stop()
    
    if nodes_file and predictions_file:
        try:
            # Read the files with additional error handling
            try:
                nodes_df = pd.read_csv(nodes_file, na_values=['', ' '], thousands=',')
            except Exception as e:
                st.error(f"Error reading node.csv: {str(e)}")
                st.stop()
                
            try:
                predictions_df = pd.read_excel(predictions_file)
            except Exception as e:
                st.error(f"Error reading predictions file: {str(e)}")
                st.stop()
            
            # Validate required columns
            required_node_columns = ['hub', 'trip_trip_ref_number', 'trip_trip_id', 'visit_sequence']
            required_pred_columns = ['Hub', 'trip_trip_ref_number', 'trip_trip_id', 'Defaults', 'avg DRR', 'Max DRR', 'Time']
            
            missing_node_cols = [col for col in required_node_columns if col not in nodes_df.columns]
            missing_pred_cols = [col for col in required_pred_columns if col not in predictions_df.columns]
            
            if missing_node_cols:
                st.error(f"Missing required columns in node.csv: {', '.join(missing_node_cols)}")
                st.stop()
            
            if missing_pred_cols:
                st.error(f"Missing required columns in predictions file: {', '.join(missing_pred_cols)}")
                st.stop()
            
            # Display data overview
            st.subheader("Data Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Delivery Trips", len(nodes_df['trip_trip_ref_number'].unique()))
            with col2:
                st.metric("Unique Trip IDs", len(nodes_df['trip_trip_id'].unique()))
            with col3:
                st.metric("Total Stops", len(nodes_df))
            with col4:
                st.metric("Predicted Defaults", len(predictions_df[predictions_df['Defaults'] > 0]))
            
            # Process the data
            final_df, output_columns = process_data(nodes_df, predictions_df)
            
            if final_df is not None:
                st.success(f"Successfully identified {len(final_df)} at-risk stops across {final_df['trip_trip_ref_number'].nunique()} trips")
                
                # Create breakdown with trip_trip_id
                breakdown = final_df.groupby(['hub', 'trip_trip_ref_number', 'trip_trip_id']).agg({
                    'visit_sequence': ['count', lambda x: sorted(x.unique())],
                    'predicted_defaults': 'first',
                    'actual_defaults_marked': 'first'
                }).round(2)
                breakdown.columns = ['Stops Found', 'Sequences', 'Defaults Predicted', 'Defaults Marked']
                
                # Display results
                st.subheader("Results Breakdown")
                st.dataframe(breakdown)
                
                # Visualization
                st.subheader("Visualization")
                fig = px.bar(
                    breakdown.reset_index(), 
                    x='trip_trip_ref_number',
                    y=['Stops Found', 'Defaults Predicted'],
                    color='trip_trip_id',
                    title='At-Risk Stops vs Predicted Defaults by Trip',
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Download button
                st.subheader("Download Results")
                
                # Convert to Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    final_df[output_columns].to_excel(writer, index=False)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                st.download_button(
                    label="📥 Download Results as Excel",
                    data=output.getvalue(),
                    file_name=f'at_risk_stops_{timestamp}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                st.warning("No at-risk stops found in the data. This might be because:\n\n" +
                          "1. No matching reference numbers between the files\n" +
                          "2. No defaults predicted\n" +
                          "3. Hub names don't match between files\n" +
                          "4. Trip IDs don't match between files")
                
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            st.info("Please make sure your files have the required columns and format.")

if __name__ == "__main__":
    main() 