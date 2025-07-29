import smtplib
from email.message import EmailMessage
from datetime import datetime
import pandas as pd

# Email account config (fake creds)
LIBRARY_EMAIL = "libralinkcpsc@gmail.com"
LIBRARY_PASSWORD = "qdgp tlkt ednf ycui"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_overdue_emails():
    try:
        # Load book and user data
        book_df = pd.read_excel("BookList.xlsx")
        user_df = pd.read_excel("users.xlsx")

        today = datetime.now().date()

        # Filter books that are overdue and checked out
        book_df["Expected Return"] = pd.to_datetime(book_df["Expected Return"], errors="coerce")
        overdue_books = book_df[
            (book_df["Expected Return"].notna()) &
            (book_df["Expected Return"].dt.date < today) &
            (book_df["In Stock"].str.strip().str.lower() == "no")
        ]

        # Prepare and send emails
        for _, book in overdue_books.iterrows():
            username = book["Who Checked"]
            user_row = user_df[user_df["username"] == username]

            if user_row.empty:
                continue  # Skip if no matching user found

            user_email = user_row.iloc[0]["email"]
            book_title = book["Title"]
            due_date = book["Expected Return"].strftime("%Y-%m-%d")

            msg = EmailMessage()
            msg["Subject"] = f"📚 Overdue Book Reminder - {book_title}"
            msg["From"] = LIBRARY_EMAIL
            msg["To"] = user_email
            msg.set_content(f"""
Hi {username},

This is a reminder that your borrowed book:

    📖 Title: {book_title}
    📅 Was due: {due_date}

Please return it to the library as soon as possible or reach out if an extension is needed.

Thank you,
LibraLink Library System
""")

            # Send the email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(LIBRARY_EMAIL, LIBRARY_PASSWORD)
                server.send_message(msg)

            print(f"✅ Email sent to {username} ({user_email}) for book: {book_title}")

    except Exception as e:
        print(f"❌ Failed to send overdue emails: {e}")
