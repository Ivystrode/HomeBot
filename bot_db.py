import sqlite3


def connect():
    conn = sqlite3.connect("bot_database.db")
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS ip (time text, ip_address text)")
    cur.execute(f"CREATE TABLE IF NOT EXISTS authorised_users (id INTEGER PRIMARY KEY, Name text, Type text)")
    print("[Homebot] Database created")
    conn.commit()
    conn.close()
    
# ==========IP ADDRESSES==========

def insert(time, ip):
    conn=sqlite3.connect("bot_database.db", timeout=5)
    cur=conn.cursor()
    cur.execute("INSERT INTO ip VALUES (?, ?)", (time, ip))
    conn.commit()
    conn.close()
    
def get_latest_ip():    
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM ip")
    rows=cur.fetchall()
    conn.close()
    return rows[-1][-1]

# ==========USERS==========

def add_authorised_user(id, name, type):
    conn=sqlite3.connect("bot_database.db", timeout=5)
    cur=conn.cursor()
    cur.execute("INSERT INTO authorised_users VALUES (?, ?, ?)", (id, name.lower(), type))
    conn.commit()
    conn.close()
    
def get_all_users():    
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    
    try:
        cur.execute(f"SELECT * FROM authorised_users")
        users=cur.fetchall()
        conn.close()
        return users
    except:
        print("not found...")
        return "not found"
    
connect()