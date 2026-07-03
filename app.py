import streamlit as st
import requests
import time
from datetime import datetime

# ==================== CONFIGURATION ====================
API_BASE_URL = "https://games.accbazaar.shop"
API_KEY = "panthers_ySfegn1vdco_lf9chq_-KbG7YAe0YyZMlAadcQ"  # ⚠️ আপনার আসল API Key দিন

# Hardcoded Apps (Fallback)
HARDCODED_APPS = [
    "567slot_game", "mbmbet_game", "yonoslot_game", "okrummy_game", "Yono777_game",
    "toprummy_game", "Yonogame_game", "spincrush_game", "789jackpot_game", "hirummy_game",
    "indslot_game", "maha_game", "Yono_vip", "Spin777_game", "Hindi777_game",
    "Bingo_game", "jaiho777_game", "jaiho91_game", "Rummyludo_game", "Shareslots_game", "SpinLucky_game"
]

# ==================== API FUNCTIONS ====================
def make_request(endpoint, method='GET', data=None, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
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

def get_wallet_balance():
    return make_request('/v1/account/balance')

def get_registrations(limit=10):
    return make_request('/v1/account/registrations', params={'limit': limit})

def get_balance_history():
    return make_request('/v1/account/balance_history')

def get_services_list():
    return make_request('/v1/services/list')

def check_game_balance(app_name, device_id):
    return make_request('/api/check_game_balance', params={'app_name': app_name, 'device_id': device_id})

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state: st.session_state.logged_in = True
if 'task_ids' not in st.session_state: st.session_state.task_ids = {}
if 'available_apps' not in st.session_state: st.session_state.available_apps = HARDCODED_APPS

# ==================== UI ====================
st.set_page_config(page_title="Panther Tool", page_icon="🐆", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🐆 Panther Tool")
    menu = st.radio("Navigation", [
        "🏠 Dashboard", 
        "📝 Multi-App Registration", 
        "💰 Wallet Balance", 
        "🎮 Game Balance Check",
        "📜 Registration History",
        "💸 Balance History"
    ])
    st.markdown("---")
    st.caption("Powered by Panther API")

# ==================== DASHBOARD ====================
if menu == "🏠 Dashboard":
    st.title("🏠 Dashboard")
    res = get_wallet_balance()
    if res.get('status') == 'success':
        col1, col2 = st.columns(2)
        col1.metric("Wallet Balance", f"Rs. {res.get('balance', 0)}")
        col2.metric("Username", res.get('username', 'N/A'))
    else:
        st.error("Failed to load dashboard. Check API Key.")

# ==================== MULTI-APP REGISTRATION ====================
elif menu == "📝 Multi-App Registration":
    st.title("📝 Multi-App Registration")
    st.info("একটি নাম্বারে ৫টি পর্যন্ত অ্যাপে একসাথে OTP পাঠানো যাবে।")
    
    # Fetch apps dynamically
    if st.button("🔄 Refresh Apps List"):
        res = get_services_list()
        if res.get('status') == 'success':
            st.session_state.available_apps = [s['app_name'] for s in res.get('services', [])]
            st.success("Apps list updated!")
            st.rerun()

    apps = st.session_state.available_apps
    selected_apps = st.multiselect("১. অ্যাপ সিলেক্ট করুন (সর্বোচ্চ ৫টি)", apps, max_selections=5)
    phone = st.text_input("২. ফোন নাম্বার দিন", placeholder="9876543210")
    
    st.markdown("---")
    
    # Step 1: Send OTP
    if st.button("📤 Send OTP for All", type="primary"):
        if not selected_apps: st.warning("অন্যতম একটি অ্যাপ সিলেক্ট করুন।")
        elif not phone: st.warning("ফোন নাম্বার দিন।")
        else:
            st.session_state.task_ids = {}
            for app in selected_apps:
                with st.spinner(f"Sending OTP for {app}..."):
                    res = send_otp(app, phone)
                    if res.get('status') == 'success':
                        st.session_state.task_ids[app] = res.get('task_id')
                        st.success(f"✅ {app}: OTP Sent! (Task ID: {res.get('task_id')[:10]}...)")
                    else:
                        st.error(f"❌ {app}: {res.get('message')}")
    
    # Step 2: Verify OTP
    if st.session_state.task_ids:
        st.markdown("---")
        st.subheader("৩. OTP দিয়ে Verify করুন")
        
        otps = {}
        for app, task_id in list(st.session_state.task_ids.items()):
            col1, col2 = st.columns([3, 1])
            with col1:
                otps[app] = st.text_input(f"OTP for {app}", key=f"otp_in_{app}")
            with col2:
                if st.button("❌ Cancel", key=f"cancel_{app}"):
                    res = cancel_task(task_id)
                    st.info(res.get('message', 'Cancelled'))
                    del st.session_state.task_ids[app]
                    st.rerun()
                    
        if st.button("✅ Verify & Register All", type="primary"):
            for app, task_id in list(st.session_state.task_ids.items()):
                otp = otps.get(app, "")
                if not otp:
                    st.warning(f"Missing OTP for {app}")
                    continue
                
                with st.spinner(f"Verifying {app}..."):
                    res = verify_otp(task_id, otp)
                    if res.get('status') == 'success':
                        data = res.get('data', {})
                        st.success(f"✅ {app} Registered Successfully!")
                        st.json(data)
                        del st.session_state.task_ids[app] # Remove after success
                    else:
                        st.error(f"❌ {app}: {res.get('message')}")

# ==================== WALLET BALANCE ====================
elif menu == "💰 Wallet Balance":
    st.title("💰 Wallet Balance")
    if st.button("🔄 Refresh Balance"):
        res = get_wallet_balance()
        if res.get('status') == 'success':
            st.metric("Available Balance", f"Rs. {res.get('balance', 0)}")
            st.write(f"Username: **{res.get('username', 'N/A')}**")
        else:
            st.error(res.get('message'))

# ==================== GAME BALANCE CHECK ====================
elif menu == "🎮 Game Balance Check":
    st.title("🎮 Game Balance Check")
    st.info("Register করা Device ID দিয়ে গেমের ভেতরের ব্যালেন্স চেক করুন।")
    
    col1, col2 = st.columns(2)
    with col1:
        app_name = st.selectbox("Select App", st.session_state.available_apps)
    with col2:
        device_id = st.text_input("Device ID", placeholder="e33a4ecee18783a5")
        
    if st.button("🔍 Check Game Balance", type="primary"):
        if device_id:
            res = check_game_balance(app_name, device_id)
            if res.get('status') == 'success':
                col1, col2, col3 = st.columns(3)
                col1.metric("UID", res.get('uid'))
                col2.metric("Balance", res.get('balance'))
                col3.metric("Dcoin", res.get('dcoin'))
            else:
                st.error(res.get('message'))
        else:
            st.warning("Device ID দিন।")

# ==================== REGISTRATION HISTORY ====================
elif menu == "📜 Registration History":
    st.title("📜 Recent Registrations")
    limit = st.slider("কতগুলো দেখবেন?", 1, 50, 10)
    
    if st.button("🔄 Load History"):
        res = get_registrations(limit=limit)
        if res.get('status') == 'success':
            data = res.get('data', [])
            if data:
                st.dataframe(data, use_container_width=True)
            else:
                st.info("কোনো registration পাওয়া যায়নি।")
        else:
            st.error(res.get('message'))

# ==================== BALANCE HISTORY ====================
elif menu == "💸 Balance History":
    st.title("💸 Balance History (Transactions)")
    
    if st.button("🔄 Load Transactions"):
        res = get_balance_history()
        if res.get('status') == 'success':
            data = res.get('data', [])
            if data:
                st.dataframe(data, use_container_width=True)
            else:
                st.info("কোনো transaction পাওয়া যায়নি।")
        else:
            st.error(res.get('message'))
