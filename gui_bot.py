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
        # Connect to Google Sheets using your secrets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(creds)
        
        # Open your sheet (must match your sheet name exactly)
        sheet = gc.open("Chat logs").sheet1
        
        # Current time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # This sends data to Columns A, B, C, D, and E in order
        sheet.append_row([timestamp, name, email, user_msg, bot_msg])
    except Exception as e:
        st.sidebar.warning(f"Logging Note: {e}")

# --- 4. LOGIN GATEKEEPER ---
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
            if user_name and user_email:
                st.session_state.user_name = user_name
                st.session_state.user_email = user_email
                st.session_state.signed_in = True
                st.rerun() 
            else:
                st.error("Both name and email are required!")
    st.stop() 

# --- 5. CHAT INTERFACE ---
st.title("🤖 Ibrahim's nigga")
st.sidebar.info(f"User: {st.session_state.user_name}")

# Logout button
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
        # Get AI Response
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # CALL THE LOGGING FUNCTION
        log_to_sheet(
            st.session_state.user_name, 
            st.session_state.user_email, 
            prompt, 
            answer
        )
        
    except Exception as e:
        st.error(f"AI Error: {e}")
