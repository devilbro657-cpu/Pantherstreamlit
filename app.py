import streamlit as st
import requests
import time
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# ==================== CONFIGURATION ====================
DB_PATH = "panther.db"

# Default API Config
DEFAULT_API_BASE_URL = "https://games.accbazaar.shop"
DEFAULT_API_KEY = "panthers_V3vGXVJFfnia6o-FHwPoad4odaPbBbcAa8wIlw"

AVAILABLE_APPS = [
    "567slot_game", "Yono_vip", "mbmbet_game", "yonoslot_game",
    "789jackpot_game", "okrummy_game", "Yono777_game", "toprummy_game",
    "Yonogame_game", "spincrush_game", "hirummy_game", "indslot_game",
    "maha_game", "Spin777_game", "Hindi777_game", "Bingo_game",
    "jaiho777_game", "jaiho91_game", "Rummyludo_game", "Shareslots_game",
    "SpinLucky_game"
]

APP_PRICES = {app: 3.0 for app in AVAILABLE_APPS}

# ==================== DATABASE FUNCTIONS ====================
def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Config table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    # Registrations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT,
            device_id TEXT,
            account_balance REAL DEFAULT 0,
            otp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default config
    cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', 
                   ('API_BASE_URL', DEFAULT_API_BASE_URL))
    cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', 
                   ('API_KEY', DEFAULT_API_KEY))
    cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', 
                   ('OTP_SEND_DELAY', '2'))
    
    conn.commit()
    conn.close()

