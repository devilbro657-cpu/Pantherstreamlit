import streamlit as st
import requests
import json
import os
from datetime import datetime
import pandas as pd

# ==================== CONFIGURATION ====================
API_BASE_URL = "https://games.accbazaar.shop"
API_KEY = "panthers_ySfegn1vdco_lf9chq_-KbG7YAe0YyZMlAadcQ"  # ⚠️ আপনার API Key দিন
SECRET_KEY = "your-secret-key-here"

# Available Apps
AVAILABLE_APPS = [
    "567slot_game", "mbmbet_game", "yonoslot_game", "Yono_vip",
    "789jackpot_game", "toprummy_game", "Yonogame_game",
    "spincrush_game", "hirummy_game", "indslot_game",
    "maha_game", "Yono777_game", "Yonogame_game",
    "okrummy_game", "Bingo_game", "jaiho777_game"
]

# ==================== DATABASE (Simple JSON) ====================
DB_FILE = "panther_data.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {
        'users': [
            {'id': 1, 'username': 'admin', 'password': 'admin123', 'role': 'admin', 'created_at': str(datetime.now())},
            {'id': 2, 'username': 'user1', 'password': 'user123', 'role': 'subuser', 'created_at': str(datetime.now())}
        ],
        'registrations': [],
        'activity_logs': [],
        'next_user_id': 3,
        'next_reg_id': 1,
        'next_log_id': 1
    }

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init_db():
    data = load_db()
    save_db(data)
    return data

# ==================== API FUNCTIONS ====================
def make_api_request(endpoint, method='GET', data=None, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json; charset=utf-8'
    }
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=15)
        else:
            response = requests.post(url, headers=headers, json=data, params=params, timeout=15)
        return response.json()
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# ==================== AUTH FUNCTIONS ====================
def authenticate_user(username, password, db_data):
    for user in db_data['users']:
        if user['username'] == username and user['password'] == password:
            return user
    return None

def create_user(username, password, role, db_data):
    for user in db_data['users']:
        if user['username'] == username:
            return False, "User already exists"
    
    new_user = {
        'id': db_data['next_user_id'],
        'username': username,
        'password': password,
        'role': role,
        'created_at': str(datetime.now())
    }
    db_data['users'].append(new_user)
    db_data['next_user_id'] += 1
    save_db(db_data)
    return True, "User created successfully"

def delete_user(user_id, db_data):
    db_data['users'] = [u for u in db_data['users'] if u['id'] != user_id]
    save_db(db_data)
    return True

def log_activity(user_id, username, action, db_data, **kwargs):
    log = {
        'id': db_data['next_log_id'],
        'user_id': user_id,
        'username': username,
        'action': action,
        'timestamp': str(datetime.now()),
        'details': kwargs
    }
    db_data['activity_logs'].append(log)
    db_data['next_log_id'] += 1
    save_db(db_data)

def save_registration(user_id, username, app_name, phone, password, device_id, balance, otp, db_data):
    reg = {
        'id': db_data['next_reg_id'],
        'user_id': user_id,
        'username': username,
        'app_name': app_name,
        'phone': phone,
        'password': password,
        'device_id': device_id,
        'balance': balance,
        'otp': otp,
        'created_at': str(datetime.now())
    }
    db_data['registrations'].append(reg)
    db_data['next_reg_id'] += 1
    save_db(db_data)
    return reg

def get_all_users_stats(db_data):
    stats = []
    for user in db_data['users']:
        user_regs = [r for r in db_data['registrations'] if r.get('user_id') == user['id']]
        today = datetime.now().strftime('%Y-%m-%d')
        today_regs = [r for r in user_regs if r.get('created_at', '').startswith(today)]
        
        stats.append({
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'total_registrations': len(user_regs),
            'today_registrations': len(today_regs)
        })
    return stats

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'db_data' not in st.session_state:
    st.session_state.db_data = init_db()
if 'active_tasks' not in st.session_state:
    st.session_state.active_tasks = {}
if 'success_counter' not in st.session_state:
    st.session_state.success_counter = {app: 0 for app in AVAILABLE_APPS}

