import autogen
import os
# Import the functions from your tools file
from tools.file_tools import create_file, read_file, create_directory
from tools.web_tools import web_search, fetch_webpage_content
from tools.git_tools import git_commit

# Set up your local Ollama LLM
config_list = [
    {
        "model": "llama3:8b",
        "api_key": "NA", # Not needed for a local model
        "base_url": "http://localhost:11434/v1",
        "price": [0, 0] # Add this line to specify zero cost for local models
    }
]

# Create a User Proxy Agent
# This agent represents you, the user. It can execute code and talk to other agents.
user_proxy_agent = autogen.UserProxyAgent(
    name="user_proxy_agent",
    system_message="A human admin. You will execute function calls and can ask for clarification. Reply 'exit' to end the conversation.",
    human_input_mode="ALWAYS", # We set this to ALWAYS to enable human-in-the-loop for approvals.
    max_consecutive_auto_reply=5,
    code_execution_config={"use_docker": False},
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", "").upper()
)

# Create an Assistant Agent
# This agent will act as your coding partner. It can write and execute code.
assistant_agent = autogen.AssistantAgent(
    name="assistant_agent",
    system_message="You are a helpful AI assistant and Core Developer Agent for Aeonforge. You have access to functions to search the web, read/write files, create directories, fetch webpage content, and make git commits. You can request API keys from the user when needed using the human-in-the-loop system. Always propose a plan first, execute it step by step, and ask for user approval before making git commits. Reply 'TERMINATE' when the task is done.",
    llm_config={"config_list": config_list}
)

# Register the functions with both agents
user_proxy_agent.register_function(
    function_map={
        "create_file": create_file,
        "read_file": read_file,
        "create_directory": create_directory,
        "web_search": web_search,
        "fetch_webpage_content": fetch_webpage_content,
        "git_commit": git_commit,
    }
)
assistant_agent.register_function(
    function_map={
        "create_file": create_file,
        "read_file": read_file,
        "create_directory": create_directory,
        "web_search": web_search,
        "fetch_webpage_content": fetch_webpage_content,
        "git_commit": git_commit,
    }
)

# Start the conversation
# This is where we give the agent a task.
user_proxy_agent.initiate_chat(
    assistant_agent,
    message="""
    1. Create a new directory named 'scaffold_project'.
    2. Inside 'scaffold_project', initialize a new git repository. (Note: You don't have a tool for this yet, so you should ask me to do it or generate python code with the `git` library).
    3. Perform a web search for 'best practices for python project structure'.
    4. Based on the search results, create a README.md file inside 'scaffold_project' with a summary of the best practices.
    5. After the file is created, ask for my approval and then create a git commit with the message 'Initial project structure and README'.
    """
)