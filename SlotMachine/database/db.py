import sqlite3 as sql
import os

def get_db_connection():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'case.db')
    conn = sql.connect(db_path)
    return conn

def initialize_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Game data table
    c.execute('''CREATE TABLE IF NOT EXISTS game_data (
                    id INTEGER PRIMARY KEY,
                    jackpot_pool INTEGER,
                    win_probability REAL
                )''')
    
    # Analytics summary table
    c.execute('''CREATE TABLE IF NOT EXISTS analytics_summary (
                    id INTEGER PRIMARY KEY,
                    session_date TEXT,
                    total_spins INTEGER DEFAULT 0,
                    total_bets REAL DEFAULT 0,
                    total_wins REAL DEFAULT 0,
                    rtp_percentage REAL DEFAULT 0,
                    win_rate_percentage REAL DEFAULT 0,
                    bonus_rounds INTEGER DEFAULT 0,
                    jackpot_wins INTEGER DEFAULT 0,
                    last_updated TEXT
                )''')
    
    # User profiles table
    c.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    balance REAL DEFAULT 1000,
                    session_count INTEGER DEFAULT 0,
                    total_spins INTEGER DEFAULT 0,
                    total_bets REAL DEFAULT 0,
                    total_wins REAL DEFAULT 0,
                    biggest_win REAL DEFAULT 0,
                    created_at TEXT,
                    last_login TEXT,
                    is_active INTEGER DEFAULT 1
                )''')
    
    # Session logs table
    c.execute('''CREATE TABLE IF NOT EXISTS session_logs (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    start_balance REAL,
                    end_balance REAL,
                    session_spins INTEGER DEFAULT 0,
                    session_bets REAL DEFAULT 0,
                    session_wins REAL DEFAULT 0,
                    session_duration INTEGER DEFAULT 0,
                    started_at TEXT,
                    ended_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )''')
    
    conn.commit()

    # Initialize database with default values if empty
    c.execute('SELECT COUNT(*) FROM game_data')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO game_data (jackpot_pool, win_probability) VALUES (?, ?)', (500, 0.1))
        conn.commit()

    conn.close()

def save_analytics_to_db(analytics_data):
    """Save analytics summary to database"""
    from datetime import datetime
    
    conn = get_db_connection()
    c = conn.cursor()
    
    session_date = datetime.now().strftime('%Y-%m-%d')
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if today's record exists
    c.execute('SELECT id FROM analytics_summary WHERE session_date = ?', (session_date,))
    existing = c.fetchone()
    
    if existing:
        # Update existing record
        c.execute('''UPDATE analytics_summary SET 
                     total_spins = ?, total_bets = ?, total_wins = ?,
                     rtp_percentage = ?, win_rate_percentage = ?,
                     bonus_rounds = ?, jackpot_wins = ?, last_updated = ?
                     WHERE session_date = ?''',
                  (analytics_data['total_spins'], analytics_data['total_bets'],
                   analytics_data['total_wins'], analytics_data['rtp_percentage'],
                   analytics_data['win_rate_percentage'], analytics_data['bonus_count'],
                   analytics_data['jackpot_count'], last_updated, session_date))
    else:
        # Insert new record
        c.execute('''INSERT INTO analytics_summary 
                     (session_date, total_spins, total_bets, total_wins,
                      rtp_percentage, win_rate_percentage, bonus_rounds,
                      jackpot_wins, last_updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (session_date, analytics_data['total_spins'], analytics_data['total_bets'],
                   analytics_data['total_wins'], analytics_data['rtp_percentage'],
                   analytics_data['win_rate_percentage'], analytics_data['bonus_count'],
                   analytics_data['jackpot_count'], last_updated))
    
    conn.commit()
    conn.close()

