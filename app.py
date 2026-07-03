import streamlit as st
import requests
import os
from datetime import datetime
import json

# ==================== CONFIGURATION ====================
API_BASE_URL = "https://games.accbazaar.shop"
API_KEY = "আপনার-API-KEY-এখানে-লিখুন"  # ⚠️ আপনার API Key দিন
FLASK_SECRET_KEY = "your-secret-key"

# ==================== DATABASE FUNCTIONS ====================
# Streamlit session state দিয়ে database simulate করব

def init_db():
    """Initialize database tables in session state"""
    if 'users' not in st.session_state:
        st.session_state.users = [
            {'id': 1, 'username': 'admin', 'password': 'admin123', 'role': 'admin', 'created_at': datetime.now().isoformat()},
            {'id': 2, 'username': 'user1', 'password': 'user123', 'role': 'subuser', 'created_at': datetime.now().isoformat()}
        ]
    
    if 'registrations' not in st.session_state:
        st.session_state.registrations = []
    
    if 'activity_logs' not in st.session_state:
        st.session_state.activity_logs = []

def get_user_by_username(username):
    """Get user by username"""
    for user in st.session_state.users:
        if user['username'] == username:
            return user
    return None

def authenticate_user(username, password):
    """Authenticate user"""
    user = get_user_by_username(username)
    if user and user['password'] == password:
        return user
    return None

def log_activity(user_id, username, action, **kwargs):
    """Log activity"""
    log = {
        'id': len(st.session_state.activity_logs) + 1,
        'user_id': user_id,
        'username': username,
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'details': kwargs
    }
    st.session_state.activity_logs.append(log)

def get_all_users():
    """Get all users"""
    return st.session_state.users

def create_user(username, password, role='subuser'):
    """Create new user"""
    # Check if user exists
    if get_user_by_username(username):
        return False, "User already exists"
    
    new_id = len(st.session_state.users) + 1
    new_user = {
        'id': new_id,
        'username': username,
        'password': password,
        'role': role,
        'created_at': datetime.now().isoformat()
    }
    st.session_state.users.append(new_user)
    return True, "User created successfully"

def delete_user(user_id):
    """Delete user"""
    st.session_state.users = [u for u in st.session_state.users if u['id'] != user_id]
    return True

def get_all_users_stats():
    """Get user statistics"""
    stats = []
    for user in st.session_state.users:
        user_regs = [r for r in st.session_state.registrations if r.get('user_id') == user['id']]
        today = datetime.now().date().isoformat()
        today_regs = [r for r in user_regs if r.get('created_at', '').startswith(today)]
        
        stats.append({
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'total_registrations': len(user_regs),
            'today_registrations': len(today_regs)
        })
    return stats

def save_registration(user_id, username, app_name, phone, password, device_id, balance, otp):
    """Save registration"""
    reg = {
        'id': len(st.session_state.registrations) + 1,
        'user_id': user_id,
        'username': username,
        'app_name': app_name,
        'phone': phone,
        'device_id': device_id,
        'balance': balance,
        'otp': otp,
        'created_at': datetime.now().isoformat()
    }
    st.session_state.registrations.append(reg)
    return True

def get_registrations(user_id=None, limit=100):
    """Get registrations"""
    regs = st.session_state.registrations
    if user_id:
        regs = [r for r in regs if r.get('user_id') == user_id]
    return regs[-limit:]

def get_activity_logs(user_id=None, limit=100):
    """Get activity logs"""
    logs = st.session_state.activity_logs
    if user_id:
        logs = [l for l in logs if l.get('user_id') == user_id]
    return logs[-limit:]

# ==================== API FUNCTIONS ====================

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

# ==================== SESSION STATE ====================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'role' not in st.session_state:
    st.session_state.role = ''
if 'success_counter' not in st.session_state:
    st.session_state.success_counter = {}

# Initialize database
init_db()

# ==================== AUTHENTICATION ====================

def login_user(username, password):
    """Login user"""
    user = authenticate_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user_id = user['id']
        st.session_state.username = user['username']
        st.session_state.role = user['role']
        log_activity(user['id'], user['username'], 'login', status='success')
        return True
    return False

def logout_user():
    """Logout user"""
    if st.session_state.user_id:
        log_activity(st.session_state.user_id, st.session_state.username, 'logout')
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ''
    st.session_state.role = ''

# ==================== LOGIN PAGE ====================

