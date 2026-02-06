import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="My Cloud Bot", page_icon="🤖")

# 1. Setup the Cloud Brain (Groq)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Secret Key Error: {e}")
    st.stop()

# 2. Load and Clean Data
def get_data():
    if os.path.exists("data.txt"):
        try:
            with open("data.txt", "r", encoding="utf-8") as f:
                # We strip extra spaces to prevent formatting errors
                return f.read().strip()
        except:
            return "Error reading data file."
    return "No custom data found."

knowledge = get_data()

st.title("🤖 My Live Knowledge Bot")

# 3. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. The Chat Logic
if prompt := st.chat_input("Ask me something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # We create a fresh list to ensure no hidden "junk" data is sent
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"Use this info: {knowledge}"},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"API Request Failed: {e}")

