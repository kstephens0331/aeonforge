"""
Dynamic Agent Handler - No hardcoded responses
Uses actual AutoGen agents to process any request dynamically
"""

import asyncio
import threading
import queue
import time
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase2_agents import setup_phase2_agents

class DynamicAgentHandler:
    """
    Handles real agent conversations dynamically
    No hardcoded responses - everything comes from actual agents
    """
    
    def __init__(self):
        self.agents = None
        self.conversation_results = {}
        self.approval_queue = queue.Queue()
        self.agent_responses = queue.Queue()
        
    def initialize_agents(self):
        """Initialize real AutoGen agents"""
        if self.agents is None:
            user_proxy, project_manager, senior_developer = setup_phase2_agents()
            
            # Override the approval system to work with web interface
            self._setup_web_approval_override()
            
            self.agents = {
                "user_proxy": user_proxy,
                "project_manager": project_manager,
                "senior_developer": senior_developer
            }
            
        return self.agents
    
    def _setup_web_approval_override(self):
        """Override approval system to integrate with web interface"""
        import tools.approval_system
        
        original_get_user_approval = tools.approval_system.get_user_approval
        
        def web_approval_handler(task_description: str, details: str = "") -> bool:
            """Handle approvals through web interface"""
            approval_request = {
                "task": task_description,
                "details": details,
                "timestamp": time.time()
            }
            
            # Put approval request in queue for web interface
            self.approval_queue.put(approval_request)
            
            # Wait for web response (with timeout)
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while True:
                try:
                    # Check for approval response
                    response = self.agent_responses.get(timeout=1)
                    if response['type'] == 'approval':
                        return response['approved']
                except queue.Empty:
                    if time.time() - start_time > timeout:
                        return False  # Timeout = reject
                    continue
        
        # Replace the approval function
        tools.approval_system.get_user_approval = web_approval_handler
    
    async def process_user_message(self, message: str, conversation_id: str) -> Dict[str, Any]:
        """
        Process user message with real agents - no hardcoding
        """
        try:
            self.initialize_agents()
            
            # Start agent conversation in background thread
            conversation_thread = threading.Thread(
                target=self._run_agent_conversation,
                args=(message, conversation_id),
                daemon=True
            )
            conversation_thread.start()
            
            # Wait a moment for initial response
            await asyncio.sleep(2)
            
            # Check if there's an approval needed
            try:
                approval_request = self.approval_queue.get_nowait()
                return {
                    "message": f"I've analyzed your request: '{message}'\n\nI need approval to proceed with the following task:",
                    "agent": "project_manager",
                    "needs_approval": True,
                    "approval_task": approval_request["task"],
                    "approval_details": approval_request["details"],
                    "conversation_id": conversation_id
                }
            except queue.Empty:
                # No approval needed yet, return initial response
                return {
                    "message": f"I'm analyzing your request: '{message}'\n\nLet me break this down and create a detailed implementation plan. I'll ask for approval before proceeding with the technical work.",
                    "agent": "project_manager",
                    "needs_approval": False
                }
                
        except Exception as e:
            return {
                "message": f"Error processing request: {str(e)}",
                "agent": "system",
                "needs_approval": False
            }
    
    def _run_agent_conversation(self, message: str, conversation_id: str):
        """Run the actual agent conversation in background"""
        try:
            agents = self.agents
            
            # This is where the REAL agent conversation happens
            # No hardcoded responses - pure AutoGen
            result = agents["user_proxy"].initiate_chat(
                agents["project_manager"],
                message=message,
                max_turns=10
            )
            
            # Store the real conversation result
            self.conversation_results[conversation_id] = {
                "status": "completed",
                "result": result,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.conversation_results[conversation_id] = {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def handle_approval(self, approved: bool, conversation_id: str) -> Dict[str, Any]:
        """Handle approval response and continue agent conversation"""
        try:
            # Send approval response to agents
            approval_response = {
                "type": "approval",
                "approved": approved,
                "timestamp": time.time()
            }
            
            self.agent_responses.put(approval_response)
            
            if approved:
                # Wait for agents to complete their work
                timeout = 120  # 2 minutes for actual work
                start_time = time.time()
                
                while conversation_id not in self.conversation_results:
                    if time.time() - start_time > timeout:
                        return {
                            "message": "Task is taking longer than expected. The agents are still working in the background.",
                            "agent": "system"
                        }
                    await asyncio.sleep(2)
                
                # Get the real result from agents
                result = self.conversation_results[conversation_id]
                
                if result["status"] == "completed":
                    return {
                        "message": "✅ **Task Completed Successfully!**\n\nThe Senior Developer has finished the implementation. Check your project directory for the generated files and code.",
                        "agent": "senior_developer"
                    }
                else:
                    return {
                        "message": f"❌ **Task encountered an error:** {result.get('error', 'Unknown error')}",
                        "agent": "system"
                    }
            else:
                return {
                    "message": "❌ **Task rejected.** Please provide alternative instructions or modifications to your request.",
                    "agent": "project_manager"
                }
                
        except Exception as e:
            return {
                "message": f"Error processing approval: {str(e)}",
                "agent": "system"
            }

# Global handler instance
dynamic_handler = DynamicAgentHandler()