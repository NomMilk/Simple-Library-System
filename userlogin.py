from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_cors import CORS
import pandas as pd
import os
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
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
#Flask route for the home page
@app.route("/")
def home():
    return render_template("index.html")

#Flask route to handle book excel
@app.route("/books")
def show_books():
    try:
        df = pd.read_excel("BookList.xlsx")
        books = df.to_dict(orient="records")

        # Unique genres and years
        genres = sorted(df["Genre"].dropna().unique())
        years = sorted(df["Year"].dropna().unique())

        return render_template("books.html", books=books, genres=genres, years=years)
    except Exception as e:
        return f"Error loading books: {str(e)}", 500
# Flask route to handle POST and get /register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    data = request.get_json() or request.form
    try:
        add_user(
            username=data["username"],
            password=data["password"],
            email=data["email"],
            role=data.get("role", "member")
        )
        # Redirect to home after successful registration
        return redirect(url_for("home"))
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500

    
#Flask route to handle post and get /login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("sign_in.html")

    try:
        # Handle both fetch JSON or form data
        data = request.get_json() or request.form
        print("Login data received:", data)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return "Missing username or password", 400

        df = load_users()
        hashed = hash_password(password)

        user = df[(df["username"] == username) & (df["password"] == hashed)]

        if user.empty:
            return "Invalid username or password", 401

        row = user.iloc[0]
        session["username"] = row["username"]
        session["role"] = row["role"]
        session["email"] = row["email"]

        return redirect(url_for("home"))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Server error: {e}", 500

#Flask route for book pages
@app.route("/book/<isbn>")
def book_detail(isbn):
    try:
        df = pd.read_excel("BookList.xlsx")
        book = df[df["ISBN"].astype(str) == str(isbn)]

        if book.empty:
            return f"Book with ISBN {isbn} not found", 404

        book_data = book.iloc[0].to_dict()
        return render_template("book_detail.html", book=book_data)

    except Exception as e:
        return f"Error loading book: {str(e)}", 500
@app.route("/request-book/<isbn>", methods=["POST"])
def request_book(isbn):
    if "username" not in session:
        return "You must be logged in to request a book", 403

    try:
        # Load book data
        df = pd.read_excel("BookList.xlsx")
        book = df[df["ISBN"].astype(str) == str(isbn)]

        if book.empty:
            return f"Book with ISBN {isbn} not found", 404

        book_title = book.iloc[0]["Title"]
        requester = session["username"]

        # Append to a requests Excel sheet
        req_file = "BookRequests.xlsx"
        if os.path.exists(req_file):
            req_df = pd.read_excel(req_file)
        else:
            req_df = pd.DataFrame(columns=["username", "isbn", "title", "status"])

        new_request = {
            "username": requester,
            "isbn": isbn,
            "title": book_title,
            "status": "Pending"
        }

        req_df = pd.concat([req_df, pd.DataFrame([new_request])], ignore_index=True)
        req_df.to_excel(req_file, index=False)

        return redirect(url_for('book_detail', isbn=isbn))

    except Exception as e:
        return f"Error processing request: {str(e)}", 500
#Flask route to staff dashboard
@app.route("/staff-dashboard")
def staff_dashboard():
    #if session.get("role") != "staff":
       # return "Access denied", 403

    # Load user accounts
    users = pd.read_excel("users.xlsx").to_dict(orient="records")

    # Load book requests
    try:
        requests_df = pd.read_excel("BookRequests.xlsx")
        requests = requests_df.to_dict(orient="records")
    except:
        requests = []

    return render_template("staff_dashboard.html", users=users, requests=requests)
#Flask route to account page
@app.route("/account")
def account_page():
    if "username" not in session:
        return redirect(url_for("register"))

    username = session["username"]
    try:
        df = pd.read_excel("BookList.xlsx")
        rented = df[df["Who Checked"] == username]
        rented_books = rented[["Title", "ISBN", "Expected Return"]].rename(columns={
            "Title": "title",
            "ISBN": "isbn",
            "Expected Return": "expected_return"
        }).to_dict(orient="records")
    except:
        rented_books = []

    return render_template("account.html",
                           username=username,
                           email=session["email"],
                           role=session["role"],
                           rented_books=rented_books)

@app.route("/register-page")
def register_page():
    return render_template("register.html")
# flask route for changing passwords
@app.route("/change-password", methods=["POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))

    data = request.form
    current_pw = data.get("current_password")
    new_pw = data.get("new_password")
    confirm_pw = data.get("confirm_password")

    if new_pw != confirm_pw:
        return "Passwords do not match", 400

    df = load_users()
    hashed_current = hash_password(current_pw)
    user_idx = df[(df["username"] == session["username"]) & (df["password"] == hashed_current)].index

    if user_idx.empty:
        return "Current password incorrect", 403

    df.loc[user_idx[0], "password"] = hash_password(new_pw)
    df.to_excel(EXCEL_FILE, index=False)

    return redirect(url_for("account_page"))
#flask route for book requests
@app.route("/handle-request", methods=["POST"])
def handle_request():
    isbn = request.form.get("isbn")
    username = request.form.get("username")
    action = request.form.get("action")  # 'approve' or 'deny'

    if not isbn or not username or not action:
        return "Invalid request", 400

    # Load book request sheet
    req_file = "BookRequests.xlsx"
    if not os.path.exists(req_file):
        return "No request file found", 404

    df = pd.read_excel(req_file)

    # Find the request by both ISBN and username
    idx = df[(df["isbn"].astype(str) == str(isbn)) & (df["username"] == username)].index

    if not idx.empty:
        status = "Approved" if action == "approve" else "Denied"
        df.at[idx[0], "status"] = status
        df.to_excel(req_file, index=False)

        # Update book availability only if approved
        if status == "Approved":
            books_df = pd.read_excel("BookList.xlsx")
            book_idx = books_df[books_df["ISBN"].astype(str) == str(isbn)].index

            if not book_idx.empty:
                books_df.at[book_idx[0], "In Stock"] = "No"
                books_df.at[book_idx[0], "Who Checked"] = username
                books_df.to_excel("BookList.xlsx", index=False)

        return redirect(url_for("staff_dashboard"))

    return "Request not found", 404


if __name__ == "__main__":
    init_user_file()
    app.run(debug=True)
