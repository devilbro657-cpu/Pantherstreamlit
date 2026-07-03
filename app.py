import streamlit as st
import requests
import time
from datetime import datetime

# ==================== CONFIGURATION ====================
API_BASE_URL = "https://games.accbazaar.shop"
API_KEY = "আপনার-API-KEY-এখানে-লিখুন"  # ⚠️ আপনার আসল API Key দিন

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

def get_services_list():
    return make_request('/v1/services/list')

def get_registrations(limit=10):
    return make_request('/v1/account/registrations', params={'limit': limit})

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'available_apps' not in st.session_state:
    st.session_state.available_apps = HARDCODED_APPS
if 'app_tasks' not in st.session_state:
    # app_tasks = {app_name: {'task_id': ..., 'phone': ..., 'status': 'pending'|'success'|'failed', 'otp_sent_at': ...}}
    st.session_state.app_tasks = {}

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

# ==================== LOGIN PAGE ====================
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Panther Tool")
        st.markdown("---")
        
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Login", type="primary", use_container_width=True):
                if login(username, password):
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        with col_b:
            if st.button("Clear", use_container_width=True):
                st.rerun()

else:
    # ==================== MAIN APP ====================
    st.set_page_config(page_title="Panther Tool", page_icon="🐆", layout="wide")
    
    # Custom CSS
    st.markdown("""
    <style>
    .app-card {
        padding: 1.2rem;
        border-radius: 0.8rem;
        background-color: #1e293b;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    .app-card-success {
        padding: 1.2rem;
        border-radius: 0.8rem;
        background-color: #064e3b;
        border: 1px solid #059669;
        margin-bottom: 1rem;
    }
    .app-card-failed {
        padding: 1.2rem;
        border-radius: 0.8rem;
        background-color: #450a0a;
        border: 1px solid #dc2626;
        margin-bottom: 1rem;
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
        
        page = st.radio("Menu", ["📝 Registration Tool", "📜 History"], label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # ==================== REGISTRATION TOOL ====================
    if page == "📝 Registration Tool":
        st.title("📝 Registration Tool")
        st.markdown("---")
        
        # ===== STEP 1: Select Apps =====
        st.subheader("১. অ্যাপ সিলেক্ট করুন")
        
        if st.button("🔄 Refresh Apps"):
            res = get_services_list()
            if res.get('status') == 'success':
                st.session_state.available_apps = [s['app_name'] for s in res.get('services', [])]
                st.success(f"✅ {len(st.session_state.available_apps)} apps loaded!")
                st.rerun()
        
        selected_apps = st.multiselect(
            "অ্যাপ সিলেক্ট করুন (একাধিক)",
            st.session_state.available_apps,
            help="একাধিক অ্যাপ সিলেক্ট করতে পারেন"
        )
        
        if selected_apps:
            st.info(f"✅ {len(selected_apps)} app(s) selected")
        
        st.markdown("---")
        
        # ===== STEP 2: Phone Number =====
        st.subheader("২. ফোন নাম্বার দিন")
        
        phone = st.text_input(
            "📱 ফোন নাম্বার",
            placeholder="9876543210",
            key="main_phone"
        )
        
        st.markdown("---")
        
        # ===== STEP 3: Send OTP to All Apps =====
        st.subheader(". সব অ্যাপে OTP পাঠান")
        
        if st.button("📤 সব অ্যাপে OTP পাঠান", type="primary", use_container_width=True):
            if not selected_apps:
                st.error("❌ অন্তত একটি অ্যাপ সিলেক্ট করুন")
            elif not phone or len(phone) < 10:
                st.error("❌ সঠিক ফোন নাম্বার দিন")
            else:
                # Reset app_tasks for selected apps
                st.session_state.app_tasks = {}
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total = len(selected_apps)
                
                for i, app in enumerate(selected_apps):
                    status_text.info(f"⏳ {app} - OTP পাঠানো হচ্ছে...")
                    
                    res = send_otp(app, phone)
                    
                    if res.get('status') == 'success':
                        st.session_state.app_tasks[app] = {
                            'task_id': res.get('task_id'),
                            'phone': phone,
                            'status': 'pending',
                            'otp_sent_at': datetime.now().isoformat(),
                            'message': ''
                        }
                        status_text.success(f"✅ {app} - OTP পাঠানো হয়েছে!")
                    else:
                        st.session_state.app_tasks[app] = {
                            'task_id': None,
                            'phone': phone,
                            'status': 'failed',
                            'otp_sent_at': None,
                            'message': res.get('message', 'Failed')
                        }
                        status_text.error(f"❌ {app} - {res.get('message', 'Failed')}")
                    
                    progress_bar.progress((i + 1) / total)
                    
                    # 2.5 second gap between each OTP send
                    if i < total - 1:
                        time.sleep(2.5)
                
                status_text.empty()
                st.balloons()
                st.rerun()
        
        # ===== STEP 4: Show OTP Cards for Each App =====
        if st.session_state.app_tasks:
            st.markdown("---")
            st.subheader("৪. OTP Verify করুন")
            
            # Count statuses
            pending_count = sum(1 for t in st.session_state.app_tasks.values() if t['status'] == 'pending')
            success_count = sum(1 for t in st.session_state.app_tasks.values() if t['status'] == 'success')
            failed_count = sum(1 for t in st.session_state.app_tasks.values() if t['status'] == 'failed')
            
            col1, col2, col3 = st.columns(3)
            col1.metric(" Pending", pending_count)
            col2.metric("✅ Success", success_count)
            col3.metric("❌ Failed", failed_count)
            
            st.markdown("---")
            
            # Show each app card
            for app, task_info in list(st.session_state.app_tasks.items()):
                phone_num = task_info['phone']
                task_id = task_info['task_id']
                status = task_info['status']
                
                if status == 'success':
                    # Success card
                    st.markdown(f"""
                    <div class="app-card-success">
                        <h3>✅ {app} - DONE</h3>
                        <p>📱 Phone: {phone_num}</p>
                        <p> Password: {task_info.get('password', 'N/A')}</p>
                        <p>💰 Balance: Rs. {task_info.get('balance', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif status == 'failed':
                    # Failed card
                    st.markdown(f"""
                    <div class="app-card-failed">
                        <h3>❌ {app} - FAILED</h3>
                        <p>📱 Phone: {phone_num}</p>
                        <p>⚠️ {task_info.get('message', 'Unknown error')}</p>
                        <p> 5 মিনিট অপেক্ষা করুন নতুন OTP এর জন্য</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                else:
                    # Pending card - needs OTP verification
                    with st.container():
                        st.markdown(f"""
                        <div class="app-card">
                            <h3> {app}</h3>
                            <p>📞 Phone: {phone_num}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_otp, col_btn = st.columns([3, 1])
                        
                        with col_otp:
                            otp_input = st.text_input(
                                "OTP কোড (4 digits)",
                                placeholder="Enter OTP",
                                key=f"otp_input_{app}",
                                label_visibility="collapsed"
                            )
                        
                        with col_btn:
                            verify_clicked = st.button(
                                "✅ Verify",
                                key=f"verify_{app}",
                                use_container_width=True,
                                type="primary"
                            )
                        
                        resend_clicked = st.button(
                            "🔄 Resend OTP",
                            key=f"resend_{app}",
                            use_container_width=True
                        )
                        
                        # Handle Verify
                        if verify_clicked:
                            if not otp_input or len(otp_input) != 4:
                                st.warning("⚠️ 4 digit OTP দিন")
                            elif not task_id:
                                st.error("❌ Task ID নেই")
                            else:
                                with st.spinner(f"⏳ {app} verify হচ্ছে..."):
                                    res = verify_otp(task_id, otp_input)
                                    
                                    if res.get('status') == 'success':
                                        data = res.get('data', {})
                                        st.session_state.app_tasks[app] = {
                                            'task_id': task_id,
                                            'phone': phone_num,
                                            'status': 'success',
                                            'password': data.get('password', 'N/A'),
                                            'balance': data.get('account_balance', 0),
                                            'message': ''
                                        }
                                        st.success(f"✅ {app} - Registration Successful!")
                                        st.rerun()
                                    else:
                                        st.session_state.app_tasks[app]['status'] = 'failed'
                                        st.session_state.app_tasks[app]['message'] = res.get('message', 'Wrong OTP')
                                        st.error(f"❌ {app} - OTP Failed! 5 মিনিট অপেক্ষা করুন।")
                                        st.rerun()
                        
                        # Handle Resend OTP
                        if resend_clicked:
                            if task_id:
                                # Cancel old task first
                                cancel_task(task_id)
                            
                            with st.spinner(f"⏳ {app} - নতুন OTP পাঠানো হচ্ছে..."):
                                res = send_otp(app, phone_num)
                                
                                if res.get('status') == 'success':
                                    st.session_state.app_tasks[app] = {
                                        'task_id': res.get('task_id'),
                                        'phone': phone_num,
                                        'status': 'pending',
                                        'otp_sent_at': datetime.now().isoformat(),
                                        'message': ''
                                    }
                                    st.success(f"✅ {app} - নতুন OTP পাঠানো হয়েছে!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {app} - {res.get('message', 'Failed')}")
                        
                        st.markdown("---")
    
    # ==================== HISTORY ====================
    elif page == " History":
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