def get_config(key, default=None):
    """Get config from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default
    except:
        return default

def set_config(key, value):
    """Set config in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO config (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = ?
        ''', (key, value, value))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def log_registration(app_name, phone, password, device_id, balance, otp):
    """Log registration"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO registrations 
            (app_name, phone, password, device_id, account_balance, otp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (app_name, phone, password, device_id, balance, otp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging: {e}")

def get_registrations(limit=100):
    """Get recent registrations"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM registrations 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        records = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return [dict(zip(columns, row)) for row in records]
    except:
        return []

# ==================== API FUNCTIONS ====================
def make_api_request(endpoint, method='GET', data=None, params=None):
    """Make API request"""
    base_url = get_config('API_BASE_URL', DEFAULT_API_BASE_URL)
    api_key = get_config('API_KEY', DEFAULT_API_KEY)
    
    url = f"{base_url}{endpoint}"
    headers = {
        'X-API-Key': api_key,
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
    """Send OTP"""
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

# ==================== STREAMLIT APP ====================
def main():
    st.set_page_config(
        page_title="PANTHER - Registration Tool",
        page_icon="🐆",
        layout="wide"
    )
    
    # Initialize database
    init_db()
    
    # Initialize session state
    if 'tasks' not in st.session_state:
        st.session_state.tasks = {}
    if 'task_order' not in st.session_state:
        st.session_state.task_order = []
    if 'app_success_count' not in st.session_state:
        st.session_state.app_success_count = {app: 0 for app in AVAILABLE_APPS}
    
    # Sidebar
    with st.sidebar:
        st.title("🐆 PANTHER")
        
        # Balance Check
        st.subheader("💰 Account")
        if st.button("Check Balance", use_container_width=True):
            with st.spinner("Fetching..."):
                result = get_balance()
                if result.get('status') == 'success':
                    st.success(f"Balance: Rs. {result.get('balance')}")
                else:
                    st.error(f"Failed: {result.get('message')}")
        
        st.markdown("---")
        
        # Settings
        st.subheader("⚙️ Settings")
        with st.expander("API Configuration"):
            current_base = get_config('API_BASE_URL', DEFAULT_API_BASE_URL)
            current_key = get_config('API_KEY', DEFAULT_API_KEY)
            current_delay = int(get_config('OTP_SEND_DELAY', '2'))
            
            new_base = st.text_input("Base URL", value=current_base)
            new_key = st.text_input("API Key", value=current_key, type="password")
            new_delay = st.number_input("OTP Delay (sec)", value=current_delay, min_value=0, max_value=10)
            
            if st.button("Save Config", use_container_width=True):
                set_config('API_BASE_URL', new_base)
                set_config('API_KEY', new_key)
                set_config('OTP_SEND_DELAY', str(new_delay))
                st.success("Saved!")
        
        st.markdown("---")
        
        # Stats
        st.subheader("📊 Stats")
        st.metric("Total Success", sum(st.session_state.app_success_count.values()))
        st.metric("Pending Tasks", len(st.session_state.tasks))
    
    # Main Content
    st.title("🐆 PANTHER Registration Tool")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📱 Send OTP", "✅ Verify OTP", "📋 Records"])
    
    # ==================== TAB 1: SEND OTP ====================
    with tab1:
        st.subheader("📱 Send OTP - Multiple Apps")
        st.info("💡 Maximum 5 apps at a time (API limit)")
        
        # App Selection
        st.markdown("**Select Apps:**")
        cols = st.columns(4)
        selected_apps = []
        
        for i, app in enumerate(AVAILABLE_APPS):
            with cols[i % 4]:
                if st.checkbox(app, key=f"app_{app}"):
                    selected_apps.append(app)
        
        if len(selected_apps) > 5:
            st.error("⚠️ Maximum 5 apps allowed!")
            selected_apps = selected_apps[:5]
        
        st.markdown(f"**Selected:** {len(selected_apps)} apps")
        
        # Phone Number
        phone = st.text_input("📞 Phone Number (10 digits)", max_chars=10, placeholder="9876543210")
        
        # Send Button
        if st.button("🚀 Send OTPs", type="primary", use_container_width=True):
            if not selected_apps:
                st.warning("Please select at least one app")
            elif not phone or not phone.isdigit() or len(phone) != 10:
                st.warning("Please enter valid 10-digit phone number")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                delay = int(get_config('OTP_SEND_DELAY', '2'))
                
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
                        st.success(f"✅ {app}: OTP sent")
                    else:
                        st.error(f"❌ {app}: {result.get('message')}")
                    
                    progress_bar.progress((i + 1) / len(selected_apps))
                    
                    if i < len(selected_apps) - 1:
                        time.sleep(delay)
                
                status_text.text("✅ All OTPs sent!")
                st.rerun()
    
    # ==================== TAB 2: VERIFY OTP ====================
    with tab2:
        st.subheader("✅ Verify OTP")
        
        if not st.session_state.tasks:
            st.info("No pending tasks. Send OTP first!")
        else:
            # Show pending tasks
            pending_tasks = {tid: t for tid, t in st.session_state.tasks.items() 
                           if t['status'] == 'pending'}
            
            if pending_tasks:
                st.markdown(f"**Pending Tasks:** {len(pending_tasks)}")
                
                # Quick Verify All
                st.markdown("---")
                st.markdown("### ⚡ Quick Verify (Same OTP for all)")
                quick_otp = st.text_input("Enter OTP", max_chars=4, key="quick_otp")
                
                if st.button("✅ Verify All", type="primary", use_container_width=True):
                    if not quick_otp:
                        st.warning("Enter OTP")
                    else:
                        for task_id in list(pending_tasks.keys()):
                            task = st.session_state.tasks[task_id]
                            result = verify_otp(task_id, quick_otp)
                            
                            if result.get('status') == 'success':
                                task['status'] = 'completed'
                                app_name = task['app_name']
                                st.session_state.app_success_count[app_name] += 1
                                
                                reg_data = result.get('data', {})
                                log_registration(
                                    app_name,
                                    task['phone'],
                                    reg_data.get('password', ''),
                                    reg_data.get('device_id', ''),
                                    reg_data.get('account_balance', 0),
                                    quick_otp
                                )
                                
                                st.success(f"✅ {app_name} - {task['phone']}")
                                st.json(reg_data)
                                break  # Stop on first success
                            else:
                                st.warning(f"❌ {task['app_name']} failed, trying next...")
                        st.rerun()
                
                st.markdown("---")
                
                # Individual Verify
                st.markdown("### 📱 Individual Verification")
                
                for task_id in st.session_state.task_order[:]:
                    if task_id not in st.session_state.tasks:
                        continue
                    
                    task = st.session_state.tasks[task_id]
                    
                    with st.expander(f"{task['app_name']} - {task['phone']} ({task['status']})", 
                                   expanded=(task['status'] == 'pending')):
                        
                        if task['status'] == 'pending':
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                otp = st.text_input("OTP", max_chars=4, key=f"otp_{task_id}")
                            
                            with col2:
                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button("✅ Verify", key=f"verify_{task_id}"):
                                    if not otp:
                                        st.warning("Enter OTP")
                                    else:
                                        result = verify_otp(task_id, otp)
                                        
                                        if result.get('status') == 'success':
                                            task['status'] = 'completed'
                                            app_name = task['app_name']
                                            st.session_state.app_success_count[app_name] += 1
                                            
                                            reg_data = result.get('data', {})
                                            log_registration(
                                                app_name,
                                                task['phone'],
                                                reg_data.get('password', ''),
                                                reg_data.get('device_id', ''),
                                                reg_data.get('account_balance', 0),
                                                otp
                                            )
                                            
                                            st.success("✅ Success!")
                                            st.json(reg_data)
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Failed: {result.get('message')}")
                            
                            if st.button("❌ Cancel", key=f"cancel_{task_id}"):
                                result = cancel_task(task_id)
                                if result.get('status') == 'success':
                                    del st.session_state.tasks[task_id]
                                    st.session_state.task_order.remove(task_id)
                                    st.info("Cancelled")
                                    st.rerun()
    
    # ==================== TAB 3: RECORDS ====================
    with tab3:
        st.subheader("📋 Recent Registrations")
        
        records = get_registrations(100)
        
        if records:
            df = pd.DataFrame(records)
            st.dataframe(df, use_container_width=True)
            
            # Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name="panther_records.csv",
                mime="text/csv"
            )
        else:
            st.info("No records yet")

if __name__ == "__main__":
    main()
