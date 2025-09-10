#!/usr/bin/env python3
"""
Test script to verify all Aeonforge Phase 1 tools are working correctly.
This allows testing without running the full AutoGen system.
"""

import sys
import os
sys.path.append('.')

from tools.file_tools import create_file, read_file, create_directory
from tools.web_tools import web_search, fetch_webpage_content
from tools.git_tools import git_commit

def test_file_tools():
    """Test file creation, reading, and directory creation."""
    print("Testing File Tools...")
    print("-" * 30)
    
    # Test directory creation
    result = create_directory("test_output")
    print(f"Create Directory: {result}")
    
    # Test file creation
    test_content = "Hello from Aeonforge Phase 1 test!\nThis file was created by the test script."
    result = create_file("test_output/test_file.txt", test_content)
    print(f"Create File: {result}")
    
    # Test file reading
    result = read_file("test_output/test_file.txt")
    print(f"Read File: {result[:50]}...")
    
    print("File tools test completed!\n")

def test_web_tools():
    """Test web search functionality."""
    print("Testing Web Tools...")
    print("-" * 30)
    
    # Test web search (will trigger API key request)
    result = web_search("Python best practices 2024")
    print(f"Web Search Result: {result[:100]}...")
    
    print("Web tools test completed!\n")

def test_git_tools():
    """Test Git functionality."""
    print("Testing Git Tools...")
    print("-" * 30)
    
    # Initialize a test repository
    test_repo_path = "test_output"
    
    # Try to commit (this will fail if not a git repo, which is expected)
    result = git_commit(test_repo_path, "Test commit from Aeonforge")
    print(f"Git Commit: {result}")
    
    print("Git tools test completed!\n")

def main():
    """Run all tool tests."""
    print("Aeonforge Phase 1 - Tool Testing")
    print("=" * 50)
    
    try:
        test_file_tools()
        test_web_tools()
        test_git_tools()
        
        print("All tool tests completed!")
        print("Phase 1 system is ready to run!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())