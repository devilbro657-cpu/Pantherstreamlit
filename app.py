import streamlit as st
import requests
import time
from datetime import datetime

# ==================== CONFIGURATION ====================
API_BASE_URL = "https://games.accbazaar.shop"
API_KEY = "আপনার-API-KEY-এখানে-লিখুন"

# Hardcoded Apps
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
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = True
if 'task_ids' not in st.session_state: 
    st.session_state.task_ids = {}
if 'available_apps' not in st.session_state: 
    st.session_state.available_apps = HARDCODED_APPS
if 'phone_number' not in st.session_state:
    st.session_state.phone_number = ""

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Panther Tool", 
    page_icon="🐆", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin-bottom: 0.5rem;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin-bottom: 0.5rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.title("🐆 Panther Tool")
    st.markdown("---")
    
    menu = st.radio(
        "📋 Menu", 
        ["🏠 Dashboard", "📝 Registration", "💰 Wallet", "🎮 Game Balance", "📜 History"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("API Status: ✅ Active")
    st.caption(f"Base URL: {API_BASE_URL[:30]}...")

# ==================== DASHBOARD ====================
if menu == "🏠 Dashboard":
    st.title("🏠 Dashboard")
    st.markdown("---")
    
    # Wallet Balance
    col1, col2, col3 = st.columns(3)
    
    with col1:
        res = get_wallet_balance()
        if res.get('status') == 'success':
            st.metric("💰 Wallet Balance", f"Rs. {res.get('balance', 0)}")
        else:
            st.metric("💰 Wallet Balance", "N/A")
    
    with col2:
        st.metric("📱 Active Tasks", len(st.session_state.task_ids))
    
    with col3:
        st.metric("🎮 Available Apps", len(st.session_state.available_apps))
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 New Registration", use_container_width=True):
            st.session_state.menu = "📝 Registration"
            st.rerun()
    
    with col2:
        if st.button("💰 Check Balance", use_container_width=True):
            st.session_state.menu = "💰 Wallet"
            st.rerun()
    
    with col3:
        if st.button(" View History", use_container_width=True):
            st.session_state.menu = "📜 History"
            st.rerun()
    
    with col4:
        if st.button("🔄 Refresh Apps", use_container_width=True):
            res = get_services_list()
            if res.get('status') == 'success':
                st.session_state.available_apps = [s['app_name'] for s in res.get('services', [])]
                st.success("Apps updated!")
                st.rerun()

# ==================== REGISTRATION ====================
elif menu == "📝 Registration":
    st.title("📝 Multi-App Registration")
    st.markdown("একটি নাম্বারে একাধিক অ্যাপে রেজিস্ট্রেশন করুন (সর্বোচ্চ ৫টি)")
    st.markdown("---")
    
    # Step 1: Select Apps & Phone
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_apps = st.multiselect(
            "🎮 অ্যাপ সিলেক্ট করুন (সর্বোচ্চ ৫টি)",
            st.session_state.available_apps,
            max_selections=5,
            help="একাধিক অ্যাপ সিলেক্ট করতে পারেন"
        )
    
    with col2:
        phone = st.text_input(
            "📱 ফোন নাম্বার",
            value=st.session_state.phone_number,
            placeholder="9876543210",
            help="একই নাম্বার সব অ্যাপের জন্য ব্যবহার হবে"
        )
        st.session_state.phone_number = phone
    
    # Step 2: Send OTP
    st.markdown("---")
    st.subheader("📤 OTP পাঠান")
    
    if st.button("📤 সব অ্যাপে OTP পাঠান", type="primary", use_container_width=True):
        if not selected_apps:
            st.error("❌ অন্তত একটি অ্যাপ সিলেক্ট করুন")
        elif not phone:
            st.error("❌ ফোন নাম্বার দিন")
        elif len(phone) < 10:
            st.error("❌ সঠিক ফোন নাম্বার দিন")
        else:
            st.session_state.task_ids = {}
            success_count = 0
            error_apps = []
            
            progress_bar = st.progress(0)
            
            for i, app in enumerate(selected_apps):
                with st.spinner(f"⏳ {app}..."):
                    res = send_otp(app, phone)
                    
                    if res.get('status') == 'success':
                        st.session_state.task_ids[app] = res.get('task_id')
                        success_count += 1
                    else:
                        error_apps.append(f"{app}: {res.get('message', 'Unknown error')}")
                    
                    progress_bar.progress((i + 1) / len(selected_apps))
            
            # Summary
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if success_count > 0:
                    st.success(f"✅ {success_count}/{len(selected_apps)} অ্যাপে OTP সফল")
            
            with col2:
                if error_apps:
                    with st.expander(f"❌ {len(error_apps)}টি Error দেখুন"):
                        for err in error_apps:
                            st.error(err)
            
            if success_count > 0:
                st.balloons()
                st.rerun()
    
    # Step 3: Verify OTP
    if st.session_state.task_ids:
        st.markdown("---")
        st.subheader("✅ OTP Verify করুন")
        
        otp_inputs = {}
        
        # Create expanders for each app
        for app, task_id in list(st.session_state.task_ids.items()):
            with st.expander(f"📱 {app}", expanded=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    otp_inputs[app] = st.text_input(
                        "OTP কোড",
                        placeholder="4-digit OTP",
                        key=f"otp_{app}",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_{app}", use_container_width=True):
                        res = cancel_task(task_id)
                        del st.session_state.task_ids[app]
                        st.info(f"🚫 {app} cancelled")
                        st.rerun()
                
                if task_id:
                    st.caption(f"Task ID: `{task_id[:15]}...`")
        
        # Verify All Button
        st.markdown("---")
        if st.button("✅ সব Verify করুন", type="primary", use_container_width=True):
            success_regs = []
            failed_regs = []
            
            for app, task_id in list(st.session_state.task_ids.items()):
                otp = otp_inputs.get(app, "").strip()
                
                if not otp:
                    failed_regs.append(f"{app}: OTP খালি")
                    continue
                
                if len(otp) != 4:
                    failed_regs.append(f"{app}: OTP 4 digits হতে হবে")
                    continue
                
                with st.spinner(f"⏳ Verifying {app}..."):
                    res = verify_otp(task_id, otp)
                    
                    if res.get('status') == 'success':
                        data = res.get('data', {})
                        success_regs.append({
                            'app': app,
                            'phone': data.get('phone'),
                            'password': data.get('password'),
                            'balance': data.get('account_balance')
                        })
                        del st.session_state.task_ids[app]
                    else:
                        failed_regs.append(f"{app}: {res.get('message', 'Failed')}")
            
            # Results
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if success_regs:
                    st.success(f"✅ {len(success_regs)}টি সফল")
                    for reg in success_regs:
                        st.info(f"🎮 {reg['app']}\n📱 {reg['phone']}\n🔑 {reg['password']}\n💰 Rs. {reg['balance']}")
            
            with col2:
                if failed_regs:
                    st.error(f"❌ {len(failed_regs)}টি ব্যর্থ")
                    for fail in failed_regs:
                        st.warning(fail)
            
            if success_regs:
                st.balloons()

# ==================== WALLET ====================
elif menu == "💰 Wallet":
    st.title("💰 Wallet & Balance")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Balance", use_container_width=True):
            res = get_wallet_balance()
            if res.get('status') == 'success':
                st.metric("Available Balance", f"Rs. {res.get('balance', 0)}")
                st.success(f"👤 Username: {res.get('username', 'N/A')}")
            else:
                st.error(res.get('message'))
    
    with col2:
        st.metric("Active Tasks", len(st.session_state.task_ids))

# ==================== GAME BALANCE ====================
elif menu == "🎮 Game Balance":
    st.title("🎮 Game Balance Check")
    st.markdown("Register করা Device ID দিয়ে গেমের ভেতরের ব্যালেন্স চেক করুন")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        app_name = st.selectbox("অ্যাপ সিলেক্ট করুন", st.session_state.available_apps)
    
    with col2:
        device_id = st.text_input("Device ID", placeholder="e33a4ecee18783a5")
    
    with col3:
        if st.button("🔍 Check", use_container_width=True, type="primary"):
            if device_id:
                res = check_game_balance(app_name, device_id)
                if res.get('status') == 'success':
                    st.success("✅ Balance Found")
                    st.json(res)
                else:
                    st.error(res.get('message'))
            else:
                st.warning("Device ID দিন")

# ==================== HISTORY ====================
elif menu == "📜 History":
    st.title("📜 Registration History")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📝 Registrations", "💸 Transactions"])
    
    with tab1:
        limit = st.slider("কতগুলো দেখবেন?", 1, 50, 10)
        
        if st.button("🔄 Load", use_container_width=True):
            res = get_registrations(limit=limit)
            if res.get('status') == 'success':
                data = res.get('data', [])
                if data:
                    st.dataframe(data, use_container_width=True)
                else:
                    st.info("কোনো registration নেই")
            else:
                st.error(res.get('message'))
    
    with tab2:
        if st.button("🔄 Load Transactions", use_container_width=True):
            res = get_balance_history()
            if res.get('status') == 'success':
                data = res.get('data', [])
                if data:
                    st.dataframe(data, use_container_width=True)
                else:
                    st.info("কোনো transaction নেই")
            else:
                st.error(res.get('message'))