# ==================== LOGIN PAGE ====================
if not st.session_state.logged_in:
    st.set_page_config(page_title="Panther Tool - Login", page_icon="🐆", layout="centered")
    
    st.markdown("""
    <style>
    .login-box {
        background: linear-gradient(135deg, #1a1f3a 0%, #0d1117 100%);
        padding: 3rem;
        border-radius: 20px;
        border: 1px solid #2a3050;
        max-width: 450px;
        margin: 3rem auto;
        text-align: center;
    }
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-box">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🐆</div>
        <h1 style="margin: 0; color: #ffffff; font-size: 2.5rem;">PANTHER</h1>
        <p style="color: #64748b; margin: 0.5rem 0 2rem 0;">Tool with Admin Panel</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", placeholder="Enter username")
    with col2:
        password = st.text_input("Password", type="password", placeholder="Enter password")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                user = authenticate_user(username, password, st.session_state.db_data)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    log_activity(user['id'], user['username'], 'login', st.session_state.db_data, status='success')
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter username and password")
    
    with col_b:
        if st.button("Clear", use_container_width=True):
            st.rerun()

else:
    # ==================== MAIN APP ====================
    user = st.session_state.user
    db_data = st.session_state.db_data
    
    # Sidebar
    with st.sidebar:
        st.title(f"🐆 Panther Tool")
        st.markdown("---")
        st.write(f"👤 **User:** {user['username']}")
        st.write(f"🔑 **Role:** {user['role'].upper()}")
        st.markdown("---")
        
        if user['role'] == 'admin':
            menu = st.radio(
                "Navigation",
                ["🏠 Dashboard", "👥 User Management", "📊 Admin Panel", "📝 Registration", "💰 Check Balance", "📜 History"],
                index=0
            )
        else:
            menu = st.radio(
                "Navigation",
                ["🏠 Home", "📝 Registration", "💰 Check Balance", "📊 My Registrations"],
                index=0
            )
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True, type="secondary"):
            log_activity(user['id'], user['username'], 'logout', db_data)
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    
    # ==================== DASHBOARD (ADMIN) ====================
    if menu == "🏠 Dashboard" and user['role'] == 'admin':
        st.title("🏠 Admin Dashboard")
        st.markdown("---")
        
        # Statistics
        stats = get_all_users_stats(db_data)
        total_users = len(stats)
        total_regs = sum(s['total_registrations'] for s in stats)
        today_regs = sum(s['today_registrations'] for s in stats)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Users", total_users)
        col2.metric("Total Registrations", total_regs)
        col3.metric("Today's Registrations", today_regs)
        
        st.markdown("---")
        
        # Recent Registrations
        st.subheader("Recent Registrations")
        if db_data['registrations']:
            recent_regs = db_data['registrations'][-10:]
            df = pd.DataFrame(recent_regs)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No registrations yet")
    
    # ==================== USER MANAGEMENT (ADMIN) ====================
    elif menu == "👥 User Management" and user['role'] == 'admin':
        st.title("👥 User Management")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["➕ Create User", "👁️ View Users"])
        
        with tab1:
            st.subheader("Create New User")
            
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username", key="new_username")
                new_password = st.text_input("Password", type="password", key="new_password")
            with col2:
                new_role = st.selectbox("Role", ["subuser", "admin"], key="new_role")
            
            if st.button("Create User", type="primary"):
                if new_username and new_password:
                    success, message = create_user(new_username, new_password, new_role, db_data)
                    if success:
                        log_activity(user['id'], user['username'], 'create_user', db_data, details=f'Created user: {new_username}')
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill all fields")
        
        with tab2:
            st.subheader("All Users")
            if db_data['users']:
                users_df = pd.DataFrame(db_data['users'])
                st.dataframe(users_df, use_container_width=True)
                
                st.markdown("---")
                st.subheader("Delete User")
                users_to_delete = [u for u in db_data['users'] if u['username'] != 'admin']
                if users_to_delete:
                    user_to_delete = st.selectbox(
                        "Select User to Delete",
                        [f"{u['username']} (ID: {u['id']})" for u in users_to_delete]
                    )
                    if st.button("Delete User", type="danger"):
                        if user_to_delete:
                            uid = int(user_to_delete.split("(ID: ")[1].replace(")", ""))
                            delete_user(uid, db_data)
                            log_activity(user['id'], user['username'], 'delete_user', db_data, details=f'Deleted user ID: {uid}')
                            st.success("User deleted successfully")
                            st.rerun()
    
    # ==================== ADMIN PANEL (ADMIN) ====================
    elif menu == "📊 Admin Panel" and user['role'] == 'admin':
        st.title("📊 Admin Panel")
        st.markdown("---")
        
        # Statistics
        stats = get_all_users_stats(db_data)
        total_users = len(stats)
        total_regs = sum(s['total_registrations'] for s in stats)
        today_regs = sum(s['today_registrations'] for s in stats)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Users", total_users)
        col2.metric("Total Registrations", total_regs)
        col3.metric("Today's Registrations", today_regs)
        
        st.markdown("---")
        
        # Activity Logs
        st.subheader("Activity Logs")
        if db_data['activity_logs']:
            logs_df = pd.DataFrame(db_data['activity_logs'][-50:])
            st.dataframe(logs_df, use_container_width=True)
        else:
            st.info("No activity logs yet")
    
    # ==================== REGISTRATION (ALL USERS) ====================
    elif menu in ["📝 Registration", "📝 Registration"]:
        st.title("📝 Account Registration")
        st.markdown("---")
        
        # Available apps
        selected_app = st.selectbox("Select App", AVAILABLE_APPS)
        
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Phone Number", placeholder="+8801XXXXXXXXX")
            password = st.text_input("Password", type="password")
        with col2:
            otp = st.text_input("OTP Code", placeholder="Enter OTP")
            device_id = st.text_input("Device ID (Optional)", placeholder="Enter device ID")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Send OTP", type="primary", use_container_width=True):
                if phone and selected_app:
                    with st.spinner("Sending OTP..."):
                        result = make_api_request('/v1/account/send_otp', method='POST', data={
                            'app_name': selected_app,
                            'phone': phone
                        })
                        if result.get('status') == 'success':
                            st.success("OTP sent successfully!")
                            log_activity(user['id'], user['username'], 'send_otp', db_data,
                                       app_name=selected_app, phone=phone, status='success')
                        else:
                            st.error(f"Error: {result.get('message', 'Unknown error')}")
                            log_activity(user['id'], user['username'], 'send_otp', db_data,
                                       app_name=selected_app, phone=phone, status='failed')
                else:
                    st.warning("Please enter phone number and select app")
        
        with col2:
            if st.button("✅ Register", type="primary", use_container_width=True):
                if phone and password and otp:
                    with st.spinner("Registering..."):
                        result = make_api_request('/v1/account/register', method='POST', data={
                            'app_name': selected_app,
                            'phone': phone,
                            'password': password,
                            'otp': otp,
                            'device_id': device_id
                        })
                        
                        if result.get('status') == 'success':
                            st.success("Registration successful!")
                            data = result.get('data', {})
                            st.json(data)
                            
                            # Save to database
                            save_registration(
                                user['id'], user['username'],
                                selected_app, phone, password, device_id,
                                data.get('account_balance', 0),
                                otp,
                                db_data
                            )
                            
                            log_activity(user['id'], user['username'], 'register', db_data,
                                       app_name=selected_app, phone=phone, status='success')
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('message', 'Unknown error')}")
                            log_activity(user['id'], user['username'], 'register', db_data,
                                       app_name=selected_app, phone=phone, status='failed')
                else:
                    st.warning("Please fill all required fields")
    
    # ==================== CHECK BALANCE ====================
    elif menu == "💰 Check Balance":
        st.title("💰 Check Account Balance")
        st.markdown("---")
        
        selected_app = st.selectbox("Select App", AVAILABLE_APPS, key="balance_app")
        phone = st.text_input("Phone Number", placeholder="+8801XXXXXXXXX", key="balance_phone")
        
        if st.button("🔍 Check Balance", type="primary"):
            if phone and selected_app:
                with st.spinner("Checking balance..."):
                    result = make_api_request('/v1/account/balance', params={
                        'app_name': selected_app,
                        'phone': phone
                    })
                    if result.get('status') == 'success':
                        st.metric("Account Balance", f"Rs. {result.get('data', {}).get('balance', 'N/A')}")
                        st.success("Balance retrieved successfully")
                    else:
                        st.error(f"Error: {result.get('message', 'Unknown error')}")
            else:
                st.warning("Please enter phone number and select app")
    
    # ==================== HISTORY / MY REGISTRATIONS ====================
    elif menu in ["📜 History", "📊 My Registrations"]:
        st.title("📜 Registration History")
        st.markdown("---")
        
        if user['role'] == 'admin':
            # Admin sees all registrations
            limit = st.slider("Number of records", 10, 200, 50)
            regs = db_data['registrations'][-limit:]
        else:
            # Subuser sees only their registrations
            st.write(f"Showing your registrations only")
            regs = [r for r in db_data['registrations'] if r.get('user_id') == user['id']]
        
        if regs:
            df = pd.DataFrame(regs)
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"registrations_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No registrations found")
    
    # ==================== HOME (SUBUSER) ====================
    elif menu == "🏠 Home":
        st.title(" Welcome to Panther Tool")
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