def get_historical_analytics():
    """Get historical analytics from database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''SELECT session_date, total_spins, total_bets, total_wins,
                 rtp_percentage, win_rate_percentage, bonus_rounds, jackpot_wins
                 FROM analytics_summary ORDER BY session_date DESC LIMIT 10''')
    
    results = c.fetchall()
    conn.close()
    
    return results

def create_user_profile(username, starting_balance=1000):
    """Create a new user profile with username and return the profile data"""
    from datetime import datetime
    
    conn = get_db_connection()
    c = conn.cursor()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        c.execute('''INSERT INTO user_profiles 
                     (username, balance, created_at, last_login) 
                     VALUES (?, ?, ?, ?)''',
                  (username, starting_balance, current_time, current_time))
        
        user_id = c.lastrowid
        conn.commit()
        
        # Return the created user profile
        user_profile = {
            'user_id': user_id,
            'username': username,
            'balance': starting_balance,
            'session_count': 0,
            'total_spins': 0,
            'total_bets': 0.0,
            'total_wins': 0.0,
            'biggest_win': 0.0,
            'created_at': current_time,
            'last_login': current_time,
            'is_active': 1
        }
        
        print(f"✅ Created new user profile: {username} (ID: {user_id})")
        return user_profile
        
    except Exception as e:
        print(f"❌ Error creating user profile: {e}")
        return None
    finally:
        conn.close()

def load_balance(user_id):
    """Load user balance from database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('SELECT balance FROM user_profiles WHERE user_id = ? AND is_active = 1', (user_id,))
        result = c.fetchone()
        
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print(f"❌ Error loading balance: {e}")
        return None
    finally:
        conn.close()

def save_balance(user_id, balance):
    """Save user balance to database (upsert)"""
    from datetime import datetime
    
    conn = get_db_connection()
    c = conn.cursor()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Check if user exists
        c.execute('SELECT user_id FROM user_profiles WHERE user_id = ?', (user_id,))
        exists = c.fetchone()
        
        if exists:
            # Update existing user
            c.execute('''UPDATE user_profiles 
                         SET balance = ?, last_login = ? 
                         WHERE user_id = ?''',
                      (balance, current_time, user_id))
        else:
            # Create new user
            c.execute('''INSERT INTO user_profiles 
                         (user_id, username, balance, created_at, last_login) 
                         VALUES (?, ?, ?, ?, ?)''',
                      (user_id, f"Player_{user_id}", balance, current_time, current_time))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error saving balance: {e}")
        return False
    finally:
        conn.close()

def update_user_stats(user_id, spins=0, bets=0, wins=0, biggest_win=0):
    """Update user statistics"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''UPDATE user_profiles 
                     SET total_spins = total_spins + ?,
                         total_bets = total_bets + ?,
                         total_wins = total_wins + ?,
                         biggest_win = CASE WHEN ? > biggest_win THEN ? ELSE biggest_win END
                     WHERE user_id = ?''',
                  (spins, bets, wins, biggest_win, biggest_win, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error updating user stats: {e}")
        return False
    finally:
        conn.close()

def get_user_profile(user_id):
    """Get complete user profile information by user_id"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''SELECT user_id, username, balance, session_count, total_spins,
                            total_bets, total_wins, biggest_win, created_at, last_login
                     FROM user_profiles WHERE user_id = ? AND is_active = 1''', (user_id,))
        
        result = c.fetchone()
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1], 
                'balance': result[2],
                'session_count': result[3],
                'total_spins': result[4],
                'total_bets': result[5],
                'total_wins': result[6],
                'biggest_win': result[7],
                'created_at': result[8],
                'last_login': result[9]
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        return None
    finally:
        conn.close()

def get_user_profile_by_username(username):
    """Get complete user profile information by username"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''SELECT user_id, username, balance, session_count, total_spins,
                            total_bets, total_wins, biggest_win, created_at, last_login
                     FROM user_profiles WHERE username = ? AND is_active = 1''', (username,))
        
        result = c.fetchone()
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1], 
                'balance': result[2],
                'session_count': result[3],
                'total_spins': result[4],
                'total_bets': result[5],
                'total_wins': result[6],
                'biggest_win': result[7],
                'created_at': result[8],
                'last_login': result[9]
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        return None
    finally:
        conn.close()

