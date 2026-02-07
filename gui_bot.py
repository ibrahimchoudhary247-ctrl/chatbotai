import streamlit as st
from groq import Groq
import os
from datetime import datetime

# --- 1. PAGE CONFIG & CUSTOM THEME ---
st.set_page_config(page_title="AI Knowledge Pro", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #30363D;
    }
    .stChatInputContainer { padding-bottom: 20px; }
    section[data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CLOUD BRAIN SETUP (GROQ) ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Secret Key Error: {e}")
    st.stop()

# --- 3. DATA & LOGGING FUNCTIONS ---
def get_data():
    if os.path.exists("data.txt"):
        try:
            with open("data.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            return "Error reading data file."
    return "No custom data found."

# NEW: Permanent History Function
def save_to_permanent_log(user_input, bot_response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Date: {timestamp}\nUser: {user_input}\nBot: {bot_response}\n{'-'*30}\n"
    # This writes to a file that stays on the server during the session
    with open("permanent_history.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

def read_permanent_log():
    if os.path.exists("permanent_history.txt"):
        with open("permanent_history.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "No permanent history yet."

knowledge = get_data()

# --- 4. SIDEBAR & LOGGING ---
with st.sidebar:
    st.title("⚙️ Owner Control")
    st.markdown("---")
    
    st.subheader("📜 Permanent History")
    # This button allows YOU to see everything ever asked
    if st.checkbox("Show All-Time History"):
        history = read_permanent_log()
        st.text_area("History Log", history, height=300)
    
    st.markdown("---")
    if st.button("🗑️ Clear Current View"):
        st.session_state.messages = []
        st.rerun()

# --- 5. MAIN CHAT INTERFACE ---
st.title("🤖 My Knowledge Bot")
st.caption("Custom data loaded. History is being recorded permanently.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. CHAT LOGIC ---
if prompt := st.chat_input("Ask me something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant. Use this info: {knowledge}"},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            # SAVE TO PERMANENT FILE
            save_to_permanent_log(prompt, answer)
            
        except Exception as e:
            st.error(f"API Limit or Error: {e}")
