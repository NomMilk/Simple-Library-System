from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
import pandas as pd
import os
import hashlib


app = Flask(__name__)
CORS(app)
EXCEL_FILE = "users.xlsx"

# if else to create the spreadsheet
def init_user_file():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["username", "password", "email", "role"])
        df.to_excel(EXCEL_FILE, index=False)

# Hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load current users from Excel
def load_users():
    return pd.read_excel(EXCEL_FILE)

# Add new user
def add_user(username, password, email, role="member"):
    df = load_users()
    if username in df["username"].values:
        raise ValueError("Username already exists.")
    
    new_user = pd.DataFrame([{
        "username": username,
        "password": hash_password(password),
        "email": email,
        "role": role
    }])
    
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
#Flask route to handle book excel
@app.route("/books")
def show_books():
    try:
        df = pd.read_excel("BookList.xlsx")
        books = df.to_dict(orient="records")
        return render_template("books.html", books=books)
    except Exception as e:
        import traceback
        traceback.print_exc()  # 🔍 Print full error to terminal
        return f"Error loading books: {str(e)}", 500
# Flask route to handle POST /register
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    try:
        add_user(
            username=data["username"],
            password=data["password"],
            email=data["email"],
            role=data.get("role", "member")
        )
        return jsonify({"message": "Account created successfully."}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500
    
#Flask route to handle post /login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    try:
        df = load_users()
        hashed = hash_password(data["password"])
        
        user = df[(df["username"] == data["username"]) & (df["password"] == hashed)]

        if user.empty:
            raise ValueError("Invalid username or password.")

        row = user.iloc[0]
        session["username"] = row["username"]
        session["role"] = row["role"]
        session["email"] = row["email"]

        return jsonify({
            "message": f"Login successful. Welcome, {row['username']}!",
            "role": row["role"]
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500


if __name__ == "__main__":
    init_user_file()
    app.run(debug=True)
