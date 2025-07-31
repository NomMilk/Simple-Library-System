Project Description: 
A software system that manages the operations of a library. It will allow for users to quickly search for books, lend books, process returns, and manage members. The system will also generate reports for library staff and send overdue notices to members via email. 

Hai-Duong To - QA and Documentation
Homan Qiu - Front-end Developer
Jerrel Durgin - Back-end Developer
Sean Evasco - PM

 The following Python packages are necessary to run this program:

- Flask (`flask`)
- Flask-CORS (`flask-cors`)
- Pandas (`pandas`)
- OpenPyXL (`openpyxl`)

You can install everything at once with:

```bash
pip install -r requirements.txt

Note: The 'openpyxl' package is necessary to read/write Excel (.xlsx) files.

--------------------------------------------------
Running the Local Server
--------------------------------------------------

1. Open your terminal or command prompt.
2. Navigate to the project folder:

    cd path/to/Simple-Library-System

3. Start the Flask server:

    python userlogin.py

4. Open your browser and visit:

    http://localhost:5000/
or alternatively,

    http://127.0.0.1:5000/

You should see the LibraLink homepage.

Project Structure
=================

Simple-Library-System/
│
├── userlogin.py              – Main Flask application with routes for login, book management,
│                              account, staff dashboard, requests, email reminders, etc.
├── user_system.py            – Optional helper module defining UserManager and user/role classes
│
├── BookList.xlsx             – Excel sheet tracking all books (Title, Author, Genre, ISBN,
│                              In Stock, Who Checked, Expected Return, etc.)
├── BookRequests.xlsx         – Tracks requests from users (username, ISBN, title, status)
└── users.xlsx                – User accounts: username, hashed password, email, role
│
├── templates/                – Jinja HTML templates
│   ├── index.html            – Homepage (landing page)
│   ├── books.html            – Book catalog page with filters, search, sorting
│   ├── book_detail.html      – Single-book details and request form
│   ├── account.html          – User account page with rented books & password change form
│   ├── sign_in.html          – Login form design
│   ├── register.html         – Account creation form
│   ├── staff_dashboard.html  – Dashboard for staff: pending requests, overdue books, selectors
│
├── static/                   – Static web assets
│   └── Css/
│       ├── Global.css        – Core styling using LibraLink color palette
│       ├── SubTabs.css       – Subsection/tab styles
│       └── StaffDashboard.css– Optional CSS for staff-dashboard specific styling
│   └── Scripts/
│       ├── MoveDownWhileScroll.js – Custom scroll behavior script
│   └── fonts/
│       └── Roboto.ttf        – Base typeface used globally
│
└── requirements.txt          – Lists Python dependencies:
                             flask
                             flask-cors
                             pandas
                             openpyxl
--------------------------------------------------
notes
--------------------------------------------------

- Make sure Excel files exist before running the app.
- All `.xlsx` files must have correct column headers.
- Use the same Python environment where packages are installed.
- Default Flask port is 5000, please make sure it's not blocked.