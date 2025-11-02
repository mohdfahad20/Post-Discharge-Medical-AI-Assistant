"""
FastAPI Backend for Multi-Agent Medical Assistant
Handles chat requests and routes them through LangGraph workflow
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.graph.workflow import create_workflow
from backend.utils.logger import SystemLogger

app = FastAPI(title="Medical AI Assistant API", version="1.0.0")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logger
logger = SystemLogger()

# Initialize workflow
workflow = create_workflow()

# Request/Response Models
class ChatRequest(BaseModel):
    patient_name: Optional[str] = None
    message: str
    session_id: str
    conversation_history: List[Dict] = []

class ChatResponse(BaseModel):
    response: str
    agent: str
    sources: List[Dict] = []
    logs: List[Dict] = []
    patient_data: Optional[Dict] = None

# Session storage (in production, use Redis/database)
sessions = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Medical AI Assistant",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes messages through multi-agent workflow
    """
    try:
        # Log incoming request
        logger.log_interaction(
            agent="api",
            action="chat_request_received",
            input_data=request.message,
            output="Processing...",
            success=True,
            metadata={"session_id": request.session_id}
        )
        
        # Get or create session
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                "patient_name": None,
                "patient_data": None,
                "conversation_history": [],
                "current_agent": "receptionist"
            }
        
        session = sessions[request.session_id]
        
        # Update session with patient name if provided
        if request.patient_name:
            session["patient_name"] = request.patient_name
        
        # Prepare initial state for workflow
        initial_state = {
            "patient_name": session.get("patient_name"),
            "patient_data": session.get("patient_data"),
            "message": request.message,
            "conversation_history": request.conversation_history,
            "current_agent": session.get("current_agent", "receptionist"),
            "response": "",
            "sources": [],
            "should_route_to_clinical": False,
            "session_id": request.session_id
        }
        
        # Run workflow
        final_state = workflow.invoke(initial_state)
        
        # Update session
        sessions[request.session_id].update({
            "patient_name": final_state.get("patient_name"),
            "patient_data": final_state.get("patient_data"),
            "current_agent": final_state.get("current_agent"),
            "conversation_history": final_state.get("conversation_history", [])
        })
        
        # Get logs from logger
        recent_logs = logger.get_recent_logs(limit=10)
        
        # Log successful response
        logger.log_interaction(
            agent=final_state.get("current_agent", "unknown"),
            action="chat_response_sent",
            input_data=request.message,
            output=final_state.get("response", "")[:200],
            success=True,
            metadata={
                "session_id": request.session_id,
                "sources_count": len(final_state.get("sources", []))
            }
        )
        
        return ChatResponse(
            response=final_state.get("response", ""),
            agent=final_state.get("current_agent", "receptionist"),
            sources=final_state.get("sources", []),
            logs=recent_logs,
            patient_data=final_state.get("patient_data")
        )
        
    except Exception as e:
        logger.log_interaction(
            agent="api",
            action="chat_error",
            input_data=request.message,
            output=str(e),
            success=False,
            metadata={"session_id": request.session_id}
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs(limit: int = 50):
    """Get recent system logs"""
    return {"logs": logger.get_recent_logs(limit=limit)}

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} cleared"}
    return {"message": "Session not found"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "active_sessions": len(sessions),
        "total_logs": len(logger.logs),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Medical AI Assistant Backend...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )