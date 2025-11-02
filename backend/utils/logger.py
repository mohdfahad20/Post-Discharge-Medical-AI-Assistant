"""
Comprehensive Logging System for Multi-Agent Workflow
Logs all interactions, agent handoffs, and system events
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class SystemLogger:
    """
    Centralized logging system for all agent interactions
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(SystemLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.logs = []
        self.log_file = "logs/system_logs.json"
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Load existing logs if available
        self._load_logs()
    
    def _load_logs(self):
        """Load existing logs from file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.logs = json.load(f)
            except:
                self.logs = []
    
    def _save_logs(self):
        """Save logs to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.logs, f, indent=2)
        except Exception as e:
            print(f"Error saving logs: {str(e)}")
    
    def log_interaction(
        self,
        agent: str,
        action: str,
        input_data: str,
        output: str,
        success: bool,
        metadata: Optional[Dict] = None
    ):
        """
        Log an agent interaction
        
        Args:
            agent: Agent name (receptionist, clinical, api, etc.)
            action: Action performed (process_message, query_rag, etc.)
            input_data: Input to the action
            output: Output from the action
            success: Whether action succeeded
            metadata: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "input": input_data[:500] if input_data else "",  # Truncate long inputs
            "output": output[:500] if output else "",  # Truncate long outputs
            "success": success,
            "metadata": metadata or {}
        }
        
        self.logs.append(log_entry)
        
        # Save every 10 logs
        if len(self.logs) % 10 == 0:
            self._save_logs()
        
        # Print to console for debugging
        status = "✅" if success else "❌"
        print(f"{status} [{agent}] {action}: {output[:100]}")
    
    def log_agent_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        message: str
    ):
        """
        Log agent-to-agent handoff
        """
        self.log_interaction(
            agent="system",
            action="agent_handoff",
            input_data=f"{from_agent} -> {to_agent}",
            output=reason,
            success=True,
            metadata={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message": message[:200]
            }
        )
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get most recent logs"""
        return self.logs[-limit:]
    
    def get_logs_by_agent(self, agent: str, limit: int = 50) -> List[Dict]:
        """Get logs for specific agent"""
        agent_logs = [log for log in self.logs if log["agent"] == agent]
        return agent_logs[-limit:]
    
    def get_logs_by_session(self, session_id: str) -> List[Dict]:
        """Get all logs for a session"""
        return [
            log for log in self.logs 
            if log.get("metadata", {}).get("session_id") == session_id
        ]
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs = []
        self._save_logs()
    
    def export_logs(self, filepath: str):
        """Export logs to custom file"""
        with open(filepath, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def get_statistics(self) -> Dict:
        """Get logging statistics"""
        total = len(self.logs)
        successful = sum(1 for log in self.logs if log["success"])
        failed = total - successful
        
        agents = {}
        for log in self.logs:
            agent = log["agent"]
            agents[agent] = agents.get(agent, 0) + 1
        
        return {
            "total_logs": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            "logs_by_agent": agents
        }

# Test the logger
if __name__ == "__main__":
    logger = SystemLogger()
    
    # Test logging
    logger.log_interaction(
        agent="test",
        action="test_action",
        input_data="test input",
        output="test output",
        success=True,
        metadata={"test": "metadata"}
    )
    
    # Test statistics
    stats = logger.get_statistics()
    print("\nLogger Statistics:")
    print(json.dumps(stats, indent=2))