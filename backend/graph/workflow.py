"""
LangGraph Workflow - Multi-Agent State Machine
Orchestrates routing between Receptionist and Clinical agents
"""
from langgraph.graph import StateGraph, END
from typing import Literal
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.graph.state import AgentState
from backend.agents.receptionist import receptionist_node
from backend.agents.clinical import clinical_node
from backend.utils.logger import SystemLogger

logger = SystemLogger()

def route_decision(state: AgentState) -> Literal["clinical", "end"]:
    """
    Routing decision: Should we route to clinical agent or end?
    """
    should_route = state.get("should_route_to_clinical", False)
    
    if should_route:
        logger.log_agent_handoff(
            from_agent="receptionist",
            to_agent="clinical",
            reason="Medical query detected",
            message=state.get("message", "")
        )
        return "clinical"
    else:
        return "end"

def create_workflow():
    """
    Create the LangGraph workflow with agent nodes and routing
    """
    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("receptionist", receptionist_node)
    workflow.add_node("clinical", clinical_node)
    
    # Set entry point
    workflow.set_entry_point("receptionist")
    
    # Add conditional routing from receptionist
    workflow.add_conditional_edges(
        "receptionist",
        route_decision,
        {
            "clinical": "clinical",
            "end": END
        }
    )
    
    # Clinical agent always ends
    workflow.add_edge("clinical", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.log_interaction(
        agent="system",
        action="workflow_initialized",
        input_data="",
        output="LangGraph workflow compiled successfully",
        success=True
    )
    
    return app

# For testing
if __name__ == "__main__":
    print("Testing LangGraph Workflow...\n")
    
    workflow = create_workflow()
    
    # Test state
    test_state = {
        "patient_name": None,
        "patient_data": None,
        "message": "Hello, my name is John Smith",
        "conversation_history": [],
        "current_agent": "receptionist",
        "response": "",
        "sources": [],
        "should_route_to_clinical": False,
        "session_id": "test_123"
    }
    
    print("Initial state:")
    print(f"Message: {test_state['message']}")
    print(f"Agent: {test_state['current_agent']}\n")
    
    # Run workflow
    result = workflow.invoke(test_state)
    
    print("\nFinal state:")
    print(f"Agent: {result.get('current_agent')}")
    print(f"Response: {result.get('response')[:200]}...")
    print(f"Should route: {result.get('should_route_to_clinical')}")