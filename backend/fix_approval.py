"""
Quick fix for approval system integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test the backend approval endpoint
import requests
import json

def test_backend_connection():
    """Test if backend is running and responsive"""
    try:
        response = requests.get("http://localhost:8000/")
        print(f"Backend status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Backend connection failed: {e}")
        return False

def test_approval_endpoint():
    """Test the approval endpoint specifically"""
    try:
        test_data = {
            "approval_id": "test_123",
            "approved": True,
            "conversation_id": "main"
        }
        
        response = requests.post(
            "http://localhost:8000/api/approval",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Approval endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
        
    except Exception as e:
        print(f"Approval endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Aeonforge Phase 3 Backend...")
    print("=" * 40)
    
    if test_backend_connection():
        print("✓ Backend is running")
        
        if test_approval_endpoint():
            print("✓ Approval endpoint working")
        else:
            print("✗ Approval endpoint has issues")
    else:
        print("✗ Backend not running - start with start_backend.bat")