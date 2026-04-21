# frontend/app.py
import streamlit as st
import requests
import uuid

from dotenv import load_dotenv
load_dotenv()


st.set_page_config(page_title="Digital Document Assistant", layout="wide")

st.title("📄 Digital Document Assistant")

uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, PNG)", type=["pdf", "docx", "png"])

if uploaded_file is not None:
    if st.button("Process Document"):
        with st.spinner("Sending file to backend..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                res = requests.post("http://127.0.0.1:8000/extract", files=files)
                if res.status_code == 200:
                    result = res.json()
                    st.success("✅ File extracted and embedded into FAISS vector DB")
                    st.json(result)  # optional: show backend response
                else:
                    st.error(f"Backend error: {res.status_code} - {res.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")
# ----------------- Conversational Chat Section -----------------
st.header("Ask Questions (Conversational Q&A)")

# Maintain a unique session_id per user
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Store conversation history in Streamlit session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for msg in st.session_state.messages:
    role, text = msg
    if role == "user":
        st.chat_message("user").markdown(text)
    else:
        st.chat_message("assistant").markdown(text)

# Input box for user query
if prompt := st.chat_input("Type your question about the uploaded documents..."):
    # Append user message to history
    st.session_state.messages.append(("user", prompt))
    st.chat_message("user").markdown(prompt)

    # Send query to backend
    try:
        payload = {"session_id": st.session_state.session_id, "message": prompt}
        res = requests.post("http://127.0.0.1:8000/chat", json=payload)

        if res.status_code == 200:
            data = res.json()
            answer = data.get("answer", "⚠️ No response received")
        else:
            answer = f"⚠️ Backend error: {res.status_code} - {res.text}"

    except Exception as e:
        answer = f"⚠️ Request failed: {e}"

    # Append assistant message to history
    st.session_state.messages.append(("assistant", answer))
    st.chat_message("assistant").markdown(answer)