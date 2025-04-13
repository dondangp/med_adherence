import streamlit as st
import pandas as pd
import json
import uuid
from datetime import datetime, date
import plotly.graph_objects as go
import medication_insights

st.set_page_config(page_title="Medication Tracker", layout="centered", initial_sidebar_state="auto")

# File paths
patient_file_path = "fhir_data/patient/Patient.ndjson"
med_admin_path = "fhir_data/medication_administration/MedicationAdministration.ndjson"
med_request_path = "fhir_data/medication_request/MedicationRequest.ndjson"
editable_profile_path = "editable_profile.json"
user_accounts_path = "app_data/user_accounts.json"  # Added path for user accounts

# Setup dark/light mode toggle
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Theme button in the sidebar
with st.sidebar:
    theme_label = "🌙 Switch to Dark Mode" if st.session_state.theme == "light" else "☀️ Switch to Light Mode"
    if st.button(theme_label):
        toggle_theme()
        st.rerun()

if st.session_state.theme == "dark":
    st.markdown("""
        <style>
        .stApp {
            background-color: #121212;
            color: #ffffff;
        }
                

        .css-18e3th9 {
            background-color: #121212 !important;
        }

        .block-container {
            background-color: #121212;
        }

        .css-1d391kg p, .css-1d391kg span, .css-1d391kg label, .css-1d391kg div {
            color: #ffffff !important;
        }

        /* Improve secondary button visibility (Logout, etc) */
        button[data-testid="baseButton-secondary"] {
            background-color: #333333 !important;
            color: #f0f0f0 !important;
            border: 1px solid #555555 !important;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: background-color 0.2s ease;
        }

        button[data-testid="baseButton-secondary"]:hover {
            background-color: #444444 !important;
        }

        /* Logout button text */
        .st-emotion-cache-3ps0xc p {
            color: #f5f5f5 !important;
        }

        /* 💊 Medication Adherence Insights block */
        div[style*="background-color: rgb(242, 248, 255)"] {
            background-color: #1e1e1e !important;
            color: #f0f0f0 !important;
            border-left: 4px solid #0ea5e9;
        }

        div[style*="background-color: rgb(242, 248, 255)"] p {
            color: #dddddd !important;
        }

        div[style*="background-color: rgb(242, 248, 255)"] strong {
            color: #ffffff !important;
        }

        /* Tab buttons styling (🏠 📊Home, 💊 Medications, etc) */
        button[role="tab"] {
            background-color: #2c2c2c !important;
            color: #eeeeee !important;
            border: 1px solid #444 !important;
            font-weight: 500;
        }

        button[role="tab"][aria-selected="true"] {
            background-color: #007acc !important;
            color: #ffffff !important;
        }

        /* Tab label text (for 🏠 📊Home specifically) */
        .st-emotion-cache-sh2krr p {
            color: #f5f5f5 !important;
        }
        </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
        <style>
        .stApp {
            background-color: white;
            color: #2c3e50;
        }

        .css-18e3th9 {
            background-color: white !important;
        }

        .block-container {
            background-color: white;
        }

        /* Text defaults for light mode */
        .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: black !important;
        }

        /* Fix title like "🔐 Medication Tracker Login" */
        .e1nzilvr1 {
            color: black !important;
        }

        /* Plotly axis labels and tick values */
        .xtitle, .ytitle, .xtick text, .ytick text {
            fill: black !important;
        }

        /* Custom button styling for light mode */
        button[data-testid="baseButton-secondary"] {
            background-color: #f0f0f0 !important;
            color: #1f2937 !important;
            border: 1px solid #ccc !important;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: background-color 0.2s ease;
        }

        button[data-testid="baseButton-secondary"]:hover {
            background-color: #e0e0e0 !important;
        }
        </style>
    """, unsafe_allow_html=True)



# Setup dark/light mode toggle
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"



