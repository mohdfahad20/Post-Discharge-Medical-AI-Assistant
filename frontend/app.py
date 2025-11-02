"""
Streamlit Frontend for Medical AI Assistant
Chat interface with real-time logging display
"""
import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Page config
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "patient_name" not in st.session_state:
    st.session_state.patient_name = None
if "logs" not in st.session_state:
    st.session_state.logs = []

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subheader {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .receptionist-badge {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .clinical-badge {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    .disclaimer {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏥 Post-Discharge Medical AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Your AI-powered healthcare companion</div>', unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Medical Disclaimer:</strong> This is an AI assistant for educational purposes only. 
    Always consult healthcare professionals for medical advice, diagnosis, or treatment.
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 System Info")
    
    # Session info
    st.subheader("Session")
    st.text(f"ID: {st.session_state.session_id[:8]}...")
    
    if st.session_state.patient_name:
        st.success(f"👤 Patient: {st.session_state.patient_name}")
    else:
        st.info("👤 No patient identified yet")
    
    st.divider()
    
    # Controls
    st.subheader("Controls")
    
    if st.button("🔄 New Session", use_container_width=True):
        # Clear session
        try:
            requests.delete(f"{API_URL}/session/{st.session_state.session_id}")
        except:
            pass
        
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.patient_name = None
        st.session_state.logs = []
        st.rerun()
    
    if st.button("📥 Export Chat", use_container_width=True):
        chat_export = {
            "session_id": st.session_state.session_id,
            "patient": st.session_state.patient_name,
            "timestamp": datetime.now().isoformat(),
            "messages": st.session_state.messages
        }
        
        st.download_button(
            label="Download JSON",
            data=json.dumps(chat_export, indent=2),
            file_name=f"chat_{st.session_state.session_id[:8]}.json",
            mime="application/json"
        )
    
    st.divider()
    
    # System logs
    st.subheader("📋 Recent Logs")
    
    if st.button("🔄 Refresh Logs"):
        try:
            response = requests.get(f"{API_URL}/logs?limit=10")
            if response.status_code == 200:
                st.session_state.logs = response.json().get("logs", [])
        except:
            st.error("Failed to fetch logs")
    
    # Display logs
    with st.expander("View System Logs", expanded=False):
        if st.session_state.logs:
            for log in reversed(st.session_state.logs[-10:]):
                status = "✅" if log.get("success") else "❌"
                agent = log.get("agent", "unknown")
                action = log.get("action", "unknown")
                
                st.text(f"{status} [{agent}] {action}")
                st.caption(log.get("timestamp", "")[:19])
                st.divider()
        else:
            st.info("No logs yet")

# Main chat area
st.subheader("💬 Chat")

# Display chat history
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        agent = message.get("agent", "user")
        
        with st.chat_message(role):
            if role == "assistant":
                # Show agent badge
                if agent == "receptionist":
                    st.markdown('<span class="agent-badge receptionist-badge">👋 Receptionist</span>', unsafe_allow_html=True)
                elif agent == "clinical":
                    st.markdown('<span class="agent-badge clinical-badge">🩺 Clinical AI</span>', unsafe_allow_html=True)
            
            st.write(content)
            
            # Show sources if available
            if message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.markdown(f"**{source.get('reference', 'Unknown')}**")
                        st.caption(source.get('excerpt', ''))

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(prompt)
    
    # Call API
    try:
        with st.spinner("🤔 Thinking..."):
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "patient_name": st.session_state.patient_name,
                    "message": prompt,
                    "session_id": st.session_state.session_id,
                    "conversation_history": st.session_state.messages
                },
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract patient name from response if available
            if data.get("patient_data") and not st.session_state.patient_name:
                st.session_state.patient_name = data["patient_data"].get("patient_name")
            
            # Add assistant message
            assistant_message = {
                "role": "assistant",
                "content": data["response"],
                "agent": data["agent"],
                "sources": data.get("sources", []),
                "timestamp": datetime.now().isoformat()
            }
            
            st.session_state.messages.append(assistant_message)
            
            # Update logs
            st.session_state.logs = data.get("logs", [])
            
            # Display assistant message
            with st.chat_message("assistant"):
                if data["agent"] == "receptionist":
                    st.markdown('<span class="agent-badge receptionist-badge">👋 Receptionist</span>', unsafe_allow_html=True)
                elif data["agent"] == "clinical":
                    st.markdown('<span class="agent-badge clinical-badge">🩺 Clinical AI</span>', unsafe_allow_html=True)
                
                st.write(data["response"])
                
                # Show sources if available
                if data.get("sources"):
                    with st.expander("📚 Sources"):
                        for source in data["sources"]:
                            st.markdown(f"**{source.get('reference', 'Unknown')}**")
                            st.caption(source.get('excerpt', ''))
        
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Make sure the FastAPI server is running on port 8000.")
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The query might be too complex.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
st.caption("Powered by Groq (Llama 3.3 70B), LangGraph, and ChromaDB | DataSmith AI GenAI Intern Assignment")