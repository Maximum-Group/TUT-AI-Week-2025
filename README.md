<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <a href="https://augmentedintelligence.co.za" target="_blank">
          <img src="https://augmentedintelligence.co.za/wp-content/uploads/2025/02/Untitled-design-2025-02-28T094302.192.png" alt="Augmented Intelligence" width="300"/>
        </a>
      </td>
      <td align="center" width="50%">
        <a href="https://maximumgroupdigital.co.za" target="_blank">
          <img src="https://maximumgroupdigital.co.za/wp-content/uploads/2022/06/MAXIMUM-GROUP-DIGITAL-BLUE-LOGO-GRADIENT-GLOW.png" alt="Maximum Group Digital" width="300"/>
        </a>
      </td>
    </tr>
  </table>
</div>


# Augmented Intelligence RAG Agent Application

A practical demonstration of Retrieval-Augmented Generation (RAG) agents using the Augmented Intelligence API with Streamlit applications for file upload, agent creation, and chat interaction.

## 📋 Table of Contents

- [Overview](#overview)
- [Understanding RAG Agents](#understanding-rag-agents)
- [Quick Start](#quick-start)
- [API Workflow](#api-workflow)
- [File Upload Implementation](#file-upload-implementation)
- [Agent Creation Implementation](#agent-creation-implementation)
- [Chat Implementation](#chat-implementation)
- [Complete Workflow Example](#complete-workflow-example)
- [Educational Applications](#educational-applications)

## Overview

This repository demonstrates how to build RAG (Retrieval-Augmented Generation) agents using the Augmented Intelligence API. It includes two Streamlit applications that showcase the complete workflow from document upload to conversational AI interaction.

**Applications:**
- **Agent Manager** (`agent_manager.py`): Upload files and create RAG agents
- **Chat Interface** (`chat_interface.py`): Interact with created agents

## Understanding RAG Agents

### What is RAG?

Retrieval-Augmented Generation (RAG) combines large language models with external knowledge retrieval. Instead of relying only on training data, RAG systems access specific documents to provide accurate, contextual responses.

### The RAG Workflow

1. **Document Upload**: Upload files containing domain-specific knowledge
2. **Vector Processing**: Documents are converted to searchable vector embeddings
3. **Agent Creation**: Create an AI agent with access to uploaded documents
4. **Query Processing**: When users ask questions, relevant document sections are retrieved
5. **Response Generation**: The AI generates responses using both its knowledge and retrieved context

## Quick Start

### Installation

```bash
# Clone and navigate to demo folder
git clone https://github.com/Maximum-Group/TUT-AI-Week-2025.git

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file:
```env
# Required for both applications
MAXIAI_API_KEY="your-api-key-here"

# Required only for Chat Interface
MAXIAI_AGENT_ID="your-agent-id-here"
```

### Run Applications

```bash
# Agent Manager - Create agents
streamlit run agent_manager.py
# or
python -m streamlit run agent_manager.py

# Chat Interface - Talk to agents  
streamlit run chat_interface.py
# or
python -m streamlit run chat_interface.py
```

## API Workflow

The complete workflow involves three main API interactions:

1. **POST /api/files** - Upload documents
2. **POST /api/v1/agents** - Create RAG agent with uploaded files
3. **POST /api/v1/agents/{id}/chat** - Chat with the agent

## File Upload Implementation

### Basic File Upload

```python
import requests
import streamlit as st

# API Configuration
FILES_API_URL = "https://app.augmentedintelligence.co.za/api/files"
headers = {"Authorization": f"Bearer {api_key}"}

# File upload interface
uploaded_file = st.file_uploader(
    "Choose a file",
    type=['txt', 'pdf', 'doc', 'docx', 'md', 'csv']
)

if uploaded_file:
    # Prepare file for upload
    files = {"file": uploaded_file}
    
    # Upload to API
    response = requests.post(FILES_API_URL, headers=headers, files=files)
    
    if response.status_code == 200:
        file_data = response.json()
        st.success("File uploaded successfully!")
        
        # Store file data for agent creation
        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = []
        st.session_state.uploaded_files.append(file_data)
```

### File Response Structure

When a file is successfully uploaded, the API returns:

```json
{
    "id": "file_abc123",
    "name": "document.pdf", 
    "size": 2048576,
    "type": "application/pdf",
    "createdAt": "2024-01-15T10:30:00Z"
}
```

### Managing Uploaded Files

```python
# Display uploaded files for selection
selected_files = []
if "uploaded_files" in st.session_state:
    for i, file_data in enumerate(st.session_state.uploaded_files):
        if st.checkbox(f"📄 {file_data['name']}", key=f"file_{i}"):
            selected_files.append(file_data)
```

## Agent Creation Implementation

### Agent Creation API Call

```python
# API Configuration
API_BASE_URL = "https://app.augmentedintelligence.co.za/api/v1"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Agent configuration
agent_config = {
    "name": "Document Analyzer",
    "description": "Analyzes uploaded documents and answers questions",
    "categories": ["Business", "Education"],
    "systemPrompt": "You are a helpful assistant that analyzes documents and provides detailed answers based on the content.",
    "files": selected_files  # Files from upload step
}

# Create agent
response = requests.post(f"{API_BASE_URL}/agents", headers=headers, json=agent_config)

if response.status_code in [200, 201]:
    response_data = response.json()
    agent_data = response_data.get('agent', {})
    agent_id = agent_data.get('id')
    
    st.success(f"Agent created! ID: {agent_id}")
```

### Agent Creation Response

The API returns detailed information about the created agent:

```json
{
    "agent": {
        "id": "agent_xyz789",
        "name": "Document Analyzer",
        "description": "Analyzes uploaded documents and answers questions",
        "categories": ["Business", "Education"],
        "type": "conversational",
        "files": [
            {
                "id": "file_abc123",
                "name": "document.pdf",
                "type": "application/pdf",
                "size": 2048576
            }
        ],
        "createdAt": "2024-01-15T10:35:00Z"
    },
    "creditsDeducted": 50,
    "remainingCredits": 450
}
```

### Extracting Agent ID

```python
# Extract agent ID for chat interface
if response.status_code in [200, 201]:
    response_data = response.json()
    agent_data = response_data.get('agent', {})
    agent_id = agent_data.get('id')
    
    # Display agent ID for chat interface configuration
    st.code(f"Agent ID: {agent_id}")
    st.info("Copy this ID to your .env file as MAXIAI_AGENT_ID")
```

## Chat Implementation

### Setting Up Chat Interface

```python
# Load agent using environment variable
agent_id = os.getenv("MAXIAI_AGENT_ID")

# Get agent details
response = requests.get(f"{API_BASE_URL}/agents", headers=headers)
agents = response.json().get("agents", [])

# Find specific agent
selected_agent = None
for agent in agents:
    if agent['id'] == agent_id:
        selected_agent = agent
        break
```

### Chat API Implementation

```python
# Initialize conversation state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Chat input processing
if prompt := st.chat_input("Ask me anything about the documents..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Prepare chat payload
    chat_payload = {"message": prompt}
    if st.session_state.thread_id:
        chat_payload["threadId"] = st.session_state.thread_id
    
    # Send to chat API
    response = requests.post(
        f"{API_BASE_URL}/agents/{agent_id}/chat",
        headers=headers,
        json=chat_payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        assistant_message = result.get("response")
        conversation = result.get("conversation", {})
        
        # Update thread ID for conversation continuity
        if conversation.get("threadId"):
            st.session_state.thread_id = conversation["threadId"]
        
        # Add assistant response to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": assistant_message
        })
```

### Chat Response Structure

The chat API returns:

```json
{
    "conversation": {
        "id": "conv_123",
        "threadId": "thread_456", 
        "agentId": "agent_xyz789",
        "agentName": "Document Analyzer"
    },
    "response": "Based on the uploaded document, I can see that...",
    "creditsUsed": 50,
    "remainingCredits": 400
}
```

### Thread Management

```python
# Thread continuity for context preservation
def send_message(message, thread_id=None):
    payload = {"message": message}
    if thread_id:
        payload["threadId"] = thread_id
    
    response = requests.post(f"{API_BASE_URL}/agents/{agent_id}/chat", 
                           headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result.get("response"), result.get("conversation", {}).get("threadId")
```

## Complete Workflow Example

Here's a complete example showing the full workflow from file upload to chat:

```python
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = "https://app.augmentedintelligence.co.za/api/v1"
FILES_API_URL = "https://app.augmentedintelligence.co.za/api/files"
api_key = os.getenv("MAXIAI_API_KEY")
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
file_headers = {"Authorization": f"Bearer {api_key}"}

# Step 1: Upload File
def upload_file(file):
    files = {"file": file}
    response = requests.post(FILES_API_URL, headers=file_headers, files=files)
    return response.json() if response.status_code == 200 else None

# Step 2: Create Agent
def create_agent(name, description, system_prompt, files):
    payload = {
        "name": name,
        "description": description,
        "categories": ["Education"],
        "systemPrompt": system_prompt,
        "files": files
    }
    response = requests.post(f"{API_BASE_URL}/agents", headers=headers, json=payload)
    return response.json() if response.status_code in [200, 201] else None

# Step 3: Chat with Agent
def chat_with_agent(agent_id, message, thread_id=None):
    payload = {"message": message}
    if thread_id:
        payload["threadId"] = thread_id
        
    response = requests.post(f"{API_BASE_URL}/agents/{agent_id}/chat", 
                           headers=headers, json=payload)
    return response.json() if response.status_code == 200 else None

# Example Usage
if uploaded_file := st.file_uploader("Upload a document"):
    # 1. Upload file
    file_data = upload_file(uploaded_file)
    if file_data:
        st.success(f"Uploaded: {file_data['name']}")
        
        # 2. Create agent with uploaded file
        agent_response = create_agent(
            name="My Document Agent",
            description="Answers questions about uploaded document",
            system_prompt="You are a helpful assistant that answers questions based on uploaded documents.",
            files=[file_data]
        )
        
        if agent_response:
            agent_id = agent_response['agent']['id']
            st.success(f"Agent created: {agent_id}")
            
            # 3. Chat with agent
            if question := st.text_input("Ask a question about your document:"):
                chat_response = chat_with_agent(agent_id, question)
                if chat_response:
                    st.write("**Agent Response:**")
                    st.write(chat_response['response'])
```

## API Endpoints Reference

### File Upload
- **Endpoint**: `POST /api/files`
- **Headers**: `Authorization: Bearer {api_key}`
- **Body**: Multipart form data with file
- **Response**: File metadata object

### Agent Creation  
- **Endpoint**: `POST /api/v1/agents`
- **Headers**: `Authorization: Bearer {api_key}`, `Content-Type: application/json`
- **Body**: Agent configuration JSON
- **Response**: Agent object with ID and metadata

### Chat
- **Endpoint**: `POST /api/v1/agents/{agent_id}/chat`
- **Headers**: `Authorization: Bearer {api_key}`, `Content-Type: application/json`  
- **Body**: Message and optional thread ID
- **Response**: Agent response and conversation metadata

### List Agents
- **Endpoint**: `GET /api/v1/agents`
- **Headers**: `Authorization: Bearer {api_key}`
- **Response**: Array of user's agents

## Educational Applications

### Learning Objectives

Students learn practical API integration skills:

- **REST API Usage**: Making HTTP requests with proper authentication
- **File Handling**: Uploading files via API and managing responses
- **State Management**: Maintaining conversation context across requests  
- **JSON Processing**: Working with API request/response structures
- **Environment Configuration**: Using environment variables for API keys

### Use Cases

- **Academic Research**: Upload research papers and query specific findings
- **Course Materials**: Create study assistants with textbooks and lecture notes
- **Technical Documentation**: Build help systems for complex software
- **Business Analysis**: Upload reports and extract key insights

### Best Practices

1. **Secure API Keys**: Always use environment variables, never hardcode
2. **File Management**: Store uploaded file references for agent creation
3. **Thread Continuity**: Maintain thread IDs for conversational context
4. **Response Validation**: Check status codes before processing responses
5. **Resource Management**: Be aware of credit costs for API operations

---

**This application demonstrates practical RAG implementation using the Augmented Intelligence API, showing the complete workflow from document upload to intelligent conversation.** 
