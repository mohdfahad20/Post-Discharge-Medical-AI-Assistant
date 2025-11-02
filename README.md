# 🏥 Post-Discharge Medical AI Assistant

**Multi-Agent AI System for Post-Discharge Patient Care**

A production-ready POC demonstrating RAG, LangGraph orchestration, and intelligent agent routing for nephrology patient support.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.108.0-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0-orange.svg)](https://langchain-ai.github.io/langgraph/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [System Workflow](#system-workflow)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This system provides intelligent post-discharge care through a multi-agent architecture:

- **Receptionist Agent**: Patient greeting, data retrieval, and query routing
- **Clinical AI Agent**: Medical advice using RAG + web search fallback
- **30+ Patient Database**: Realistic nephrology discharge reports
- **Comprehensive Logging**: Full observability of agent interactions
- **Source Citations**: Every response backed by textbook or web sources

**Medical Disclaimer**: This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice.

---

## ✨ Features

### 🤖 Multi-Agent System
- **Intelligent Routing**: LangGraph state machine routes queries between agents
- **Context-Aware**: Agents use patient discharge data for personalized responses
- **Seamless Handoffs**: Automatic routing from receptionist to clinical agent

### 📚 Hybrid Knowledge Base
- **RAG System**: FAISS vector store over Comprehensive Clinical Nephrology textbook
- **Web Search Fallback**: Tavily API with DuckDuckGo backup for recent research
- **Source Attribution**: All responses include citations (textbook pages or URLs)

### 🔍 Advanced Retrieval
- **Semantic Search**: HuggingFace embeddings for accurate document matching
- **Multi-Source Answers**: Combines textbook + web + patient data
- **Confidence-Based Routing**: Automatically triggers web search for low-confidence RAG results

### 📊 Comprehensive Logging
- **System-Wide Tracking**: Every interaction logged with timestamps
- **Agent Handoffs**: Clear visibility into routing decisions
- **Real-Time Monitoring**: Live log viewer in Streamlit UI
- **JSON Export**: Structured logs for analysis

### 🎨 User Experience
- **Beautiful UI**: Custom Streamlit interface with agent badges
- **Session Management**: Persistent conversations with UUID-based sessions
- **Export Capability**: Download chat history as JSON
- **Medical Safety**: Prominent disclaimers on all clinical responses

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  STARTUP.PY                         │
│  (Pre-flight checks → Backend → Frontend)           │
└───────────────────┬─────────────────────────────────┘
                    ↓
    ┌───────────────┴────────────────┐
    ↓                                ↓
┌─────────────────┐          ┌──────────────────┐
│  FASTAPI         │          │  STREAMLIT       │
│  (Port 8000)     │◄────────►│  (Port 8501)     │
│                  │   REST   │                  │
│  • /chat         │          │  • Chat UI       │
│  • /logs         │          │  • Log viewer    │
│  • /health       │          │  • Export        │
└────────┬─────────┘          └──────────────────┘
         ↓
┌─────────────────────────────────────┐
│      LANGGRAPH WORKFLOW             │
│                                     │
│  State Machine (workflow.py)        │
│      ↓                              │
│  ┌──────────┐    ┌──────────┐     │
│  │Reception │───►│ Clinical │     │
│  │  Agent   │    │  Agent   │     │
│  └────┬─────┘    └────┬─────┘     │
│       │               │            │
│       ↓               ↓            │
│  ┌─────────┐    ┌─────────┐      │
│  │ Patient │    │   RAG   │      │
│  │   DB    │    │ System  │      │
│  └─────────┘    └────┬────┘      │
│                      │            │
│                      ↓            │
│                 ┌─────────┐      │
│                 │   WEB   │      │
│                 │ SEARCH  │      │
│                 └─────────┘      │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│      SYSTEM LOGGER                  │
│   (logs/system_logs.json)           │
└─────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Core Technologies
| Component | Technology | Reason |
|-----------|-----------|--------|
| **LLM** | Groq (Llama 3.3 70B) | Free tier, fast inference, 70B reasoning |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) | Free, local, privacy-preserving |
| **Vector Store** | FAISS | Fast, local, no dependencies |
| **Database** | SQLite | Simple, embedded, perfect for POC |
| **Orchestration** | LangGraph | Clear state management, visual workflows |
| **Backend** | FastAPI | Async, auto docs, production-ready |
| **Frontend** | Streamlit | Rapid development, Python-native |
| **Web Search** | Tavily + DuckDuckGo | Medical-focused + free fallback |

