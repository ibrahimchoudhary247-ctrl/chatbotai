import streamlit as st
from groq import Groq
import os
from datetime import datetime

# --- 1. PAGE CONFIG & CUSTOM THEME ---
st.set_page_config(page_title="AI Knowledge Pro", page_icon="🤖", layout="centered")

# Custom CSS for a professional "Night Owl" look
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
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CLOUD BRAIN SETUP (GROQ) ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Secret Key Error: {e}")
    st.stop()

# --- 3. DATA LOADING ---
def get_data():
    if os.path.exists("data.txt"):
        try:
            with open("data.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            return "Error reading data file."
    return "No custom data found."

knowledge = get_data()

# --- 4. SIDEBAR & LOGGING ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("---")
    
    # Session Log (Visible only to you)
    st.subheader("📝 Session Logs")
    if "log" not in st.session_state:
        st.session_state.log = []
    
    if st.session_state.log:
        for entry in st.session_state.log:
            st.caption(entry)
    else:
        st.write("No questions yet.")

    st.markdown("---")
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.session_state.log = []
        st.rerun()

# --- 5. MAIN CHAT INTERFACE ---
st.title("🤖 My Knowledge Bot")
st.caption("Custom data loaded. I'm ready to help!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. CHAT LOGIC ---
if prompt := st.chat_input("Ask me something..."):
    # Log the time and question to the sidebar
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.log.append(f"[{timestamp}] {prompt}")
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            # SWITCHED MODEL: llama-3.1-8b-instant is faster and has higher rate limits
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
        except Exception as e:
            st.error(f"API Limit or Error: {e}")
