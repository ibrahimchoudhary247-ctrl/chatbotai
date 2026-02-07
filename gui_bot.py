import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Ibrahim's AI", page_icon="🤖")

# --- 2. INITIALIZE GEMINI (Better for unlimited free chat) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Gemini API Key Error. Check your Streamlit Secrets!")
    st.stop()

# --- 3. GOOGLE SHEETS LOGGING ---
def log_to_sheet(name, email, user_msg, bot_msg):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(creds)
        
        sheet = gc.open("Chat logs").sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Order: Time, Name, Email, User, Bot
        sheet.append_row([timestamp, name, email, user_msg, bot_msg])
    except Exception as e:
        st.sidebar.warning(f"Logging Note: {e}")

# --- 4. LOGIN GATEKEEPER WITH VALIDATION ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("👋 Welcome!")
    with st.form("login_form"):
        user_name = st.text_input("Full Name")
        user_email = st.text_input("Email Address")
        submit_button = st.form_submit_button("Start Chatting")
        
        if submit_button:
            if not user_name or not user_email:
                st.error("Please fill in both fields!")
            elif "@" not in user_email or "." not in user_email:
                st.error("Please enter a valid email address.")
            elif len(user_name) < 2:
                st.error("Please enter a real name.")
            else:
                st.session_state.user_name = user_name
                st.session_state.user_email = user_email
                st.session_state.signed_in = True
                st.rerun() 
    st.stop() 

# --- 5. CHAT INTERFACE ---
st.title("🤖 Ibrahim's nigga")
st.sidebar.info(f"User: {st.session_state.user_name}")

if st.sidebar.button("Logout"):
    st.session_state.signed_in = False
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# User Input
if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Gemini Logic
        response = model.generate_content(prompt)
        answer = response.text
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        log_to_sheet(st.session_state.user_name, st.session_state.user_email, prompt, answer)
        
    except Exception as e:
        st.error(f"AI Error: {e}")