### Key Libraries
```
langchain==0.2.16
langchain-groq==0.1.9
langgraph==0.2.0
faiss-cpu==1.7.4
sentence-transformers==2.3.1
fastapi==0.108.0
streamlit==1.29.0
tavily-python==0.2.8
```

**Total Cost: $0** (100% free-tier stack)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Groq API key ([get free key](https://console.groq.com))
- Tavily API key (optional, [get free key](https://tavily.com))

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/medical-ai-assistant.git
cd medical-ai-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.template .env
# Edit .env and add your API keys:
#   GROQ_API_KEY=your_groq_key_here
#   TAVILY_API_KEY=your_tavily_key_here (optional)

# 5. Run Day 1 setup (one-time data preparation)
python scripts/generate_dummy_patients.py
python scripts/setup_database.py
python scripts/process_nephrology_book.py

# 6. Start the application
python startup.py
```

The application will automatically:
- ✅ Check dependencies
- ✅ Validate environment
- ✅ Start FastAPI backend (port 8000)
- ✅ Start Streamlit frontend (port 8501)
- ✅ Open browser to http://localhost:8501

---

## 📁 Project Structure

```
medical-ai-assistant/
├── 📄 .env                        # Environment variables (API keys)
├── 📄 requirements.txt            # Python dependencies
├── 📄 startup.py                  # Easy application launcher
│
├── 📁 backend/                    # FastAPI backend
│   ├── 📄 main.py                # API endpoints (/chat, /logs, /health)
│   ├── 📁 agents/
│   │   ├── 📄 receptionist.py    # Patient greeting & routing
│   │   └── 📄 clinical.py        # Medical advice with RAG
│   ├── 📁 graph/
│   │   ├── 📄 state.py           # LangGraph state schema
│   │   └── 📄 workflow.py        # Multi-agent orchestration
│   ├── 📁 tools/
│   │   └── 📄 web_search.py      # Tavily/DDG search
│   └── 📁 utils/
│       └── 📄 logger.py           # Comprehensive logging
│
├── 📁 frontend/
│   └── 📄 app.py                  # Streamlit UI
│
├── 📁 src/                        # Core libraries
│   ├── 📁 rag/
│   │   └── 📄 rag_system.py      # FAISS + Groq RAG
│   └── 📁 tools/
│       └── 📄 patient_retrieval.py # Database queries
│
├── 📁 scripts/                    # Setup scripts
│   ├── 📄 generate_dummy_patients.py  # Create 30 patients
│   ├── 📄 setup_database.py           # Initialize SQLite
│   └── 📄 process_nephrology_book.py  # PDF → FAISS
│
├── 📁 data/                       # Persistent data
│   ├── 📄 patients.db            # SQLite database
│   ├── 📄 patients.json          # Patient records
│   ├── 📄 nephrology_textbook.pdf # Reference book
│   └── 📁 vectorstore/           # FAISS index
│
└── 📁 logs/
    └── 📄 system_logs.json       # All interactions logged
```

---

## 🔄 System Workflow

### Example Conversation

#### Step 1: Initial Greeting
```
User: "Hello"
Receptionist Agent: "Hi! I'm your post-discharge care assistant. 
                     What's your name?"
```

#### Step 2: Patient Identification
```
User: "My name is John Smith"
Receptionist Agent: [Fetches data from database]
                    "Hi John! I found your discharge report from 
                    January 15th for Chronic Kidney Disease Stage 3.
                    How are you feeling today?"
```

#### Step 3: Medical Query → Agent Routing
```
User: "I have swelling in my legs"
Receptionist Agent: "This sounds like a medical concern. Let me 
                     connect you with our Clinical AI Agent."
                     
[AGENT HANDOFF LOGGED]

Clinical Agent: [Queries RAG system]
                "Based on your CKD diagnosis and nephrology 
                guidelines, leg swelling can indicate fluid 
                retention. This is one of the warning signs 
                mentioned in your discharge instructions.
                
                [Source: Comprehensive Clinical Nephrology, Page 142]
                
                You should:
                1. Monitor your weight daily
                2. Check if you're following fluid restrictions
                3. Contact your nephrologist if swelling worsens
                
                ⚠️ Medical Disclaimer: This information is for 
                educational purposes only."
```

#### Step 4: Web Search Fallback
```
User: "What's the latest research on SGLT2 inhibitors for CKD?"
Clinical Agent: [Detects temporal keywords: "latest"]
                [Triggers web search]
                
                "According to recent medical research:
                
                📊 AI Summary: SGLT2 inhibitors have shown...
                
                🔍 Sources:
                1. Recent CKD Study (NIH.gov)
                2. SGLT2 Inhibitor Guidelines (KidneyOrg)
                
                [Using web search for recent information]
                
                ⚠️ Medical Disclaimer..."
```

---

## 📚 API Documentation

### Endpoints

#### `POST /chat`
Process user messages through multi-agent workflow.

**Request:**
```json
{
  "patient_name": "John Smith",
  "message": "I have swelling",
  "session_id": "uuid-here",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "Based on your CKD diagnosis...",
  "agent": "clinical",
  "sources": [
    {
      "type": "textbook",
      "reference": "Comprehensive Clinical Nephrology, Page 142",
      "excerpt": "Leg swelling indicates..."
    }
  ],
  "logs": [...],
  "patient_data": {...}
}
```

#### `GET /logs?limit=50`
Get recent system logs.

#### `GET /health`
Health check endpoint.

#### `DELETE /session/{session_id}`
Clear a session.

**Interactive Docs**: http://localhost:8000/docs

---

## 🧪 Testing

### Manual Testing
```bash
# Test patient retrieval
python src/tools/patient_retrieval.py

# Test RAG system
python src/rag/rag_system.py

# Test web search
python backend/tools/web_search.py

# Test full workflow
python backend/graph/workflow.py
```

### Test Conversation Flow
1. Start application: `python startup.py`
2. Open UI: http://localhost:8501
3. Say "Hello" → Should ask for name
4. Provide name → Should fetch patient data
5. Ask medical question → Should route to clinical agent
6. Check logs in sidebar → Should show agent handoff

### Expected Results
- ✅ Receptionist fetches patient data
- ✅ Medical queries route to clinical agent
- ✅ RAG returns textbook citations
- ✅ Web search triggered for recent queries
- ✅ All interactions logged

---

## 🔧 Development

### Adding a New Agent

1. Create agent file: `backend/agents/new_agent.py`
```python
class NewAgent:
    def __init__(self):
        self.llm = ChatGroq(...)
    
    def process(self, state: dict) -> dict:
        # Your logic here
        return state

new_agent = NewAgent()

def new_agent_node(state: dict) -> dict:
    return new_agent.process(state)
```

2. Update workflow: `backend/graph/workflow.py`
```python
workflow.add_node("new_agent", new_agent_node)
workflow.add_edge("receptionist", "new_agent")
```

### Adding New Tools

1. Create tool file: `backend/tools/my_tool.py`
2. Implement tool function
3. Import in agent: `from backend.tools.my_tool import my_tool`
4. Use in agent's `process()` method

### Environment Variables

```bash
# Required
GROQ_API_KEY=gsk_...           # Groq LLM access
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional
TAVILY_API_KEY=tvly_...        # Web search (optional, falls back to DDG)
TEMPERATURE=0.1                # LLM temperature
```

---

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "startup.py"]
```

### Production Checklist
- [ ] Replace in-memory sessions with Redis
- [ ] Upgrade SQLite to PostgreSQL
- [ ] Add authentication (JWT tokens)
- [ ] Enable HTTPS/SSL
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Add monitoring (Prometheus + Grafana)
- [ ] Implement log rotation
- [ ] Add unit tests
- [ ] Set up CI/CD pipeline

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

### Code Style
- Follow PEP 8
- Add docstrings to all functions
- Include type hints
- Update tests

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **DataSmith AI** - For the internship opportunity
- **Groq** - For free LLM access
- **LangChain/LangGraph** - For agent orchestration framework
- **Comprehensive Clinical Nephrology** - Medical reference material

---

## 📞 Contact

For questions or support:
- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/medical-ai-assistant/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/medical-ai-assistant/discussions)

---