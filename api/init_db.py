import sqlite3
import argparse
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_user(db, username, password):
    hashed_password = hash_password(password)
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    db.commit()
    print(f"User {username} created successfully.")

def main():
    parser = argparse.ArgumentParser(description="Initialize the database and create users.")
    parser.add_argument("--username", required=True, help="Username for the new user")
    parser.add_argument("--password", required=True, help="Password for the new user")

    args = parser.parse_args()

    db = sqlite3.connect("auth.db")

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

    # Create user
    create_user(db, args.username, args.password)

    db.close()

if __name__ == "__main__":
    main()