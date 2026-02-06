import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="My Cloud Bot", page_icon="🤖")

# 1. Setup the Cloud Brain (Groq)
# Locally: It looks for a secret file. Online: It looks at Streamlit's settings.
try:
    # CORRECT VERSION:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Missing Groq API Key! Please add it to your secrets.")
    st.stop()

# 2. Load your data.txt
def get_data():
    if os.path.exists("data.txt"):
        with open("data.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "No custom data found."

knowledge = get_data()

st.title("🤖 My Live Knowledge Bot")

# 3. Chat History (Remembers what you said)
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
        # This sends your data + your question to Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"You are a helpful assistant. Use this info: {knowledge}"},
                {"role": "user", "content": prompt},
            ],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

