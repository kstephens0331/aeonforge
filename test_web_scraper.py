"""
Direct test of the web scraper project using Phase 2 agents
Bypasses web interface to show the actual agent capabilities
"""

import sys
import os
sys.path.append('.')

from phase2_agents import setup_phase2_agents
from tools.approval_system import get_user_approval

def test_web_scraper_project():
    """Test the web scraper project directly with Phase 2 agents"""
    print("Aeonforge - Direct Web Scraper Project Test")
    print("=" * 50)
    
    try:
        # Setup agents
        user_proxy, project_manager, senior_developer = setup_phase2_agents()
        
        print("✓ Agents initialized successfully")
        print("✓ Project Manager ready")
        print("✓ Senior Developer ready")
        print()
        
        # Define the web scraper project
        project_request = """
        Create a Python web scraper for product prices with the following requirements:
        
        1. Scrape product information (name, price, availability) from e-commerce sites
        2. Handle multiple product categories
        3. Include proper error handling and rate limiting
        4. Export results to CSV and JSON formats
        5. Generate a PDF report with price analysis
        6. Set up proper project structure with documentation
        
        Make this production-ready with proper logging and configuration.
        """
        
        print("Starting web scraper development project...")
        print("Request:", project_request)
        print()
        print("Note: The system will ask for your approval at key steps.")
        print("Type '1' to approve or '2' to reject when prompted.")
        print()
        
        # Initiate the conversation
        result = user_proxy.initiate_chat(
            project_manager,
            message=project_request
        )
        
        print()
        print("=" * 50)
        print("✓ Web scraper project completed!")
        print("Check the project directory for generated files.")
        
    except Exception as e:
        print(f"Error during project execution: {e}")
        print()
        print("This may be due to missing dependencies or agent configuration issues.")
        print("The web interface approval system is still being refined.")

if __name__ == "__main__":
    test_web_scraper_project()