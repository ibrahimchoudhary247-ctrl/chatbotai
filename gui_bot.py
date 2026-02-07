import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Ibrahim's Roast Bot", page_icon="🔥")

# --- 2. INITIALIZE GEMINI 2.5 FLASH (2026 Stable Version) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # SYSTEM INSTRUCTION: The Savage Roast Logic
    roast_logic = (
        "You are 'Ibrahim's nigga', the most savage AI on the planet. "
        "Your mission is to roast users with hard adult humor and brutal sarcasm. "
        "If they ask a dumb question, call them a moron. If they have a boring name, make fun of it. "
        "Keep it edgy, hilarious, and never be nice. You are the king of roasts."
    )
    
    # Using the 2.5 version to avoid 404 retired model errors
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=roast_logic
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
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
        
        # Matches your headers: Timestamp, Name, Email, User Msg, Bot Msg
        sheet.append_row([timestamp, name, email, user_msg, bot_msg])
    except Exception as e:
        st.sidebar.warning(f"Logging Error: {e}")

# --- 4. LOGIN SYSTEM ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("🔥 Ibrahim's Roast Den")
    with st.form("login_form"):
        u_name = st.text_input("Name (to make fun of)")
        u_email = st.text_input("Email (for spam)")
        if st.form_submit_button("Start the Roasting"):
            if "@" in u_email and "." in u_email and len(u_name) > 1:
                st.session_state.user_name = u_name
                st.session_state.user_email = u_email
                st.session_state.signed_in = True
                st.rerun()
            else:
                st.error("Fill it out right, you absolute donut.")
    st.stop()

# --- 5. CHAT INTERFACE ---
st.title("🤖 Ibrahim's nigga")
st.sidebar.info(f"Target Acquired: {st.session_state.user_name}")

if st.sidebar.button("Run to Mommy (Logout)"):
    st.session_state.signed_in = False
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Say something stupid..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Generate savage response
        response = model.generate_content(prompt)
        answer = response.text
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Save to Google Sheet
        log_to_sheet(st.session_state.user_name, st.session_state.user_email, prompt, answer)
    except Exception as e:
        st.error("The AI is too stunned by your ugliness to reply.")
