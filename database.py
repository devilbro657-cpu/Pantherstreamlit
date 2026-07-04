import sqlite3
import os
from datetime import datetime
from config import DB_PATH

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Config table (NEW)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'subuser',
            api_key TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Registrations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            app_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT,
            device_id TEXT,
            account_balance REAL DEFAULT 0,
            otp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Activity logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT NOT NULL,
            app_name TEXT,
            phone TEXT,
            otp TEXT,
            status TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, password, role, is_active)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin123', 'admin', 1))
    
    # Insert default config if not exists
    import config
    default_configs = {
        'API_BASE_URL': config.API_BASE_URL,
        'API_KEY': config.API_KEY,
        'OTP_SEND_DELAY': str(config.OTP_SEND_DELAY)
    }
    
    for key, value in default_configs.items():
        cursor.execute('''
            INSERT OR IGNORE INTO config (key, value)
            VALUES (?, ?)
        ''', (key, value))
    
    conn.commit()
    conn.close()

def get_config(key, default=None):
    """Get config value from database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result['value'] if result else default
    except:
        return default

def set_config(key, value):
    """Set config value in database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP
        ''', (key, value, value))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error setting config: {e}")
        return False

def get_all_config():
    """Get all config from database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM config")
        configs = {row['key']: row['value'] for row in cursor.fetchall()}
        conn.close()
        return configs
    except:
        return {}

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password, role='subuser'):
    """Create new user"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, role, is_active)
            VALUES (?, ?, ?, ?)
        ''', (username, password, role, 1))
        conn.commit()
        conn.close()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, str(e)

def delete_user(user_id):
    """Delete user"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_all_users():
    """Get all users"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()
    return users

def get_all_users_stats():
    """Get all users with stats"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            u.id,
            u.username,
            u.role,
            u.created_at,
            COUNT(r.id) as total_registrations,
            SUM(CASE WHEN DATE(r.created_at) = DATE('now') THEN 1 ELSE 0 END) as today_registrations
        FROM users u
        LEFT JOIN registrations r ON u.id = r.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    return users

def log_registration(user_id, username, app_name, phone, password, device_id, balance, otp):
    """Log successful registration"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO registrations 
            (user_id, username, app_name, phone, password, device_id, account_balance, otp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, app_name, phone, password, device_id, balance, otp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging registration: {e}")

def log_activity(user_id, username, action, app_name=None, phone=None, otp=None, status=None, details=None):
    """Log user activity"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activity_logs 
            (user_id, username, action, app_name, phone, otp, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, action, app_name, phone, otp, status, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging activity: {e}")

def get_registrations(user_id=None, limit=100):
    """Get registrations"""
    conn = get_db()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute('''
            SELECT * FROM registrations 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM registrations 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    records = cursor.fetchall()
    conn.close()
    return records

def get_activity_logs(user_id=None, limit=100):
    """Get activity logs"""
    conn = get_db()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute('''
            SELECT * FROM activity_logs 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM activity_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    logs = cursor.fetchall()
    conn.close()
    return logs

def get_records_with_filters(date_from=None, date_to=None, search=None, page=1, per_page=50):
    """Get records with filters and pagination"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT r.*, u.username 
        FROM registrations r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if date_from:
        query += ' AND DATE(r.created_at) >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND DATE(r.created_at) <= ?'
        params.append(date_to)
    
    if search:
        query += ' AND (r.app_name LIKE ? OR r.phone LIKE ? OR u.username LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])
    
    # Get total count
    count_query = query.replace('SELECT r.*, u.username', 'SELECT COUNT(*) as total')
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']
    
    # Get paginated records
    query += ' ORDER BY r.created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    records = cursor.fetchall()
    
    conn.close()
    
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    return {
        'records': [dict(r) for r in records],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }
