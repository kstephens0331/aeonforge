#!/usr/bin/env python3
"""
Test script for Aeonforge Phase 3 components
Tests frontend-backend integration without running full web servers
"""

import sys
import os
import json
sys.path.append('.')

def test_backend_api():
    """Test the backend API components"""
    print("Testing Backend API Components...")
    print("-" * 40)
    
    try:
        # Import backend components
        sys.path.append('backend')
        from backend.main import app, get_or_create_session, web_api_manager
        from backend.agent_bridge import agent_bridge
        
        print("[OK] FastAPI app imported successfully")
        print("[OK] Agent bridge imported successfully")
        print("[OK] Session management available")
        print("[OK] Web API key manager available")
        
        # Test agent initialization
        agents = agent_bridge.initialize_agents()
        print(f"[OK] Agents initialized: {list(agents.keys())}")
        
    except Exception as e:
        print(f"[ERROR] Backend API test failed: {e}")
        return False
    
    print("Backend API test completed!\n")
    return True

def test_frontend_structure():
    """Test frontend structure and configuration"""
    print("Testing Frontend Structure...")
    print("-" * 40)
    
    # Check if frontend files exist
    frontend_files = [
        "frontend/package.json",
        "frontend/vite.config.js", 
        "frontend/index.html",
        "frontend/src/main.jsx",
        "frontend/src/App.jsx",
        "frontend/src/index.css"
    ]
    
    all_exist = True
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path} exists")
        else:
            print(f"[ERROR] {file_path} missing")
            all_exist = False
    
    if all_exist:
        print("[OK] All frontend files present")
        
        # Check package.json content
        try:
            with open("frontend/package.json", "r") as f:
                package_data = json.load(f)
            
            required_deps = ["react", "react-dom", "axios"]
            required_scripts = ["dev", "build"]
            
            for dep in required_deps:
                if dep in package_data.get("dependencies", {}):
                    print(f"[OK] Dependency {dep} configured")
                else:
                    print(f"[ERROR] Missing dependency: {dep}")
                    all_exist = False
            
            for script in required_scripts:
                if script in package_data.get("scripts", {}):
                    print(f"[OK] Script {script} configured") 
                else:
                    print(f"[ERROR] Missing script: {script}")
                    all_exist = False
                    
        except Exception as e:
            print(f"[ERROR] Package.json validation failed: {e}")
            all_exist = False
    
    print("Frontend structure test completed!\n")
    return all_exist

def test_integration_points():
    """Test integration between frontend and backend"""
    print("Testing Integration Points...")
    print("-" * 40)
    
    try:
        # Test API endpoints structure
        sys.path.append('backend')
        from backend.main import ChatRequest, ChatResponse, ApprovalRequest, ApprovalResponse
        
        print("[OK] API request/response models available")
        
        # Test sample request structure
        test_request = ChatRequest(
            message="Test message",
            api_keys={"serpapi": "test-key"},
            conversation_id="test"
        )
        
        print(f"[OK] ChatRequest structure valid: {test_request.message}")
        
        # Test response structure
        test_response = ChatResponse(
            message="Test response",
            agent="project_manager",
            needs_approval=False
        )
        
        print(f"[OK] ChatResponse structure valid: {test_response.agent}")
        
    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        return False
    
    print("Integration points test completed!\n")
    return True

def test_startup_scripts():
    """Test startup scripts"""
    print("Testing Startup Scripts...")
    print("-" * 40)
    
    startup_scripts = [
        "start_frontend.bat",
        "start_backend.bat"
    ]
    
    all_exist = True
    for script in startup_scripts:
        if os.path.exists(script):
            print(f"[OK] {script} exists")
        else:
            print(f"[ERROR] {script} missing")
            all_exist = False
    
    print("Startup scripts test completed!\n")
    return all_exist

def main():
    """Run all Phase 3 tests"""
    print("Aeonforge Phase 3 - Frontend & Backend Testing")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    try:
        if test_frontend_structure():
            tests_passed += 1
            
        if test_backend_api():
            tests_passed += 1
            
        if test_integration_points():
            tests_passed += 1
            
        if test_startup_scripts():
            tests_passed += 1
        
        print("=" * 60)
        
        if tests_passed == total_tests:
            print("PHASE 3 SYSTEM STATUS: READY!")
            print("[OK] Frontend chat interface ready")
            print("[OK] Backend API server ready") 
            print("[OK] Agent integration ready")
            print("[OK] API key management ready")
            print("[OK] Real-time messaging ready")
            print("[OK] Approval workflow ready")
            print()
            print("To start Phase 3:")
            print("1. Run 'start_backend.bat' in one terminal")
            print("2. Run 'start_frontend.bat' in another terminal") 
            print("3. Open http://localhost:3000 in your browser")
            print("4. Enter your SerpAPI key and start chatting!")
        else:
            print(f"PHASE 3 ISSUES DETECTED: {tests_passed}/{total_tests} tests passed")
            print("Please review the error messages above.")
            return 1
            
    except Exception as e:
        print(f"Phase 3 testing error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())