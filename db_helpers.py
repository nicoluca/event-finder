import sqlite3
from sqlite3 import Error

from datetime import datetime


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
    print("Connection to SQLite DB successful")

def execute_sql(sql, params=None):
    with sqlite3.connect(db_name, check_same_thread=False) as conn:
        if params:
            print(params)
            cursor = conn.execute(sql, params)
        else:
            cursor = conn.execute(sql)
        return cursor.fetchall()

def create_event_table_if_not_exists():
    execute_sql('''CREATE TABLE IF NOT EXISTS events
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             description TEXT NOT NULL,
             datetime DATETIME NOT NULL,
             location TEXT NOT NULL,
             user_id INTEGER NOT NULL,
             FOREIGN KEY (user_id) REFERENCES users(id))''')
    execute_sql('''
             Create UNIQUE INDEX IF NOT EXISTS name ON events (name)''')
    print("Event table created or found")

def create_user_table_if_not_exists():
    execute_sql('''CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            username TEXT NOT NULL,
            hash TEXT NOT NULL)''')
    execute_sql('''
             Create UNIQUE INDEX IF NOT EXISTS username ON users (username)''')
    print("User table created or found")


def create_event_attendees_table_if_not_exists():
    execute_sql('''CREATE TABLE IF NOT EXISTS event_attendees
             (event_id INTEGER NOT NULL,
             user_id INTEGER NOT NULL,
             PRIMARY KEY (event_id, user_id),
             FOREIGN KEY (event_id) REFERENCES events(id),
             FOREIGN KEY (user_id) REFERENCES users(id))''')
    print("Event attendees table created or found")


def create_event(name, description, datetime_str, location, user_id):
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
    #formatted_datetime = datetime.strftime('%Y-%m-%d %H:%M:%S')    
    execute_sql('''INSERT INTO events
             (name, description, datetime, location, user_id) 
             VALUES (?, ?, ?, ?, ?)''', 
             (name, description, datetime_obj, location, user_id))

#not yet used
#def update_event(name, description, date, time, location, user_id, id):
#    execute_sql('''UPDATE events
#             SET name = ?, description = ?, date = ?, time = ?, location = ?, user_id = ?
#             WHERE id = ?''', 
#             (name, description, datetime, location, user_id, id))

def delete_event(id):
    execute_sql('''DELETE FROM events WHERE id = ?''', (id,))

def get_events():
    return execute_sql('''SELECT * FROM events ORDER BY datetime DESC''')

def get_event(id):
    return execute_sql('''SELECT * FROM events WHERE id = ?''', (id,))

def get_events_by_organiser(user_id):
    return execute_sql('''SELECT * FROM events WHERE user_id = ?''', (user_id,))

def get_event_attendees(event_id):
    return execute_sql('''SELECT * FROM event_attendees WHERE event_id = ?''', (event_id,))

def create_user(username, email, hash):
    execute_sql('''INSERT INTO users
             (username, email, hash) VALUES (?, ?, ?)''', (username, email, hash))

def check_email_exists(email):
    return execute_sql('''SELECT email FROM users WHERE email = ?''', (email,))

def check_username_exists(username):
    return execute_sql('''SELECT username FROM users WHERE username = ?''', (username,))

def get_username_and_hash(email):
    print(email)
    return execute_sql('''SELECT username, hash FROM users WHERE email = ?''', (email,))

def get_user_id_from_email(email):
    return execute_sql('''SELECT id FROM users WHERE email = ?''', (email,))[0][0]

def get_user_id(username):
    return execute_sql('''SELECT id FROM users WHERE username = ?''', (username,))

def get_username(user_id):
    return execute_sql('''SELECT username FROM users WHERE id = ?''', (user_id,))[0][0]

def join_event(user_id, event_id):
    print(user_id, event_id)
    execute_sql('''INSERT INTO event_attendees
             (user_id, event_id) VALUES (?, ?)''', (user_id, event_id))
    
def check_user_is_attending_event(user_id, event_id):
    # Return a boolean
    if execute_sql('''SELECT * FROM event_attendees WHERE user_id = ? AND event_id = ?''', (user_id, event_id)):
        return True
    else:
        return False
    
def leave_event(user_id, event_id):
    execute_sql('''DELETE FROM event_attendees WHERE user_id = ? AND event_id = ?''', (user_id, event_id))

def get_events_by_attendee(user_id):
    print("get_events_by_attendee")
    print(execute_sql('''SELECT * FROM events WHERE id IN (SELECT event_id FROM event_attendees WHERE user_id = ?)''', (user_id,)))
    return execute_sql('''SELECT * FROM events WHERE id IN (SELECT event_id FROM event_attendees WHERE user_id = ?)''', (user_id,))

def get_number_of_attendees(event_id):
    return execute_sql('''SELECT COUNT(*) FROM event_attendees WHERE event_id = ?''', (event_id,))[0][0]