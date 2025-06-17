import imaplib
import os
import json
from pyexpat import model
import re
from numpy import vectorize
import psycopg2
import joblib
import email
import nltk
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


# Download required NLTK data
nltk.download("punkt")
nltk.download("stopwords")

app = FastAPI()

# CORS settings – allow your Angular app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL Database configuration
DB_CONFIG = {
    "dbname": "email_db",
    "user": "postgres",
    "password": "ps",
    "host": "localhost",
    "port": 5432,
}

# Helper: Get a new database connection
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# Ensure required tables exist
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)
    # Create emails table (for storing classified emails)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id SERIAL PRIMARY KEY,
            user_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            classification TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

create_tables()

# Load and Save users in data.json
def load_users():
    if os.path.exists("data.json"):
        with open("data.json", "r") as file:
            return json.load(file)["users"]
    return []

def save_users(users):
    with open("data.json", "w") as file:
        json.dump({"users": users}, file, indent=4)



# @app.get("/emails/")
# async def get_emails():
#     users = load_users()
#     if not users:
#         raise HTTPException(status_code=404, detail="No users found.")

#     all_emails = []
#     for user in users:
#         all_emails.append({
#             "email": user["email"],
#             "classification": "ham"  # Example classification
#         })

#     return {"emails": all_emails}

# Pydantic model for login/registration request
class LoginRequest(BaseModel):
    email: str
    password: str

# Authenticate user by checking data.json and database
def authenticate_user(email: str, password: str):
    users = load_users()
    for user in users:
        if user["email"] == email and user["password"] == password:
            print(f"✅ User {email} authenticated via data.json!")
            return True
    # Check in PostgreSQL
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            print(f"✅ User {email} authenticated via PostgreSQL!")
            return True
    except Exception as e:
        print("❌ Database Error:", e)
    print(f"❌ Authentication failed for {email}")
    return False

# Register new user – append to data.json and insert into the database
def register_user(email: str, password: str):
    users = load_users()
    # If user exists, skip registration
    for user in users:
        if user["email"] == email:
            return
    users.append({"email": email, "password": password})
    save_users(users)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        conn.close()
        print(f"✅ User {email} registered successfully!")
    except Exception as e:
        print("❌ Error saving user to database:", e)

# Login endpoint – if user is new, register them; if existing, authenticate
@app.post("/login/")
def login(request: LoginRequest):
    if authenticate_user(request.email, request.password):
        return {"message": "Login successful"}
    # If not found, register new user and then consider login successful
    register_user(request.email, request.password)
    return {"message": "New user registered and logged in"}

# Fetch emails using IMAP
def fetch_emails_imap(user_email, user_password, max_emails=10):
    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user_email, user_password)
        mail.select("inbox")

        # Search for all emails in the inbox
        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()[-max_emails:]  # Get latest 'max_emails' emails

        emails = []
        for e_id in reversed(email_ids):  # Fetch newest emails first
            result, msg_data = mail.fetch(e_id, "(RFC822)")
            if result != "OK":
                continue

            # Parse the email content
            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg["Subject"]
            body = ""

            # Extract email body (plain text only)
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            emails.append({"subject": subject, "body": body})

        mail.logout()
        return emails

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IMAP Error: {str(e)}")

# Store fetched emails in DB
def store_emails_in_db(user_email, emails):
    conn = get_db_connection()
    cursor = conn.cursor()
    for email_data in emails:
        cursor.execute(
            "INSERT INTO emails (user_email, subject, body, classification) VALUES (%s, %s, %s, %s)",
            (user_email, email_data["subject"], email_data["body"], "Unclassified"),
        )
    conn.commit()
    conn.close()

# Get emails endpoint
@app.post("/emails/")
def get_emails(request: LoginRequest):
    if not authenticate_user(request.email, request.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    emails = fetch_emails_imap(request.email, request.password, max_emails=10)
    store_emails_in_db(request.email, emails)
    return {"emails": emails}

print("✅ Backend is running successfully!")