import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_BASE_URL = "https://app.augmentedintelligence.co.za/api/v1"
FILES_API_URL = "https://app.augmentedintelligence.co.za/api/files"

def main():
    st.set_page_config(
        page_title="MaxiAI - Agent Manager",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 MaxiAI Agent Manager")
    st.markdown("Upload files, create agents, and manage your AI assistants")
    
    # Get API key from environment variable
    api_key = os.getenv("MAXIAI_API_KEY")
    
    if not api_key:
        st.error("❌ Missing MAXIAI_API_KEY environment variable")
        st.info("💡 Set MAXIAI_API_KEY in your environment")
        st.stop()
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    file_headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload Files", "🤖 Create Agent", "📋 My Agents"])
    
    # Tab 1: File Upload
    with tab1:
        st.header("📤 Upload Files")
        st.markdown("Upload documents to use as knowledge bases for your agents")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'pdf', 'doc', 'docx', 'md', 'csv'],
            help="Supported formats: TXT, PDF, DOC, DOCX, MD, CSV"
        )
        
        if uploaded_file and st.button("Upload File", type="primary"):
            with st.spinner(f"Uploading {uploaded_file.name}..."):
                try:
                    files = {"file": uploaded_file}
                    response = requests.post(FILES_API_URL, headers=file_headers, files=files)
                    
                    if response.status_code == 200:
                        file_data = response.json()
                        st.success("✅ File uploaded successfully!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**File ID:** `{file_data['id']}`")
                            st.write(f"**Name:** {file_data['name']}")
                        with col2:
                            st.write(f"**Size:** {file_data['size']} bytes")
                            st.write(f"**Type:** {file_data['type']}")
                        
                        # Store in session state
                        if "uploaded_files" not in st.session_state:
                            st.session_state.uploaded_files = []
                        st.session_state.uploaded_files.append(file_data)
                        
                    else:
                        st.error(f"❌ Upload failed: {response.status_code}")
                        st.text(response.text)
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Tab 2: Create Agent
    with tab2:
        st.header("🤖 Create Agent")
        st.markdown("Create a custom AI agent with specific capabilities")
        
        with st.form("create_agent_form"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                agent_name = st.text_input("Agent Name", placeholder="e.g., Document Analyzer")
                agent_description = st.text_area(
                    "Description", 
                    placeholder="Describe what your agent does...",
                    height=100
                )
                
                categories = st.multiselect(
                    "Categories",
                    ["Business", "Education", "Technology", "Healthcare", "Finance", "Research", "Other"],
                    default=["Business"]
                )
                
                system_prompt = st.text_area(
                    "System Prompt",
                    placeholder="You are a helpful assistant that...",
                    height=150,
                    help="Define your agent's personality and capabilities"
                )
            
            with col2:
                st.subheader("📁 Attach Files")
                selected_files = []
                
                if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
                    for i, file_data in enumerate(st.session_state.uploaded_files):
                        if st.checkbox(f"📄 {file_data['name']}", key=f"file_{i}"):
                            selected_files.append(file_data)
                    
                    if selected_files:
                        st.success(f"✅ {len(selected_files)} file(s) selected")
                else:
                    st.info("No files uploaded yet")
            
            submitted = st.form_submit_button("🚀 Create Agent", type="primary")
            
            if submitted:
                if not all([agent_name, agent_description, categories, system_prompt]):
                    st.error("❌ Please fill in all required fields")
                else:
                    with st.spinner("Creating agent..."):
                        try:
                            payload = {
                                "name": agent_name,
                                "description": agent_description,
                                "categories": categories,
                                "systemPrompt": system_prompt,
                                "files": selected_files
                            }
                            
                            response = requests.post(f"{API_BASE_URL}/agents", headers=headers, json=payload)
                            
                            if response.status_code in [200, 201]:
                                response_data = response.json()
                                agent_data = response_data.get('agent', {})
                                st.success("✅ Agent created successfully!")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    agent_id = agent_data.get('id', 'Not found')
                                    st.write(f"**Agent ID:** `{agent_id}`")
                                    st.write(f"**Name:** {agent_data.get('name', 'Unknown')}")
                                with col2:
                                    st.write(f"**Categories:** {', '.join(agent_data.get('categories', []))}")
                                    st.write(f"**Files:** {len(agent_data.get('files', []))} attached")
                                
                                # Show credit information
                                if response_data.get('creditsDeducted'):
                                    st.info(f"💰 Credits used: {response_data['creditsDeducted']} | Remaining: {response_data.get('remainingCredits', 'Unknown')}")
                                
                            else:
                                st.error(f"❌ Failed to create agent: {response.status_code}")
                                st.text(response.text)
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    # Tab 3: List Agents
    with tab3:
        st.header("📋 My Agents")
        
        if st.button("🔄 Refresh", type="secondary"):
            st.rerun()
        
        with st.spinner("Loading agents..."):
            try:
                response = requests.get(f"{API_BASE_URL}/agents", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    agents = data.get("agents", [])
                    pagination = data.get("pagination", {})
                    
                    if agents:
                        st.success(f"✅ Found {len(agents)} agent(s) | Total: {pagination.get('total', len(agents))}")
                        
                        for agent in agents:
                            with st.expander(f"🤖 {agent['name']}"):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.write(f"**Description:** {agent['description']}")
                                    st.write(f"**Categories:** {', '.join(agent['categories'])}")
                                    st.write(f"**Created:** {agent.get('createdAt', 'Unknown')}")
                                    
                                    if agent.get('files'):
                                        st.write("**Attached Files:**")
                                        for file in agent['files']:
                                            st.write(f"• 📄 {file.get('name', 'Unknown')} ({file.get('size', 0)} bytes)")
                                
                                with col2:
                                    agent_id = agent.get('id', 'Unknown')
                                    st.code(f"Agent ID:\n{agent_id}", language="text")
                                    
                                    if st.button(f"💬 Chat with {agent.get('name', 'Unknown')}", key=f"chat_{agent_id}"):
                                        st.info("💡 Use the Chat Interface app to chat with this agent!")
                                        st.code(f"Agent ID: {agent_id}")
                    else:
                        st.info("📝 No agents found. Create your first agent above!")
                        
                else:
                    st.error(f"❌ Failed to load agents: {response.status_code}")
                    st.text(response.text)
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **💰 Credit Costs:**
    - Create Agent: 50 credits
    - Upload Files: Free
    - List Agents: Free
    """)

if __name__ == "__main__":
    main() 