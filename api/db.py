import sqlite3
import argparse
import bcrypt
import os

db_path = "db/auth.db"

def initialize_database(db_path: str):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to the database (this will create the file if it doesn't exist)
    db = sqlite3.connect(db_path)

    # Create users table if it doesn't exist
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)
    db.commit()
    db.close()
    print(f"Database initialized at {db_path}")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_user(db_path:str, username:str, password:str) -> bool:
    try :
        hashed_password = hash_password(password)
        db=sqlite3.connect(db_path)
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        db.commit()
        db.close()
        print(f"User {username} created successfully.")
        return { "success": True, "message":f"User {username} created successfully." }
    except sqlite3.IntegrityError:
        print(f"User {username} already exists.")
        return { "success": False, "message":f"User {username} already exists." }
    except Exception as e:
        print(f"An error occurred: {e}")
        return { "success": False, "message":f"An error occurred: {e}" }

def main():
    parser = argparse.ArgumentParser(description="Initialize the database and create users.")
    parser.add_argument("--init", action="store_true", help="Initialize the database")
    parser.add_argument("--username", help="Username for the new user")
    parser.add_argument("--password", help="Password for the new user")

    args = parser.parse_args()

    
    if args.init:
        initialize_database(db_path)
    elif args.username and args.password:
        create_user(db_path, args.username, args.password)
    else:
        parser.error("You must specify either --init to initialize the database or both --username and --password to create a user.")

if __name__ == "__main__":
    main()