import streamlit as st
from garmin_planner.client import Client
from garmin_planner.main import importWorkouts, scheduleWorkouts, parseYaml, replace_variables
import yaml
import os
import datetime

st.title("Shin Splints - Garmin Training Planner")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'garmin_client' not in st.session_state:
    st.session_state.garmin_client = None
if 'login_state' not in st.session_state:
    st.session_state.login_state = 'init'

def my_mfa_callback():
    # If the user has entered an MFA code, use it.
    if 'mfa_code' in st.session_state and st.session_state.mfa_code:
        return st.session_state.mfa_code
    
    # If no code is present, stop execution to let user enter it.
    st.session_state.login_state = 'mfa'
    st.warning("MFA code required. Please enter it below.")
    st.rerun()

# Login flow
if not st.session_state.authenticated:
    if st.session_state.login_state == 'init':
        st.header("Login")
        st.text_input("Email", key="email")
        st.text_input("Password", type="password", key="password")
        
        if st.button("Login"):
            try:
                # Create client and save to session state BEFORE login
                client = Client(st.session_state.get("email", ""), 
                                st.session_state.get("password", ""), 
                                mfa_callback=my_mfa_callback, auto_login=False)
                st.session_state.garmin_client = client
                
                if client.login():
                    st.session_state.authenticated = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Login failed")
            except Exception as e:
                st.error(f"Login error: {e}")

    elif st.session_state.login_state == 'mfa':
        st.header("MFA Verification")
        st.text_input("Enter MFA code", key="mfa_code")
        
        if st.button("Submit MFA"):
            # The callback will now find the code in session_state and return it
            if st.session_state.garmin_client.login():
                st.session_state.authenticated = True
                st.session_state.login_state = 'init'
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Login failed")

# If authenticated, show training planner
if st.session_state.authenticated:
    st.header("Training Plan Generator")
    
    uploaded_file = st.file_uploader("Choose a training plan YAML file", type=["yaml", "yml"])
    start_date = st.date_input("Training Plan Start Date", datetime.date.today())
    
    if uploaded_file is not None and st.button("Generate & Push Workouts"):
        data = yaml.safe_load(uploaded_file)
        
        # Preprocess data (similar to main.py)
        # replace definitions
        if "definitions" in data:
            definitionsDict = data['definitions']
            data = replace_variables(data, definitionsDict)
        
        garminCon = st.session_state.garmin_client
        
        # import workouts
        if "workouts" in data:
            workouts = data['workouts']
            # Assume deleteSameNameWorkout: False for now
            importWorkouts(workouts=workouts, 
                           toDeletePrevious=False, 
                           conn=garminCon)
            st.success("Workouts imported successfully!")
            
        # schedule workouts
        if "schedulePlan" in data:
            schedulePlan = data['schedulePlan']
            workouts = schedulePlan['workouts']
            scheduleWorkouts(start_date, workouts, garminCon)
            st.success("Workouts scheduled successfully!")
