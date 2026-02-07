import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from groq import Groq
from datetime import datetime

# --- GOOGLE SHEETS LOGGING FUNCTION ---
def log_to_sheet(user_msg, bot_msg):
    try:
        # Define the scope for Sheets and Drive
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Pull the credentials directly from Streamlit Secrets
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open your spreadsheet (must match your sheet name exactly!)
        sheet = client.open("Chat logs").sheet1
        
        # Create a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Append the new row to the sheet
        sheet.append_row([timestamp, user_msg, bot_msg])
    except Exception as e:
        # This will show in the sidebar if something goes wrong
        st.sidebar.error(f"Logging Error: {e}")

# --- INITIALIZE GROQ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- CHAT UI ---
st.title("🤖 Chatbot with Permanent History")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history on the screen
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# User Input
if prompt := st.chat_input("Ask me a question..."):
    # 1. Add user message to session
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get AI Response
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content
    
    # 3. Add bot message to session
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    
    # 4. SAVE TO GOOGLE SHEET PERMANENTLY
    log_to_sheet(prompt, answer)
