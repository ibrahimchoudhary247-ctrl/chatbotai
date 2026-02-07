import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from groq import Groq
from datetime import datetime

# --- 1. INITIALIZE GROQ SAFELY ---
# This matches the name in your secrets box exactly
try:
    groq_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=groq_key)
except Exception as e:
    st.error("Groq API Key Error. Check your Streamlit Secrets!")
    st.stop()

# --- 2. GOOGLE SHEETS LOGGING ---
def log_to_sheet(user_msg, bot_msg):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(creds)
        
        # Open your sheet
        sheet = gc.open("Chat logs").sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, user_msg, bot_msg])
    except Exception as e:
        # We use a warning so the bot keeps working even if logging fails
        st.sidebar.warning(f"Note: Could not log to sheet. {e}")

# --- 3. CHAT INTERFACE ---
st.title("Hi There' I am IBRAHIM's NIGGA How Can I Be a Problem For u today😋?")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ask me a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # This is where your error was happening
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Try to log it
        log_to_sheet(prompt, answer)
        
    except Exception as e:
        st.error(f"AI Error: {e}")