if st.session_state.theme == "dark":
    st.markdown("""
        <style>
        /* General background and base text */
        html, body, .stApp {
            background-color: #121212 !important;
            color: #ffffff !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }

        /* Main container */
        .block-container {
            background-color: #121212 !important;
        }

        /* Cards and containers */
        .stat-card,
        .chart-container,
        .insights-section,
        .reminder-section,
        .dashboard-header,
        .medication-item {
            background-color: #1f1f1f !important;
            color: #ffffff !important;
            border: 1px solid #333;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            background-color: #2c2c2c !important;
            color: #ffffff !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: #007acc !important;
            color: white !important;
        }

        /* Forms and text fields */
        input, textarea, select, button {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
            border-color: #333 !important;
        }

        /* Force text inside common widgets */
        .stTextInput > div > input,
        .stSelectbox > div,
        .stSelectbox label,
        .stMarkdown,
        .stMarkdown p,
        .stMarkdown span,
        .stMarkdown div,
        label, span, div, p, h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }

        /* Medication taken highlight */
        .taken-medication {
            background-color: #14532d !important;
            border-color: #22c55e !important;
            color: #ffffff !important;
        }

        /* Alerts */
        .interaction-alert {
            background-color: #2a2a00 !important;
            color: #ffffcc !important;
        }

        /* Footer */
        footer, .footer {
            background-color: #121212 !important;
            color: #aaaaaa !important;
        }

        /* Fix button contrast */
        .stButton>button {
            background-color: #333 !important;
            color: white !important;
            border: 1px solid #444 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    

else:
    st.markdown("""
        <style>
        .stApp {
            background-color: white;
            color: #2c3e50;
        }
        .css-18e3th9 {
            background-color: white !important;
        }
        .block-container {
            background-color: white;
        }

        /* 🔐 Medication Tracker Login header */
        .st-emotion-cache-10trblm {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)




# Define help section function
def help_section():
    st.title("Help & Support")
    
    st.markdown("## 📌 About the Medication Tracker")
    st.write(
        "This application helps patients track their medication intake, receive reminders, "
        "monitor side effects, and gain insights through reports and analytics. "
        "If you need assistance, check out the FAQs below or contact support."
    )

    st.markdown("## ❓ Frequently Asked Questions (FAQs)")

    with st.expander("How do I log my medication?"):
        st.write("Go to the 'Home' tab, and check the box next to your medication to mark it as taken.")

    with st.expander("How do I view my medications?"):
        st.write("Visit the 'Medications' tab to see all your active and inactive medications.")

    with st.expander("How is my adherence rate calculated?"):
        st.write("Your adherence rate is calculated based on the medications you've taken versus those you were scheduled to take. The app tracks this data and displays it as a percentage.")

    with st.expander("Can I update my personal information?"):
        st.write("Yes! Go to the 'Profile' tab to update your personal details.")

    with st.expander("What should I do if I experience side effects?"):
        st.write("Contact your healthcare provider immediately if you experience unexpected side effects.")

    with st.expander("How can I contact support?"):
        st.write("You can reach us at **support@medtracker.com** or call **+1-800-123-4567**.")

    st.markdown("## 📞 Contact & Support")
    st.info("For further assistance, email us at **support@medtracker.com** or call **+1-800-123-4567**.")

# Load user accounts
@st.cache_data
def load_user_accounts():
    try:
        with open(user_accounts_path, "r") as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading user accounts: {e}")
        return []

# Load patient
@st.cache_data
def load_patient(patient_id=None):
    try:
        with open(patient_file_path, "r") as file:
            #st.write(f"patient_file_path, {patient_file_path}")
            patient_data = json.loads(file.readline())
            #st.write(f"patient_data, {patient_data['name'][0]['family']}")
            # If a specific patient ID is provided, try to load that patient instead
            if patient_id:
                # Reset file pointer and search for the patient with matching ID
                file.seek(0)
                for line in file:
                    try:
                        patient = json.loads(line)
                        if patient.get("id") == patient_id:
                            return patient
                    except:
                        continue
            return patient_data
    except Exception as e:
        st.error(f"Error loading patient data: {e}")
        return {}

# Load NDJSON
def load_ndjson(path):
    try:
        with open(path, "r") as f:
            return [json.loads(line) for line in f]
    except:
        return []

# Convert editable profile back to FHIR format
def update_fhir_patient(current_patient, profile_data):
    # Create a copy of the current patient to avoid modifying the original
    updated_patient = current_patient.copy()
    
    # Update name
    if updated_patient.get("name") and len(updated_patient["name"]) > 0:
        if profile_data.get("first_name"):
            if "given" not in updated_patient["name"][0]:
                updated_patient["name"][0]["given"] = []
            
            if len(updated_patient["name"][0]["given"]) > 0:
                updated_patient["name"][0]["given"][0] = profile_data["first_name"]
            else:
                updated_patient["name"][0]["given"].append(profile_data["first_name"])
        
        if profile_data.get("last_name"):
            updated_patient["name"][0]["family"] = profile_data["last_name"]
    
    # Update birthDate
    if profile_data.get("birth_date") and profile_data["birth_date"] != "N/A":
        updated_patient["birthDate"] = profile_data["birth_date"]
    
    # Update gender
    if profile_data.get("gender") and profile_data["gender"] != "unknown":
        updated_patient["gender"] = profile_data["gender"]
    
    # Update telecom (phone and email)
    if "telecom" not in updated_patient:
        updated_patient["telecom"] = []
    
    # Update phone
    phone_found = False
    for i, telecom in enumerate(updated_patient.get("telecom", [])):
        if telecom.get("system") == "phone":
            if profile_data.get("phone") and profile_data["phone"] != "N/A":
                updated_patient["telecom"][i]["value"] = profile_data["phone"]
            phone_found = True
            break
    
    if not phone_found and profile_data.get("phone") and profile_data["phone"] != "N/A":
        updated_patient["telecom"].append({
            "system": "phone",
            "value": profile_data["phone"],
            "use": "home"
        })
    
    # Update email
    email_found = False
    for i, telecom in enumerate(updated_patient.get("telecom", [])):
        if telecom.get("system") == "email":
            if profile_data.get("email") and profile_data["email"] != "N/A":
                updated_patient["telecom"][i]["value"] = profile_data["email"]
            email_found = True
            break
    
    if not email_found and profile_data.get("email") and profile_data["email"] != "N/A":
        updated_patient["telecom"].append({
            "system": "email",
            "value": profile_data["email"],
            "use": "home"
        })
    
    # Update address
    if profile_data.get("address") and profile_data["address"] != "N/A":
        if "address" not in updated_patient or not updated_patient["address"]:
            updated_patient["address"] = [{"text": profile_data["address"]}]
        else:
            updated_patient["address"][0]["text"] = profile_data["address"]
    
    # Update race
    if profile_data.get("race"):
        race_found = False
        for i, extension in enumerate(updated_patient.get("extension", [])):
            if extension.get("url") == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                race_found = True
                for j, race_ext in enumerate(extension.get("extension", [])):
                    if race_ext.get("url") == "text":
                        updated_patient["extension"][i]["extension"][j]["valueString"] = profile_data["race"]
                        break
                break
        
        if not race_found:
            if "extension" not in updated_patient:
                updated_patient["extension"] = []
            updated_patient["extension"].append({
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                "extension": [
                    {
                        "url": "text",
                        "valueString": profile_data["race"]
                    }
                ]
            })
    
    # Update ethnicity
    if profile_data.get("ethnicity"):
        ethnicity_found = False
        for i, extension in enumerate(updated_patient.get("extension", [])):
            if extension.get("url") == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
                ethnicity_found = True
                for j, eth_ext in enumerate(extension.get("extension", [])):
                    if eth_ext.get("url") == "text":
                        updated_patient["extension"][i]["extension"][j]["valueString"] = profile_data["ethnicity"]
                        break
                break
        
        if not ethnicity_found:
            if "extension" not in updated_patient:
                updated_patient["extension"] = []
            updated_patient["extension"].append({
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
                "extension": [
                    {
                        "url": "text",
                        "valueString": profile_data["ethnicity"]
                    }
                ]
            })
    
    # Update language
    if profile_data.get("language"):
        if "communication" not in updated_patient or not updated_patient["communication"]:
            updated_patient["communication"] = [
                {
                    "language": {
                        "text": profile_data["language"]
                    }
                }
            ]
        else:
            if "language" not in updated_patient["communication"][0]:
                updated_patient["communication"][0]["language"] = {}
            updated_patient["communication"][0]["language"]["text"] = profile_data["language"]
    
    return updated_patient

# Save patient data back to FHIR resource
def save_patient_data(patient_data):
    try:
        patient_id = patient_data.get("id")
        if not patient_id:
            return False, "Invalid patient data: no patient ID found"
        
        # Read all patients from the file
        all_patients = []
        try:
            with open(patient_file_path, "r") as file:
                for line in file:
                    try:
                        p = json.loads(line)
                        all_patients.append(p)
                    except:
                        continue
        except Exception as e:
            return False, f"Error reading patient file: {e}"
        
        # Find and update the patient
        updated = False
        for i, p in enumerate(all_patients):
            if p.get("id") == patient_id:
                all_patients[i] = patient_data
                updated = True
                break
        
        if not updated:
            return False, f"Patient with ID {patient_id} not found"
        
        # Write all patients back to the file
        try:
            with open(patient_file_path, "w") as file:
                for p in all_patients:
                    file.write(json.dumps(p) + "\n")
            return True, "Patient data updated successfully"
        except Exception as e:
            return False, f"Error writing to patient file: {e}"
            
    except Exception as e:
        return False, f"Error saving patient data: {e}"
    
from datetime import datetime, date, timedelta

def get_date_range(period: str):
    today = date.today()
    
    if period == "daily":
        # Start & end are the same
        return today, today
    
    elif period == "weekly":
        start = today - timedelta(days=6)  # last 7 days (today included)
        return start, today
    
    elif period == "monthly":
        start = today.replace(day=1)  # first day of the current month
        return start, today

    else:
        return today, today  # default fallback

# Get user profile from user_accounts.json and patient resource
def get_user_profile(username):
    user_accounts = load_user_accounts()
    for user in user_accounts:
        if user.get("username") == username:
            patient_id = user.get("patient_id", "")
            
            # Create a basic profile with user account info
            profile = {
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", ""),
                "patient_id": patient_id,
                # Add other profile fields with default values
                "birth_date": "N/A",
                "gender": "unknown",
                "race": "",
                "ethnicity": "",
                "language": "",
                "religion": "",
                "address": "N/A",
                "email": "N/A",
                "phone": "N/A"
            }
            
            # If we have a patient_id, try to get the actual patient data
            if patient_id:
                patient_data = load_patient(patient_id)
                #st.write(f"patient_data, {patient_data['name'][0]['family']}")
                if patient_data:
                    # Extract information from patient resource
                    name = patient_data.get("name", [{}])[0]
                    profile.update({
                        "first_name": name.get("given", [""])[0] if name.get("given") else "",
                        "last_name": name.get("family", ""),
                        "birth_date": patient_data.get("birthDate", "N/A"),
                        "gender": patient_data.get("gender", "unknown"),
                        "address": patient_data.get("address", [{}])[0].get("text", 
                                 " ".join(patient_data.get("address", [{}])[0].get("line", [""])) + 
                                 ", " + patient_data.get("address", [{}])[0].get("city", "") +
                                 ", " + patient_data.get("address", [{}])[0].get("state", "") +
                                 " " + patient_data.get("address", [{}])[0].get("postalCode", "")
                                 ) if patient_data.get("address") else "N/A",
                        "phone": next((t.get("value", "N/A") for t in patient_data.get("telecom", []) 
                                    if t.get("system") == "phone"), "N/A"),
                        "email": next((t.get("value", "N/A") for t in patient_data.get("telecom", []) 
                                    if t.get("system") == "email"), "N/A"),
                    })
                    
                    # Extract race from extension
                    for ext in patient_data.get("extension", []):
                        if ext.get("url") == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                            for race_ext in ext.get("extension", []):
                                if race_ext.get("url") == "text":
                                    profile["race"] = race_ext.get("valueString", "")
                        
                        # Extract ethnicity from extension
                        elif ext.get("url") == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
                            for eth_ext in ext.get("extension", []):
                                if eth_ext.get("url") == "text":
                                    profile["ethnicity"] = eth_ext.get("valueString", "")
                    
                    # Extract language from communication
                    if patient_data.get("communication"):
                        for comm in patient_data.get("communication", []):
                            if comm.get("language", {}).get("text"):
                                profile["language"] = comm.get("language", {}).get("text", "")
            
            return profile
    return None

# Check if medication was taken today
def was_medication_taken_today(med_id, administrations):
    today = date.today().isoformat()
    for admin in administrations:
        # Skip if not a MedicationAdministration
        if admin.get("resourceType") != "MedicationAdministration":
            continue
            
        # Get the medication ID from the administration
        admin_med_id = None
        for coding in admin.get("medicationCodeableConcept", {}).get("coding", []):
            if coding.get("system") == "http://www.nlm.nih.gov/research/umls/rxnorm":
                admin_med_id = coding.get("code")
                break
                
        if not admin_med_id:
            admin_med_id = admin.get("medicationCodeableConcept", {}).get("text", "")
            
        # Check if this is the medication we're looking for
        if admin_med_id != med_id:
            continue
            
        # Check if the administration was today
        admin_date = None
        try:
            admin_datetime = admin.get("effectiveDateTime", "")
            if admin_datetime:
                admin_date = admin_datetime.split("T")[0]  # Extract just the date part
        except:
            continue
            
        if admin_date == today:
            return True
            
    return False

# Authenticate user
def authenticate(username, password):
    user_accounts = load_user_accounts()
    for user in user_accounts:
        if user.get("username") == username and user.get("password") == password:
            return True
    return False

# Load data
patient = load_patient()  # Default patient data (will be replaced with specific patient after login)
med_requests = load_ndjson(med_request_path)
med_administrations = load_ndjson(med_admin_path)

# Session state
if "username" not in st.session_state:
    st.session_state.username = None

if "current_patient" not in st.session_state:
    st.session_state.current_patient = None

if "editable_profile" not in st.session_state:
    st.session_state.editable_profile = {
        "first_name": "",
        "last_name": "",
        "birth_date": "N/A",
        "gender": "unknown",
        "race": "",
        "ethnicity": "",
        "language": "",
        "religion": "",
        "address": "N/A",
        "email": "N/A",
        "phone": "N/A",
        "patient_id": ""
    }

query_params = st.query_params
if "logged_in" not in st.session_state:
    st.session_state.logged_in = query_params.get("auth") == "true"
    st.session_state.username = query_params.get("user")

if st.session_state.logged_in and st.session_state.username and not st.session_state.current_patient:
    user_profile = get_user_profile(st.session_state.username)
    if user_profile:
        st.session_state.editable_profile = user_profile
        if user_profile.get("patient_id"):
            patient_data = load_patient(user_profile.get("patient_id"))
            if patient_data:
                st.session_state.current_patient = patient_data


# Initialize taken medications in session state if not present
if "taken_medications" not in st.session_state:
    st.session_state.taken_medications = {}

# Get today's date for tracking
today = date.today().isoformat()
if "current_date" not in st.session_state:
    st.session_state.current_date = today
# If date changed, reset tracking
elif st.session_state.current_date != today:
    st.session_state.current_date = today
    st.session_state.taken_medications = {}

# Login
if not st.session_state.logged_in:
    st.title("🔐 Medication Tracker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            
            # Load user profile from user_accounts.json and patient resource
            user_profile = get_user_profile(username)
            if user_profile:
                st.session_state.editable_profile = user_profile
                
                # Update the patient data based on the patient_id
                if user_profile.get("patient_id"):
                    patient_data = load_patient(user_profile.get("patient_id"))
                    if patient_data:
                        st.session_state.current_patient = patient_data
                    else:
                        st.warning("Patient data not found. Some features may be limited.")
                
            st.query_params.update({"auth": "true", "user": username})
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

if st.session_state.logged_in:
    st.markdown("""
    <style>
        .logout-button-container {
            position: fixed;
            top: 50px;  /* Adjusted from 10px to 50px */
            right: 25px;
            z-index: 9999;
        }
        .logout-button-container button {
            background-color: #f0f0f0;
            color: #1f2937;
            border: 1px solid #ccc;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
        }
    </style>
    <div class="logout-button-container">
        <form action="" method="post">
            <button type="submit" name="logout">Logout</button>
        </form>
    </div>
    """, unsafe_allow_html=True)

    # Trigger logout via query param workaround
    query_params = st.query_params
    if query_params.get("logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.query_params.update({"auth": "false", "user": ""})
        st.rerun()


# Extract medications
active_medications, stopped_medications = [], []
for entry in med_requests:
    if entry.get("resourceType") != "MedicationRequest":
        continue
    med_text = entry.get("medicationCodeableConcept", {}).get("text", "Unknown")
    coding = next((c for c in entry.get("medicationCodeableConcept", {}).get("coding", []) if c.get("system") == "http://www.nlm.nih.gov/research/umls/rxnorm"), {})
    dosage = entry.get("dosageInstruction", [{}])[0].get("text", "Dosage not specified")
    prescriber = entry.get("requester", {}).get("display", "Unknown Prescriber")
    effective_date = entry.get("authoredOn", "Unknown Date")
    med = {
        "Medication": med_text,
        "Dosage": dosage,
        "Prescriber": prescriber,
        "Effective Date": effective_date,
        "RequestID": entry.get("id", ""),
        "RXnormCode": coding.get("code", ""),
        "RXnormSystem": coding.get("system", ""),
        "RXnormDisplay": coding.get("display", med_text),
        "Original": entry
    }
    (active_medications if entry.get("status") == "active" else stopped_medications).append(med)

# Custom CSS
st.markdown("""
    <style>
        /* Force selectbox label + options to be white in dark mode */
    div[data-baseweb="select"] div {
        color: #ffffff !important;
    }
    /* Make text inside gender selection boxes white */
    .st-emotion-cache-sy3zga {
        color: #ffffff !important;
    }
        
    .stApp { background-color: white; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f8ff;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        color: #2c3e50;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e90ff !important;
        color: white !important;
    }
    p, span, label, .stMarkdown, div { color: #2c3e50 !important; }
    .medication-item {
        background-color: #f8f9fa;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .taken-medication {
        background-color: #d4edda;
        border-color: #c3e6cb;
    }
    
</style>
""", unsafe_allow_html=True)

# Tabs
home, medications, profile, help = st.tabs(["\U0001F3E0 📊Home", "\U0001F48A Medications", "Profile", "\u2753 Help"])



def calculate_adherence_rate(active_meds, med_administrations, period="daily"):
    start_date, end_date = get_date_range(period)
    today = date.today()
    
    # If there are no active medications, return 100% adherence
    if not active_meds:
        return 1.0
    
    # All distinct medication IDs (we'll compare by RXnormCode if present)
    active_codes = [
        med["RXnormCode"] if med["RXnormCode"] else med["Medication"]
        for med in active_meds
    ]
    
    # Helper: convert an ISO date string ("2023-03-05T09:00:00") to date object
    def parse_admin_date(admin):
        try:
            return datetime.fromisoformat(admin["effectiveDateTime"]).date()
        except:
            try:
                # Some dates might be in a different format
                return datetime.strptime(admin["effectiveDateTime"].split('T')[0], "%Y-%m-%d").date()
            except:
                return None
    
    # Build a dict: day -> set of meds taken that day
    daily_taken_map = {}
    
    for admin in med_administrations:
        admin_date = parse_admin_date(admin)
        if admin_date is None:
            continue
        
        if start_date <= admin_date <= end_date:
            # Determine which medication was administered
            med_code = None
            coding_list = admin.get("medicationCodeableConcept", {}).get("coding", [])
            for c in coding_list:
                if c.get("system") == "http://www.nlm.nih.gov/research/umls/rxnorm":
                    med_code = c.get("code")
                    break
            if not med_code:
                # If no RxNorm code found, try the text fallback
                med_code = admin.get("medicationCodeableConcept", {}).get("text", "")
            
            # Record this medication in the daily map
            if admin_date not in daily_taken_map:
                daily_taken_map[admin_date] = set()
            daily_taken_map[admin_date].add(med_code)
    
    # IMPORTANT: Check if today is the first day of the month/week
    # If yes, and if all medications are taken today, return 100%
    if period == "monthly" and today.day == 1:
        # First day of month
        all_taken_today = True
        for code in active_codes:
            if code not in daily_taken_map.get(today, set()):
                all_taken_today = False
                break
        if all_taken_today:
            return 1.0  # 100% adherence
    
    if period == "weekly" and today.weekday() == 0:  # Monday is 0
        # First day of week
        all_taken_today = True
        for code in active_codes:
            if code not in daily_taken_map.get(today, set()):
                all_taken_today = False
                break
        if all_taken_today:
            return 1.0  # 100% adherence
    
    # For any period where all medications taken today = 100% adherence for that period
    # This applies even if it's not the first day of the period
    # If we're just starting to track (no historical data), and everything is taken today,
    # then adherence should be 100%
    if len(daily_taken_map) <= 1 and today in daily_taken_map:
        # We only have data for today
        all_taken_today = True
        for code in active_codes:
            if code not in daily_taken_map.get(today, set()):
                all_taken_today = False
                break
        if all_taken_today:
            return 1.0  # 100% adherence
    
    # For new tracking periods with sparse data, use only days with actual data
    days_with_data = [day for day in daily_taken_map.keys() if start_date <= day <= end_date]
    if days_with_data:
        # Adjust dates to only include days when medications were tracked
        adjusted_start = max(start_date, min(days_with_data))
        adjusted_end = min(end_date, max(days_with_data))
    else:
        adjusted_start = start_date
        adjusted_end = end_date
    
    # Now walk through each day in the chosen period
    total_days = (adjusted_end - adjusted_start).days + 1
    
    # We only expect medications on days that have already occurred
    total_medications_expected = total_days * len(active_codes)
    
    medications_taken_count = 0
    
    current_day = adjusted_start
    while current_day <= adjusted_end:
        # For each day, see which meds were taken
        meds_taken_today = daily_taken_map.get(current_day, set())
        
        # Count how many of the active meds are in meds_taken_today
        for code in active_codes:
            if code in meds_taken_today:
                medications_taken_count += 1
        
        current_day += timedelta(days=1)
    
    if total_medications_expected == 0:
        return 1.0  # If no medications are expected, adherence is perfect
    
    return medications_taken_count / total_medications_expected

# Home dashboard section with the original styling from the enhanced version plus insights
with home:
    # Enhanced styling with cards and modern layout
    st.markdown("""
    <style>
    .dashboard-header {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .card-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
        color: #2c3e50;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9rem;
        text-align: center;
        color: #7f8c8d;
    }
    .chart-container {
        margin-top: 20px;
        padding: 15px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .health-tip {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        border-left: 5px solid #2196f3;
    }
    .reminder-section {
        margin-top: 25px;
        background-color: #fff8e1;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
    .taken-medication {
        background-color: #d4edda;
        border-color: #c3e6cb;
    }
    .email-section {
        margin-top: 15px;
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
    }
    .insights-section {
        margin-top: 20px;
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .interaction-alert {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        border-left: 5px solid #ffc107;
    }
    .api-setup {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section with greeting and time
    current_time = datetime.now().strftime("%I:%M %p")
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>Medication Tracker Dashboard</h1>
        <h3>Hello, {st.session_state.editable_profile['first_name']}!</h3>
        <p>Updated as of {current_date} | {current_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard statistics section
    col1, col2, col3 = st.columns(3)
    
    # Calculate statistics directly from the database to avoid reset on refresh
    def count_medications_taken_today():
        taken_count = 0
        for med in active_medications:
            med_id = med["RXnormCode"] or med["Medication"]
            if was_medication_taken_today(med_id, med_administrations):
                taken_count += 1
        return taken_count
    
    # Get counts directly from the database
    total_active_meds = len(active_medications)
    total_taken_today = count_medications_taken_today()
    remaining_meds = total_active_meds - total_taken_today
    
    # Get adherence rates for different periods
    daily_rate = calculate_adherence_rate(active_medications, med_administrations, period="daily") * 100
    weekly_rate = calculate_adherence_rate(active_medications, med_administrations, period="weekly") * 100
    monthly_rate = calculate_adherence_rate(active_medications, med_administrations, period="monthly") * 100
    
    # Function to determine color based on percentage
    def get_color(rate):
        if rate >= 80:
            return "#28a745"  # Green
        elif rate >= 50:
            return "#ffc107"  # Yellow/Orange
        else:
            return "#dc3545"  # Red
    
    # Adherence rate card
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="card-header">Today's Adherence</div>
            <div class="metric-value" style="color: {get_color(daily_rate)};">{daily_rate:.1f}%</div>
            <div class="metric-label">Medications taken today</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Medications count card
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="card-header">Medication Progress</div>
            <div class="metric-value">{total_taken_today}/{total_active_meds}</div>
            <div class="metric-label">Medications taken/total</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Weekly trend card
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="card-header">Weekly Adherence</div>
            <div class="metric-value" style="color: {get_color(weekly_rate)};">{weekly_rate:.1f}%</div>
            <div class="metric-label">Last 7 days average</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Adherence trend visualization
    st.markdown("""
    <div class="chart-container">
        <div class="card-header">Adherence Trend</div>
    """, unsafe_allow_html=True)
    
    # Create sample data for adherence trend
    # In production, this would be real historical data
    adherence_data = {
        "Daily": daily_rate,
        "Weekly": weekly_rate, 
        "Monthly": monthly_rate
    }
    
    # Generate a Plotly bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=list(adherence_data.keys()),
        y=list(adherence_data.values()),
        marker_color=[get_color(daily_rate), get_color(weekly_rate), get_color(monthly_rate)],
        text=[f"{val:.1f}%" for val in adherence_data.values()],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Adherence Rate by Period",
        xaxis_title="Time Period",
        yaxis_title="Adherence Rate (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Add this section after your existing medication tracking section in the home tab

    # New detailed insights section with tabs
    st.markdown("""
    <div class="chart-container">
        <div class="card-header">📊 Medication Analytics</div>
    """, unsafe_allow_html=True)

    # Create tabs for the different analytics sections
    analytics_tabs = st.tabs(["Medication Adherence", "Adherence Patterns"])

    # 1. Individual Medication Adherence Tab - Improved for long medication names
    with analytics_tabs[0]:
        st.subheader("Individual Medication Adherence")
        
        # Calculate adherence rate for each individual medication using real data
        individual_adherence = {}
        
        for med in active_medications:
            med_id = med["RXnormCode"] or med["Medication"]
            med_name = med["Medication"]
            
            # Calculate days medication was taken based on actual administration records
            days_with_data = []
            days_taken = 0
            
            # Start date for analysis (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=29)  # Last 30 days including today
            
            # Build list of dates to check
            current_date = start_date
            while current_date <= end_date:
                days_with_data.append(current_date)
                current_date += timedelta(days=1)
            
            # Check each day for administration records
            for check_date in days_with_data:
                was_taken = False
                for admin in med_administrations:
                    # Skip if not a MedicationAdministration
                    if admin.get("resourceType") != "MedicationAdministration":
                        continue
                    
                    # Get the medication ID from the administration
                    admin_med_id = None
                    for coding in admin.get("medicationCodeableConcept", {}).get("coding", []):
                        if coding.get("system") == "http://www.nlm.nih.gov/research/umls/rxnorm":
                            admin_med_id = coding.get("code")
                            break
                    
                    if not admin_med_id:
                        admin_med_id = admin.get("medicationCodeableConcept", {}).get("text", "")
                    
                    # Skip if not the medication we're looking for
                    if admin_med_id != med_id:
                        continue
                    
                    # Check if the administration was on the check date
                    admin_date = None
                    try:
                        admin_datetime = admin.get("effectiveDateTime", "")
                        if admin_datetime:
                            admin_date = datetime.fromisoformat(admin_datetime).date()
                    except:
                        continue
                    
                    if admin_date == check_date:
                        was_taken = True
                        break
                
                if was_taken:
                    days_taken += 1
            
            # Calculate adherence rate for this medication
            if len(days_with_data) > 0:
                adherence_rate = (days_taken / len(days_with_data)) * 100
            else:
                adherence_rate = 0
            
            individual_adherence[med_name] = adherence_rate
        
        # IMPROVED: For long medication names, use a horizontal bar chart instead of vertical
        fig = go.Figure()
        
        med_names = list(individual_adherence.keys())
        adherence_values = list(individual_adherence.values())
        med_colors = [get_color(rate) for rate in adherence_values]
        
        # Shorten medication names if they're too long
        shortened_names = []
        for name in med_names:
            if len(name) > 20:
                shortened_names.append(name[:18] + "...")
            else:
                shortened_names.append(name)
        
        # Create horizontal bar chart for better display of long medication names
        fig.add_trace(go.Bar(
            y=shortened_names,  # Now y-axis has medication names
            x=adherence_values, # Now x-axis has adherence values
            marker_color=med_colors,
            text=[f"{val:.1f}%" for val in adherence_values],
            textposition='auto',
            orientation='h'  # Horizontal bars
        ))
        
        fig.update_layout(
            title="30-Day Adherence Rate by Medication",
            yaxis_title="Medication",
            xaxis_title="Adherence Rate (%)",
            xaxis=dict(range=[0, 100]),
            height=max(300, len(med_names) * 40),  # Dynamic height based on number of medications
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Medication with highest and lowest adherence
        if individual_adherence and len(individual_adherence) > 1:
            max_adherence = max(individual_adherence.items(), key=lambda x: x[1])
            min_adherence = min(individual_adherence.items(), key=lambda x: x[1])
            
            # Format long medication names for display
            max_med_name = max_adherence[0]
            min_med_name = min_adherence[0]
            if len(max_med_name) > 25:
                max_med_name = max_med_name[:23] + "..."
            if len(min_med_name) > 25:
                min_med_name = min_med_name[:23] + "..."
            
            st.markdown(f"""
            <div style="background-color: #f2f8ff; padding: 15px; border-radius: 10px; margin-top: 15px;">
                <h4 style="color: #1e70c1 !important;">💊 Medication Adherence Insights</h4>
                <p><strong>Best adherence:</strong> {max_med_name} ({max_adherence[1]:.1f}%)</p>
                <p><strong>Needs improvement:</strong> {min_med_name} ({min_adherence[1]:.1f}%)</p>
                <p>Consider setting specific reminders for medications with lower adherence rates.</p>
            </div>
            """, unsafe_allow_html=True)
        elif individual_adherence and len(individual_adherence) == 1:
            med_name = list(individual_adherence.keys())[0]
            adherence_value = list(individual_adherence.values())[0]
            
            status = "Good adherence" if adherence_value >= 80 else "Moderate adherence" if adherence_value >= 50 else "Needs improvement"
            
            st.markdown(f"""
            <div style="background-color: #f2f8ff; padding: 15px; border-radius: 10px; margin-top: 15px;">
                <h4 style="color: #1e70c1 !important;">💊 Medication Adherence Insights</h4>
                <p><strong>{status}:</strong> {med_name} ({adherence_value:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)

    # 2. Adherence Patterns Tab
    with analytics_tabs[1]:
        st.subheader("Weekly Adherence Patterns")
        
        # Analyze adherence patterns by day of week using real data
        adherence_by_day = {
            "Monday": {"taken": 0, "total": 0},
            "Tuesday": {"taken": 0, "total": 0},
            "Wednesday": {"taken": 0, "total": 0},
            "Thursday": {"taken": 0, "total": 0},
            "Friday": {"taken": 0, "total": 0},
            "Saturday": {"taken": 0, "total": 0},
            "Sunday": {"taken": 0, "total": 0}
        }
        
        # Analyze the last 90 days
        end_date = date.today()
        start_date = end_date - timedelta(days=89)  # Last 90 days
        
        # For each day in the range
        current_date = start_date
        while current_date <= end_date:
            day_name = current_date.strftime("%A")  # Get day name (Monday, Tuesday, etc.)
            
            # For each medication
            for med in active_medications:
                med_id = med["RXnormCode"] or med["Medication"]
                adherence_by_day[day_name]["total"] += 1
                
                # Check if medication was taken on this day
                was_taken = False
                for admin in med_administrations:
                    # Skip if not a MedicationAdministration
                    if admin.get("resourceType") != "MedicationAdministration":
                        continue
                    
                    # Get the medication ID from the administration
                    admin_med_id = None
                    for coding in admin.get("medicationCodeableConcept", {}).get("coding", []):
                        if coding.get("system") == "http://www.nlm.nih.gov/research/umls/rxnorm":
                            admin_med_id = coding.get("code")
                            break
                    
                    if not admin_med_id:
                        admin_med_id = admin.get("medicationCodeableConcept", {}).get("text", "")
                    
                    # Skip if not the medication we're looking for
                    if admin_med_id != med_id:
                        continue
                    
                    # Check if the administration was on the current date
                    admin_date = None
                    try:
                        admin_datetime = admin.get("effectiveDateTime", "")
                        if admin_datetime:
                            admin_date = datetime.fromisoformat(admin_datetime).date()
                    except:
                        continue
                    
                    if admin_date == current_date:
                        was_taken = True
                        break
                
                if was_taken:
                    adherence_by_day[day_name]["taken"] += 1
            
            current_date += timedelta(days=1)
        
        # Calculate percentages
        adherence_percentages = {}
        for day, data in adherence_by_day.items():
            if data["total"] > 0:
                adherence_percentages[day] = (data["taken"] / data["total"]) * 100
            else:
                adherence_percentages[day] = 0
        
        # Reorder days of week
        ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ordered_percentages = [adherence_percentages.get(day, 0) for day in ordered_days]
        
        # Create a cleaner line chart with area fill for better visualization
        fig = go.Figure()
        
        # Add area chart under the line for visual appeal
        fig.add_trace(go.Scatter(
            x=ordered_days,
            y=ordered_percentages,
            mode='lines',
            line=dict(color='rgba(30, 144, 255, 0.2)', width=0),
            fill='tozeroy',
            fillcolor='rgba(30, 144, 255, 0.1)',
            showlegend=False
        ))
        
        # Add line with markers on top
        fig.add_trace(go.Scatter(
            x=ordered_days,
            y=ordered_percentages,
            mode='lines+markers',
            line=dict(color='#1e90ff', width=3),
            marker=dict(size=10, color=ordered_percentages, colorscale='RdYlGn', cmin=0, cmax=100),
            showlegend=False
        ))
        
        # Add data labels
        for i, day in enumerate(ordered_days):
            fig.add_annotation(
                x=day,
                y=ordered_percentages[i],
                text=f"{ordered_percentages[i]:.0f}%",
                showarrow=False,
                yshift=15,
                font=dict(color="#2c3e50")
            )
        
        fig.update_layout(
            title="Adherence Pattern by Day of Week",
            xaxis_title="Day of Week",
            yaxis_title="Adherence Rate (%)",
            yaxis=dict(range=[0, 100]),
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Find days with highest and lowest adherence
        if adherence_percentages:
            days_with_data = [day for day, pct in adherence_percentages.items() if pct > 0]
            
            if days_with_data:
                filtered_percentages = {day: pct for day, pct in adherence_percentages.items() if pct > 0}
                max_day = max(filtered_percentages.items(), key=lambda x: x[1])
                min_day = min(filtered_percentages.items(), key=lambda x: x[1])
                
                # Create two columns for better layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 15px; border-radius: 10px; height: 100%;">
                        <h4 style="color: #155724 !important;">Best Day</h4>
                        <div style="font-size: 2rem; font-weight: bold; margin: 10px 0;">{max_day[0]}</div>
                        <div style="font-size: 1.2rem;">{max_day[1]:.1f}% Adherence</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; height: 100%;">
                        <h4 style="color: #856404 !important;">Day to Improve</h4>
                        <div style="font-size: 2rem; font-weight: bold; margin: 10px 0;">{min_day[0]}</div>
                        <div style="font-size: 1.2rem;">{min_day[1]:.1f}% Adherence</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add tip box below
                st.markdown(f"""
                <div style="background-color: #f2f8ff; padding: 15px; border-radius: 10px; margin-top: 15px;">
                    <h4 style="color: #1e70c1 !important;">💡 Suggestion</h4>
                    <p>You tend to miss medications more often on {min_day[0]}s. Consider setting additional reminders or creating a specific routine for this day.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Not enough data yet to identify weekly patterns. Keep tracking your medications to see insights.")

    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add medication insights section
    st.markdown("""
    <div class="insights-section">
        <div class="card-header">💡 Medication Insights & Analysis</div>
    """, unsafe_allow_html=True)
    
    openai_api_key = medication_insights.load_api_key()
    
    # Cache the results to avoid repeated API calls
    if "drug_interactions_result" not in st.session_state:
        st.session_state.drug_interactions_result = None
        
    drug_interactions_tab, medication_info_tab = st.tabs(["Drug Interactions", "Medication Information"])
    
    with drug_interactions_tab:
        if st.button("Check for Drug Interactions"):
            with st.spinner("Analyzing potential drug interactions..."):
                interaction_results = medication_insights.detect_drug_interactions(active_medications, openai_api_key)
                st.session_state.drug_interactions_result = interaction_results
        
        # Display cached or new results
        if st.session_state.drug_interactions_result:
            st.markdown(st.session_state.drug_interactions_result)
        else:
            st.info("Click the button above to check for potential drug interactions between your medications.")
    
    with medication_info_tab:
        # Cache the results to avoid repeated API calls
        if "medication_insights_result" not in st.session_state:
            st.session_state.medication_insights_result = None
            st.session_state.selected_medication_for_insights = None
        
        # Option to select specific medication or all
        medication_options = ["All Active Medications"] + [med["Medication"] for med in active_medications]
        selected_medication = st.selectbox("Select Medication", medication_options)
        
        if st.button("Generate Medication Insights") or (st.session_state.medication_insights_result and st.session_state.selected_medication_for_insights == selected_medication):
            if st.session_state.medication_insights_result and st.session_state.selected_medication_for_insights == selected_medication:
                # Use cached results if available for the same selection
                st.markdown(st.session_state.medication_insights_result)
            else:
                with st.spinner("Generating medication insights..."):
                    if selected_medication == "All Active Medications":
                        meds_to_analyze = active_medications
                    else:
                        meds_to_analyze = [med for med in active_medications if med["Medication"] == selected_medication]
                    
                    insights_data = medication_insights.generate_medication_insights(meds_to_analyze, openai_api_key)
                    formatted_insights = medication_insights.format_insights(insights_data)
                    
                    # Cache the results
                    st.session_state.medication_insights_result = formatted_insights
                    st.session_state.selected_medication_for_insights = selected_medication
                    
                    st.markdown(formatted_insights)
        else:
            st.info("Select a medication above and click 'Generate Medication Insights' to view detailed information.")
    
    # Add a disclaimer
    st.markdown("""
    <div style="font-size: 0.8rem; margin-top: 20px; color: #6c757d;">
        <p><strong>Disclaimer</strong>: The information provided here is for educational purposes only and should not replace professional medical advice. 
        Always consult with your healthcare provider before making any changes to your medication regimen.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Medication tracking section
    st.markdown("""
    <div class="reminder-section">
        <h4>Today's Medication Tracking</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for already taken medications today from database
    for med in active_medications:
        med_id = med["RXnormCode"] or med["Medication"]
        if med_id not in st.session_state.taken_medications:
            # Check if this medication was already taken today according to the database
            if was_medication_taken_today(med_id, med_administrations):
                st.session_state.taken_medications[med_id] = True
    
    # Create grid layout for medications
    med_cols = st.columns(2)
    col_idx = 0
    
    for i, med in enumerate(active_medications):
        med_id = med["RXnormCode"] or med["Medication"]
        k = f"med_checkbox_{i}"
        
        # Get initial value for checkbox - True if already taken today
        initial_value = med_id in st.session_state.taken_medications and st.session_state.taken_medications[med_id]
        
        # Display in alternating columns
        with med_cols[col_idx]:
            # Display checkbox with appropriate label
            label = f"{med['Medication']} ({med['Dosage']})"
            if initial_value:
                label += " ✓"
            
            # Add a special class if taken today
            extra_class = "taken-medication" if initial_value else ""
            
            st.markdown(f"<div class='medication-item {extra_class}'>", unsafe_allow_html=True)
            
            # Create the checkbox
            checked = st.checkbox(label, value=initial_value, key=k)
            
            # If status changed from unchecked to checked
            if checked and not initial_value:
                # Record in session state
                st.session_state.taken_medications[med_id] = True
                
                # Create MedicationAdministration entry
                med_admin_entry = {
                    "resourceType": "MedicationAdministration",
                    "id": str(uuid.uuid4()),
                    "status": "completed",
                    "medicationCodeableConcept": {
                        "coding": [
                            {
                                "system": med['RXnormSystem'] or "http://www.nlm.nih.gov/research/umls/rxnorm",
                                "code": med['RXnormCode'] or "Unknown",
                                "display": med['RXnormDisplay'] or med['Medication']
                            }
                        ],
                        "text": med["Medication"]
                    },
                    "subject": med["Original"].get("subject", {"reference": f"Patient/{st.session_state.editable_profile.get('patient_id', '')}"}),
                    "context": med["Original"].get("encounter", {"reference": f"Encounter/{str(uuid.uuid4())}"}),
                    "effectiveDateTime": datetime.now().isoformat(),
                    "reasonCode": med["Original"].get("reasonCode", [
                        {
                            "coding": [{
                                "system": "http://terminology.hl7.org/CodeSystem/reason-medication-given",
                                "code": "b",
                                "display": "Given as Ordered"
                            }],
                            "text": "Self-administered medication"
                        }
                    ]),
                    "performer": [{"actor": {"display": "Patient"}}]
                }
                
                # Write to NDJSON file
                with open(med_admin_path, "a") as f:
                    f.write(json.dumps(med_admin_entry) + "\n")
                
                # Reload administrations to update the in-memory list
                med_administrations.append(med_admin_entry)
                
                st.success(f"✅ Recorded: {med['Medication']}")
                
            # Update session state if checkbox was unchecked
            elif not checked and initial_value:
                st.session_state.taken_medications[med_id] = False
                st.warning(f"⚠️ Unmarked: {med['Medication']} - Note: the database record still exists")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Toggle column for next medication
        col_idx = 1 - col_idx



#  Medications
with medications:
    tab1, tab2 = st.tabs(["💊 Active Medications", "❌ Inactive Medications"])
    with tab1:
        with st.expander("➕ Add New Medication"):
            new_med = {
                "medication": st.text_input("Medication Name"),
                "rxnorm_code": st.text_input("RXNorm Code"),
                "dosage": st.text_input("Dosage Instructions"),
                "prescriber": st.text_input("Prescriber Name"),
                "status": st.selectbox("Status", ["active", "stopped"], index=0)
            }

            if st.button("Add Medication"):
                new_entry = {
                    "resourceType": "MedicationRequest",
                    "id": str(uuid.uuid4()),
                    "meta": {
                        "profile": [
                            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest"
                        ]
                    },
                    "status": new_med["status"],
                    "intent": "order",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/medicationrequest-category",
                            "code": "community",
                            "display": "Community"
                        }],
                        "text": "Community"
                    }],
                    "medicationCodeableConcept": {
                        "coding": [{
                            "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                            "code": new_med["rxnorm_code"],
                            "display": new_med["medication"]
                        }],
                        "text": new_med["medication"]
                    },
                    "subject": {
                        "reference": f"Patient/{st.session_state.editable_profile.get('patient_id', '')}"
                    },
                    "authoredOn": datetime.now().isoformat(),
                    "requester": {
                        "reference": "Practitioner/example",
                        "display": new_med["prescriber"]
                    },
                    "dosageInstruction": [{
                        "text": new_med["dosage"]
                    }]
                }

                with open(med_request_path, "a") as f:
                    f.write(json.dumps(new_entry) + "\n")

                st.success("✅ Medication added successfully!")
                st.rerun()

        for med in active_medications:
            med_id = med["RXnormCode"] or med["Medication"]
            taken_today = med_id in st.session_state.taken_medications and st.session_state.taken_medications[med_id]
            
            # Add a special class if taken today
            extra_class = "taken-medication" if taken_today else ""
            
            st.markdown(f"""
            <div class='medication-item {extra_class}'>
                <b>{med['Medication']}</b><br>
                <i>{med['Dosage']}</i><br>
                <span>Prescribed by: {med['Prescriber']}</span><br>
                <span>Effective Date: {med['Effective Date']}</span><br>
                <span>RXnorm Code: {med['RXnormCode'] or 'N/A'}</span>
                {f"<br><b>✓ Taken today</b>" if taken_today else ""}
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"✏️ Edit: {med['Medication']}"):
                med['Medication'] = st.text_input("Medication Name", value=med["Medication"], key=f"name_{med['RequestID']}")
                med['Dosage'] = st.text_input("Dosage", value=med["Dosage"], key=f"dosage_{med['RequestID']}")
                med['Prescriber'] = st.text_input("Prescriber", value=med["Prescriber"], key=f"doc_{med['RequestID']}")
                new_status = st.selectbox("Status", ["active", "stopped"], index=0 if med["Original"]["status"] == "active" else 1, key=f"status_{med['RequestID']}")
                
                if st.button(f"Save Changes to {med['Medication']}", key=f"save_{med['RequestID']}"):
                    all_requests = load_ndjson(med_request_path)
                    updated_requests = []
                    for entry in all_requests:
                        if entry.get("id") == med["RequestID"]:
                            entry["medicationCodeableConcept"]["text"] = med["Medication"]
                            entry["medicationCodeableConcept"]["coding"][0]["display"] = med["Medication"]
                            entry["medicationCodeableConcept"]["coding"][0]["code"] = med["RXnormCode"]
                            entry["dosageInstruction"][0]["text"] = med["Dosage"]
                            entry["requester"]["display"] = med["Prescriber"]
                            entry["status"] = new_status
                        updated_requests.append(entry)

                    with open(med_request_path, "w") as f:
                        for entry in updated_requests:
                            f.write(json.dumps(entry) + "\n")

                    st.success("✅ Medication updated!")
                    st.rerun()

                if st.button(f"🗑 Delete {med['Medication']} ", key=f"delete_{med['RequestID']}"):
                    all_requests = load_ndjson(med_request_path)
                    updated_requests = []
                    for entry in all_requests:
                        if entry.get("id") == med["RequestID"]:
                            entry["status"] = "stopped"
                        updated_requests.append(entry)

                    with open(med_request_path, "w") as f:
                        for entry in updated_requests:
                            f.write(json.dumps(entry) + "\n")

                    st.warning(f"❌ Marked as Inactive: {med['Medication']}")
                    st.rerun()

            
    with tab2:
        if stopped_medications:
            for med in stopped_medications:
                st.markdown(f"""
                <div class='medication-item'>
                    <b>{med['Medication']}</b><br>
                    <i>{med['Dosage']}</i><br>
                    <span>Prescribed by: {med['Prescriber']}</span><br>
                    <span>Effective Date: {med['Effective Date']}</span><br>
                    <span>RXnorm Code: {med['RXnormCode'] or 'N/A'}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No inactive medications found.")


# Profile
CONDITIONS_PATH = "fhir_data/condition/Condition.ndjson"
IMMUNIZATION_PATH = "fhir_data/immunization/Immunization.ndjson"
ALLERGIES_PATH = "fhir_data/allergy_intolerance/AllergyIntolerance.ndjson"
with profile:
    # Maintain active tab in session state
    tab_labels = ["Personal Information", "Contact Information", "Conditions", "Immunizations", "Allergies"]
    if "active_profile_tab" not in st.session_state:
        st.session_state.active_profile_tab = tab_labels[0]

    # Save logic before tabs
    if st.button("💾 Save Profile"):
        st.session_state.editable_profile = {
            "first_name": st.session_state.get("editable_profile_first_name", ""),
            "last_name": st.session_state.get("editable_profile_last_name", ""),
            "birth_date": st.session_state.get("editable_profile_birth_date", "N/A"),
            "gender": st.session_state.get("editable_profile_gender", "unknown"),
            "race": st.session_state.get("editable_profile_race", ""),
            "ethnicity": st.session_state.get("editable_profile_ethnicity", ""),
            "language": st.session_state.get("editable_profile_language", ""),
            "religion": st.session_state.get("editable_profile_religion", ""),
            "address": st.session_state.get("editable_profile_address", "N/A"),
            "email": st.session_state.get("editable_profile_email", "N/A"),
            "phone": st.session_state.get("editable_profile_phone", "N/A"),
            "patient_id": st.session_state.editable_profile.get("patient_id", "")
        }

        if st.session_state.current_patient:
            updated_patient = update_fhir_patient(st.session_state.current_patient, st.session_state.editable_profile)
            success, message = save_patient_data(updated_patient)

            if success:
                load_patient.clear()  # Clear cache
                st.session_state.current_patient = load_patient(updated_patient["id"])
                st.success("✅ Patient FHIR resource updated successfully.")
                st.rerun()  # Ensure UI reflects update immediately
            else:
                st.error(f"❌ Error saving patient data: {message}")
        else:
            st.error("⚠️ No patient resource found to update.")

    # Tabs for profile sections
    selected_tab_index = tab_labels.index(st.session_state.active_profile_tab)
    tabs = st.tabs(tab_labels)

    # Personal Info
    with tabs[0]:
        st.session_state.active_profile_tab = tab_labels[0]
        st.text_input("First Name", value=st.session_state.editable_profile.get("first_name", ""), key="editable_profile_first_name")
        st.text_input("Last Name", value=st.session_state.editable_profile.get("last_name", ""), key="editable_profile_last_name")
        st.text_input("Date of Birth", value=st.session_state.editable_profile.get("birth_date", ""), key="editable_profile_birth_date")

        gender_options = ["Male", "Female", "Other"]
        current_gender = st.session_state.editable_profile.get("gender", "unknown").capitalize()
        if current_gender not in gender_options:
            current_gender = "Other"
        st.selectbox("Gender", gender_options, index=gender_options.index(current_gender), key="editable_profile_gender")

        st.text_input("Race", value=st.session_state.editable_profile.get("race", ""), key="editable_profile_race")
        st.text_input("Ethnicity", value=st.session_state.editable_profile.get("ethnicity", ""), key="editable_profile_ethnicity")
        st.text_input("Language", value=st.session_state.editable_profile.get("language", ""), key="editable_profile_language")
        st.text_input("Religion", value=st.session_state.editable_profile.get("religion", ""), key="editable_profile_religion")

    # Contact Info
    with tabs[1]:
        st.session_state.active_profile_tab = tab_labels[1]
        st.text_input("Address", value=st.session_state.editable_profile.get("address", ""), key="editable_profile_address")
        st.text_input("Email", value=st.session_state.editable_profile.get("email", ""), key="editable_profile_email")
        st.text_input("Phone Number", value=st.session_state.editable_profile.get("phone", ""), key="editable_profile_phone")

    # Conditions
    with tabs[2]:
        st.session_state.active_profile_tab = tab_labels[2]
        def load_conditions():
            try:
                with open(CONDITIONS_PATH, "r") as f:
                    return [json.loads(line) for line in f if line.strip()]
            except Exception as e:
                print(f"❌ Failed to load conditions: {e}")
                return []

        conditions = load_conditions()
        if conditions:
            for condition in conditions:
                with st.container():
                    st.markdown(
                        """
                        <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                            <h4 style="margin: 0;"> {}</h4>
                            <p><strong>Status:</strong> {}</p>
                            <p><strong>Onset Date:</strong> {}</p>
                        </div>
                        """.format(
                            condition["code"]["text"],
                            condition['clinicalStatus']['coding'][0]['display'],
                            condition.get('onsetDateTime', 'Unknown')
                        ),
                        unsafe_allow_html=True
                    )
        else:
            st.write("No conditions available.")

    # Immunizations
    with tabs[3]:
        st.session_state.active_profile_tab = tab_labels[3]
        def load_immunizations():
            try:
                with open(IMMUNIZATION_PATH, "r") as f:
                    return [json.loads(line) for line in f if line.strip()]
            except Exception as e:
                st.error(f"❌ Failed to load immunizations: {e}")
                return []

        immunizations = load_immunizations()
        if immunizations:
            for immunization in immunizations:
                with st.container():
                    st.markdown(
                        """
                        <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                            <h4 style="margin: 0;"> {}</h4>
                            <p><strong>Date:</strong> {}</p>
                            <p><strong>Location:</strong> {}</p>
                        </div>
                        """.format(
                            immunization["vaccineCode"]["text"],
                            immunization.get('occurrenceDateTime', 'Unknown'),
                            immunization.get('location', {}).get('display', 'Unknown')
                        ),
                        unsafe_allow_html=True
                    )
        else:
            st.write("No immunizations available.")

    # Allergies
    with tabs[4]:
        st.session_state.active_profile_tab = tab_labels[4]
        def load_allergies():
            try:
                with open(ALLERGIES_PATH, "r") as f:
                    return [json.loads(line) for line in f if line.strip()]
            except Exception as e:
                st.error(f"❌ Failed to load allergies: {e}")
                return []

        allergies = load_allergies()
        if allergies:
            for allergy in allergies:
                with st.container():
                    st.markdown(
                        """
                        <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                            <h4 style="margin: 0;"> {}</h4>
                            <p><strong>Category:</strong> {}</p>
                            <p><strong>Reaction:</strong> {}</p>
                        </div> 
                        """.format(
                            allergy["code"]["text"],
                            ", ".join(allergy.get("category", ["Unknown"])),
                            allergy.get("reaction", [{"text": "Unknown"}])[0].get("text", "Unknown")
                        ),
                        unsafe_allow_html=True
                    )
        else:
            st.write("No allergies available.")

# Footer
st.markdown("""<hr style="margin-top: 3rem;">
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        Practicum Project for Georgia Tech CS6440 <br>
        © 2025 Medication Adherence Tracker <br>
        Have questions? <a href='support@medtracker.com '>Contact Us</a><br>
    </div>
""", unsafe_allow_html=True)




# Help
with help:
    help_section() 


import threading
import time
from datetime import datetime
import smtplib
from email.message import EmailMessage
import json

# === Configuration === #
GMAIL_ADDRESS = "cs6440medicationtracker@gmail.com"
GMAIL_APP_PASSWORD = "nobn kuta ecgz dkti"
USER_ACCOUNTS_PATH = "app_data/user_accounts.json"
MED_REQUEST_PATH = "fhir_data/medication_request/MedicationRequest.ndjson"

# === Load user accounts === #
def load_user_accounts():
    try:
        with open(USER_ACCOUNTS_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load user accounts: {e}")
        return []

# === Load active medications === #
def load_active_medications():
    try:
        with open(MED_REQUEST_PATH, "r") as f:
            return [json.loads(line) for line in f if line.strip() and json.loads(line).get("status") == "active"]
    except Exception as e:
        print(f"❌ Failed to load medications: {e}")
        return []

# === Send email === #
def send_email(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Reminder sent to {to_email}")
    except Exception as e:
        print(f"❌ Email error: {e}")

# === Scheduler === #
last_sent_time = None

def reminder_loop():
    global last_sent_time
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        send_times = ["07:00", "14:00", "19:00"]

        if current_time in send_times and current_time != last_sent_time:
            print(f"📧 Sending reminders at {current_time}")
            users = load_user_accounts()
            active_meds = load_active_medications()

            # Load today's medication administrations
            try:
                with open("fhir_data/medication_administration/MedicationAdministration.ndjson", "r") as f:
                    administrations = [json.loads(line) for line in f if line.strip()]
            except:
                administrations = []

            today_str = date.today().isoformat()

            for user in users:
                email = user.get("email")
                patient_id = user.get("patient_id", "")
                username = user.get("username", "")
                first_name = user.get("first_name", "Patient")

                if not email or not patient_id:
                    continue

                # Filter active medications for this user
                user_meds = [
                    m for m in active_meds
                    if patient_id in m.get("subject", {}).get("reference", "")
                ]

                # Determine which medications were not taken today
                unchecked_meds = []
                for med in user_meds:
                    med_code = next(
                        (c.get("code") for c in med.get("medicationCodeableConcept", {}).get("coding", [])),
                        med.get("medicationCodeableConcept", {}).get("text", "")
                    )

                    taken_today = False
                    for admin in administrations:
                        if admin.get("subject", {}).get("reference", "").endswith(patient_id):
                            admin_code = next(
                                (c.get("code") for c in admin.get("medicationCodeableConcept", {}).get("coding", [])),
                                admin.get("medicationCodeableConcept", {}).get("text", "")
                            )
                            if admin_code == med_code and today_str in admin.get("effectiveDateTime", ""):
                                taken_today = True
                                break

                    if not taken_today:
                        unchecked_meds.append(med)

                if not unchecked_meds:
                    continue  # No unchecked meds = no reminder needed

                # Build email body
                med_list = "\n".join([
                    f"- {m.get('medicationCodeableConcept', {}).get('text', 'Unknown')}"
                    for m in unchecked_meds
                ])
                url = f"http://localhost:8501/?auth=true&user={username}"  # Update to match your deployment
                body = f"""Hi {first_name},

💊 This is your medication reminder for today.

The following medications have NOT been logged as taken:

{med_list}

Please log them at:
{url}

Stay healthy!  
– Medication Tracker
"""
                send_email(email, "💊 Medication Reminder – Meds Pending Today", body)

            last_sent_time = current_time

        time.sleep(60)

with st.expander("📧 Test Email Service"):
    test_email = st.session_state.editable_profile.get("email", "")
    
    if st.button("Send Test Email"):
        patient_id = st.session_state.editable_profile.get("patient_id", "")
        first_name = st.session_state.editable_profile.get("first_name", "Patient")

        # Load current user's active medications
        user_meds = [
            m for m in load_active_medications()
            if patient_id in m.get("subject", {}).get("reference", "")
        ]

        # Load medication administrations
        try:
            with open("fhir_data/medication_administration/MedicationAdministration.ndjson", "r") as f:
                administrations = [json.loads(line) for line in f if line.strip()]
        except:
            administrations = []

        today_str = date.today().isoformat()

        # Filter unchecked meds
        unchecked_meds = []
        for med in user_meds:
            med_code = next(
                (c.get("code") for c in med.get("medicationCodeableConcept", {}).get("coding", [])),
                med.get("medicationCodeableConcept", {}).get("text", "")
            )

            taken_today = False
            for admin in administrations:
                if admin.get("subject", {}).get("reference", "").endswith(patient_id):
                    admin_code = next(
                        (c.get("code") for c in admin.get("medicationCodeableConcept", {}).get("coding", [])),
                        admin.get("medicationCodeableConcept", {}).get("text", "")
                    )
                    if admin_code == med_code and today_str in admin.get("effectiveDateTime", ""):
                        taken_today = True
                        break
            if not taken_today:
                unchecked_meds.append(med)

        # Build med list
        if unchecked_meds:
            med_list = "\n".join([
                f"- {m.get('medicationCodeableConcept', {}).get('text', 'Unknown')}"
                for m in unchecked_meds
            ])
        else:
            med_list = "🎉 All medications have been logged today. Great job!"

        # Final body
        test_body = f"""Hi {first_name},

This is a test email from the Medication Tracker app.

🧾 Here’s a preview of the medications NOT logged as taken today:

{med_list}

To update your checklist, visit:
http://localhost:8501/?auth=true&user={st.session_state.username}

✅ If you received this, your email system is working!

– Medication Tracker
"""

        send_email(test_email, "✅ Medication Tracker Test Email", test_body)



# Auto-refresh every 30 minutes
REFRESH_INTERVAL_SECONDS = 1800  # 30 minutes

# Initialize last refresh time
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# Check if it's time to refresh
if time.time() - st.session_state.last_refresh_time > REFRESH_INTERVAL_SECONDS:
    st.session_state.last_refresh_time = time.time()
    st.toast("🔁 Refreshed to keep the app alive!")  # Optional: visual indicator
    st.experimental_rerun()


