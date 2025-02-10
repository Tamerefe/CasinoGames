import sqlite3 as sql

def get_db_connection():
    conn = sql.connect('SlotMachine/database/case.db')
    return conn

def initialize_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS game_data (
                    id INTEGER PRIMARY KEY,
                    jackpot_pool INTEGER,
                    win_probability REAL
                )''')
    conn.commit()

    # Initialize database with default values if empty
    c.execute('SELECT COUNT(*) FROM game_data')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO game_data (jackpot_pool, win_probability) VALUES (?, ?)', (500, 0.1))
        conn.commit()

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

initialize_db()
jackpot_pool, win_probability = fetch_initial_values()