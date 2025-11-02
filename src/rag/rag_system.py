"""
RAG System for Nephrology Reference Book
Uses FAISS for vector search and LangChain for retrieval
"""
import os
from typing import List, Dict, Tuple
from datetime import datetime
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq 
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class NephrologyRAG:
    def __init__(self, vectorstore_path: str = "data/vectorstore"):
        """
        Initialize RAG system with FAISS vector store
        """
        self.vectorstore_path = vectorstore_path
        self.log_entries = []
        
        # Load embeddings
        from langchain_community.embeddings import HuggingFaceEmbeddings

        # Load embeddings
        print("Loading HuggingFace embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
        model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load FAISS index
        print("Loading FAISS vector store...")
        self.vectorstore = FAISS.load_local(
            vectorstore_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        print(f"✅ Loaded vector store with {self.vectorstore.index.ntotal} vectors")
        
        # Initialize LLM - Set API key in environment first
        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1
        ) 
        
        # Create retrieval chain
        self._setup_retrieval_chain()
    
    def _log(self, action: str, query: str, output: str, success: bool, metadata: Dict = None):
        """Internal logging"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": "rag_system",
            "action": action,
            "query": query,
            "output": output[:200] if output else "",
            "success": success,
            "metadata": metadata or {}
        }
        self.log_entries.append(log_entry)
    
    def _setup_retrieval_chain(self):
        """Setup RetrievalQA chain with custom prompt"""
        
        prompt_template = """You are a clinical AI assistant specializing in nephrology. 
Use the following context from the Comprehensive Clinical Nephrology textbook to answer the question.

If the context contains relevant information, provide a clear, medically accurate answer with citations.
If the context doesn't contain enough information, say "I don't have sufficient information in my reference materials to answer this question fully."

Always include:
1. A clear answer based on the context
2. Citation to the source material (page number)
3. Medical disclaimer if giving clinical advice

Context from nephrology textbook:
{context}

Question: {question}

Answer (with citations):"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 4}  # Retrieve top 4 chunks
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
    
    def query(self, question: str, return_sources: bool = True) -> Dict:
        """
        Query the RAG system
        
        Args:
            question: User's medical query
            return_sources: Whether to include source citations
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # Execute RAG query
            result = self.qa_chain.invoke({"query": question})
            
            answer = result['result']
            source_docs = result.get('source_documents', [])
            
            # Format sources
            sources = []
            if return_sources and source_docs:
                for doc in source_docs:
                    sources.append({
                        "page": doc.metadata.get('page', 'Unknown'),
                        "source": doc.metadata.get('source', 'Unknown'),
                        "excerpt": doc.page_content[:150] + "..."
                    })
            
            # Log successful query
            self._log(
                "query",
                question,
                answer,
                True,
                {"num_sources": len(sources)}
            )
            
            return {
                "answer": answer,
                "sources": sources,
                "success": True,
                "used_rag": True
            }
            
        except Exception as e:
            error_msg = f"RAG query failed: {str(e)}"
            self._log("query", question, error_msg, False)
            return {
                "answer": None,
                "error": error_msg,
                "success": False,
                "used_rag": False
            }
    
    def similarity_search(self, query: str, k: int = 4) -> List[Tuple[str, float, Dict]]:
        """
        Direct similarity search (useful for debugging)
        
        Returns:
            List of (content, score, metadata) tuples
        """
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append((
                    doc.page_content,
                    score,
                    doc.metadata
                ))
            
            self._log(
                "similarity_search",
                query,
                f"Found {len(results)} results",
                True
            )
            
            return formatted_results
            
        except Exception as e:
            self._log("similarity_search", query, f"Error: {str(e)}", False)
            return []
    
    def format_answer_with_citations(self, answer: str, sources: List[Dict]) -> str:
        """
        Format answer with proper citations
        """
        formatted = answer + "\n\n"
        
        if sources:
            formatted += "📚 Sources:\n"
            for i, source in enumerate(sources, 1):
                formatted += f"{i}. Page {source['page']} - {source['source']}\n"
                formatted += f"   \"{source['excerpt']}\"\n\n"
        
        formatted += "\n⚠️ Medical Disclaimer: This information is for educational purposes only. Always consult with healthcare professionals for medical advice."
        
        return formatted
    
    def get_logs(self) -> List[Dict]:
        """Return all logged interactions"""
        return self.log_entries


# LangChain Tool Wrapper
def create_langchain_rag_tool():
    """
    Create LangChain-compatible tool for RAG queries
    """
    from langchain.tools import Tool
    
    rag_system = NephrologyRAG()
    
    def query_nephrology_book(question: str) -> str:
        """Query the nephrology reference textbook for medical information"""
        result = rag_system.query(question)
        
        if result['success']:
            return rag_system.format_answer_with_citations(
                result['answer'],
                result['sources']
            )
        else:
            return f"Unable to retrieve information: {result.get('error', 'Unknown error')}"
    
    tool = Tool(
        name="query_nephrology_textbook",
        description=(
            "Searches the Comprehensive Clinical Nephrology textbook to answer "
            "medical questions about kidney disease, treatments, symptoms, and clinical guidelines. "
            "Use this for any nephrology-related medical questions. "
            "Input should be a clear medical question."
        ),
        func=query_nephrology_book
    )
    
    return tool, rag_system


# Test the RAG system
if __name__ == "__main__":
    print("Testing RAG System...\n")
    
    rag = NephrologyRAG()
    
    # Test queries
    test_questions = [
        "What are the symptoms of chronic kidney disease?",
        "What medications are used for CKD treatment?",
        "What dietary restrictions are recommended for kidney patients?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print('='*60)
        
        result = rag.query(question)
        
        if result['success']:
            print(f"\n{result['answer']}")
            print(f"\n📚 Found {len(result['sources'])} sources")
            for i, source in enumerate(result['sources'][:2], 1):
                print(f"\n{i}. Page {source['page']}:")
                print(f"   {source['excerpt']}")
        else:
            print(f"\n❌ Error: {result['error']}")
    
    # Show logs
    print(f"\n\n{'='*60}")
    print("Query Logs:")
    print('='*60)
    for log in rag.get_logs():
        print(f"{log['timestamp']} - {log['action']}: Success={log['success']}")