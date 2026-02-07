import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from groq import Groq
from datetime import datetime

# --- 1. PAGE CONFIG & TITLE ---
st.set_page_config(page_title="Ibrahim's AI", page_icon="🤖")

# --- 2. INITIALIZE GROQ ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Groq API Key Error. Check your Streamlit Secrets!")
    st.stop()

# --- 3. THE "LOG TO SHEET" FUNCTION ---
def log_to_sheet(name, email, user_msg, bot_msg):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(creds)
        
        sheet = gc.open("Chat logs").sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Order: Timestamp, Name, Email, User Message, Bot Response
        sheet.append_row([timestamp, name, email, user_msg, bot_msg])
    except Exception as e:
        st.sidebar.warning(f"Logging Note: {e}")

# --- 4. LOGIN GATEKEEPER WITH VALIDATION ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("👋 Welcome!")
    st.subheader("Please sign in to start chatting")
    
    with st.form("login_form"):
        user_name = st.text_input("Full Name")
        user_email = st.text_input("Email Address")
        submit_button = st.form_submit_button("Start Chatting")
        
        if submit_button:
            # Check for empty fields
            if not user_name or not user_email:
                st.error("Please fill in both fields!")
            # Basic email format check
            elif "@" not in user_email or "." not in user_email:
                st.error("Please enter a valid email address.")
            # Name length check
            elif len(user_name) < 2:
                st.error("Please enter a valid name (at least 2 letters).")
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

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        log_to_sheet(
            st.session_state.user_name, 
            st.session_state.user_email, 
            prompt, 
            answer
        )
        
    except Exception as e:
        st.error(f"AI Error: {e}")
