import streamlit as st
import requests
from datetime import datetime

# ==================== CONFIGURATION ====================
API_BASE_URL = "https://games.accbazaar.shop"
API_KEY = "আপনার-API-KEY-এখানে-লিখুন"  # ⚠️ আপনার API Key দিন

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

def get_services_list():
    return make_request('/v1/services/list')

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'task_ids' not in st.session_state:
    st.session_state.task_ids = {}
if 'available_apps' not in st.session_state:
    st.session_state.available_apps = HARDCODED_APPS
if 'phone_number' not in st.session_state:
    st.session_state.phone_number = ""

# ==================== AUTHENTICATION ====================
def login(username, password):
    """Simple login - Replace with your actual auth"""
    if username == "admin" and password == "admin123":
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = "admin"
        return True
    elif username and password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = "user"
        return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.role = ""
    st.session_state.task_ids = {}

# ==================== LOGIN PAGE ====================
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login - Panther Tool", page_icon="🔐", layout="centered")
    
    # Custom CSS
    st.markdown("""
    <style>
    .login-box {
        padding: 2rem;
        border-radius: 1rem;
        background-color: #1e1e1e;
        margin: 2rem auto;
        max-width: 400px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.title("🔐 Panther Tool")
        st.markdown("---")
        
        username = st.text_input("Username", placeholder="Enter username", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("Login", type="primary", use_container_width=True):
                if login(username, password):
                    st.success("✅ Login successful!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with col_b:
            if st.button("Clear", use_container_width=True):
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<center>Made with ❤️ using Panther API</center>", unsafe_allow_html=True)

else:
    # ==================== MAIN APP AFTER LOGIN ====================
    st.set_page_config(page_title="Panther Tool", page_icon="🐆", layout="wide")
    
    # Custom CSS
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
    .stButton>button {
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        st.markdown("---")
        
        menu = st.radio(
            "📋 Menu",
            ["🏠 Dashboard", "📝 Registration Tool", "💰 Wallet", "📜 History"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
        
        st.caption("🐆 Panther Tool v1.0")
    
    # ==================== DASHBOARD ====================
    if menu == "🏠 Dashboard":
        st.title("🏠 Dashboard")
        st.markdown("---")
        
        # Fetch wallet balance
        wallet_res = get_wallet_balance()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if wallet_res.get('status') == 'success':
                st.metric("💰 Wallet Balance", f"Rs. {wallet_res.get('balance', 0)}")
            else:
                st.metric("💰 Wallet Balance", "N/A")
        
        with col2:
            st.metric("📱 Active Tasks", len(st.session_state.task_ids))
        
        with col3:
            st.metric("🎮 Available Apps", len(st.session_state.available_apps))
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 New Registration", use_container_width=True, type="primary"):
                st.session_state.menu = "📝 Registration Tool"
                st.rerun()
        
        with col2:
            if st.button("💰 Check Balance", use_container_width=True):
                st.session_state.menu = "💰 Wallet"
                st.rerun()
        
        with col3:
            if st.button("📜 View History", use_container_width=True):
                st.session_state.menu = "📜 History"
                st.rerun()
        
        st.markdown("---")
        
        # Recent Activity
        st.subheader("📊 Recent Registrations")
        
        if st.button("🔄 Load Recent", use_container_width=True):
            res = get_registrations(limit=5)
            if res.get('status') == 'success':
                data = res.get('data', [])
                if data:
                    st.dataframe(data, use_container_width=True)
                else:
                    st.info("No recent registrations")
            else:
                st.error(res.get('message'))
    
    # ==================== REGISTRATION TOOL ====================
    elif menu == "📝 Registration Tool":
        st.title("📝 Registration Tool")
        st.markdown("একাধিক অ্যাপে একসাথে রেজিস্ট্রেশন করুন (সর্বোচ্চ ৫টি)")
        st.markdown("---")
        
        # Step 1: Select Apps
        st.subheader("১. অ্যাপ সিলেক্ট করুন")
        
        # Refresh Apps button
        if st.button("🔄 Refresh Apps List"):
            res = get_services_list()
            if res.get('status') == 'success':
                st.session_state.available_apps = [s['app_name'] for s in res.get('services', [])]
                st.success(f"✅ {len(st.session_state.available_apps)} apps loaded!")
                st.rerun()
        
        selected_apps = st.multiselect(
            "অ্যাপ সিলেক্ট করুন (সর্বোচ্চ ৫টি)",
            st.session_state.available_apps,
            max_selections=5,
            help="একাধিক অ্যাপ সিলেক্ট করতে পারেন"
        )
        
        if selected_apps:
            st.info(f"✅ {len(selected_apps)} app(s) selected: {', '.join(selected_apps)}")
        
        st.markdown("---")
        
        # Step 2: Phone & Password
        st.subheader("২. তথ্য দিন")
        
        col1, col2 = st.columns(2)
        
        with col1:
            phone = st.text_input(
                "📱 ফোন নাম্বার",
                value=st.session_state.phone_number,
                placeholder="9876543210"
            )
            st.session_state.phone_number = phone
        
        with col2:
            password = st.text_input("🔑 পাসওয়ার্ড", type="password", placeholder="Enter password")
        
        device_id = st.text_input("📲 Device ID (Optional)", placeholder="e33a4ecee18783a5")
        
        st.markdown("---")
        
        # Step 3: Send OTP
        st.subheader("৩. OTP পাঠান")
        
        if st.button("📤 সব অ্যাপে OTP পাঠান", type="primary", use_container_width=True):
            if not selected_apps:
                st.error("❌ অন্তত একটি অ্যাপ সিলেক্ট করুন")
            elif not phone:
                st.error("❌ ফোন নাম্বার দিন")
            elif len(phone) < 10:
                st.error("❌ সঠিক ফোন নাম্বার দিন")
            else:
                st.session_state.task_ids = {}
                progress_bar = st.progress(0)
                
                for i, app in enumerate(selected_apps):
                    with st.spinner(f"⏳ {app}..."):
                        res = send_otp(app, phone)
                        
                        if res.get('status') == 'success':
                            st.session_state.task_ids[app] = res.get('task_id')
                            st.success(f"✅ {app}: OTP Sent!")
                        else:
                            st.error(f"❌ {app}: {res.get('message', 'Failed')}")
                        
                        progress_bar.progress((i + 1) / len(selected_apps))
                
                if st.session_state.task_ids:
                    st.balloons()
                    st.rerun()
        
        # Step 4: Verify OTP
        if st.session_state.task_ids:
            st.markdown("---")
            st.subheader("৪. OTP Verify করুন")
            
            otp_inputs = {}
            
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
                    
                    st.caption(f"Task ID: `{task_id[:15]}...`")
            
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
                            with st.expander(f"🎮 {reg['app']}"):
                                st.write(f"📱 Phone: {reg['phone']}")
                                st.write(f"🔑 Password: {reg['password']}")
                                st.write(f"💰 Balance: Rs. {reg['balance']}")
                
                with col2:
                    if failed_regs:
                        st.error(f"❌ {len(failed_regs)}টি ব্যর্থ")
                        for fail in failed_regs:
                            st.warning(fail)
                
                if success_regs:
                    st.balloons()
    
    # ==================== WALLET ====================
    elif menu == "💰 Wallet":
        st.title("💰 Wallet")
        st.markdown("---")
        
        if st.button("🔄 Refresh Balance", type="primary", use_container_width=True):
            res = get_wallet_balance()
            if res.get('status') == 'success':
                st.metric("Available Balance", f"Rs. {res.get('balance', 0)}")
                st.success(f"👤 Username: {res.get('username', 'N/A')}")
            else:
                st.error(res.get('message'))
    
    # ==================== HISTORY ====================
    elif menu == "📜 History":
        st.title("📜 Registration History")
        st.markdown("---")
        
        limit = st.slider("কতগুলো দেখবেন?", 1, 50, 10)
        
        if st.button("🔄 Load History", type="primary", use_container_width=True):
            res = get_registrations(limit=limit)
            if res.get('status') == 'success':
                data = res.get('data', [])
                if data:
                    st.dataframe(data, use_container_width=True)
                else:
                    st.info("কোনো registration নেই")
            else:
                st.error(res.get('message'))
