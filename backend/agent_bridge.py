"""
Agent Bridge - Connects web frontend to AutoGen multi-agent system
Handles real agent conversations and approvals
"""

import asyncio
import threading
import queue
import time
from typing import Dict, Any, Optional, Callable
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase2_agents import setup_phase2_agents
from tools.approval_system import get_user_approval

class AgentBridge:
    """
    Bridge between web frontend and AutoGen agents
    Handles asynchronous agent conversations with web-based approvals
    """
    
    def __init__(self):
        self.agents = None
        self.conversations = {}
        self.pending_approvals = {}
        self.approval_responses = {}
        
    def initialize_agents(self):
        """Initialize the AutoGen agents"""
        if self.agents is None:
            user_proxy, project_manager, senior_developer = setup_phase2_agents()
            self.agents = {
                "user_proxy": user_proxy,
                "project_manager": project_manager,
                "senior_developer": senior_developer
            }
            
            # Override approval system to work with web frontend
            self._setup_web_approval_system()
            
        return self.agents
    
    def _setup_web_approval_system(self):
        """Override the approval system to work with web interface"""
        original_get_user_approval = get_user_approval
        
        def web_get_user_approval(task_description: str, details: str = "") -> bool:
            """Web-compatible approval function"""
            approval_id = f"approval_{int(time.time())}"
            
            # Store approval request
            self.pending_approvals[approval_id] = {
                "task": task_description,
                "details": details,
                "timestamp": time.time()
            }
            
            # Wait for web response (with timeout)
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while approval_id not in self.approval_responses:
                if time.time() - start_time > timeout:
                    return False  # Timeout - reject by default
                time.sleep(0.5)
            
            # Get response
            approved = self.approval_responses[approval_id]
            del self.approval_responses[approval_id]
            del self.pending_approvals[approval_id]
            
            return approved
        
        # Replace the approval function in tools
        import tools.approval_system
        tools.approval_system.get_user_approval = web_get_user_approval
    
    async def start_conversation(self, conversation_id: str, initial_message: str) -> Dict[str, Any]:
        """Start a conversation with the agents"""
        agents = self.initialize_agents()
        
        # Create conversation thread
        conversation_thread = threading.Thread(
            target=self._run_agent_conversation,
            args=(conversation_id, initial_message),
            daemon=True
        )
        conversation_thread.start()
        
        return {
            "status": "started",
            "conversation_id": conversation_id,
            "message": "Conversation started with Project Manager"
        }
    
    def _run_agent_conversation(self, conversation_id: str, message: str):
        """Run the actual agent conversation in a separate thread"""
        try:
            agents = self.agents
            
            # Start conversation between user proxy and project manager
            result = agents["user_proxy"].initiate_chat(
                agents["project_manager"],
                message=message
            )
            
            # Store conversation result
            self.conversations[conversation_id] = {
                "status": "completed",
                "result": result,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.conversations[conversation_id] = {
                "status": "error", 
                "error": str(e),
                "timestamp": time.time()
            }
    
    def get_pending_approvals(self) -> Dict[str, Any]:
        """Get any pending approval requests"""
        return self.pending_approvals.copy()
    
    def submit_approval(self, approval_id: str, approved: bool) -> bool:
        """Submit an approval response"""
        if approval_id in self.pending_approvals:
            self.approval_responses[approval_id] = approved
            return True
        return False
    
    def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Get the status of a conversation"""
        return self.conversations.get(conversation_id, {"status": "not_found"})

# Global bridge instance
agent_bridge = AgentBridge()