"""
Receptionist Agent - Handles patient greeting, data retrieval, and routing
"""
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tools.patient_retrieval import PatientRetrievalTool
from backend.utils.logger import SystemLogger

logger = SystemLogger()
patient_tool = PatientRetrievalTool()

class ReceptionistAgent:
    """
    Receptionist Agent handles:
    - Patient greeting
    - Patient data retrieval
    - Contextual follow-up questions
    - Routing medical queries to Clinical Agent
    """
    
    def __init__(self):
    # Ensure API key is in environment
        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        
        self.system_prompt = """You are a friendly and professional medical receptionist AI assistant for a post-discharge care service.

Your responsibilities:
1. Greet patients warmly and ask for their name if not provided
2. When you have the patient's name, retrieve their discharge information
3. Ask contextual follow-up questions based on their discharge data
4. Detect medical queries and route them to the Clinical AI Agent
5. Keep conversation warm but professional

IMPORTANT RULES:
- If patient mentions ANY medical symptoms, concerns, or questions about their condition/medications/diet, immediately route to Clinical Agent
- Medical queries include: symptoms, medication questions, diet concerns, side effects, treatment questions
- DO NOT attempt to answer medical questions yourself - always route to Clinical Agent
- Be empathetic and reassuring

When routing to Clinical Agent, say: "This sounds like a medical question. Let me connect you with our Clinical AI Agent who can help you better."

Current context will be provided with patient data if available."""

    def process(self, state: dict) -> dict:
        """
        Process receptionist logic
        """
        message = state.get("message", "")
        patient_name = state.get("patient_name")
        patient_data = state.get("patient_data")
        conversation_history = state.get("conversation_history", [])
        
        logger.log_interaction(
            agent="receptionist",
            action="process_message",
            input_data=message,
            output="Processing...",
            success=True
        )
        
        # Check if we need to fetch patient data
        if not patient_data and patient_name:
            logger.log_interaction(
                agent="receptionist",
                action="fetching_patient_data",
                input_data=patient_name,
                output="Querying database...",
                success=True
            )
            
            patient_data = patient_tool.get_patient_by_name(patient_name)
            state["patient_data"] = patient_data
            
            if patient_data and "error" not in patient_data:
                logger.log_interaction(
                    agent="receptionist",
                    action="patient_data_retrieved",
                    input_data=patient_name,
                    output=f"Found: {patient_data.get('patient_name')}",
                    success=True
                )
            else:
                logger.log_interaction(
                    agent="receptionist",
                    action="patient_data_not_found",
                    input_data=patient_name,
                    output="Patient not found in database",
                    success=False
                )
        
        # Build context
        context = self._build_context(patient_data, conversation_history)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", f"Context: {context}"),
            ("human", message)
        ])
        
        # Generate response
        chain = prompt | self.llm
        response = chain.invoke({"message": message})
        
        response_text = response.content
        
        # Check if should route to clinical agent
        should_route = self._should_route_to_clinical(message, response_text)
        
        logger.log_interaction(
            agent="receptionist",
            action="generate_response",
            input_data=message,
            output=response_text[:200],
            success=True,
            metadata={"should_route": should_route}
        )
        
        # Update state
        state["response"] = response_text
        state["current_agent"] = "receptionist"
        state["should_route_to_clinical"] = should_route
        
        return state
    
    def _build_context(self, patient_data: dict, conversation_history: list) -> str:
        """Build context for the agent"""
        context_parts = []
        
        if patient_data and "error" not in patient_data:
            context_parts.append("PATIENT DATA:")
            context_parts.append(patient_tool.format_patient_summary(patient_data))
        else:
            context_parts.append("No patient data loaded yet.")
        
        if conversation_history:
            context_parts.append("\nRECENT CONVERSATION:")
            for msg in conversation_history[-3:]:  # Last 3 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def _should_route_to_clinical(self, message: str, response: str) -> bool:
        """
        Detect if query should be routed to clinical agent
        """
        medical_keywords = [
            "symptom", "pain", "swelling", "medication", "side effect",
            "treatment", "diet", "dizzy", "nausea", "headache", "fever",
            "blood", "urine", "pressure", "worried", "concern", "help",
            "creatinine", "kidney", "dialysis", "doctor", "hospital",
            "emergency", "breathe", "chest", "heart"
        ]
        
        routing_phrases = [
            "clinical ai agent",
            "medical question",
            "let me connect you",
            "route to clinical"
        ]
        
        message_lower = message.lower()
        response_lower = response.lower()
        
        # Check if message contains medical keywords
        has_medical_keywords = any(keyword in message_lower for keyword in medical_keywords)
        
        # Check if response indicates routing
        indicates_routing = any(phrase in response_lower for phrase in routing_phrases)
        
        return has_medical_keywords or indicates_routing

# Singleton instance
receptionist_agent = ReceptionistAgent()

def receptionist_node(state: dict) -> dict:
    """LangGraph node function"""
    return receptionist_agent.process(state)