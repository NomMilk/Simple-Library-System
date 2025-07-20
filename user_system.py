import pandas as pd
import os
import hashlib

EXCEL_FILE = "users.xlsx"

# Base member class
class Member:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password  # Note: should be hashed when stored
        self.email = email

    def can_request_book(self):
        return True

    def can_manage_users(self):
        return False

# Guest class
class Guest:
    def __init__(self):
        self.username = "Guest"

    def can_request_book(self):
        return False

    def can_manage_users(self):
        return False

    def is_guest(self):
        return True

# Member subclass
class LibraryMember(Member):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)

# Staff subclass
class LibraryStaff(Member):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)

    def can_manage_users(self):
        return True

# User manager class to interface with login spreadsheet
class UserManager:
    def __init__(self):
        if not os.path.exists(EXCEL_FILE):
            df = pd.DataFrame(columns=["username", "password", "email", "role"])
            df.to_excel(EXCEL_FILE, index=False)

    #password hash
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    #load users(self explanatory)
    def load_users(self):
        return pd.read_excel(EXCEL_FILE)
    
    #add user method/registration
    def add_user(self, username, password, email, role="member"):
        df = self.load_users()
        #loads users and checks if the username is duplicated
        if username in df["username"].values:
            raise ValueError("Username already exists.")
        #hashes new password
        hashed = self.hash_password(password)
        #creates impliments row for the user
        df = pd.concat([df, pd.DataFrame([{
            "username": username,
            "password": hashed,
            "email": email,
            "role": role
        }])], ignore_index=True)

        df.to_excel(EXCEL_FILE, index=False)

    #validates user credentials
    def validate_login(self, username, password):
        df = self.load_users()
        hashed = self.hash_password(password)

        user = df[(df["username"] == username) & (df["password"] == hashed)]
        if user.empty:
            raise ValueError("Invalid username or password.")
        return self.create_user_object(username)
    #create user object and sort into staff or member
    def create_user_object(self, username):
        df = self.load_users()
        row = df[df["username"] == username].iloc[0]
        if row["role"] == "staff":
            return LibraryStaff(row["username"], row["password"], row["email"])
        else:
            return LibraryMember(row["username"], row["password"], row["email"])