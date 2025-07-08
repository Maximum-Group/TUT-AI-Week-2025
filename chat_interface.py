import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_BASE_URL = "https://app.augmentedintelligence.co.za/api/v1"

def main():
    # Initialize session state first
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    
    # Get configuration from environment variables
    api_key = os.getenv("MAXIAI_API_KEY")
    agent_id = os.getenv("MAXIAI_AGENT_ID")
    
    if not api_key:
        st.error("❌ Missing MAXIAI_API_KEY environment variable")
        st.info("💡 Set MAXIAI_API_KEY in your environment")
        st.stop()
    
    if not agent_id:
        st.error("❌ Missing MAXIAI_AGENT_ID environment variable")
        st.info("💡 Set MAXIAI_AGENT_ID in your environment")
        st.stop()
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Load agent details
    try:
        response = requests.get(f"{API_BASE_URL}/agents", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", [])
            
            # Find the specified agent
            selected_agent = None
            for agent in agents:
                if agent['id'] == agent_id:
                    selected_agent = agent
                    break
            
            if not selected_agent:
                st.error(f"❌ Agent with ID '{agent_id}' not found")
                st.info("💡 Check your MAXIAI_AGENT_ID environment variable")
                st.stop()
                
        else:
            st.error(f"❌ Failed to load agent: {response.status_code}")
            st.text(response.text)
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Error loading agent: {str(e)}")
        st.stop()
    
    # Configure page with agent name
    st.set_page_config(
        page_title=f"{selected_agent['name']} - MaxiAI Chat",
        page_icon="💬",
        layout="wide"
    )
    
    # Display chat header with agent name and clear button
    header_col1, header_col2 = st.columns([4, 1])
    
    with header_col1:
        st.title(f"💬 {selected_agent['name']}")
        st.markdown(f"*{selected_agent['description']}*")
    
    with header_col2:
        if len(st.session_state.messages) > 0:
            st.markdown("")  # Add some spacing to align with title
            if st.button("🗑️ Clear Chat", type="secondary", key="header_clear"):
                st.session_state.messages = []
                st.session_state.thread_id = None
                st.rerun()
    
    st.markdown("---")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input (always render to keep the input bar visible)
    chat_input = st.chat_input("Type your message here...")
    
    # Check for pending question from suggested buttons
    prompt = None
    if hasattr(st.session_state, 'pending_question'):
        prompt = st.session_state.pending_question
        del st.session_state.pending_question
    elif chat_input:
        prompt = chat_input
    
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Prepare payload
                    payload = {"message": prompt}
                    if st.session_state.thread_id:
                        payload["threadId"] = st.session_state.thread_id
                    
                    # Call chat API
                    response = requests.post(
                        f"{API_BASE_URL}/agents/{agent_id}/chat",
                        headers=headers,
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # v1 API returns 'response' (not 'message') and threadId in conversation object
                        assistant_message = result.get("response", "No response received")
                        conversation = result.get("conversation", {})
                        thread_id = conversation.get("threadId")
                        
                        # Update thread ID
                        if thread_id:
                            st.session_state.thread_id = thread_id
                        
                        # Display assistant response
                        st.markdown(assistant_message)
                        
                        # Add assistant message to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": assistant_message
                        })
                        
                    elif response.status_code == 402:
                        error_msg = "I'm temporarily unavailable. Please try again later."
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })
                        
                    elif response.status_code == 429:
                        error_msg = "I'm receiving too many requests. Please wait a moment and try again."
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })
                        
                    else:
                        error_msg = "Sorry, I'm having trouble responding right now. Please try again."
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })
                        
                except requests.exceptions.Timeout:
                    error_msg = "I'm taking longer than usual to respond. Please try asking again."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
                    
                except Exception as e:
                    error_msg = "Something went wrong. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
    

    # Show sample questions for first time users
    if len(st.session_state.messages) == 0:
        st.markdown("---")
        
        sample_questions = [
            "Hello! How can you help me today?",
            "What do you know about?",
            "Tell me about your capabilities",
            "Can you help me with questions?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(sample_questions):
            with cols[i % 2]:
                if st.button(question, key=f"sample_{i}", use_container_width=True):
                    # Set the question to be processed through the API
                    st.session_state.pending_question = question
                    st.rerun()

if __name__ == "__main__":
    main() 