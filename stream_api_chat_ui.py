####
## Fully functional Agent UI with memory and response streaming from fastapi backend server
###

import streamlit as st
import requests


def initialize_session_state():
    """Initialize session state variables"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "stream_val" not in st.session_state:
        st.session_state.stream_val = False
    

def display_chat_history():
    """Display the chat history"""
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        elif message["role"] == "assistant" and message["content"] != '':
            with st.chat_message("assistant"):
                st.write(message["content"])

def call_api(user_prompt: str, stream: bool ):
    
    if stream:
        url = 'http://127.0.0.1:8000/agent/chat'
        data = {
            "user_prompt": user_prompt,
            "stream": stream
            }
        header = {"Content-Type": "application/json"}
        return requests.post(url=url, headers=header, json=data, stream=True)
    else:
        url = 'http://127.0.0.1:8000/agent/chat'
        data = {
            "user_prompt": user_prompt,
            "stream": stream
            }
        header = {"Content-Type": "application/json"}
        return requests.post(url=url, headers=header, json=data)

def main():
    st.set_page_config(page_title="UelloSend Support Agent", page_icon="🤖")
    st.title("UelloSend Support Agent 🤖")
    
    #Initialize Session
    initialize_session_state()

    # Add a button in the sidebar to set the streaming value
    with st.sidebar:
        st.selectbox("Set Streaming: ", [True, False], key="stream_val")
        if st.button("Update", type='primary'):
            st.rerun()

    # Display chat history
    display_chat_history()
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):

        # Add user message to chat history
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": prompt 
            }
        )
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get response from chatbot
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            with st.spinner("Thinking..."):
                stream_value = st.session_state.stream_val
                response = call_api(prompt, stream_value)

                if response.status_code == 200:
                    if stream_value:
                        chunk_text = ""
                        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                            if chunk:
                                chunk_text += chunk
                                message_placeholder.write(chunk_text)
                        
                    else:
                            chunk_text = response.json()["message"]["content"]
                            message_placeholder.write(chunk_text)
                            

                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": chunk_text
                    })
    
    

if __name__ == "__main__":
    main()