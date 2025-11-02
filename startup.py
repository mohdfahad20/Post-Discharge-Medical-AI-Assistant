"""
Easy startup script for the Medical AI Assistant
Starts both FastAPI backend and Streamlit frontend
"""
import subprocess
import time
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "streamlit", "langgraph",
        "langchain", "langchain-groq", "duckduckgo-search"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("\n✅ All dependencies installed!\n")
    return True

def check_env_file():
    """Check if .env file exists and has required keys"""
    print("🔍 Checking environment variables...")
    
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("\nCreate a .env file with:")
        print("GROQ_API_KEY=your_key_here")
        print("LLM_MODEL=llama-3.3-70b-versatile")
        print("EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2")
        print("TEMPERATURE=0.1")
        return False
    
    with open(".env", "r") as f:
        env_content = f.read()
        if "GROQ_API_KEY" in env_content:
            print("  ✅ GROQ_API_KEY found")
        else:
            print("  ❌ GROQ_API_KEY missing in .env")
            return False
    
    print("\n✅ Environment configured!\n")
    return True

def check_data_setup():
    """Check if Day 1 data is ready"""
    print("🔍 Checking Day 1 data setup...")
    
    checks = {
        "data/patients.db": "Patient database",
        "data/vectorstore": "Vector store"
    }
    
    all_good = True
    for path, name in checks.items():
        if os.path.exists(path):
            print(f"  ✅ {name}")
        else:
            print(f"  ⚠️  {name} not found (some features may not work)")
            all_good = False
    
    if not all_good:
        print("\n⚠️  Run Day 1 scripts first if you haven't:")
        print("  python scripts/generate_dummy_patients.py")
        print("  python scripts/setup_database.py")
        print("  python scripts/process_nephrology_book.py")
    
    print()
    return True  # Don't block startup

def create_init_files():
    """Create __init__.py files if they don't exist"""
    init_paths = [
        "backend/__init__.py",
        "backend/agents/__init__.py",
        "backend/graph/__init__.py",
        "backend/tools/__init__.py",
        "backend/utils/__init__.py"
    ]
    
    for path in init_paths:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(path):
            open(path, 'a').close()

def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return backend_process

def start_frontend():
    """Start Streamlit frontend"""
    print("🚀 Starting Streamlit frontend...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return frontend_process

def main():
    """Main startup sequence"""
    print("="*60)
    print("🏥 MEDICAL AI ASSISTANT - STARTUP")
    print("="*60)
    print()
    
    # Pre-flight checks
    if not check_dependencies():
        print("\n❌ Dependency check failed. Fix issues and try again.")
        return
    
    if not check_env_file():
        print("\n❌ Environment check failed. Fix .env file and try again.")
        return
    
    check_data_setup()
    
    # Create init files
    create_init_files()
    
    print("="*60)
    print("🚀 STARTING SERVICES")
    print("="*60)
    print()
    
    # Start backend
    backend = start_backend()
    print("⏳ Waiting for backend to start...")
    time.sleep(5)
    
    # Check if backend started
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend started successfully!")
        else:
            print("⚠️  Backend may not be ready yet")
    except:
        print("⚠️  Backend connection failed - it may still be starting")
    
    print()
    
    # Start frontend
    frontend = start_frontend()
    print("⏳ Waiting for frontend to start...")
    time.sleep(3)
    
    print()
    print("="*60)
    print("✅ APPLICATION STARTED!")
    print("="*60)
    print()
    print("🌐 Access the application:")
    print("   Frontend: http://localhost:8501")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop all services")
    print("="*60)
    
    try:
        # Wait for keyboard interrupt
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("✅ All services stopped.")

if __name__ == "__main__":
    main()