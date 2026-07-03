import streamlit as st
import requests
import os
from datetime import datetime

# ==================== CONFIGURATION ====================
API_BASE_URL = st.secrets.get("API_BASE_URL", "https://games.accbazaar.shop")
API_KEY = st.secrets.get("API_KEY", "your-api-key")

# ==================== HELPER FUNCTIONS ====================

def make_api_request(endpoint, method='GET', data=None, params=None):
    """Make API request to Panther backend"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=10)
        else:
            response = requests.post(url, headers=headers, json=data, params=params, timeout=10)
        return response.json()
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def send_otp(app_name, phone):
    """Send OTP for registration"""
    return make_api_request('/v1/account/send_otp', method='POST', data={
        'app_name': app_name,
        'phone': phone
    })


def register_account(app_name, phone, password, otp, device_id=''):
    """Complete registration"""
    return make_api_request('/v1/account/register', method='POST', data={
        'app_name': app_name,
        'phone': phone,
        'password': password,
        'otp': otp,
        'device_id': device_id
    })


def get_balance(app_name, phone):
    """Get account balance"""
    return make_api_request('/v1/account/balance', params={
        'app_name': app_name,
        'phone': phone
    })


def get_registrations(limit=10):
    """Get recent registrations"""
    return make_api_request('/v1/account/registrations', params={'limit': limit})


# ==================== SESSION STATE ====================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'role' not in st.session_state:
    st.session_state.role = ''

# ==================== AUTHENTICATION ====================

def login(username, password):
    """Simple login (replace with your auth logic)"""
    # For demo - replace with actual authentication
    if username == "admin" and password == "admin123":
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = 'admin'
        return True
    elif username and password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = 'user'
        return True
    return False


def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.role = ''

# ==================== LOGIN PAGE ====================

if not st.session_state.logged_in:
    st.set_page_config(page_title="Login - Panther Tool", page_icon="🔐")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔐 Panther Tool Login")
        st.markdown("---")
        
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("Login", type="primary", use_container_width=True):
                if login(username, password):
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        with col_b:
            if st.button("Clear", use_container_width=True):
                st.rerun()

else:
    # ==================== MAIN APP ====================
    st.set_page_config(page_title="Panther Tool", page_icon="🐆", layout="wide")
    
    # Sidebar
    with st.sidebar:
        st.title(f"🐆 Panther Tool")
        st.markdown(f"**Welcome:** {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.role}")
        st.markdown("---")
        
        menu = st.radio(
            "Navigation",
            ["🏠 Home", "📝 Registration", "💰 Check Balance", "📊 Recent Registrations"]
        )
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # ==================== HOME PAGE ====================
    
    if menu == "🏠 Home":
        st.title("🐆 Welcome to Panther Tool")
        st.markdown("### Features:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Feature 1", "Quick Registration")
            st.info("✅ OTP-based verification")
        
        with col2:
            st.metric("Feature 2", "Balance Check")
            st.info("✅ Real-time balance")
        
        with col3:
            st.metric("Feature 3", "Activity Tracking")
            st.info("✅ Complete logs")
        
        st.markdown("---")
        st.markdown("### How to Use:")
        st.markdown("""
        1. **Registration** - Create new accounts with OTP verification
        2. **Check Balance** - View account balance anytime
        3. **Recent Registrations** - View your registration history
        """)
    
    # ==================== REGISTRATION PAGE ====================
    
    elif menu == "📝 Registration":
        st.title("📝 Account Registration")
        
        # Available apps (update with actual apps)
        available_apps = ["app1", "app2", "app3"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            app_name = st.selectbox("Select App", available_apps)
            phone = st.text_input("Phone Number", placeholder="+8801XXXXXXXXX")
        
        with col2:
            password = st.text_input("Password", type="password")
            otp = st.text_input("OTP Code", placeholder="Enter OTP received")
        
        device_id = st.text_input("Device ID (Optional)", placeholder="Enter device ID")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Send OTP", type="primary", use_container_width=True):
                if phone and app_name:
                    with st.spinner("Sending OTP..."):
                        result = send_otp(app_name, phone)
                        if result.get('status') == 'success':
                            st.success("✅ OTP sent successfully!")
                            st.info("Check your phone for OTP")
                        else:
                            st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
                else:
                    st.warning("⚠️ Please enter phone number and select app")
        
        with col2:
            if st.button("✅ Register", type="primary", use_container_width=True):
                if phone and password and otp:
                    with st.spinner("Registering account..."):
                        result = register_account(app_name, phone, password, otp, device_id)
                        if result.get('status') == 'success':
                            st.success("✅ Registration successful!")
                            st.json(result.get('data', {}))
                        else:
                            st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
                else:
                    st.warning("⚠️ Please fill all required fields")
    
    # ==================== BALANCE CHECK PAGE ====================
    
    elif menu == "💰 Check Balance":
        st.title("💰 Check Account Balance")
        
        available_apps = ["app1", "app2", "app3"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            app_name = st.selectbox("Select App", available_apps, key="balance_app")
            phone = st.text_input("Phone Number", placeholder="+8801XXXXXXXXX", key="balance_phone")
        
        if st.button("🔍 Check Balance", type="primary", use_container_width=True):
            if phone and app_name:
                with st.spinner("Checking balance..."):
                    result = get_balance(app_name, phone)
                    if result.get('status') == 'success':
                        balance = result.get('data', {}).get('balance', 'N/A')
                        st.metric("Account Balance", f"{balance}")
                        st.success("✅ Balance retrieved successfully")
                    else:
                        st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
            else:
                st.warning("⚠️ Please enter phone number and select app")
    
    # ==================== RECENT REGISTRATIONS PAGE ====================
    
    elif menu == "📊 Recent Registrations":
        st.title("📊 Recent Registrations")
        
        limit = st.slider("Number of records", min_value=10, max_value=100, value=10)
        
        if st.button("🔄 Load Data", type="primary", use_container_width=True):
            with st.spinner("Loading registrations..."):
                result = get_registrations(limit)
                if result.get('status') == 'success':
                    registrations = result.get('data', [])
                    if registrations:
                        st.dataframe(registrations, use_container_width=True)
                        
                        # Download option
                        csv_data = []
                        for reg in registrations:
                            csv_data.append({
                                'Phone': reg.get('phone', ''),
                                'App': reg.get('app_name', ''),
                                'Date': reg.get('created_at', ''),
                                'Status': reg.get('status', '')
                            })
                        
                        import pandas as pd
                        df = pd.DataFrame(csv_data)
                        csv = df.to_csv(index=False)
                        
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"registrations_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("ℹ️ No registrations found")
                else:
                    st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
    
    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit")
