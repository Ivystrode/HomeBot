import sqlite3


def connect():
    conn = sqlite3.connect("bot_database.db")
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS ip (time text, ip_address text)")
    cur.execute(f"CREATE TABLE IF NOT EXISTS devices (MAC text, time_first_seen text, trusted integer)")
    cur.execute(f"CREATE TABLE IF NOT EXISTS authorised_users (id INTEGER PRIMARY KEY, Name text, Type text)")
    cur.execute(f"CREATE TABLE IF NOT EXISTS reminders (user_id integer, username text, detail text, time text)")
    cur.execute(f"CREATE TABLE IF NOT EXISTS units (id TEXT PRIMARY KEY, name text, address text, type text, status text)")
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
    

# ==========REMINDERS==========
def add_reminder(user_id, username, detail, time):
    conn=sqlite3.connect("bot_database.db", timeout=5)
    cur=conn.cursor()
    cur.execute("INSERT INTO reminders VALUES (?, ?, ?, ?)", (user_id, username, detail, time))
    conn.commit()
    conn.close()
    
def get_reminders():    
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    
    try:
        cur.execute(f"SELECT * FROM reminders")
        reminders=cur.fetchall()
        # reminders = [{k:item[k] for k in item.keys()} for item in results]
        conn.close()
        return reminders
    except:
        print("not found...")
        return "not found"
    
def delete_reminder(detail):
    conn=sqlite3.connect("bot_database.db", timeout=5)
    cur=conn.cursor()
    cur.execute(f"DELETE FROM reminders WHERE detail=?", (detail,))
    conn.commit()
    conn.close()
    print("deleted")

# ==========UNITS==========
def get_all_units():    
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    
    try:
        cur.execute(f"SELECT * FROM units")
        units=cur.fetchall()
        conn.close()
        return units
    except:
        print("not found...")
        return "not found"
    
def get_unit_address(unitname):
    unitname = unitname.lower()
    conn=sqlite3.connect("bot_database.db")
    cur = conn.cursor()

    cur.execute("SELECT * from units WHERE name=?", (unitname,))
    result = cur.fetchall()
    conn.close()
    
    if result:
        return result[0][2]
    else:
        print(f"[HUB] DATABASE: {unitname} not found, it may not have checked in recently")

def get_unit_name(address):    
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM units WHERE address=?", (address,))
    rows=cur.fetchall()
    conn.close()
    return rows[0][1]

def check_unit_status(address):
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM units WHERE address=?", (address,))
    result=cur.fetchall()
    conn.close()
    return result[0][4] # status
    
def insert_unit(id, name, address, type, status):
    conn=sqlite3.connect("bot_database.db", timeout=5)
    cur=conn.cursor()
    try:
        cur.execute("INSERT INTO units VALUES (?, ?, ?, ?, ?)", (id, name.lower(), address, type, status))
    except Exception as e:
        print("[HUB] DATABASE: Entry error: {e}")
    finally:
        conn.commit()
        conn.close()
    
def delete(address):
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    cur.execute("DELETE FROM units WHERE address=?", (address,)) 
    conn.commit()
    conn.close()

def update_unit(address, status):
    conn=sqlite3.connect("bot_database.db", timeout=10)
    cur=conn.cursor()
    cur.execute(f"UPDATE units SET status=? WHERE address=?", (status, address))
    conn.commit()
    conn.close()

# MAC ADDRESS DETECTOR...
def add_device(mac, time, trusted):
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    cur.execute(f"INSERT INTO devices VALUES (?, ?, ?)", (mac, time, trusted))
    conn.commit()
    conn.close()

def check_device_trusted(mac):
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM devices WHERE mac=?", (mac,))
    result=cur.fetchall()
    conn.close()
    print(result)
    return result[0][2] # trusted status (0 or 1..)

def get_all_devices():    
    conn=sqlite3.connect("bot_database.db")
    cur=conn.cursor()
    
    try:
        cur.execute(f"SELECT * FROM devices")
        devices=cur.fetchall()
        conn.close()
        return devices
    except:
        print("not found...")
        return "not found"

    
connect()