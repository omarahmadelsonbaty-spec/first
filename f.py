import sqlite3
import re
import hashlib
import os

# Password requirements: at least 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
regex_password = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

# Connect to database
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Initialize Database with password column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT UNIQUE, 
        age INTEGER, 
        password TEXT,
        current_user BOOLEAN DEFAULT 0
    )
''')
conn.commit()


def hash_password(password):
    """Securely hash password using PBKDF2-HMAC with a unique salt."""
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return salt.hex() + ':' + pwd_hash.hex()


def verify_password(stored_password, provided_password):
    """Verify a stored hash against a provided password."""
    try:
        salt_hex, hash_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100_000)
        return pwd_hash.hex() == hash_hex
    except Exception:
        return False


def user_exists(name):
    """Helper to check if a username exists in SQLite."""
    row = cursor.execute("SELECT 1 FROM users WHERE name = ?", (name,)).fetchone()
    return row is not None


def set_active_user(name):
    """Sets a specific user as active and deactivates all others."""
    cursor.execute("UPDATE users SET current_user = 0")
    if name:
        cursor.execute("UPDATE users SET current_user = 1 WHERE name = ?", (name,))
    conn.commit()


def create():
    while True:
        name = input("\nEnter your name (or type 'exit' to quit): ").strip().lower()
        if name == 'exit':
            return
        if not name:
            print("Name cannot be empty. Please try again.")
            continue
        if user_exists(name):
            print(f"User '{name}' already exists. Please try again.")
            continue

        while True:
            age_input = input("Enter your age: ").strip()
            if age_input.isdigit() and int(age_input) > 0:
                age = int(age_input)
                break
            print("Age must be a positive integer. Please try again.")

        while True:
            password = input("Enter your password: ").strip()
            if password == "":
                print("Password cannot be empty. Please try again.")
            elif not re.match(regex_password, password):
                print("Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
            else:
                confirmation = input(f"Are you sure you want to use username: {name}, age: {age}? (yes/no): ").strip().lower()
                if confirmation == 'yes':
                    hashed_pw = hash_password(password)
                    cursor.execute(
                        "INSERT INTO users (name, age, password, current_user) VALUES (?, ?, ?, 0)",
                        (name, age, hashed_pw)
                    )
                    conn.commit()
                    set_active_user(name)
                    print(f"User '{name}' created and logged in successfully.")
                    dashboard()
                    return
                elif confirmation == 'no':
                    print("User creation cancelled.")
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")


def login():
    while True:
        name = input("\nEnter your name to login (or type 'exit' to quit): ").strip().lower()
        if name == 'exit':
            return
        if not name:
            print("Name cannot be empty. Please try again.")
            continue
        
        row = cursor.execute("SELECT password FROM users WHERE name = ?", (name,)).fetchone()
        if not row:
            print(f"User '{name}' does not exist. Please try again.")
            continue
        
        stored_password = row[0]
        remaining_attempts = 3
        
        while remaining_attempts > 0:
            password = input("Enter your password: ").strip()
            if verify_password(stored_password, password):
                set_active_user(name)
                print(f"User '{name}' logged in successfully.")
                dashboard()
                return
            else:
                remaining_attempts -= 1
                print(f"Incorrect password. Remaining attempts: {remaining_attempts}")
        
        print("Too many failed attempts. Returning to main menu.")
        return


def change_user_detail():
    while True:
        choice = input("\nWhat would you like to change? (name/age/cancel): ").strip().lower()
        if choice == "cancel":
            break
        elif choice == "name":
            new_name = input("Enter new name: ").strip().lower()
            if not new_name:
                print("Name cannot be empty.")
            elif user_exists(new_name):
                print(f"User '{new_name}' already exists.")
            else:
                cursor.execute("UPDATE users SET name = ? WHERE current_user = 1", (new_name,))
                conn.commit()
                print(f"Name changed to '{new_name}' successfully.")
                break
        elif choice == "age":
            new_age = input("Enter new age: ").strip()
            if not new_age.isdigit() or int(new_age) <= 0:
                print("Age must be a positive integer.")
            else:
                cursor.execute("UPDATE users SET age = ? WHERE current_user = 1", (int(new_age),))
                conn.commit()
                print(f"Age changed to '{new_age}' successfully.")
                break
        else:
            print("Invalid option. Please enter 'name', 'age', or 'cancel'.")


def dashboard():
    while True:
        current_user = cursor.execute("SELECT name, age FROM users WHERE current_user = 1").fetchone()
        if not current_user:
            print("\nNo user is currently logged in.")
            break

        print(f"\n--- Dashboard ({current_user[0].title()}) ---")
        print("1. View Profile")
        print("2. Change Details")
        print("3. Logout")
        print("4. Back to Main Menu")

        choice = input("Enter choice: ").strip().lower()

        if choice in ("1", "view"):
            print(f"\n[Profile] Name: {current_user[0].title()}, Age: {current_user[1]}")
        elif choice in ("2", "change"):
            change_user_detail()
        elif choice in ("3", "logout"):
            set_active_user(None)
            print("Logged out successfully.")
            break
        elif choice in ("4", "back", "exit"):
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    try:
        while True:
            print("\n=== Main Menu ===")
            print("1. Create User")
            print("2. Login")
            print("3. Exit")

            choice = input("Enter your choice: ").strip()

            if choice == '1':
                create()
            elif choice == '2':
                login()
            elif choice == '3':
                set_active_user(None)
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please try again.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()