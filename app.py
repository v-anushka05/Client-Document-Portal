import streamlit as st
import os
import pandas as pd
from datetime import datetime
import re
import requests
from streamlit_lottie import st_lottie

# ==================== CONFIGURATION ====================
DATA_FILE = "upload_status.csv"
UPLOAD_DIR = "uploads"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
LOGO_PATH = "logo.png"  # Put your logo file here or leave blank
# ========================================================

# Create folders and CSV if not exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["client_name", "file_name", "upload_time", "status"])
    df.to_csv(DATA_FILE, index=False)
else:
    df = pd.read_csv(DATA_FILE)

# Function to load lottie animation from URL
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Lottie animation URL (free)
lottie_url = "https://assets6.lottiefiles.com/packages/lf20_jcikwtux.json"
lottie_animation = load_lottieurl(lottie_url)

# Utility functions
def sanitize_filename(name):
    name = name.strip()
    name = re.sub(r'[^\w\-_\. ]', '_', name)
    return name

def save_upload(client_name, uploaded_file):
    safe_client_name = sanitize_filename(client_name)
    client_folder = os.path.join(UPLOAD_DIR, safe_client_name)
    os.makedirs(client_folder, exist_ok=True)
    file_path = os.path.join(client_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    global df
    new_entry = {
        "client_name": client_name.strip(),
        "file_name": uploaded_file.name,
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Received"
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def client_mode():
    st.markdown("<h2 style='color:#4CAF50;'>📤 Client Document Upload Portal</h2>", unsafe_allow_html=True)
    client_name = st.text_input("Enter Your Full Name")
    uploaded_file = st.file_uploader("Select File to Upload (PDF, DOCX, XLSX, etc.)")

    if st.button("Upload File"):
        if not client_name or not uploaded_file:
            st.error("Please provide your name and upload a file.")
        else:
            save_upload(client_name, uploaded_file)
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    if client_name:
        st.markdown("### 📄 Your Uploaded Files")
        client_files = df[df["client_name"].str.lower().str.strip() == client_name.lower().strip()]
        if client_files.empty:
            st.info("No files found for this name yet.")
        else:
            st.table(client_files[["file_name", "upload_time", "status"]])

def admin_login():
    st.markdown("<h2 style='color:#FF5722;'>🔐 Admin Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state["admin_authenticated"] = True
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

def admin_panel():
    st.markdown("<h2 style='color:#2196F3;'>👨‍💼 Admin Dashboard</h2>", unsafe_allow_html=True)
    global df
    if df.empty:
        st.info("No uploads available.")
        return

    st.subheader("All Uploaded Files")
    st.dataframe(df, use_container_width=True)
    st.markdown("---")
    st.subheader("Update File Status")
    clients = df['client_name'].unique()
    selected_client = st.selectbox("Select Client", clients)
    client_files = df[df['client_name'] == selected_client]['file_name'].tolist()
    selected_file = st.selectbox("Select File", client_files)
    new_status = st.selectbox("New Status", ["Received", "In Review", "Completed", "Rejected"])
    if st.button("Update Status"):
        df.loc[(df['client_name'] == selected_client) & (df['file_name'] == selected_file), 'status'] = new_status
        df.to_csv(DATA_FILE, index=False)
        st.success("Status updated successfully!")

# ========== PAGE SETUP ==========
st.set_page_config(page_title="Client Document Portal", page_icon="📁", layout="wide")

# Top Hero Section
col1, col2 = st.columns([1, 3])

with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
    else:
        st.markdown("<h3 style='color:#777;'>Your Logo Here</h3>", unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style="background-color:#0f4c75;padding:20px;border-radius:10px">
        <h1 style="color:white;text-align:center;">Client Document Management System</h1>
        <p style="color:white;text-align:center;">Secure File Upload & Admin Review Portal</p>
        </div>
        """, unsafe_allow_html=True)

# Lottie animation below banner
if lottie_animation:
    st_lottie(lottie_animation, speed=1, width=600, height=300, key="client_upload_animation")
else:
    st.warning("Lottie animation failed to load.")

# App Navigation
menu = st.sidebar.radio("Navigation", ["Client Upload", "Admin Login", "Admin Panel"])

if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if menu == "Client Upload":
    client_mode()
elif menu == "Admin Login":
    if not st.session_state["admin_authenticated"]:
        admin_login()
    else:
        st.success("You are already logged in!")
elif menu == "Admin Panel":
    if st.session_state["admin_authenticated"]:
        admin_panel()
    else:
        st.warning("Please login first via Admin Login.")
