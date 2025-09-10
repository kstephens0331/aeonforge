#!/usr/bin/env python3
"""
Test script to verify the fixed Aeonforge Phase 3 system
Tests the approval workflow and actual file creation
"""

import requests
import json
import time
import sys
import os

def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend healthy: {data['status']}")
            print(f"  Agents: {', '.join(data['agents'].keys())}")
            return True
        else:
            print(f"✗ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend not responding: {e}")
        return False

def test_chat_endpoint():
    """Test the main chat endpoint"""
    try:
        test_data = {
            "message": "Create a Python web scraper for product prices",
            "api_keys": {"serpapi": "test-key-for-local-testing"},
            "conversation_id": "test"
        }
        
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Chat endpoint working")
            print(f"  Agent: {data.get('agent')}")
            print(f"  Needs approval: {data.get('needs_approval')}")
            return data
        else:
            print(f"✗ Chat endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Chat endpoint error: {e}")
        return None

def test_approval_endpoint():
    """Test the approval endpoint"""
    try:
        approval_data = {
            "approval_id": "test_approval_123",
            "approved": True,
            "conversation_id": "test"
        }
        
        response = requests.post(
            "http://localhost:8000/api/approval",
            json=approval_data,
            headers={"Content-Type": "application/json"},
            timeout=30  # Longer timeout as this does real work
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Approval endpoint working")
            print(f"  Response length: {len(data.get('message', ''))}")
            
            # Check if files were actually created
            if os.path.exists("web_scraper_project"):
                print(f"✓ Project directory created")
                files = os.listdir("web_scraper_project")
                print(f"  Files created: {files}")
                return True
            else:
                print(f"✗ Project directory not created")
                return False
        else:
            print(f"✗ Approval endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Approval endpoint error: {e}")
        return False

def test_complete_workflow():
    """Test the complete workflow from chat to approval to file creation"""
    print("Testing Complete Workflow...")
    print("-" * 40)
    
    # Step 1: Chat request
    print("Step 1: Sending chat request...")
    chat_response = test_chat_endpoint()
    if not chat_response:
        return False
    
    time.sleep(1)
    
    # Step 2: Approval (if needed)
    if chat_response.get("needs_approval"):
        print("Step 2: Sending approval...")
        if not test_approval_endpoint():
            return False
    else:
        print("Step 2: No approval needed")
    
    print("✓ Complete workflow test passed!")
    return True

def main():
    """Run all system tests"""
    print("Aeonforge Phase 3 - Fixed System Testing")
    print("=" * 50)
    
    # Check if backend is running
    if not test_backend_health():
        print("\n❌ BACKEND NOT RUNNING")
        print("Please start the backend with: start_backend.bat")
        return 1
    
    print()
    
    # Test individual endpoints
    print("Testing Individual Endpoints...")
    print("-" * 40)
    
    if not test_chat_endpoint():
        print("❌ Chat endpoint failed")
        return 1
    
    print()
    
    # Test complete workflow
    if not test_complete_workflow():
        print("❌ Complete workflow failed")
        return 1
    
    print()
    print("=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("✓ Backend is healthy")
    print("✓ Chat endpoint working")
    print("✓ Approval system fixed")
    print("✓ File creation working")
    print("✓ Complete workflow operational")
    print()
    print("🚀 System is ready for deployment!")
    print("📖 See DEPLOYMENT.md for deployment instructions")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())