import streamlit as st
import requests
import pandas as pd
from typing import List, Dict
import hashlib
from datetime import datetime, timedelta
from  src.helpers.config import API_SECRET_KEY

# Constants
API_BASE_URL = "http://localhost:8000"  # Update this with your FastAPI server URL

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

def get_headers():
    """Get headers with current API key"""
    return {
        "X-API-Key": st.session_state.api_key,
        "Content-Type": "application/json"
    }

def check_api_status() -> Dict:
    """Check if the API is running and get its status"""
    try:
        response = requests.get(f"{API_BASE_URL}/status", headers=get_headers())
        return response.json()
    except requests.exceptions.RequestException:
        return {"status": "API server is not running"}

def train_model(texts: List[str], labels: List[str]) -> Dict:
    """Train the model with provided texts and labels"""
    payload = {
        "texts": texts,
        "labels": labels
    }
    response = requests.post(f"{API_BASE_URL}/train", headers=get_headers(), json=payload)
    return response.json()

def predict_text(text: str) -> Dict:
    """Get prediction for a single text"""
    payload = {"text": text}
    response = requests.post(f"{API_BASE_URL}/predict", headers=get_headers(), json=payload)
    return response.json()

def predict_batch(texts: List[str]) -> Dict:
    """Get predictions for multiple texts"""
    payload = {"texts": texts}
    response = requests.post(f"{API_BASE_URL}/predict-batch", headers=get_headers(), json=payload)
    return response.json()

def verify_password(password: str) -> bool:
    """Verify password against API_SECRET_KEY"""
    return password == API_SECRET_KEY

def logout():
    """Clear session state and log out user"""
    st.session_state.logged_in = False
    st.session_state.api_key = None

# Login UI
if not st.session_state.logged_in:
    st.title("Login")
    
    with st.form("login_form"):
        password = st.text_input("API Secret Key", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if verify_password(password):
                st.session_state.logged_in = True
                st.session_state.api_key = password  # Use the API secret key as the API key
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid API Secret Key")

else:
    # Main App UI
    st.title("NLP Training and Prediction Dashboard")
    
    # Logout button in sidebar
    with st.sidebar:
        if st.button("Logout"):
            logout()
            st.experimental_rerun()
        
        st.header("API Status")
        status = check_api_status()
        st.json(status)

    st.markdown("---")

    # Main app tabs
    tab1, tab2, tab3 = st.tabs(["Training", "Single Prediction", "Batch Prediction"])

    # Training Tab
    with tab1:
        st.header("Train Model")
        
        uploaded_file = st.file_uploader("Upload CSV file with 'text' and 'label' columns", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            if 'text' in df.columns and 'label' in df.columns:
                st.dataframe(df.head())
                
                if st.button("Train Model"):
                    with st.spinner("Training model..."):
                        try:
                            result = train_model(df['text'].tolist(), df['label'].tolist())
                            st.success("Training completed!")
                            st.json(result)
                        except Exception as e:
                            st.error(f"Error during training: {str(e)}")
            else:
                st.error("CSV file must contain 'text' and 'label' columns")

    # Single Prediction Tab
    with tab2:
        st.header("Single Text Prediction")
        
        input_text = st.text_area("Enter text for prediction")
        if st.button("Predict"):
            if input_text:
                with st.spinner("Getting prediction..."):
                    try:
                        result = predict_text(input_text)
                        st.json(result)
                    except Exception as e:
                        st.error(f"Error during prediction: {str(e)}")
            else:
                st.warning("Please enter some text for prediction")

    # Batch Prediction Tab
    with tab3:
        st.header("Batch Prediction")
        
        uploaded_file = st.file_uploader("Upload CSV file with 'text' column for batch prediction", type=['csv'], key="batch_upload")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            if 'text' in df.columns:
                st.dataframe(df.head())
                
                if st.button("Predict Batch"):
                    with st.spinner("Processing batch prediction..."):
                        try:
                            result = predict_batch(df['text'].tolist())
                            
                            # Create DataFrame with predictions
                            predictions_df = pd.DataFrame(result['predictions'])
                            st.write("Prediction Results:")
                            st.dataframe(predictions_df)
                            
                            # Download button for predictions
                            csv = predictions_df.to_csv(index=False)
                            st.download_button(
                                label="Download predictions as CSV",
                                data=csv,
                                file_name="predictions.csv",
                                mime="text/csv"
                            )
                        except Exception as e:
                            st.error(f"Error during batch prediction: {str(e)}")
            else:
                st.error("CSV file must contain a 'text' column")