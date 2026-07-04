import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
import database as db
import auth
import config

# Page config
st.set_page_config(
    page_title="PANTHER - Registration Tool",
    page_icon="🐆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.init_db()

# Load config from database (NEW)
def load_config():
    """Load configuration from database"""
    config.API_BASE_URL = db.get_config('API_BASE_URL', config.API_BASE_URL)
    config.API_KEY = db.get_config('API_KEY', config.API_KEY)
    config.OTP_SEND_DELAY = int(db.get_config('OTP_SEND_DELAY', config.OTP_SEND_DELAY))

# Load config on startup
load_config()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'tasks' not in st.session_state:
    st.session_state.tasks = {}
if 'task_order' not in st.session_state:
    st.session_state.task_order = []
if 'app_success_count' not in st.session_state:
    st.session_state.app_success_count = {app: 0 for app in config.AVAILABLE_APPS}

# ==================== API FUNCTIONS ====================

def make_api_request(endpoint, method='GET', data=None, params=None):
    """Make API request to Panther backend"""
    url = f"{config.API_BASE_URL}{endpoint}"
    headers = {
        'X-API-Key': config.API_KEY,
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

def get_balance():
    """Get account balance"""
    return make_api_request('/v1/account/balance')

def send_otp(phone, app_name):
    """Send OTP for registration"""
    payload = {'phone': phone, 'app_name': app_name}
    return make_api_request('/v1/register/send_otp', method='POST', data=payload)

def verify_otp(task_id, otp):
    """Verify OTP"""
    payload = {'task_id': task_id, 'otp': otp}
    return make_api_request('/v1/register/verify_otp', method='POST', data=payload)

def cancel_task(task_id):
    """Cancel task"""
    payload = {'task_id': task_id}
    return make_api_request('/v1/register/cancel_task', method='POST', data=payload)

# ==================== LOGIN PAGE ====================

def login_page():
    """Login page"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .logo-icon {
            font-size: 60px;
            text-align: center;
            margin-bottom: 20px;
        }
        .logo-title {
            font-size: 32px;
            font-weight: 800;
            text-align: center;
            color: #1a202c;
            margin-bottom: 10px;
        }
        .logo-subtitle {
            font-size: 14px;
            text-align: center;
            color: #64748b;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="logo-icon">🐆</div>', unsafe_allow_html=True)
        st.markdown('<div class="logo-title">PANTHER</div>', unsafe_allow_html=True)
        st.markdown('<div class="logo-subtitle">Registration Tool</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit:
                if not username or not password:
                    st.error("Username and password required")
                else:
                    user = auth.authenticate_user(username, password)
                    if user:
                        auth.login_user(user)
                        db.log_activity(user['id'], user['username'], 'login', status='success')
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

# ==================== MAIN TOOL PAGE ====================

def main_tool_page():
    """Main tool page"""
    user = auth.get_current_user()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 🐆 PANTHER")
        st.markdown(f"**User:** {user['username']}")
        st.markdown(f"**Role:** {user['role'].upper()}")
        
        # Balance
        if st.button("💰 Check Balance", use_container_width=True):
            with st.spinner("Fetching balance..."):
                result = get_balance()
                if result.get('status') == 'success':
                    st.success(f"Balance: Rs. {result.get('balance')}")
                else:
                    st.error(f"Failed: {result.get('message')}")
        
        st.markdown("---")
        
        # Admin link
        if auth.is_admin():
            if st.button("⚙️ Admin Panel", use_container_width=True):
                st.session_state.page = 'admin'
                st.rerun()
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            db.log_activity(user['id'], user['username'], 'logout')
            auth.logout_user()
            st.rerun()
    
    # Main content
    st.title("🐆 PANTHER Registration Tool")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Done", sum(st.session_state.app_success_count.values()))
    with col2:
        st.metric("Pending Tasks", len(st.session_state.tasks))
    with col3:
        st.metric("Active Apps", len([a for a, c in st.session_state.app_success_count.items() if c > 0]))
    
    # Tabs
    tab1, tab2 = st.tabs(["📱 Multi App", "🎯 Single App + Multi Number"])
    
    with tab1:
        multi_app_mode()
    
    with tab2:
        single_app_multi_number_mode()
    
    # OTP Section
    if st.session_state.tasks:
        st.markdown("---")
        st.subheader("⚡ OTP Verification")
        otp_verification_section()

def multi_app_mode():
    """Multi app mode - one number, multiple apps"""
    st.subheader("📱 Send OTP - Multiple Apps")
    
    # App selection
    st.markdown("**Select Apps (Max 5 due to API limit)**")
    
    selected_apps = []
    cols = st.columns(4)
    
    for i, app in enumerate(config.AVAILABLE_APPS):
        col_idx = i % 4
        with cols[col_idx]:
            if st.checkbox(app, key=f"multi_{app}"):
                selected_apps.append(app)
    
    if len(selected_apps) > 5:
        st.warning("⚠️ Maximum 5 apps allowed due to API rate limit")
        selected_apps = selected_apps[:5]
    
    # Phone number
    phone = st.text_input("Phone Number (10 digits)", max_chars=10, key="phone_multi")
    
    # Send button
    if st.button("🚀 Send All OTPs", type="primary", use_container_width=True):
        if not selected_apps:
            st.warning("Please select at least one app")
        elif not phone or not phone.isdigit() or len(phone) != 10:
            st.warning("Please enter a valid 10-digit phone number")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, app in enumerate(selected_apps):
                status_text.text(f"Sending OTP for {app}...")
                result = send_otp(phone, app)
                
                if result.get('status') == 'success':
                    task_id = result.get('task_id')
                    st.session_state.tasks[task_id] = {
                        'phone': phone,
                        'app_name': app,
                        'created_at': datetime.now(),
                        'status': 'pending'
                    }
                    st.session_state.task_order.append(task_id)
                    db.log_activity(
                        st.session_state.user_id,
                        st.session_state.username,
                        'send_otp',
                        app_name=app,
                        phone=phone,
                        status='pending'
                    )
                else:
                    st.error(f"Failed for {app}: {result.get('message')}")
                
                progress_bar.progress((i + 1) / len(selected_apps))
                time.sleep(config.OTP_SEND_DELAY)
            
            status_text.text("✅ OTP sending completed!")
            st.rerun()

def single_app_multi_number_mode():
    """Single app mode - one app, multiple numbers"""
    st.subheader("🎯 Send OTP - Single App, Multiple Numbers")
    
    # App selection (single)
    st.markdown("**Select ONE App**")
    
    selected_app = None
    cols = st.columns(4)
    
    for i, app in enumerate(config.AVAILABLE_APPS):
        col_idx = i % 4
        with cols[col_idx]:
            if st.radio("", [app], key=f"single_{app}", label_visibility="collapsed"):
                selected_app = app
    
    # Phone numbers
    phones_text = st.text_area(
        "Multiple Phone Numbers (space or comma separated)",
        placeholder="e.g., 8250893769 8293317107 or 8250893769,8293317107",
        height=100,
        key="phones_single"
    )
    
    # Parse phone numbers
    phones = []
    if phones_text:
        phones = [p.strip() for p in phones_text.replace(',', ' ').split() if p.strip()]
    
    # Send button
    if st.button("🚀 Send OTPs to All Numbers", type="primary", use_container_width=True):
        if not selected_app:
            st.warning("Please select one app")
        elif not phones:
            st.warning("Please enter at least one phone number")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, phone in enumerate(phones):
                if not phone.isdigit() or len(phone) != 10:
                    st.error(f"Invalid phone number: {phone}")
                    continue
                
                status_text.text(f"Sending OTP for {phone}...")
                result = send_otp(phone, selected_app)
                
                if result.get('status') == 'success':
                    task_id = result.get('task_id')
                    st.session_state.tasks[task_id] = {
                        'phone': phone,
                        'app_name': selected_app,
                        'created_at': datetime.now(),
                        'status': 'pending'
                    }
                    st.session_state.task_order.append(task_id)
                    db.log_activity(
                        st.session_state.user_id,
                        st.session_state.username,
                        'send_otp',
                        app_name=selected_app,
                        phone=phone,
                        status='pending'
                    )
                else:
                    st.error(f"Failed for {phone}: {result.get('message')}")
                
                progress_bar.progress((i + 1) / len(phones))
                time.sleep(config.OTP_SEND_DELAY)
            
            status_text.text("✅ OTP sending completed!")
            st.rerun()

def otp_verification_section():
    """OTP verification section"""
    
    # Quick submit all OTPs
    st.markdown("### ⚡ Quick Submit All OTPs")
    st.info("💡 Enter one OTP, it will try on all pending apps. Success হলে stop করবে, failed হলে পরের app এ যাবে।")
    
    # Show pending apps
    pending_apps = [st.session_state.tasks[tid]['app_name'] for tid in st.session_state.task_order if tid in st.session_state.tasks]
    if pending_apps:
        st.markdown(f"**Pending Apps:** {', '.join(pending_apps)}")
    
    # Quick OTP input
    quick_otp = st.text_input("Enter OTP (for all pending)", max_chars=4, key="quick_otp")
    
    if st.button("✅ Submit OTP to All", type="primary", use_container_width=True):
        if not quick_otp:
            st.warning("Please enter OTP")
        else:
            for task_id in st.session_state.task_order[:]:
                if task_id not in st.session_state.tasks:
                    continue
                
                task = st.session_state.tasks[task_id]
                if task['status'] != 'pending':
                    continue
                
                result = verify_otp(task_id, quick_otp)
                
                if result.get('status') == 'success':
                    task['status'] = 'completed'
                    app_name = task['app_name']
                    st.session_state.app_success_count[app_name] += 1
                    
                    reg_data = result.get('data', {})
                    db.log_registration(
                        st.session_state.user_id,
                        st.session_state.username,
                        app_name,
                        task['phone'],
                        reg_data.get('password', ''),
                        reg_data.get('device_id', ''),
                        reg_data.get('account_balance', 0),
                        quick_otp
                    )
                    db.log_activity(
                        st.session_state.user_id,
                        st.session_state.username,
                        'verify_otp_success',
                        app_name=app_name,
                        phone=task['phone'],
                        otp=quick_otp,
                        status='success'
                    )
                    
                    st.success(f"✅ {app_name} - {task['phone']} registered successfully!")
                    break  # Stop on first success
                else:
                    st.warning(f"❌ {app_name} failed, trying next...")
            
            st.rerun()
    
    st.markdown("---")
    
    # Individual task verification
    st.markdown("### 📱 Individual Task Verification")
    
    for task_id in st.session_state.task_order[:]:
        if task_id not in st.session_state.tasks:
            continue
        
        task = st.session_state.tasks[task_id]
        
        with st.expander(f"{task['app_name']} - {task['phone']} ({task['status']})", expanded=(task['status'] == 'pending')):
            if task['status'] == 'pending':
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    otp = st.text_input("OTP", max_chars=4, key=f"otp_{task_id}")
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✅ Verify", key=f"verify_{task_id}"):
                        if not otp:
                            st.warning("Please enter OTP")
                        else:
                            result = verify_otp(task_id, otp)
                            
                            if result.get('status') == 'success':
                                task['status'] = 'completed'
                                app_name = task['app_name']
                                st.session_state.app_success_count[app_name] += 1
                                
                                reg_data = result.get('data', {})
                                db.log_registration(
                                    st.session_state.user_id,
                                    st.session_state.username,
                                    app_name,
                                    task['phone'],
                                    reg_data.get('password', ''),
                                    reg_data.get('device_id', ''),
                                    reg_data.get('account_balance', 0),
                                    otp
                                )
                                db.log_activity(
                                    st.session_state.user_id,
                                    st.session_state.username,
                                    'verify_otp_success',
                                    app_name=app_name,
                                    phone=task['phone'],
                                    otp=otp,
                                    status='success'
                                )
                                
                                st.success("✅ Registration successful!")
                                st.json(reg_data)
                                st.rerun()
                            else:
                                st.error(f"❌ Verification failed: {result.get('message')}")
                
                if st.button("❌ Cancel Task", key=f"cancel_{task_id}"):
                    result = cancel_task(task_id)
                    if result.get('status') == 'success':
                        del st.session_state.tasks[task_id]
                        st.session_state.task_order.remove(task_id)
                        st.info("Task cancelled")
                        st.rerun()
                    else:
                        st.error(f"Failed to cancel: {result.get('message')}")
            
            elif task['status'] == 'completed':
                st.success("✅ Completed")

# ==================== ADMIN PAGE ====================

def admin_page():
    """Admin panel"""
    if not auth.is_admin():
        st.error("Access Denied: Admin only")
        return
    
    user = auth.get_current_user()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 🐆 PANTHER ADMIN")
        st.markdown(f"**User:** {user['username']}")
        st.markdown(f"**Role:** ADMIN")
        
        st.markdown("---")
        
        if st.button("🔙 Back to Tool", use_container_width=True):
            st.session_state.page = 'main'
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True):
            db.log_activity(user['id'], user['username'], 'logout')
            auth.logout_user()
            st.rerun()
    
    # Main content
    st.title("⚙️ Admin Panel")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Records", "👥 Users", "📈 Stats", "⚙️ Config"])
    
    with tab1:
        records_tracker()
    
    with tab2:
        user_management()
    
    with tab3:
        statistics()
    
    with tab4:
        configuration()

def records_tracker():
    """Records tracker"""
    st.subheader("📋 Records Tracker")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_from = st.date_input("From", value=datetime.now() - timedelta(days=7))
    
    with col2:
        date_to = st.date_input("To", value=datetime.now())
    
    with col3:
        search = st.text_input("Search", placeholder="App / Phone / Username")
    
    # Quick date buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Today"):
            st.session_state.date_from = datetime.now()
            st.session_state.date_to = datetime.now()
            st.rerun()
    
    with col2:
        if st.button("7 Days"):
            st.session_state.date_from = datetime.now() - timedelta(days=7)
            st.session_state.date_to = datetime.now()
            st.rerun()
    
    with col3:
        if st.button("All"):
            st.session_state.date_from = None
            st.session_state.date_to = None
            st.rerun()
    
    # Get records
    page = st.session_state.get('records_page', 1)
    per_page = 50
    
    result = db.get_records_with_filters(
        date_from=date_from.strftime('%Y-%m-%d') if date_from else None,
        date_to=date_to.strftime('%Y-%m-%d') if date_to else None,
        search=search,
        page=page,
        per_page=per_page
    )
    
    records = result['records']
    total = result['total']
    total_pages = result['total_pages']
    
    # Download button
    if st.button("⬇️ Download CSV", use_container_width=True):
        if records:
            df = pd.DataFrame(records)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Click to Download",
                data=csv,
                file_name="panther_records.csv",
                mime="text/csv"
            )
    
    # Display records
    if records:
        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True)
        
        # Pagination
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Prev") and page > 1:
                st.session_state.records_page = page - 1
                st.rerun()
        
        with col2:
            st.markdown(f"<div style='text-align: center;'>Page <strong>{page}</strong> / <strong>{total_pages}</strong> · Total: <strong>{total}</strong></div>", unsafe_allow_html=True)
        
        with col3:
            if st.button("Next →") and page < total_pages:
                st.session_state.records_page = page + 1
                st.rerun()
    else:
        st.info("No records found")

def user_management():
    """User management"""
    st.subheader("👥 User Management")
    
    # Create user
    st.markdown("### ➕ Create Sub-User")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_username = st.text_input("Username", key="new_username")
    
    with col2:
        new_password = st.text_input("Password", type="password", key="new_password")
    
    if st.button("➕ Create User", type="primary"):
        if not new_username or not new_password:
            st.warning("Username and password required")
        else:
            success, message = db.create_user(new_username, new_password, 'subuser')
            if success:
                db.log_activity(
                    st.session_state.user_id,
                    st.session_state.username,
                    'create_user',
                    details=f'Created user: {new_username}'
                )
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    st.markdown("---")
    
    # User list
    st.markdown("### 👥 All Users")
    
    users = db.get_all_users()
    
    if users:
        for user in users:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{user['username']}**")
                st.caption(f"Role: {user['role']} | Created: {user['created_at']}")
            
            with col2:
                st.markdown(f"<span style='background: {'#fee2e2' if user['role'] == 'admin' else '#dbeafe'}; color: {'#dc2626' if user['role'] == 'admin' else '#1e40af'}; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 700;'>{user['role'].upper()}</span>", unsafe_allow_html=True)
            
            with col3:
                if user['username'] != 'admin':  # Can't delete admin
                    if st.button("🗑️ Delete", key=f"delete_{user['id']}"):
                        db.delete_user(user['id'])
                        db.log_activity(
                            st.session_state.user_id,
                            st.session_state.username,
                            'delete_user',
                            details=f'Deleted user ID: {user["id"]}'
                        )
                        st.rerun()
    else:
        st.info("No users found")

def statistics():
    """Statistics"""
    st.subheader("📈 Statistics")
    
    users = db.get_all_users_stats()
    
    total_users = len(users)
    total_registrations = sum(u['total_registrations'] for u in users)
    today_registrations = sum(u['today_registrations'] for u in users)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", total_users)
    
    with col2:
        st.metric("Total Registrations", total_registrations)
    
    with col3:
        st.metric("Today's Registrations", today_registrations)
    
    st.markdown("---")
    
    # User stats table
    if users:
        df = pd.DataFrame(users)
        st.dataframe(df, use_container_width=True)

def configuration():
    """Configuration - NOW WITH DATABASE STORAGE"""
    st.subheader("⚙️ Configuration")
    
    st.info("💡 এই সেটিংস Database এ সেভ হবে এবং পরের বার অ্যাপ চালু হলে অটোমেটিক লোড হবে।")
    
    # Load current config from database
    current_base_url = db.get_config('API_BASE_URL', config.API_BASE_URL)
    current_api_key = db.get_config('API_KEY', config.API_KEY)
    current_otp_delay = int(db.get_config('OTP_SEND_DELAY', config.OTP_SEND_DELAY))
    
    st.markdown("### 🔧 API Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        base_url = st.text_input("API Base URL", value=current_base_url, key="config_base_url")
    
    with col2:
        api_key = st.text_input("API Key", value=current_api_key, type="password", key="config_api_key")
    
    otp_delay = st.number_input("OTP Send Delay (seconds)", value=current_otp_delay, min_value=0, max_value=10, key="config_otp_delay")
    
    # Show current active config
    st.markdown("---")
    st.markdown("### 📊 Current Active Configuration")
    st.code(f"""
API_BASE_URL: {config.API_BASE_URL}
API_KEY: {config.API_KEY[:20]}...
OTP_SEND_DELAY: {config.OTP_SEND_DELAY} seconds
    """)
    
    if st.button("💾 Save Configuration", type="primary", use_container_width=True):
        if not base_url or not api_key:
            st.warning("Base URL and API Key required")
        else:
            # Save to database
            success = True
            success &= db.set_config('API_BASE_URL', base_url)
            success &= db.set_config('API_KEY', api_key)
            success &= db.set_config('OTP_SEND_DELAY', str(otp_delay))
            
            if success:
                # Update runtime config
                config.API_BASE_URL = base_url
                config.API_KEY = api_key
                config.OTP_SEND_DELAY = otp_delay
                
                db.log_activity(
                    st.session_state.user_id,
                    st.session_state.username,
                    'update_config',
                    details=f'Updated API config: {base_url}'
                )
                
                st.success("✅ Configuration saved successfully! Changes will take effect immediately.")
                st.balloons()
            else:
                st.error("❌ Failed to save configuration")

# ==================== MAIN ====================

def main():
    """Main function"""
    # Initialize session state for page
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    
    # Check if logged in
    if not auth.is_logged_in():
        login_page()
    else:
        if st.session_state.page == 'admin' and auth.is_admin():
            admin_page()
        else:
            main_tool_page()

if __name__ == "__main__":
    main()
