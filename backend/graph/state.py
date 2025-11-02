"""
State Schema for LangGraph Multi-Agent Workflow
Defines the structure of data flowing through the agent graph
"""
from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    """
    State that flows through the multi-agent workflow
    """
    # Patient information
    patient_name: Optional[str]
    patient_data: Optional[Dict]
    
    # Conversation
    message: str
    conversation_history: List[Dict]
    
    # Agent control
    current_agent: str  # "receptionist" or "clinical"
    should_route_to_clinical: bool
    
    # Response
    response: str
    sources: List[Dict]
    
    # Session
    session_id: str