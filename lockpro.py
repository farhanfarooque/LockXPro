import hashlib
import random
import time
import mysql.connector
import smtplib
from cryptography.fernet import Fernet

class LockXPro:
    def __init__(self):
        self.db = None
        self.cursor = None
        self.master_password = None
        self.email = None
        self.db_name = None
        self.table_name = None
        self.key = Fernet.generate_key()

    def display_intro(self):
        print("Welcome to LockXPro. Your personal password manager.")

    def set_master_password(self):
        self.master_password = input("Set your master password: ")
        hashed_password = self.hash_password(self.master_password)

    def save_hashed_password(self, hashed_password):
        with open("master_password_hash.txt", "w") as file:
            file.write(hashed_password)

    def load_hashed_password(self):
        try:
            with open("master_password_hash.txt", "r") as file:
                return file.read()
        except FileNotFoundError:
            print("No master password set. Please set up a new master password.")
            return None

    def set_master_password(self):
        self.master_password = input("Set your master password: ")
        hashed_password = self.hash_password(self.master_password)
        self.save_hashed_password(hashed_password)

    def verify_master_password(self):
        entered_password = input("Enter your master password to continue: ")
        hashed_entered_password = self.hash_password(entered_password)
        saved_hashed_password = self.load_hashed_password()

        return hashed_entered_password == saved_hashed_password

    def run(self):
        self.display_intro()

        if not self.load_hashed_password():
            self.set_master_password()

        if self.verify_master_password():
            self.setup_database()
            while True:
                choice = input("Choose an option: [1] Add Password, [2] Retrieve Password, [3] Exit: ")
                if choice == '1':
                    self.add_password()
                elif choice == '2':
                    self.retrieve_password()
                elif choice == '3':
                    break
                else:
                    print("Invalid choice. Please try again.")
        else:
            print("Invalid master password. Exiting program.")


    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def setup_database(self):
        db_password = input("Enter your MySQL password: ")
        self.db = mysql.connector.connect(host='localhost', user='root', password=db_password)
        self.cursor = self.db.cursor()
        self.db_name = input("Enter database name: ")
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
        self.cursor.execute(f"USE {self.db_name}")
        self.setup_table()

    def setup_table(self):
        self.table_name = input("Enter table name for storing passwords: ")
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    url VARCHAR(255),
                                    username VARCHAR(255),
                                    password VARCHAR(255)
                                );"""
        self.cursor.execute(create_table_query)

    def add_password(self):
        url = input("Enter the URL: ")
        username = input("Enter the username: ")
        password = input("Enter the password: ")
        # Encrypt the password here using self.key
        encrypted_password = self.encrypt_password(password)
        insert_query = f"INSERT INTO {self.table_name} (url, username, password) VALUES (%s, %s, %s)"
        self.cursor.execute(insert_query, (url, username, encrypted_password))
        self.db.commit()

    def encrypt_password(self, password):
        f = Fernet(self.key)
        return f.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        f = Fernet(self.key)
        return f.decrypt(encrypted_password.encode()).decode()

    def retrieve_password(self):
        url = input("Enter the URL to find the password: ")
        query = f"SELECT username, password FROM {self.table_name} WHERE url = %s"
        self.cursor.execute(query, (url,))
        result = self.cursor.fetchone()
        if result:
            username, encrypted_password = result
            password = self.decrypt_password(encrypted_password)
            print(f"Username: {username}, Password: {password}")
        else:
            print("No data found for the given URL.")

    def run(self):
        self.display_intro()
        self.set_master_password()
        self.setup_database()
        while True:
            choice = input("Choose an option: [1] Add Password, [2] Retrieve Password, [3] Exit: ")
            if choice == '1':
                self.add_password()
            elif choice == '2':
                self.retrieve_password()
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")

def main():
    manager = LockXPro()
    manager.run()

if __name__ == "__main__":
    main()