def list_user_profiles():
    """List all active user profiles"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''SELECT user_id, username, balance, total_spins, last_login
                     FROM user_profiles WHERE is_active = 1 
                     ORDER BY last_login DESC''')
        
        results = c.fetchall()
        return results
    except Exception as e:
        print(f"❌ Error listing user profiles: {e}")
        return []
    finally:
        conn.close()

def start_session(user_id, starting_balance):
    """Start a new gaming session"""
    from datetime import datetime
    
    conn = get_db_connection()
    c = conn.cursor()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        c.execute('''INSERT INTO session_logs 
                     (user_id, start_balance, started_at) 
                     VALUES (?, ?, ?)''',
                  (user_id, starting_balance, current_time))
        
        session_id = c.lastrowid
        
        # Update user session count
        c.execute('''UPDATE user_profiles 
                     SET session_count = session_count + 1 
                     WHERE user_id = ?''', (user_id,))
        
        conn.commit()
        return session_id
    except Exception as e:
        print(f"❌ Error starting session: {e}")
        return None
    finally:
        conn.close()

def end_session(session_id, end_balance, session_spins, session_bets, session_wins):
    """End a gaming session"""
    from datetime import datetime
    
    conn = get_db_connection()
    c = conn.cursor()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Get session start time to calculate duration
        c.execute('SELECT started_at FROM session_logs WHERE session_id = ?', (session_id,))
        result = c.fetchone()
        
        if result:
            start_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
            duration = int((end_time - start_time).total_seconds())
            
            c.execute('''UPDATE session_logs 
                         SET end_balance = ?, session_spins = ?, session_bets = ?,
                             session_wins = ?, session_duration = ?, ended_at = ?
                         WHERE session_id = ?''',
                      (end_balance, session_spins, session_bets, session_wins, duration, current_time, session_id))
            
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Error ending session: {e}")
        return False
    finally:
        conn.close()

def get_user_sessions(user_id, limit=10):
    """Get user's recent sessions"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''SELECT session_id, start_balance, end_balance, session_spins,
                            session_bets, session_wins, session_duration, started_at, ended_at
                     FROM session_logs 
                     WHERE user_id = ? 
                     ORDER BY started_at DESC 
                     LIMIT ?''', (user_id, limit))
        
        results = c.fetchall()
        return results
    except Exception as e:
        print(f"❌ Error getting user sessions: {e}")
        return []
    finally:
        conn.close()

def get_session_stats(user_id):
    """Get aggregated session statistics for a user"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''SELECT 
                        COUNT(*) as total_sessions,
                        AVG(session_duration) as avg_duration,
                        MAX(session_spins) as max_spins_per_session,
                        AVG(session_spins) as avg_spins_per_session,
                        SUM(session_bets) as lifetime_bets,
                        SUM(session_wins) as lifetime_wins
                     FROM session_logs 
                     WHERE user_id = ? AND ended_at IS NOT NULL''', (user_id,))
        
        result = c.fetchone()
        
        if result:
            return {
                'total_sessions': result[0] or 0,
                'avg_duration': result[1] or 0,
                'max_spins_per_session': result[2] or 0,
                'avg_spins_per_session': result[3] or 0,
                'lifetime_bets': result[4] or 0,
                'lifetime_wins': result[5] or 0
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Error getting session stats: {e}")
        return None
    finally:
        conn.close()

def fetch_initial_values():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT jackpot_pool, win_probability FROM game_data WHERE id = 1')
    values = c.fetchone()
    conn.close()
    return values

def update_jackpot_pool(jackpot_pool):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE game_data SET jackpot_pool = ? WHERE id = 1', (jackpot_pool,))
    conn.commit()
    conn.close()