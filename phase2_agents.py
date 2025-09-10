"""
Phase 2 Multi-Agent System for Aeonforge
Specialized Project Manager and Senior Developer agents with human-in-the-loop
"""

import autogen
import os
from tools.file_tools import create_file, read_file, create_directory
from tools.web_tools import web_search, fetch_webpage_content
from tools.git_tools import git_commit
from tools.pdf_tools import create_business_document, fill_pdf_form
from tools.approval_system import get_user_approval, pause_for_user_input
from tools.self_healing import healing_system

# Set up your local Ollama LLM configuration
config_list = [
    {
        "model": "llama3:8b",
        "api_key": "NA",  # Not needed for a local model
        "base_url": "http://localhost:11434/v1",
        "price": [0, 0]  # Zero cost for local models
    }
]

class AeonforgeProjectManager(autogen.AssistantAgent):
    """
    Project Manager Agent - Handles task planning and delegation with human approval
    """
    
    def __init__(self, name="project_manager"):
        super().__init__(
            name=name,
            system_message="""You are the Project Manager for Aeonforge, an AI development system. 
            
Your responsibilities:
1. Break down high-level requests into specific, actionable tasks
2. Create detailed project plans with clear steps
3. Delegate tasks to the Senior Developer agent
4. ALWAYS ask for human approval before delegating tasks to other agents
5. Coordinate between different agents and ensure project success
6. Handle project timeline and resource management

Important: You MUST pause and request user approval with a clear 1/2 choice before delegating any task to the Senior Developer. Explain what task you want to delegate and why.

Reply with 'TASK_COMPLETED' when the entire project is finished.""",
            llm_config={"config_list": config_list}
        )

class AeonforgeSeniorDeveloper(autogen.AssistantAgent):
    """
    Senior Developer Agent - Handles technical implementation tasks
    """
    
    def __init__(self, name="senior_developer"):
        super().__init__(
            name=name,
            system_message="""You are the Senior Developer for Aeonforge, an AI development system.

Your responsibilities:
1. Implement technical solutions assigned by the Project Manager
2. Write code, create files, and manage development tasks
3. Use available tools to complete development work
4. Perform web research when needed for implementation
5. Handle git operations and version control
6. Create documentation and project files
7. Generate PDF documents and business reports when requested

Available tools: create_file, read_file, create_directory, web_search, fetch_webpage_content, git_commit, create_business_document, fill_pdf_form

Always provide detailed progress updates and ask for clarification when requirements are unclear.
Reply with 'DEVELOPMENT_COMPLETE' when your assigned task is finished.""",
            llm_config={"config_list": config_list}
        )

class AeonforgeUserProxy(autogen.UserProxyAgent):
    """
    Enhanced User Proxy Agent for Phase 2 with approval workflow
    """
    
    def __init__(self, name="user_proxy"):
        super().__init__(
            name=name,
            system_message="""You are the human administrator for the Aeonforge system. You coordinate between the Project Manager and Senior Developer agents, providing approvals and guidance.

Key responsibilities:
1. Review and approve task delegations from Project Manager
2. Provide input when agents request clarification
3. Monitor project progress and quality
4. Make final decisions on project direction

When agents ask for approval, respond with:
- "1" to approve and continue
- "2" to reject or request changes

You can also provide additional guidance or modifications to proposed plans.""",
            human_input_mode="ALWAYS",
            max_consecutive_auto_reply=5,
            code_execution_config={"use_docker": False},
            is_termination_msg=lambda x: any(term in x.get("content", "").upper() 
                                           for term in ["TASK_COMPLETED", "DEVELOPMENT_COMPLETE", "TERMINATE"])
        )

def setup_phase2_agents():
    """
    Sets up and configures all Phase 2 agents with their tools
    """
    # Create agents
    user_proxy = AeonforgeUserProxy()
    project_manager = AeonforgeProjectManager()
    senior_developer = AeonforgeSeniorDeveloper()
    
    # Register tools with all agents
    tool_map = {
        "create_file": create_file,
        "read_file": read_file,
        "create_directory": create_directory,
        "web_search": web_search,
        "fetch_webpage_content": fetch_webpage_content,
        "git_commit": git_commit,
        "create_business_document": create_business_document,
        "fill_pdf_form": fill_pdf_form,
    }
    
    # Register tools with each agent
    for agent in [user_proxy, project_manager, senior_developer]:
        agent.register_function(function_map=tool_map)
    
    return user_proxy, project_manager, senior_developer

def run_phase2_demo():
    """
    Runs a demonstration of the Phase 2 multi-agent system
    """
    print("="*60)
    print("AEONFORGE PHASE 2 - MULTI-AGENT COLLABORATION DEMO")
    print("="*60)
    
    # Setup agents
    user_proxy, project_manager, senior_developer = setup_phase2_agents()
    
    # Demo task: Create a business project with PDF documentation
    demo_task = """
    Project Request: Create a complete business project structure for a new SaaS application called 'TaskMaster'.
    
    Requirements:
    1. Research SaaS application best practices
    2. Create proper project directory structure
    3. Generate business documentation (proposal PDF)
    4. Set up git repository and initial commit
    5. Create a development roadmap document
    
    Please coordinate between Project Manager and Senior Developer to complete this task.
    """
    
    print(f"Demo Task: {demo_task}")
    print("\nStarting multi-agent conversation...")
    
    # Start the conversation
    user_proxy.initiate_chat(
        project_manager,
        message=demo_task
    )

def execute_task_with_healing(task_func, *args, **kwargs):
    """
    Wrapper to execute tasks with self-healing capabilities
    """
    task_name = kwargs.pop('task_name', 'Unknown Task')
    return healing_system.execute_with_healing(
        task_func, args, kwargs, task_name
    )

if __name__ == "__main__":
    # Run the Phase 2 demonstration
    try:
        run_phase2_demo()
    except KeyboardInterrupt:
        print("\n\nPhase 2 demo interrupted by user.")
    except Exception as e:
        print(f"\nPhase 2 demo encountered an error: {e}")
        print("Self-healing system would handle this in a production environment.")