from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from datetime import datetime, timedelta
from flask_cors import CORS
import pandas as pd
import os
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText

LIBRARY_EMAIL = "libralinkcpsc@gmail.com"
LIBRARY_PASSWORD = "qdgp tlkt ednf ycui"
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.jinja_env.globals.update(session=session)
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
#flask route for logging out
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))

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

    data = request.get_json()
    try:
        add_user(
            username=data["username"],
            password=data["password"],
            email=data["email"],
            role=data.get("role", "member")
        )

        # Log the user in immediately
        session["username"] = data["username"]
        session["email"] = data["email"]
        session["role"] = data.get("role", "member")

        # Return JSON with redirect info and success message
        return jsonify({
            "message": "✅ Account created successfully! Redirecting to home...",
            "redirect": url_for("home")
        }), 201

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
#flask route to request books
@app.route("/request-book/<isbn>", methods=["POST"])
def request_book(isbn):
    if "username" not in session:
        flash("You must be logged in to request a book.", "warning")
        return redirect(url_for("show_books"))

    try:
        # Load book list
        df = pd.read_excel("BookList.xlsx")
        df["ISBN"] = df["ISBN"].astype(str).str.strip()
        df["In Stock"] = df["In Stock"].astype(str).str.strip().str.lower()

        index = df[df["ISBN"] == str(isbn)].index
        if index.empty:
            flash("Book not found.", "error")
            return redirect(url_for("show_books"))

        # Check availability
        if df.at[index[0], "In Stock"] != "yes":
            flash("This book is currently checked out.", "warning")
            return redirect(url_for("show_books"))

        # Load or create request file
        req_file = "BookRequests.xlsx"
        if os.path.exists(req_file):
            req_df = pd.read_excel(req_file)
        else:
            req_df = pd.DataFrame(columns=["username", "isbn", "title", "status"])

        req_df["isbn"] = req_df["isbn"].astype(str).str.strip()
        req_df["username"] = req_df["username"].astype(str).str.strip()
        req_df["status"] = req_df["status"].astype(str).str.strip().str.lower()

        # Prevent duplicate request
        duplicate = req_df[
            (req_df["isbn"] == str(isbn)) &
            (req_df["username"] == session["username"]) &
            (req_df["status"] == "pending")
        ]

        if not duplicate.empty:
            flash("You have already submitted a request for this book.", "warning")
            return redirect(url_for("show_books"))

        # Add request
        new_request = {
            "username": session["username"],
            "isbn": str(isbn),
            "title": df.at[index[0], "Title"],
            "status": "Pending"
        }

        req_df = pd.concat([req_df, pd.DataFrame([new_request])], ignore_index=True)
        req_df.to_excel(req_file, index=False)

        flash(f"Request for '{new_request['title']}' submitted successfully.", "success")
        return redirect(url_for("show_books"))

    except Exception as e:
        flash(f"An error occurred while submitting your request: {str(e)}", "error")
        return redirect(url_for("show_books"))
    
#Flask route to staff dashboard
@app.route("/staff-dashboard")
def staff_dashboard():
    if session.get("role") != "staff":
        return "Access denied", 403

    users = pd.read_excel("users.xlsx").to_dict(orient="records")

    # Load book requests
    try:
        requests_df = pd.read_excel("BookRequests.xlsx")
        requests = requests_df.to_dict(orient="records")
    except:
        requests = []

    # Load book list and filter checked-out books
    try:
        books_df = pd.read_excel("BookList.xlsx")
        books_df["In Stock"] = books_df["In Stock"].astype(str).str.strip().str.lower()

        due_df = books_df[books_df["In Stock"] == "no"]
        due_books = due_df[["Title", "ISBN", "Who Checked", "Expected Return"]].to_dict(orient="records")
    except Exception as e:
        print("Book loading error:", e)
        due_books = []

    return render_template("staff_dashboard.html",
                           users=users,
                           requests=requests,
                           due_books=due_books)


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
from flask import request, redirect, url_for
from datetime import datetime, timedelta
from pandas import ExcelWriter
import pandas as pd
import os

