####
## Fully functional Agent UI with memory and response streaming
###

import streamlit as st
from support_agent import start_agent
import types
from shared_data import messages #Shared data file

STREAM = True

def initialize_session_state():
    """Initialize session state variables"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    

def display_chat_history():
    """Display the chat history"""
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        elif message["role"] == "assistant" and message["content"] != '':
            with st.chat_message("assistant"):
                st.write(message["content"])

def main():
    st.set_page_config(page_title="UelloSend Support Agent", page_icon="🤖")
    st.title("UelloSend Support Agent 🤖")
    
    #Initialize Session
    initialize_session_state()

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
                response = start_agent(prompt, STREAM)
                chunk_text = ""

                #to handle stream responses
                if isinstance(response, types.GeneratorType):
                    
                    for chunk in response:
                        if "message" in chunk:
                            chunk_text += chunk["message"].get("content", "")
                            message_placeholder.write(chunk_text)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": chunk_text
                    })

                    #Append to agent's message history
                    messages.append({
                        "role": "assistant",
                        "content": chunk_text
                    })
                else:
                    ai_response = response["message"]["content"]
                    message_placeholder.write(ai_response)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append(response["message"])
    
    # Add a clear button in the sidebar
    with st.sidebar:
        if st.button("Clear Conversation"):
            st.session_state.chat_history = []
        
            st.rerun()

if __name__ == "__main__":
    main()