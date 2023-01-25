import sqlite3
from sqlite3 import Error

db_name = 'events.db'

def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def execute_sql(sql, params=None):
    try:
        conn = sqlite3.connect(db_name, check_same_thread=False)
        if params:
            conn.execute(sql, params)
        else:
            conn.execute(sql)
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def create_event_table_if_not_exists():
    execute_sql('''CREATE TABLE IF NOT EXISTS events
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             description TEXT NOT NULL,
             date TEXT NOT NULL,
             time TEXT NOT NULL,
             location TEXT NOT NULL,
             user_id INTEGER NOT NULL,
             FOREIGN KEY (user_id) REFERENCES users(id))''')
    execute_sql('''
             Create UNIQUE INDEX name ON events (name)''')
    print("Event table created")

def create_user_table_if_not_exists():
    execute_sql('''CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            username TEXT NOT NULL,
            hash TEXT NOT NULL)''')
    execute_sql('''
             Create UNIQUE INDEX username ON users (username)''')
    print("User table created")


def create_event_attendees_table_if_not_exists():
    execute_sql('''CREATE TABLE IF NOT EXISTS event_attendees
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             event_id INTEGER NOT NULL,
             user_id INTEGER NOT NULL,
             FOREIGN KEY (event_id) REFERENCES events(id),
             FOREIGN KEY (user_id) REFERENCES users(id))''')
    execute_sql('''
             Create UNIQUE INDEX event_id ON event_attendees (event_id)''')
    print("Event attendees table created")


#not yet used
def create_event(name, description, date, time, location, user_id):
    execute_sql('''INSERT INTO event
             (name = ?, description = ?, date = ?, time = ?, location = ?, user_id = ?)''', 
             (name, description, date, time, location, user_id))

#not yet used
def update_event(name, description, date, time, location, user_id, id):
    execute_sql('''UPDATE events
             SET name = ?, description = ?, date = ?, time = ?, location = ?, user_id = ?
             WHERE id = ?''', 
             (name, description, date, time, location, user_id, id))

def delete_event(id):
    execute_sql('''DELETE FROM events WHERE id = ?''', (id))

def get_events():
    return execute_sql('''SELECT * FROM events''')

def get_event():
    return execute_sql('''SELECT * FROM events WHERE id = ?''', (id))

def get_user_events(user_id):
    return execute_sql('''SELECT * FROM events WHERE user_id = ?''', (user_id))

def get_event_attendees(event_id):
    return execute_sql('''SELECT * FROM event_attendees WHERE event_id = ?''', (event_id))

def create_user(username, email, hash):
    execute_sql('''INSERT INTO users
             (username, email, hash) VALUES (?, ?, ?)''', (username, email, hash))

def check_email_exists(email):
    return execute_sql('''SELECT email FROM users WHERE email = ?''', (email))

def check_username_exists(username):
    return execute_sql('''SELECT username FROM users WHERE username = ?''', (username))

def get_username_and_hash(email):
    return execute_sql('''SELECT username, hash FROM users WHERE email = ?''', (email))

def get_user_id(username):
    return execute_sql('''SELECT id FROM users WHERE username = ?''', (username))