@app.route("/handle-request", methods=["POST"])
def handle_request():
    isbn = request.form.get("isbn", "").strip()
    username = request.form.get("username", "").strip()
    action = request.form.get("action", "").strip().lower()

    print(f"📥 Handling request: ISBN={isbn}, User={username}, Action={action}")

    if not isbn or not username or not action:
        print("Missing parameters.")
        return "Invalid request", 400

    req_file = "BookRequests.xlsx"
    book_file = "BookList.xlsx"

    if not os.path.exists(req_file):
        print("Request file not found.")
        return "No request file found", 404

    try:
        req_df = pd.read_excel(req_file)
        print("📄 Loaded request file:")
        print(req_df)

        # Normalize formatting
        req_df["isbn"] = req_df["isbn"].astype(str).str.strip()
        req_df["username"] = req_df["username"].astype(str).str.strip()
        req_df["status"] = req_df["status"].astype(str).str.strip().str.lower()

        # Find all matching requests
        match = req_df[(req_df["isbn"] == isbn) & (req_df["username"] == username)]

        if match.empty:
            print("No matching request found.")
            return "Request not found", 404

        new_status = "approved" if action == "approve" else "denied"

        # Update all matching rows
        for i in match.index:
            print(f"📝 Updating index {i} to {new_status}")
            req_df.at[i, "status"] = new_status

        req_df.to_excel(req_file, index=False)
        print("✅ Request file updated.")

        # If approved, update the book list if it's in stock
        if new_status == "approved":
            if not os.path.exists(book_file):
                print("Book list file not found.")
                return "Book list not found", 500

            book_df = pd.read_excel(book_file)
            book_df["ISBN"] = book_df["ISBN"].astype(str).str.strip()
            book_df["In Stock"] = book_df["In Stock"].astype(str).str.strip().str.lower()

            book_match = book_df[book_df["ISBN"] == isbn]
            if not book_match.empty:
                book_idx = book_match.index[0]
                if book_df.at[book_idx, "In Stock"] == "yes":
                    book_df.at[book_idx, "In Stock"] = "No"
                    book_df.at[book_idx, "Who Checked"] = username
                    book_df.at[book_idx, "Expected Return"] = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
                    book_df.to_excel(book_file, index=False)
                    print(f"📚 Book {isbn} checked out by {username} with 2-week due date.")

        return redirect(url_for("staff_dashboard"))

    except Exception as e:
        print(f" Error during request handling: {e}")
        return f"Error handling request: {str(e)}", 500

#flask route for returning books
@app.route("/return-book", methods=["POST"])
def return_book():
    if "username" not in session:
        return redirect(url_for("register_page"))

    isbn = request.form.get("isbn")
    username = session["username"]

    try:
        df = pd.read_excel("BookList.xlsx")
        book_idx = df[(df["ISBN"].astype(str) == str(isbn)) & (df["Who Checked"] == username)].index

        if not book_idx.empty:
            df.at[book_idx[0], "In Stock"] = "Yes"
            df.at[book_idx[0], "Who Checked"] = ""
            df.to_excel("BookList.xlsx", index=False)
            return redirect(url_for("account_page"))
        else:
            return "Book not found or not checked out by you", 400

    except Exception as e:
        return f"Error returning book: {str(e)}", 500
@app.route("/extend-rental", methods=["POST"])
def extend_rental():
    if session.get("role") != "staff":
        return "Access denied", 403

    isbn = request.form.get("isbn")
    if not isbn:
        return "Missing ISBN", 400

    try:
        df = pd.read_excel("BookList.xlsx")

        index = df[df["ISBN"].astype(str) == str(isbn)].index
        if index.empty:
            return "Book not found", 404

        # Extend current due date by 14 days
        current_date_str = df.at[index[0], "Expected Return"]
        try:
            current_date = datetime.strptime(str(current_date_str), "%Y-%m-%d")
        except ValueError:
            # If original date includes time, strip it
            current_date = datetime.strptime(str(current_date_str).split()[0], "%Y-%m-%d")

        new_due = (current_date + timedelta(days=14)).strftime("%Y-%m-%d")
        df.at[index[0], "Expected Return"] = new_due
        df.to_excel("BookList.xlsx", index=False)

        return redirect(url_for("staff_dashboard"))

    except Exception as e:
        return f"Error extending rental: {str(e)}", 500
#flask route for email reminder
@app.route("/send-reminder/<isbn>/<username>", methods=["POST"])
def send_reminder(isbn, username):
    try:
        book_df = pd.read_excel("BookList.xlsx")
        user_df = pd.read_excel("users.xlsx")

        # Ensure string type
        book_df["ISBN"] = book_df["ISBN"].astype(str).str.strip()
        user_df["username"] = user_df["username"].astype(str).str.strip()

        book = book_df[book_df["ISBN"] == str(isbn)]
        user = user_df[user_df["username"] == username]

        if book.empty or user.empty:
            return "Book or user not found", 404

        email = user.iloc[0]["email"]
        title = book.iloc[0]["Title"]
        due_date = book.iloc[0].get("Expected Return", "soon")

        # Compose and send email
        subject = "Reminder: Your Library Book is Due Soon"
        body = f"Hello {username},\n\nThis is a reminder that your book \"{title}\" is due on {due_date}.\nPlease return it on time to avoid late penalties.\n\nThanks,\nLibraLink Team"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = LIBRARY_EMAIL
        msg["To"] = email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(LIBRARY_EMAIL, LIBRARY_PASSWORD)
            server.send_message(msg)

        print(f"Reminder sent to {username} ({email}) about '{title}'")

        return redirect(url_for("staff_dashboard"))
    except Exception as e:
        return f"Error sending reminder: {str(e)}", 500
@app.route("/clear-requests", methods=["POST"])
def clear_requests():
    if session.get("role") != "staff":
        return "Unauthorized", 403
    try:
        req_file = "BookRequests.xlsx"
        if os.path.exists(req_file):
            df = pd.DataFrame(columns=["username", "isbn", "title", "status"])
            df.to_excel(req_file, index=False)
        return redirect(url_for("staff_dashboard"))
    except Exception as e:
        return f"Error clearing requests: {str(e)}", 500

if __name__ == "__main__":
    init_user_file()
    app.run(debug=True)
