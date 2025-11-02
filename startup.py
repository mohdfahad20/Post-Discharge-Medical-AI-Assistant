"""
Simplified startup script - Streamlit only
Start FastAPI backend manually first: python -m uvicorn backend.main:app --reload --port 8000
"""
import subprocess
import sys
import os
import time

def check_backend():
    """Check if backend is running"""
    print("🔍 Checking if backend is running...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend is running!")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Active sessions: {data.get('active_sessions', 0)}")
            return True
        else:
            print(f"⚠️  Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print("❌ Backend not detected!")
        print("\n💡 Start backend first in another terminal:")
        print("   python -m uvicorn backend.main:app --reload --port 8000")
        print("\nOr use the combined script:")
        print("   python run_both.py")
        return False

def start_streamlit():
    """Start Streamlit frontend"""
    print("\n🚀 Starting Streamlit frontend...")
    print("   Access at: http://localhost:8501")
    print("   Press Ctrl+C to stop\n")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/app.py", 
        "--server.port", "8501"
    ])

def main():
    print("="*60)
    print("🏥 MEDICAL AI ASSISTANT - STREAMLIT LAUNCHER")
    print("="*60)
    print()
    
    # Check backend
    if not check_backend():
        print("\n⚠️  Warning: Backend not running. Streamlit will show errors.")
        response = input("\nStart Streamlit anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Start Streamlit
    start_streamlit()

if __name__ == "__main__":
    main()