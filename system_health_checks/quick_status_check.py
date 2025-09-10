#!/usr/bin/env python3
"""
Aeonforge Quick Status Check
===========================

Lightweight health check for rapid system status verification.
This runs a subset of the most critical checks for quick status updates.

Usage:
    python quick_status_check.py
    
Returns: Exit code 0 for healthy, 1 for warnings, 2 for critical issues
"""

import os
import sys
import time
import json
import importlib
from datetime import datetime
from typing import Tuple, Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

class QuickStatusChecker:
    """Lightweight system status checker for rapid health verification"""
    
    def __init__(self):
        self.project_root = project_root
        self.status = "HEALTHY"
        self.issues = []
        
    def check_core_imports(self) -> Tuple[bool, str]:
        """Test critical system imports"""
        try:
            # Test tool batch imports
            importlib.import_module("tools.natural_language")
            importlib.import_module("tools.business_productivity")
            importlib.import_module("tools.creative_design")
            importlib.import_module("tools.data_analysis")
            
            return True, "Core imports successful"
        except Exception as e:
            return False, f"Import error: {e}"
    
    def check_tool_functionality(self) -> Tuple[bool, str]:
        """Test basic tool instantiation"""
        try:
            from tools.natural_language import UniversalTranslator
            from tools.business_productivity import ExcelMaster
            
            # Test instantiation
            translator = UniversalTranslator()
            excel_tool = ExcelMaster()
            
            return True, "Tool instantiation successful"
        except Exception as e:
            return False, f"Tool instantiation error: {e}"
    
    def check_file_system(self) -> Tuple[bool, str]:
        """Check essential files and directories"""
        required_paths = [
            "tools/",
            "main.py",
            "requirements.txt",
            "PROJECT_ROADMAP.md"
        ]
        
        missing = []
        for path in required_paths:
            if not os.path.exists(os.path.join(self.project_root, path)):
                missing.append(path)
        
        if not missing:
            return True, "File system structure intact"
        else:
            return False, f"Missing: {', '.join(missing)}"
    
    def check_api_keys(self) -> Tuple[bool, str]:
        """Check if API keys are configured"""
        env_file = os.path.join(self.project_root, ".env")
        
        if not os.path.exists(env_file):
            return False, ".env file missing"
        
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            key_indicators = ["OPENAI_API_KEY", "GEMINI_API_KEY", "SERPAPI_KEY"]
            present_keys = sum(1 for key in key_indicators if key in content)
            
            if present_keys >= 2:
                return True, f"{present_keys} API keys configured"
            else:
                return False, f"Only {present_keys} API keys found"
                
        except Exception as e:
            return False, f"Error reading .env: {e}"
    
    def check_last_inspection(self) -> Tuple[bool, str]:
        """Check results of last comprehensive inspection"""
        try:
            latest_path = os.path.join(self.project_root, "system_health_checks", 
                                     "inspection_results", "latest_inspection.json")
            
            if not os.path.exists(latest_path):
                return True, "No previous inspection found"
            
            with open(latest_path, 'r') as f:
                data = json.load(f)
            
            score = data.get('overall_score', 0)
            status = data.get('system_status', 'UNKNOWN')
            critical_failures = data.get('critical_failures', 0)
            
            # Check if inspection is recent (within last 24 hours)
            inspection_time = datetime.fromisoformat(data.get('timestamp', ''))
            age_hours = (datetime.now() - inspection_time).total_seconds() / 3600
            
            if critical_failures > 0:
                return False, f"Last inspection: {critical_failures} critical failures"
            elif score < 85:
                return False, f"Last inspection: Low score {score:.1f}%"
            elif age_hours > 48:
                return True, f"Last inspection: {status} but {age_hours:.0f}h old"
            else:
                return True, f"Last inspection: {status} ({score:.1f}%)"
                
        except Exception as e:
            return True, f"Cannot read last inspection: {e}"
    
    def run_quick_check(self) -> Dict[str, Any]:
        """Run quick status check"""
        start_time = time.time()
        
        print("Aeonforge Quick Status Check")
        print("=" * 40)
        
        checks = [
            ("Core Imports", self.check_core_imports),
            ("Tool Functionality", self.check_tool_functionality),
            ("File System", self.check_file_system),
            ("API Keys", self.check_api_keys),
            ("Last Inspection", self.check_last_inspection),
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for name, check_func in checks:
            try:
                success, message = check_func()
                
                if success:
                    print(f"[PASS] {name}: {message}")
                    passed += 1
                else:
                    print(f"[FAIL] {name}: {message}")
                    failed += 1
                    self.issues.append(f"{name}: {message}")
                    
            except Exception as e:
                print(f"[WARN] {name}: Exception - {e}")
                warnings += 1
                self.issues.append(f"{name}: Exception - {e}")
        
        total_checks = len(checks)
        success_rate = (passed / total_checks) * 100
        
        # Determine overall status
        if failed > 0:
            self.status = "CRITICAL"
            exit_code = 2
        elif warnings > 0:
            self.status = "WARNING"
            exit_code = 1
        else:
            self.status = "HEALTHY"
            exit_code = 0
        
        duration = time.time() - start_time
        
        print("=" * 40)
        print(f"Status: {self.status}")
        print(f"Success Rate: {success_rate:.1f}% ({passed}/{total_checks})")
        print(f"Duration: {duration:.2f}s")
        
        if self.issues:
            print("\nIssues Found:")
            for issue in self.issues:
                print(f"  • {issue}")
        
        # Save status to file for other processes
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "status": self.status,
            "success_rate": success_rate,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "duration": duration,
            "issues": self.issues
        }
        
        status_file = os.path.join(self.project_root, "system_health_checks", "quick_status.json")
        os.makedirs(os.path.dirname(status_file), exist_ok=True)
        
        try:
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save status file: {e}")
        
        return status_data, exit_code

def main():
    """Main execution function"""
    checker = QuickStatusChecker()
    status_data, exit_code = checker.run_quick_check()
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)