if not st.session_state.logged_in:
    st.set_page_config(page_title="Login - Panther Tool", page_icon="🔐", layout="centered")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔐 Panther Tool Login")
        st.markdown("---")
        
        username = st.text_input("Username", placeholder="Enter username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("Login", type="primary", use_container_width=True):
                if login_user(username, password):
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        with col_b:
            if st.button("Clear", use_container_width=True):
                st.rerun()

else:
    # ==================== MAIN APP ====================
    st.set_page_config(page_title="Panther Tool", page_icon="🐆", layout="wide")
    
    # Sidebar
    with st.sidebar:
        st.title(f"🐆 Panther Tool")
        st.markdown(f"**👤 User:** {st.session_state.username}")
        st.markdown(f"**🔑 Role:** {st.session_state.role}")
        st.markdown("---")
        
        if st.session_state.role == 'admin':
            menu = st.radio(
                "Navigation",
                ["🏠 Home", " User Management", " Admin Panel", " Registration", " Check Balance", "📈 Activity Logs"]
            )
        else:
            menu = st.radio(
                "Navigation",
                ["🏠 Home", "📝 Registration", "💰 Check Balance", "📊 My Registrations"]
            )
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True, type="secondary"):
            logout_user()
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
        3. **Activity Logs** - Track all activities
        """)
    
    # ==================== USER MANAGEMENT (ADMIN ONLY) ====================
    
    elif menu == "👥 User Management":
        if st.session_state.role != 'admin':
            st.error("Access denied. Admin only.")
            st.stop()
        
        st.title("👥 User Management")
        
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
                    success, message = create_user(new_username, new_password, new_role)
                    if success:
                        st.success(f"✅ {message}")
                        log_activity(st.session_state.user_id, st.session_state.username, 
                                  'create_user', details=f'Created user: {new_username}')
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please fill all fields")
        
        with tab2:
            st.subheader("All Users")
            
            users = get_all_users()
            if users:
                users_df = []
                for user in users:
                    users_df.append({
                        'ID': user['id'],
                        'Username': user['username'],
                        'Role': user['role'],
                        'Created': user.get('created_at', 'N/A')[:10]
                    })
                
                st.dataframe(users_df, use_container_width=True)
                
                # Delete user
                st.markdown("---")
                st.subheader("Delete User")
                
                user_to_delete = st.selectbox("Select User to Delete", 
                                            [f"{u['username']} (ID: {u['id']})" for u in users if u['username'] != 'admin'])
                
                if st.button("Delete User", type="danger"):
                    if user_to_delete:
                        user_id = int(user_to_delete.split("(ID: ")[1].replace(")", ""))
                        delete_user(user_id)
                        st.success("✅ User deleted successfully")
                        log_activity(st.session_state.user_id, st.session_state.username, 
                                  'delete_user', details=f'Deleted user ID: {user_id}')
                        st.rerun()
    
    # ==================== ADMIN PANEL ====================
    
    elif menu == "📊 Admin Panel":
        if st.session_state.role != 'admin':
            st.error("Access denied. Admin only.")
            st.stop()
        
        st.title("📊 Admin Panel")
        
        # Statistics
        st.subheader("Statistics")
        
        stats = get_all_users_stats()
        total_users = len(stats)
        total_regs = sum(s['total_registrations'] for s in stats)
        today_regs = sum(s['today_registrations'] for s in stats)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", total_users)
        
        with col2:
            st.metric("Total Registrations", total_regs)
        
        with col3:
            st.metric("Today's Registrations", today_regs)
        
        st.markdown("---")
        
        # Recent Registrations
        st.subheader("Recent Registrations")
        
        all_regs = get_registrations(limit=50)
        if all_regs:
            regs_df = []
            for reg in all_regs:
                regs_df.append({
                    'ID': reg['id'],
                    'User': reg.get('username', 'N/A'),
                    'App': reg.get('app_name', 'N/A'),
                    'Phone': reg.get('phone', 'N/A'),
                    'Balance': reg.get('balance', 'N/A'),
                    'Date': reg.get('created_at', 'N/A')[:16]
                })
            
            st.dataframe(regs_df, use_container_width=True)
        else:
            st.info("No registrations yet")
        
        st.markdown("---")
        
        # Activity Logs
        st.subheader("Recent Activity Logs")
        
        all_logs = get_activity_logs(limit=50)
        if all_logs:
            logs_df = []
            for log in all_logs:
                logs_df.append({
                    'Time': log.get('timestamp', 'N/A')[:16],
                    'User': log.get('username', 'N/A'),
                    'Action': log.get('action', 'N/A'),
                    'Details': str(log.get('details', {}))
                })
            
            st.dataframe(logs_df, use_container_width=True)
        else:
            st.info("No activity logs yet")
    
    # ==================== REGISTRATION ====================
    
    elif menu == "📝 Registration":
        st.title("📝 Account Registration")
        
        # Available apps (update with actual apps from config)
        available_apps = ["app1", "app2", "app3"]  # Replace with config.AVAILABLE_APPS
        
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
                        result = make_api_request('/v1/account/send_otp', method='POST', data={
                            'app_name': app_name,
                            'phone': phone
                        })
                        if result.get('status') == 'success':
                            st.success("✅ OTP sent successfully!")
                            st.info("Check your phone for OTP")
                            log_activity(st.session_state.user_id, st.session_state.username, 
                                       'send_otp', app_name=app_name, phone=phone, status='success')
                        else:
                            st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
                            log_activity(st.session_state.user_id, st.session_state.username, 
                                       'send_otp', app_name=app_name, phone=phone, status='failed')
                else:
                    st.warning("⚠️ Please enter phone number and select app")
        
        with col2:
            if st.button("✅ Register", type="primary", use_container_width=True):
                if phone and password and otp:
                    with st.spinner("Registering account..."):
                        result = make_api_request('/v1/account/register', method='POST', data={
                            'app_name': app_name,
                            'phone': phone,
                            'password': password,
                            'otp': otp,
                            'device_id': device_id
                        })
                        
                        if result.get('status') == 'success':
                            st.success("✅ Registration successful!")
                            st.json(result.get('data', {}))
                            
                            # Save to database
                            balance = result.get('data', {}).get('account_balance', 0)
                            save_registration(st.session_state.user_id, st.session_state.username,
                                            app_name, phone, password, device_id, balance, otp)
                            
                            log_activity(st.session_state.user_id, st.session_state.username, 
                                       'register', app_name=app_name, phone=phone, status='success')
                        else:
                            st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
                            log_activity(st.session_state.user_id, st.session_state.username, 
                                       'register', app_name=app_name, phone=phone, status='failed')
                else:
                    st.warning("⚠️ Please fill all required fields")
    
    # ==================== CHECK BALANCE ====================
    
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
                    result = make_api_request('/v1/account/balance', params={
                        'app_name': app_name,
                        'phone': phone
                    })
                    if result.get('status') == 'success':
                        balance = result.get('data', {}).get('balance', 'N/A')
                        st.metric("Account Balance", f"{balance}")
                        st.success("✅ Balance retrieved successfully")
                    else:
                        st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
            else:
                st.warning("⚠️ Please enter phone number and select app")
    
    # ==================== MY REGISTRATIONS ====================
    
    elif menu == "📊 My Registrations":
        st.title("📊 My Registrations")
        
        limit = st.slider("Number of records", min_value=10, max_value=100, value=10)
        
        if st.button("🔄 Load Data", type="primary", use_container_width=True):
            regs = get_registrations(user_id=st.session_state.user_id, limit=limit)
            if regs:
                regs_df = []
                for reg in regs:
                    regs_df.append({
                        'ID': reg['id'],
                        'App': reg.get('app_name', 'N/A'),
                        'Phone': reg.get('phone', 'N/A'),
                        'Balance': reg.get('balance', 'N/A'),
                        'Date': reg.get('created_at', 'N/A')[:16]
                    })
                
                st.dataframe(regs_df, use_container_width=True)
                
                # Download as CSV
                import pandas as pd
                df = pd.DataFrame(regs_df)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"my_registrations_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ No registrations found")
    
    # ==================== ACTIVITY LOGS (ADMIN ONLY) ====================
    
    elif menu == "📈 Activity Logs":
        if st.session_state.role != 'admin':
            st.error("Access denied. Admin only.")
            st.stop()
        
        st.title("📈 Activity Logs")
        
        limit = st.slider("Number of logs", min_value=10, max_value=200, value=50)
        
        if st.button("🔄 Load Logs", type="primary", use_container_width=True):
            logs = get_activity_logs(limit=limit)
            if logs:
                logs_df = []
                for log in logs:
                    logs_df.append({
                        'Time': log.get('timestamp', 'N/A'),
                        'User': log.get('username', 'N/A'),
                        'Action': log.get('action', 'N/A'),
                        'Details': str(log.get('details', {}))
                    })
                
                st.dataframe(logs_df, use_container_width=True)
            else:
                st.info("No activity logs found")
    
    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit")
