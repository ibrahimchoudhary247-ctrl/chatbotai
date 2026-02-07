import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from groq import Groq
from datetime import datetime

# --- 1. PAGE CONFIG & TITLE ---
st.set_page_config(page_title="Ibrahim's AI", page_icon="🤖")

# --- 2. INITIALIZE GROQ ---
try:
    # Pulls the key from your Streamlit Secrets box
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Groq API Key Error. Check your Streamlit Secrets!")
    st.stop()

# --- 3. GOOGLE SHEETS LOGGING ---
def log_to_sheet(name, email, user_msg, bot_msg):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Pulls the service account info from your Streamlit Secrets box
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(creds)
        
        # Opens your sheet - ensure the name matches exactly!
        sheet = gc.open("Chat logs").sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Saves 5 columns: Timestamp, Name, Email, User Message, Bot Response
        sheet.append_row([timestamp, name, email, user_msg, bot_msg])
    except Exception as e:
        st.sidebar.warning(f"Logging Error: {e}")

# --- 4. LOGIN SYSTEM (Gatekeeper) ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("👋 Welcome!")
    st.subheader("Please enter your details to start")
    
    with st.form("login_form"):
        user_name = st.text_input("What is your name?")
        user_email = st.text_input("What is your email?")
        submit_button = st.form_submit_button("Start Chatting")
        
        if submit_button:
            if user_name and user_email:
                st.session_state.user_name = user_name
                st.session_state.user_email = user_email
                st.session_state.signed_in = True
                st.rerun() # Refresh to show the chatbot
            else:
                st.error("I need both your name and email to continue!")
    st.stop() # Prevents the chatbot from loading until they sign in

# --- 5. CHATBOT INTERFACE ---
st.title("🤖 Ibrahim's nigga")
st.sidebar.success(f"Logged in as: {st.session_state.user_name}")

# Add a logout button to allow testing with different names
if st.sidebar.button("Logout"):
    st.session_state.signed_in = False
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show the conversation history on screen
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Handle new user input
if prompt := st.chat_input("Type your message here..."):
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
        
        # SAVE EVERYTHING TO THE SHEET
        log_to_sheet(
            st.session_state.user_name, 
            st.session_state.user_email, 
            prompt, 
            answer
        )
        
    except Exception as e:
        st.error(f"AI Error: {e}")
