import sqlite3
from sqlite3 import Error
#Create sql3_connection
def sql3_connection(database):
    try:
        connection = sqlite3.connect(database, check_same_thread=False)
        print("Connection established for db")
        return connection
    except Error:
        print(Error)

con = sql3_connection("data.db")
#Creates user table if it doesn't exist
def init_UserTable():
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(username text primary_key, password text)")
    con.commit()

# Takes in user with username and password
def insert_User(username, password):
    cursor = con.cursor()
    cursor.execute("INSERT INTO users(username,password) VALUES(?,?)", (username, password))
    con.commit()
    print("User: "+ str(username)+ " has been entered")

# Checks to see if username exist, returns true if it does and false otherwise
def check_UserNameExists(username):
    cursor = con.cursor()
    cursor.execute("SELECT username FROM users WHERE username = (?)", (username,))
    output = cursor.fetchone()
    return output is not None

# Checks if a user with username and password exists
def check_UserExists(username, password):
    cursor = con.cursor()
    cursor.execute("SELECT password FROM users WHERE username = (?)", (username,))
    output = cursor.fetchone()
    if (output is not None and output[0] == password):
        return True
    else:
        return False

def display_AllUsers():
    cursor = con.cursor()
    cursor.execute("SELECT username FROM users")
    output = cursor.fetchall()
    return output

def get_Password(username):
    cursor = con.cursor()
    cursor.execute("SELECT password FROM users WHERE username = (?)", (username,))
    output = cursor.fetchone()
    if (output is not None):
        return output[0]
    else:
        return None
