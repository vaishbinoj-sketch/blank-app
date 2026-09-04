import streamlit as st
# 🔴 HIDE SIDEBAR NAVIGATION (app / dashboard)
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)
#set the background of the website login page
gif_url="https://cdn.dribbble.com/userupload/21372029/file/original-c8948c19da21d1c1955c2dbd55ab8327.gif"
def set_gif_bg():
    gif_url = "https://cdn.dribbble.com/userupload/21372029/file/original-c8948c19da21d1c1955c2dbd55ab8327.gif"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
                        url("{gif_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 🔹 Apply background
set_gif_bg()

st.markdown(
    "<h1 style='font-family:Georgia; font-size:75px; color:#FFFFFF; text-align:center;'>📢 VOX LOCAL</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h1 style='font-family:Roboto; font-size:20px; color:#FFFFFF; text-align:center;'>Your Voice. Your Local. Our Priority.</h1>",
    unsafe_allow_html=True
)
# 🔹 App content  

import streamlit as st
import pandas as pd
import os

# ---------- FILE SETUP ----------
FILE = "users.csv"

if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Name","username", "password","Mail ID","dateofbirth","dateofjoin"])
    df.to_csv(FILE, index=False)

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- FUNCTIONS ----------
def load_users():
    return pd.read_csv(FILE)

def register_user(name, username, password, mail, dob, doj):
    df = load_users()
    if username in df["username"].values:
        return False
    new_user = pd.DataFrame([{
        "Name": name,
        "username": username,
        "password": password,
        "Mail ID": mail,
        "dateofbirth": dob,
        "dateofjoin": doj
        }])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(FILE, index=False)
    return True

def login_user(username, password):
    df = load_users()
    if df.empty:
        return False
    df = df.fillna("")
    user = df[(df["username"] == username) & (df["password"] == password)]
    return not user.empty

# ---------- STYLING ----------
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}
.card {
    background-color: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}
div.stButton > button {
    width: 100%;
    background-color: #4CAF50;
    color: white;
    font-size: 16px;
    border-radius: 8px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- MAIN ----------
if st.session_state.logged_in:
    st.title("🏠 Dashboard")
    st.success("You are logged in!")
    if st.button("Logout"):
        st.session_state.logged_in=False
        st.rerun()
else:
    choice=st.radio("",["Login","Register"],horizontal=True)
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        if choice=="Register":
            st.subheader("📝 Register")
            col1,col2=st.columns(2)
            with col1:
                name=st.text_input("Name")
            with col2:
                datebirth=st.date_input("Date of Birth")
            col3,col4=st.columns(2)
            with col3:
                datejoin=st.date_input("Joining Date")
            with col4:
                mail=st.text_input("Mail ID")
            new_user=st.text_input("Username")
            new_pass=st.text_input("Password",type="password")
            confirm_pass=st.text_input("Confirm Password",type="password")
            if st.button("Register"):
                if not name.strip():
                    st.error("⚠️ Please enter your name.")
                elif not mail.strip():
                    st.error("⚠️ Please enter your Mail ID.")
                elif not new_user.strip():
                    st.error("⚠️ Please enter a username.")
                elif not new_pass:
                    st.error("⚠️ Please enter a password.")
                elif not confirm_pass:
                    st.error("⚠️ Please confirm your password.")
                elif new_pass!=confirm_pass:
                    st.error("⚠️ Passwords do not match.")
                elif register_user(name,new_user,new_pass,mail,datebirth,datejoin):
                    st.success("✅ Account created successfully! Go to Login.")
                else:
                    st.warning("⚠️ Username already exists.")
        elif choice == "Login":
                users = pd.read_csv("users.csv")
                st.subheader("🔐 Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.button("Login"):
                    match = users[(users["username"] == username) & (users["password"] == password)]
                    if not match.empty:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.success("Login successful ✅")
                        st.switch_page("pages/dashboard.py")
                    else:
                        st.error("Invalid Credentials")
