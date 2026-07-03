import streamlit as st
import requests
import time
from datetime import datetime

# ==================== CONFIGURATION ====================
API_BASE_URL = "https://games.accbazaar.shop"
API_KEY = "panthers_ySfegn1vdco_lf9chq_-KbG7YAe0YyZMlAadcQ"  # ⚠️ আপনার আসল API Key দিন

# ==================== API FUNCTIONS ====================
def make_request(endpoint, method='GET', data=None, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json; charset=utf-8'}
    try:
        if method == 'POST':
            r = requests.post(url, headers=headers, json=data, timeout=15)
        else:
            r = requests.get(url, headers=headers, params=params, timeout=15)
        return r.json()
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def send_otp(app_name, phone):
    return make_request('/v1/register/send_otp', 'POST', data={'app_name': app_name, 'phone': phone})

def verify_otp(task_id, otp):
    return make_request('/v1/register/verify_otp', 'POST', data={'task_id': task_id, 'otp': otp})

def cancel_task(task_id):
    return make_request('/v1/register/cancel_task', 'POST', data={'task_id': task_id})

def get_services_list():
    return make_request('/v1/services/list')

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'available_apps' not in st.session_state:
    st.session_state.available_apps = [
        "567slot_game", "mbmbet_game", "yonoslot_game", "Yono_vip",
        "789jackpot_game", "toprummy_game", "Yonogame_game",
        "spincrush_game", "hirummy_game", "indslot_game"
    ]
if 'selected_apps' not in st.session_state:
    st.session_state.selected_apps = set()
if 'app_tasks' not in st.session_state:
    st.session_state.app_tasks = {}
if 'success_counts' not in st.session_state:
    st.session_state.success_counts = {}
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'phone_number' not in st.session_state:
    st.session_state.phone_number = ""
if 'sending_in_progress' not in st.session_state:
    st.session_state.sending_in_progress = False
if 'current_sending_app' not in st.session_state:
    st.session_state.current_sending_app = ""
if 'sending_progress' not in st.session_state:
    st.session_state.sending_progress = 0.0

# ==================== AUTHENTICATION ====================
def login(username, password):
    if username == "admin" and password == "admin123":
        st.session_state.logged_in = True
        st.session_state.username = username
        return True
    elif username and password:
        st.session_state.logged_in = True
        st.session_state.username = username
        return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.app_tasks = {}
    st.session_state.selected_apps = set()
    st.session_state.notifications = []

# ==================== CUSTOM CSS (Video UI Match) ====================
CUSTOM_CSS = """
<style>
/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp {background: #0a0e1a !important; color: #ffffff !important;}

/* Login */
.login-container {
    background: linear-gradient(135deg, #1a1f3a 0%, #0d1117 100%);
    padding: 2rem;
    border-radius: 16px;
    border: 1px solid #2a3050;
    max-width: 400px;
    margin: 3rem auto;
    text-align: center;
}

/* Header */
.panther-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, #1a1f3a 0%, #0d1117 100%);
    border-radius: 12px;
    margin-bottom: 1rem;
    border: 1px solid #2a3050;
}
.panther-logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.5rem;
    font-weight: bold;
    color: #ffffff;
}
.deep-test-btn {
    background: #1a2a4a;
    color: #60a5fa;
    border: 1px solid #2a4a7a;
    padding: 0.4rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
}
.exit-btn {
    background: #3a1a1a;
    color: #f87171;
    border: 1px solid #5a2a2a;
    padding: 0.4rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
}

/* Counter badges */
.counter-bar {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.counter-badge {
    background: #1a1f3a;
    border: 1px solid #2a3050;
    padding: 0.4rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    color: #94a3b8;
}
.counter-badge span {color: #60a5fa; font-weight: bold;}

/* Card */
.card {
    background: linear-gradient(135deg, #1a1f3a 0%, #0d1117 100%);
    border: 1px solid #2a3050;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Label */
.label-text {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.1rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

/* Status banners */
.status-banner {
    padding: 0.8rem 1rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    font-weight: 500;
}
.status-banner.success {
    background: #064e3b;
    border: 1px solid #059669;
    color: #6ee7b7;
}
.status-banner.error {
    background: #450a0a;
    border: 1px solid #dc2626;
    color: #fca5a5;
}
.status-banner.info {
    background: #1e3a5f;
    border: 1px solid #3b82f6;
    color: #93c5fd;
}

/* Progress */
.progress-container {
    background: #1a1f3a;
    border-radius: 8px;
    overflow: hidden;
    height: 8px;
    margin: 0.5rem 0;
}
.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    transition: width 0.3s;
    border-radius: 8px;
}

/* Done/Pending counter */
.done-pending {
    display: flex;
    justify-content: center;
    gap: 2rem;
    padding: 0.8rem;
    background: #1a1f3a;
    border-radius: 10px;
    margin-bottom: 1rem;
    border: 1px solid #2a3050;
}
.done-pending .done {color: #6ee7b7; font-weight: bold;}
.done-pending .pending {color: #fbbf24; font-weight: bold;}

/* App card */
.app-card {
    background: #1a1f3a;
    border: 1px solid #2a3050;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
}
.app-card.success-card {
    border-color: #059669;
    background: #064e3b;
}
.app-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}
.app-card-name {color: #60a5fa; font-weight: bold; font-size: 0.95rem;}
.app-card-status {
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}
.app-card-status.pending {
    background: #451a03;
    color: #fbbf24;
    border: 1px solid #92400e;
}
.app-card-status.done {
    background: #064e3b;
    color: #6ee7b7;
    border: 1px solid #059669;
}
.app-card-otp {
    background: #0d1117;
    border: 1px solid #2a3050;
    border-radius: 8px;
    padding: 0.8rem;
    text-align: center;
    font-size: 1.2rem;
    letter-spacing: 0.3rem;
    color: #94a3b8;
    margin-bottom: 0.8rem;
}
.app-card-otp.filled {color: #6ee7b7; letter-spacing: 0.2rem;}
.app-card-buttons {display: flex; gap: 0.5rem;}

/* Notification */
.notification {
    position: fixed;
    top: 1rem;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    padding: 0.8rem 1.5rem;
    border-radius: 10px;
    font-weight: bold;
    animation: slideDown 0.3s ease;
    min-width: 250px;
    text-align: center;
}
.notification.success {
    background: #064e3b;
    border: 1px solid #059669;
    color: #6ee7b7;
}
@keyframes slideDown {
    from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
    to { transform: translateX(-50%) translateY(0); opacity: 1; }
}

/* Streamlit overrides */
.stTextInput > div > div > input {
    background: #0d1117 !important;
    border: 1px solid #2a3050 !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    padding: 0.8rem 1rem !important;
}
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
}
</style>
"""

# ==================== LOGIN PAGE ====================
if not st.session_state.logged_in:
    st.set_page_config(page_title="Panther Panel", page_icon="🐆", layout="centered")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-container">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🐆</div>
        <h1 style="margin: 0; color: #ffffff; font-size: 2rem;">PANTHER</h1>
        <p style="color: #64748b; margin: 0.5rem 0 1.5rem 0;">Panel Login</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", placeholder="Enter username", key="login_user")
    with col2:
        password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Login", type="primary", use_container_width=True):
            if login(username, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    with col_b:
        if st.button("Clear", use_container_width=True):
            st.rerun()

else:
    # ==================== MAIN APP ====================
    st.set_page_config(page_title="Panther Panel", page_icon="🐆", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Show notifications (top banners like in video)
    for notif in st.session_state.notifications[-3:]:
        st.markdown(f'<div class="notification success">{notif}</div>', unsafe_allow_html=True)
    
    # ===== HEADER =====
    st.markdown("""
    <div class="panther-header">
        <div class="panther-logo">
            <span>🐆</span>
            <span>PANTHER</span>
        </div>
        <div style="display: flex; gap: 0.5rem;">
            <span class="deep-test-btn">👤 DEEP TEST</span>
            <span class="exit-btn">Exit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== COUNTER BADGES =====
    counter_html = '<div class="counter-bar">'
    for app, count in st.session_state.success_counts.items():
        counter_html += f'<div class="counter-badge">{app}: <span>{count}</span></div>'
    if not st.session_state.success_counts:
        for app in ['567slot', 'Yono', 'mbmbet', 'yonoslot']:
            counter_html += f'<div class="counter-badge">{app}: <span>0</span></div>'
    counter_html += '</div>'
    st.markdown(counter_html, unsafe_allow_html=True)
    
    # ===== SEND OTP SECTION =====
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🚀 Send OTP</div>', unsafe_allow_html=True)
    
    # App selection label
    st.markdown('<div class="label-text">SELECT APPS</div>', unsafe_allow_html=True)
    
    # App toggle buttons
    apps = st.session_state.available_apps
    cols_per_row = 2
    num_rows = (len(apps) + cols_per_row - 1) // cols_per_row
    
    for row in range(num_rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            app_idx = row * cols_per_row + col_idx
            if app_idx < len(apps):
                app = apps[app_idx]
                is_selected = app in st.session_state.selected_apps
                with cols[col_idx]:
                    btn_type = "primary" if is_selected else "secondary"
                    if st.button(app, key=f"app_toggle_{app}", use_container_width=True, type=btn_type):
                        if app in st.session_state.selected_apps:
                            st.session_state.selected_apps.remove(app)
                        else:
                            st.session_state.selected_apps.add(app)
                        st.rerun()
    
    # Phone number
    st.markdown('<div class="label-text" style="margin-top: 1rem;">PHONE NUMBER</div>', unsafe_allow_html=True)
    phone = st.text_input(
        "Phone Number",
        value=st.session_state.phone_number,
        placeholder="10-digit mobile number",
        label_visibility="collapsed",
        key="phone_input"
    )
    st.session_state.phone_number = phone
    
    # Send button
    send_clicked = st.button("🚀 SEND ALL OTPs", type="primary", use_container_width=True, key="send_all_btn")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== HANDLE SEND OTP =====
    if send_clicked:
        if not st.session_state.selected_apps:
            st.error("Please select at least one app")
        elif not phone or len(phone) != 10 or not phone.isdigit():
            st.error("Please enter a valid 10-digit phone number")
        else:
            st.session_state.app_tasks = {}
            st.session_state.sending_in_progress = True
            st.session_state.notifications = []
            
            total = len(st.session_state.selected_apps)
            
            for i, app in enumerate(list(st.session_state.selected_apps)):
                st.session_state.current_sending_app = app
                st.session_state.sending_progress = (i + 1) / total
                
                res = send_otp(app, phone)
                
                if res.get('status') == 'success':
                    st.session_state.app_tasks[app] = {
                        'task_id': res.get('task_id'),
                        'phone': phone,
                        'status': 'pending',
                        'otp': '',
                        'message': ''
                    }
                    st.session_state.notifications.append(f"✅ {app} sent!")
                else:
                    st.session_state.app_tasks[app] = {
                        'task_id': None,
                        'phone': phone,
                        'status': 'failed',
                        'otp': '',
                        'message': res.get('message', 'Failed')
                    }
                    st.session_state.notifications.append(f"❌ {app}: {res.get('message', 'Failed')}")
                
                # 2.5 second gap between OTPs
                if i < total - 1:
                    time.sleep(2.5)
            
            st.session_state.sending_in_progress = False
            st.session_state.current_sending_app = ""
            st.rerun()
    
    # ===== SHOW SENDING PROGRESS =====
    if st.session_state.sending_in_progress:
        st.markdown(f"""
        <div class="status-banner info">
            📦 {st.session_state.current_sending_app}...
        </div>
        <div class="progress-container">
            <div class="progress-bar" style="width: {st.session_state.sending_progress * 100}%"></div>
        </div>
        <div style="text-align: center; color: #94a3b8; margin-top: 0.5rem;">Sending...</div>
        """, unsafe_allow_html=True)
        st.rerun()
    
    # ===== SHOW STATUS BANNERS =====
    if st.session_state.notifications:
        for notif in st.session_state.notifications[-5:]:
            if notif.startswith("✅"):
                st.markdown(f'<div class="status-banner success">{notif}</div>', unsafe_allow_html=True)
            elif notif.startswith("❌"):
                st.markdown(f'<div class="status-banner error">{notif}</div>', unsafe_allow_html=True)
    
    # ===== DONE/PENDING COUNTER =====
    if st.session_state.app_tasks:
        done = sum(1 for t in st.session_state.app_tasks.values() if t['status'] == 'done')
        pending = sum(1 for t in st.session_state.app_tasks.values() if t['status'] == 'pending')
        
        st.markdown(f"""
        <div class="done-pending">
            <span class="done">✅ Done: {done}</span>
            <span class="pending"> Pending: {pending}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== QUICK SUBMIT =====
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚡ Quick Submit</div>', unsafe_allow_html=True)
        
        quick_otp = st.text_input(
            "Quick OTP",
            placeholder="1234 5678 9012",
            label_visibility="collapsed",
            key="quick_otp_input"
        )
        
        col_qs1, col_qs2 = st.columns([3, 1])
        with col_qs2:
            if st.button("Submit", type="primary", use_container_width=True, key="quick_submit_btn"):
                if quick_otp and len(quick_otp.replace(' ', '').replace('-', '')) == 4:
                    clean_otp = quick_otp.replace(' ', '').replace('-', '')
                    # Find first pending app
                    submitted = False
                    for app, task_info in st.session_state.app_tasks.items():
                        if task_info['status'] == 'pending' and task_info.get('task_id'):
                            res = verify_otp(task_info['task_id'], clean_otp)
                            if res.get('status') == 'success':
                                data = res.get('data', {})
                                st.session_state.app_tasks[app] = {
                                    'task_id': task_info['task_id'],
                                    'phone': task_info['phone'],
                                    'status': 'done',
                                    'otp': clean_otp,
                                    'password': data.get('password', 'N/A'),
                                    'balance': data.get('account_balance', 0),
                                    'message': ''
                                }
                                short = app.replace('_game', '').replace('Yono_vip', 'Yono')
                                st.session_state.success_counts[short] = st.session_state.success_counts.get(short, 0) + 1
                                st.session_state.notifications.append(f"✅ {app} ✓ {clean_otp}")
                                submitted = True
                                st.rerun()
                            else:
                                st.session_state.notifications.append(f" {app}: {res.get('message', 'Failed')}")
                                submitted = True
                                st.rerun()
                    if not submitted:
                        st.warning("No pending apps to verify")
                else:
                    st.warning("Enter 4-digit OTP")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ===== INDIVIDUAL APP CARDS =====
        for app, task_info in st.session_state.app_tasks.items():
            status = task_info['status']
            
            if status == 'done':
                st.markdown(f"""
                <div class="app-card success-card">
                    <div class="app-card-header">
                        <span class="app-card-name">{app}</span>
                        <span class="app-card-status done">✅ Done</span>
                    </div>
                    <div class="app-card-otp filled">{task_info.get('otp', '')} ✓</div>
                </div>
                """, unsafe_allow_html=True)
            
            elif status == 'failed':
                st.markdown(f"""
                <div class="app-card" style="border-color: #dc2626;">
                    <div class="app-card-header">
                        <span class="app-card-name" style="color: #f87171;">{app}</span>
                        <span class="app-card-status" style="background: #450a0a; color: #fca5a5; border-color: #dc2626;"> Failed</span>
                    </div>
                    <div style="color: #fca5a5; font-size: 0.85rem;">{task_info.get('message', 'Unknown error')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            else:
                # Pending
                otp_display = "— — — —" if not task_info.get('otp') else task_info['otp']
                otp_class = "filled" if task_info.get('otp') else ""
                
                st.markdown(f"""
                <div class="app-card">
                    <div class="app-card-header">
                        <span class="app-card-name">{app}</span>
                        <span class="app-card-status pending">⏳ Pending</span>
                    </div>
                    <div class="app-card-otp {otp_class}">{otp_display}</div>
                    <div class="app-card-buttons">
                """, unsafe_allow_html=True)
                
                col_v, col_r = st.columns(2)
                with col_v:
                    if st.button("✓ Verify", key=f"verify_{app}", use_container_width=True):
                        otp_val = st.session_state.get(f"otp_verify_{app}", "")
                        if otp_val and len(otp_val.replace(' ', '').replace('-', '')) == 4 and task_info.get('task_id'):
                            clean_otp = otp_val.replace(' ', '').replace('-', '')
                            res = verify_otp(task_info['task_id'], clean_otp)
                            if res.get('status') == 'success':
                                data = res.get('data', {})
                                st.session_state.app_tasks[app] = {
                                    'task_id': task_info['task_id'],
                                    'phone': task_info['phone'],
                                    'status': 'done',
                                    'otp': clean_otp,
                                    'password': data.get('password', 'N/A'),
                                    'balance': data.get('account_balance', 0),
                                    'message': ''
                                }
                                short = app.replace('_game', '').replace('Yono_vip', 'Yono')
                                st.session_state.success_counts[short] = st.session_state.success_counts.get(short, 0) + 1
                                st.session_state.notifications.append(f"✅ {app} ✓ {clean_otp}")
                                st.rerun()
                            else:
                                st.session_state.app_tasks[app]['status'] = 'failed'
                                st.session_state.app_tasks[app]['message'] = res.get('message', 'Invalid OTP')
                                st.session_state.notifications.append(f"❌ {app}: {res.get('message', 'Failed')}")
                                st.rerun()
                        else:
                            st.warning("Enter 4-digit OTP in the field below first")
                
                with col_r:
                    if st.button("🔄 Resend", key=f"resend_{app}", use_container_width=True):
                        if task_info.get('task_id'):
                            cancel_task(task_info['task_id'])
                        res = send_otp(app, task_info['phone'])
                        if res.get('status') == 'success':
                            st.session_state.app_tasks[app] = {
                                'task_id': res.get('task_id'),
                                'phone': task_info['phone'],
                                'status': 'pending',
                                'otp': '',
                                'message': ''
                            }
                            st.session_state.notifications.append(f"✅ {app} OTP resent!")
                            st.rerun()
                        else:
                            st.session_state.notifications.append(f"❌ {app}: {res.get('message', 'Failed')}")
                            st.rerun()
                
                # OTP input field for verify
                st.text_input("OTP", key=f"otp_verify_{app}", label_visibility="collapsed", placeholder="Enter 4-digit OTP")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.title(f" {st.session_state.username}")
        st.markdown("---")
        if st.button("Logout", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
