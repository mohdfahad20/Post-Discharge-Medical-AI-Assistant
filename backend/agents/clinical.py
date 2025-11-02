"""
Clinical Agent - Handles medical queries using RAG and web search
"""
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.rag.rag_system import NephrologyRAG
from backend.tools.web_search import web_search_tool
from backend.utils.logger import SystemLogger

logger = SystemLogger()

class ClinicalAgent:
    """
    Clinical Agent handles:
    - Medical question answering
    - RAG over nephrology textbook
    - Web search for recent information
    - Medical citations and disclaimers
    """
    
    def __init__(self):
    # Ensure API key is in environment
        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2
        )
        
        # Initialize RAG system
        try:
            self.rag_system = NephrologyRAG()
            self.rag_available = True
            logger.log_interaction(
                agent="clinical",
                action="initialize_rag",
                input_data="",
                output="RAG system loaded successfully",
                success=True
            )
        except Exception as e:
            self.rag_available = False
            logger.log_interaction(
                agent="clinical",
                action="initialize_rag",
                input_data="",
                output=f"RAG system unavailable: {str(e)}",
                success=False
            )
        
        self.system_prompt = """You are a Clinical AI Assistant specializing in nephrology and post-discharge patient care.

Your responsibilities:
1. Answer medical questions using nephrology reference materials
2. Provide evidence-based guidance for kidney disease patients
3. Always cite your sources (textbook pages or web URLs)
4. Include medical disclaimers
5. Be clear, accurate, and compassionate

CRITICAL RULES:
- ALWAYS cite sources: [Source: Comprehensive Clinical Nephrology, Page X] or [Source: URL]
- If information is from web search, clearly state "According to recent research..."
- For serious symptoms (chest pain, severe bleeding, difficulty breathing), advise immediate medical attention
- Never diagnose - only provide educational information
- Always end with medical disclaimer

Medical Disclaimer: "⚠️ This information is for educational purposes only. Always consult with your healthcare provider for medical advice, diagnosis, or treatment."

You will be provided with:
- Patient's discharge information (if available)
- Relevant excerpts from nephrology textbook (if found)
- Web search results (if needed)"""

    def process(self, state: dict) -> dict:
        """
        Process clinical query using RAG and/or web search
        """
        message = state.get("message", "")
        patient_data = state.get("patient_data")
        
        logger.log_interaction(
            agent="clinical",
            action="process_medical_query",
            input_data=message,
            output="Processing...",
            success=True
        )
        
        # Step 1: Try RAG first
        rag_result = None
        rag_used = False
        
        if self.rag_available:
            logger.log_interaction(
                agent="clinical",
                action="querying_rag",
                input_data=message,
                output="Searching nephrology textbook...",
                success=True
            )
            
            rag_result = self.rag_system.query(message, return_sources=True)
            
            if rag_result.get("success"):
                rag_used = True
                logger.log_interaction(
                    agent="clinical",
                    action="rag_query_success",
                    input_data=message,
                    output=f"Found {len(rag_result.get('sources', []))} sources",
                    success=True
                )
            else:
                logger.log_interaction(
                    agent="clinical",
                    action="rag_query_failed",
                    input_data=message,
                    output=rag_result.get("error", "Unknown error"),
                    success=False
                )
        
        # Step 2: Check if web search is needed
        web_results = None
        web_used = False
        
        if self._needs_web_search(message) or not rag_used:
            logger.log_interaction(
                agent="clinical",
                action="initiating_web_search",
                input_data=message,
                output="Searching web for recent information...",
                success=True
            )
            
            web_results = web_search_tool(message)
            
            if web_results and "ERROR" not in web_results:
                web_used = True
                logger.log_interaction(
                    agent="clinical",
                    action="web_search_success",
                    input_data=message,
                    output="Web search completed",
                    success=True
                )
            else:
                logger.log_interaction(
                    agent="clinical",
                    action="web_search_failed",
                    input_data=message,
                    output="Web search failed or no results",
                    success=False
                )
        
        # Step 3: Generate response
        response_text, sources = self._generate_response(
            message=message,
            patient_data=patient_data,
            rag_result=rag_result if rag_used else None,
            web_results=web_results if web_used else None
        )
        
        logger.log_interaction(
            agent="clinical",
            action="generate_clinical_response",
            input_data=message,
            output=response_text[:200],
            success=True,
            metadata={
                "rag_used": rag_used,
                "web_used": web_used,
                "sources_count": len(sources)
            }
        )
        
        # Update state
        state["response"] = response_text
        state["sources"] = sources
        state["current_agent"] = "clinical"
        state["should_route_to_clinical"] = False  # We're done routing
        
        return state
    
    def _needs_web_search(self, message: str) -> bool:
        """
        Determine if query needs web search (for recent research/news)
        """
        web_keywords = [
            "recent", "latest", "new", "current", "2024", "2025",
            "study", "research", "trial", "breakthrough", "news",
            "update", "development", "discovery", "finding"
        ]
        
        message_lower = message.lower()
        
        # Check for temporal keywords
        has_temporal = any(keyword in message_lower for keyword in web_keywords)
        
        # Check for specific research topics that might need recent info
        research_topics = [
            "sglt2", "inhibitor", "clinical trial", "fda approved",
            "guideline", "recommendation", "protocol"
        ]
        has_research_topic = any(topic in message_lower for topic in research_topics)
        
        return has_temporal or has_research_topic
    
    def _generate_response(
        self,
        message: str,
        patient_data: dict,
        rag_result: dict = None,
        web_results: str = None
    ) -> tuple:
        """
        Generate final clinical response
        """
        # Build context
        context_parts = []
        sources = []
        
        # Patient context
        if patient_data and "error" not in patient_data:
            context_parts.append("PATIENT INFORMATION:")
            context_parts.append(f"Diagnosis: {patient_data.get('primary_diagnosis')}")
            context_parts.append(f"Medications: {', '.join(patient_data.get('medications', []))}")
        
        # RAG context
        if rag_result and rag_result.get("success"):
            context_parts.append("\nFROM NEPHROLOGY TEXTBOOK:")
            context_parts.append(rag_result.get("answer", ""))
            
            # Add sources
            for source in rag_result.get("sources", []):
                sources.append({
                    "type": "textbook",
                    "reference": f"Comprehensive Clinical Nephrology, Page {source.get('page')}",
                    "excerpt": source.get("excerpt", "")
                })
        
        # Web search context
        if web_results:
            context_parts.append("\nFROM WEB SEARCH:")
            context_parts.append(web_results)
            sources.append({
                "type": "web",
                "reference": "Web search results",
                "excerpt": web_results[:200] + "..."
            })
        
        context = "\n\n".join(context_parts) if context_parts else "No additional context available."
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", f"Available Information:\n{context}"),
            ("human", message)
        ])
        
        # Generate response
        chain = prompt | self.llm
        response = chain.invoke({"message": message})
        
        response_text = response.content
        
        # Ensure disclaimer is present
        if "⚠️" not in response_text:
            response_text += "\n\n⚠️ This information is for educational purposes only. Always consult with your healthcare provider for medical advice."
        
        return response_text, sources

# Singleton instance
clinical_agent = ClinicalAgent()

def clinical_node(state: dict) -> dict:
    """LangGraph node function"""
    return clinical_agent.process(state)