import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
from dotenv import load_dotenv
import os
import s3access  # import s3access module

# ---------------- Load Environment Variables ----------------
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# ---------------- MySQL Connection ----------------
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
    return connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, new_email):
    connection = create_connection()
    cursor = connection.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, new_email, hashed_password)
        )
        connection.commit()
        st.success("User registered successfully!")
    except mysql.connector.Error as e:
        st.error(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def login_user(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    hashed_password = hash_password(password)
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password_hash=%s",
        (username, hashed_password)
    )
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

# ---------------- Session State Defaults ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

if "login_username" not in st.session_state:
    st.session_state.login_username = ""
if "login_password" not in st.session_state:
    st.session_state.login_password = ""

if "register_username" not in st.session_state:
    st.session_state.register_username = ""
if "register_password" not in st.session_state:
    st.session_state.register_password = ""
if "register_email" not in st.session_state:
    st.session_state.register_email = ""

# ---------------- Main Interface ----------------
st.title("Login/Register")

# ---------------- Redirect if logged in ----------------
if st.session_state.logged_in:
    s3access.run()
else:
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    # ---------------- Registration ----------------
    if choice == "Register":
        st.subheader("Create a New Account")
        new_email = st.text_input("Email ID", key="register_email")
        new_user = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
        if st.button("Register"):
            if new_user and new_password and new_email:
                if new_user.lower() != "marsrover":
                    st.error("Only the username 'marsrover' is allowed to create an account.")
                else:
                    register_user(new_user, new_password, new_email)
                # Clear registration fields
                st.session_state.register_username = ""
                st.session_state.register_password = ""
                st.session_state.register_email = ""
            else:
                st.warning("Please provide username, email, and password")

    # ---------------- Login ----------------
    elif choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if username and password:
                if username.lower() != "marsrover":
                    st.error("allowed to log in.")
                else:
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success(f"Logged in as {username}")
                        s3access.run()
                    else:
                        st.error("Invalid username or password")
                # Clear login fields after button press
                st.session_state.login_username = ""
                st.session_state.login_password = ""
            else:
                st.warning("Please provide both username and password")
                # Also clear if incomplete
                st.session_state.login_username = ""
                st.session_state.login_password = ""
