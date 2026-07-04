import streamlit as st
import requests
import time

# ==================== CONFIGURATION ====================
API_BASE_URL = "https://games.accbazaar.shop"
API_KEY = "panthers_ySfegn1vdco_lf9chq_-KbG7YAe0YyZMlAadcQ"  # ⚠️ আপনার আসল API Key দিন

HARDCODED_APPS = [
    "567slot_game", "mbmbet_game", "yonoslot_game", "Yono_vip",
    "789jackpot_game", "toprummy_game", "Yonogame_game",
    "spincrush_game", "hirummy_game", "indslot_game"
]

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

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ''
if 'available_apps' not in st.session_state: st.session_state.available_apps = HARDCODED_APPS
if 'app_tasks' not in st.session_state: st.session_state.app_tasks = {}
if 'success_counts' not in st.session_state: st.session_state.success_counts = {}
if 'phone_number' not in st.session_state: st.session_state.phone_number = ""

# ==================== AUTHENTICATION ====================
def login(username, password):
    if username == "admin" and password == "admin123":
        st.session_state.logged_in = True
        st.session_state.username = username
        return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.app_tasks = {}

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
.stApp {background: #0a0e1a !important; color: #ffffff !important;}
.card {background: #1a1f3a; border: 1px solid #2a3050; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;}
.app-card {background: #1a1f3a; border: 1px solid #2a3050; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;}
.app-card.success-card {border-color: #059669; background: #064e3b;}
.app-card-header {display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;}
.app-card-name {color: #60a5fa; font-weight: bold;}
.app-card-status.pending {background: #451a03; color: #fbbf24; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem;}
.app-card-status.done {background: #064e3b; color: #6ee7b7; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem;}
.app-card-otp {background: #0d1117; border: 1px solid #2a3050; border-radius: 8px; padding: 0.8rem; text-align: center; font-size: 1.2rem; letter-spacing: 0.3rem; color: #94a3b8; margin-bottom: 0.8rem;}
.stButton > button {border-radius: 8px !important; font-weight: 600 !important;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== LOGIN PAGE ====================
if not st.session_state.logged_in:
    st.set_page_config(page_title="Panther Panel", layout="centered")
    st.title("🐆 Panther Panel Login")
    col1, col2 = st.columns(2)
    with col1: username = st.text_input("Username")
    with col2: password = st.text_input("Password", type="password")
    if st.button("Login", type="primary", use_container_width=True):
        if login(username, password): st.rerun()
        else: st.error("Invalid credentials")

else:
    # ==================== MAIN APP ====================
    st.set_page_config(page_title="Panther Panel", layout="wide")
    
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h2 style="margin: 0;"> PANTHER</h2>
        <button style="background: #3a1a1a; color: #f87171; border: 1px solid #5a2a2a; padding: 0.4rem 1rem; border-radius: 8px;">Exit</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Counter Badges
    cols = st.columns(4)
    apps_list = ['567slot', 'Yono', 'mbmbet', 'yonoslot']
    for i, app_short in enumerate(apps_list):
        count = st.session_state.success_counts.get(app_short, 0)
        cols[i].metric(app_short, count)
    
    st.markdown("---")
    
    # ===== SEND OTP SECTION =====
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Send OTP")
    
    st.markdown('<div style="color: #64748b; font-size: 0.8rem; margin-bottom: 0.5rem;">SELECT APPS</div>', unsafe_allow_html=True)
    selected_apps = st.multiselect("Choose apps", st.session_state.available_apps)
    
    st.markdown('<div style="color: #64748b; font-size: 0.8rem; margin-top: 1rem; margin-bottom: 0.5rem;">PHONE NUMBER</div>', unsafe_allow_html=True)
    phone = st.text_input("Phone Number", value=st.session_state.phone_number, placeholder="10-digit mobile number", label_visibility="collapsed")
    st.session_state.phone_number = phone
    
    send_clicked = st.button("🚀 SEND ALL OTPs", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== HANDLE SEND OTP (FIXED TOAST ICONS) =====
    if send_clicked:
        if not selected_apps:
            st.toast("Please select at least one app", icon="️")
        elif not phone or len(phone) != 10:
            st.toast("Please enter valid 10-digit number", icon="️")
        else:
            st.session_state.app_tasks = {}
            
            with st.status("Sending OTPs...", expanded=True) as status:
                total = len(selected_apps)
                for i, app in enumerate(selected_apps):
                    st.write(f" Sending OTP to **{app}**...")
                    
                    res = send_otp(app, phone)
                    
                    if res.get('status') == 'success':
                        st.session_state.app_tasks[app] = {
                            'task_id': res.get('task_id'), 'phone': phone, 'status': 'pending', 'otp': ''
                        }
                        st.write(f"✅ **{app}**: OTP Sent successfully!")
                        st.toast(f"{app} OTP Sent!", icon="✅")
                    else:
                        msg = res.get('message', 'Unknown Error')
                        st.session_state.app_tasks[app] = {
                            'task_id': None, 'phone': phone, 'status': 'failed', 'message': msg
                        }
                        # FIXED: Replaced empty/invalid icons with valid emojis
                        if 'already' in msg.lower() or 'exist' in msg.lower():
                            st.write(f"⚠️ **{app}**: Number already registered!")
                            st.toast(f"{app}: Already exists", icon="⚠️")
                        elif 'Auth' in msg or 'Proxy' in msg:
                            st.write(f"🔑 **{app}**: Auth Error (Check API Key)")
                            st.toast(f"{app}: Auth Error", icon="")  # Fixed: was ""
                        else:
                            st.write(f"❌ **{app}**: {msg}")
                            st.toast(f"{app} Failed", icon="❌")
                    
                    if i < total - 1:
                        st.write(f"⏳ Waiting 2.5 seconds before next app...")
                        time.sleep(2.5)
                
                status.update(label="OTP Sending Process Complete!", state="complete")
            st.rerun()
    
    # ===== SHOW RESULTS =====
    if st.session_state.app_tasks:
        done = sum(1 for t in st.session_state.app_tasks.values() if t['status'] == 'done')
        pending = sum(1 for t in st.session_state.app_tasks.values() if t['status'] == 'pending')
        
        st.markdown(f"""
        <div style="display: flex; justify-content: center; gap: 2rem; margin: 1rem 0; background: #1a1f3a; padding: 0.8rem; border-radius: 10px;">
            <span style="color: #6ee7b7; font-weight: bold;">✅ Done: {done}</span>
            <span style="color: #fbbf24; font-weight: bold;">⏳ Pending: {pending}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Submit
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⚡ Quick Submit")
        quick_otp = st.text_input("Enter OTP", placeholder="1234", label_visibility="collapsed")
        col_q1, col_q2 = st.columns([3, 1])
        with col_q2:
            if st.button("Submit", type="primary", use_container_width=True):
                if quick_otp and len(quick_otp) == 4:
                    for app, task in st.session_state.app_tasks.items():
                        if task['status'] == 'pending' and task.get('task_id'):
                            res = verify_otp(task['task_id'], quick_otp)
                            if res.get('status') == 'success':
                                task['status'] = 'done'
                                task['otp'] = quick_otp
                                st.toast(f"{app} Verified!", icon="✅")
                            else:
                                st.toast(f"Verification Failed", icon="❌")
                            st.rerun()
                else:
                    st.toast("Enter 4-digit OTP", icon="⚠️")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Individual App Cards
        for app, task in st.session_state.app_tasks.items():
            if task['status'] == 'done':
                st.markdown(f"""
                <div class="app-card success-card">
                    <div class="app-card-header">
                        <span class="app-card-name">{app}</span>
                        <span class="app-card-status done">✅ Done</span>
                    </div>
                    <div class="app-card-otp" style="color: #6ee7b7;">{task['otp']} ✓</div>
                </div>
                """, unsafe_allow_html=True)
            elif task['status'] == 'pending':
                st.markdown(f"""
                <div class="app-card">
                    <div class="app-card-header">
                        <span class="app-card-name">{app}</span>
                        <span class="app-card-status pending">⏳ Pending</span>
                    </div>
                    <div class="app-card-otp">— — — —</div>
                </div>
                """, unsafe_allow_html=True)
