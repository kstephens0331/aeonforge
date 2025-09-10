#!/usr/bin/env python3
"""
Aeonforge Deployment Verification Script
========================================

This script verifies that all production deployment components are working correctly
across GitHub, Supabase, and Railway before going live.

Usage: python deployment/DEPLOYMENT_VERIFICATION_SCRIPT.py
"""

import os
import sys
import json
import time
import asyncio
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class VerificationResult:
    """Result of a verification check"""
    service: str
    check_name: str
    status: str  # "PASS", "FAIL", "WARNING", "SKIP"
    details: str
    timestamp: str
    duration: float

class DeploymentVerificationSystem:
    """Complete deployment verification system"""
    
    def __init__(self):
        self.results: List[VerificationResult] = []
        self.start_time = time.time()
        
        # Load environment variables
        self.github_repo = os.getenv('GITHUB_REPOSITORY', 'YOUR_USERNAME/aeonforge')
        self.supabase_url = os.getenv('SUPABASE_URL', '')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '')
        self.railway_backend_url = os.getenv('BACKEND_URL', '')
        self.railway_frontend_url = os.getenv('FRONTEND_URL', '')
        
    def log_result(self, service: str, check_name: str, status: str, details: str, duration: float = 0):
        """Log a verification result"""
        result = VerificationResult(
            service=service,
            check_name=check_name,
            status=status,
            details=details,
            timestamp=datetime.now().isoformat(),
            duration=duration
        )
        self.results.append(result)
        
        # Print real-time results
        status_icon = {
            "PASS": "[PASS]",
            "FAIL": "[FAIL]", 
            "WARNING": "[WARN]",
            "SKIP": "[SKIP]"
        }.get(status, "[????]")
        
        print(f"{status_icon} [{service}] {check_name}: {details}")
    
    def run_verification_check(self, service: str, check_name: str, check_function) -> bool:
        """Run individual verification check"""
        start_time = time.time()
        
        try:
            result = check_function()
            duration = time.time() - start_time
            
            if isinstance(result, tuple):
                status, details = result
            else:
                status = "PASS" if result else "FAIL"
                details = f"Check completed: {status}"
            
            self.log_result(service, check_name, status, details, duration)
            return status == "PASS"
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(service, check_name, "FAIL", f"Exception: {str(e)}", duration)
            return False
    
    # ========================================
    # GITHUB VERIFICATION CHECKS
    # ========================================
    
    def verify_github_repository(self) -> Tuple[str, str]:
        """Verify GitHub repository is accessible and properly configured"""
        try:
            # Check if repository exists and is accessible
            api_url = f"https://api.github.com/repos/{self.github_repo}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                return "PASS", f"Repository accessible - {repo_data.get('full_name', 'N/A')}"
            else:
                return "FAIL", f"Repository not accessible - HTTP {response.status_code}"
                
        except Exception as e:
            return "FAIL", f"Error checking repository: {e}"
    
    def verify_github_actions(self) -> Tuple[str, str]:
        """Verify GitHub Actions are configured and working"""
        try:
            api_url = f"https://api.github.com/repos/{self.github_repo}/actions/workflows"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                workflows_data = response.json()
                workflow_count = workflows_data.get('total_count', 0)
                
                if workflow_count > 0:
                    return "PASS", f"GitHub Actions configured - {workflow_count} workflows found"
                else:
                    return "WARNING", "No GitHub Actions workflows configured"
            else:
                return "FAIL", f"Cannot access GitHub Actions - HTTP {response.status_code}"
                
        except Exception as e:
            return "FAIL", f"Error checking GitHub Actions: {e}"
    
    def verify_github_repository_structure(self) -> Tuple[str, str]:
        """Verify essential repository files exist"""
        try:
            essential_files = [
                'README.md', 'requirements.txt', 'main.py', 'backend/main.py',
                '.gitignore', 'LICENSE', 'CONTRIBUTING.md'
            ]
            
            missing_files = []
            for file_path in essential_files:
                api_url = f"https://api.github.com/repos/{self.github_repo}/contents/{file_path}"
                response = requests.get(api_url, timeout=5)
                
                if response.status_code != 200:
                    missing_files.append(file_path)
            
            if not missing_files:
                return "PASS", f"All {len(essential_files)} essential files present"
            else:
                return "WARNING", f"Missing files: {', '.join(missing_files)}"
                
        except Exception as e:
            return "FAIL", f"Error checking repository structure: {e}"
    
    # ========================================
    # SUPABASE VERIFICATION CHECKS
    # ========================================
    
    def verify_supabase_connection(self) -> Tuple[str, str]:
        """Verify Supabase database connection"""
        try:
            if not self.supabase_url:
                return "SKIP", "Supabase URL not configured"
            
            # Test basic connectivity
            response = requests.get(f"{self.supabase_url}/rest/v1/", 
                                  headers={'apikey': self.supabase_anon_key},
                                  timeout=10)
            
            if response.status_code == 200:
                return "PASS", f"Supabase connection successful"
            else:
                return "FAIL", f"Supabase connection failed - HTTP {response.status_code}"
                
        except Exception as e:
            return "FAIL", f"Supabase connection error: {e}"
    
    def verify_supabase_schema(self) -> Tuple[str, str]:
        """Verify Supabase database schema is properly set up"""
        try:
            if not self.supabase_url:
                return "SKIP", "Supabase URL not configured"
            
            # Check for essential tables
            essential_tables = [
                'user_profiles', 'tool_categories', 'tools_registry',
                'tool_executions', 'system_health_logs'
            ]
            
            headers = {
                'apikey': self.supabase_anon_key,
                'Authorization': f'Bearer {self.supabase_anon_key}'
            }
            
            existing_tables = []
            for table in essential_tables:
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/{table}?limit=1",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    existing_tables.append(table)
            
            if len(existing_tables) == len(essential_tables):
                return "PASS", f"All {len(essential_tables)} essential tables exist"
            else:
                missing = set(essential_tables) - set(existing_tables)
                return "FAIL", f"Missing tables: {', '.join(missing)}"
                
        except Exception as e:
            return "FAIL", f"Schema verification error: {e}"
    
    def verify_supabase_tool_registration(self) -> Tuple[str, str]:
        """Verify tools are properly registered in Supabase"""
        try:
            if not self.supabase_url:
                return "SKIP", "Supabase URL not configured"
            
            headers = {
                'apikey': self.supabase_anon_key,
                'Authorization': f'Bearer {self.supabase_anon_key}'
            }
            
            # Check tool categories
            response = requests.get(
                f"{self.supabase_url}/rest/v1/tool_categories",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                categories = response.json()
                
                # Check tools registry
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/tools_registry?limit=100",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    tools = response.json()
                    return "PASS", f"Tool registration complete - {len(categories)} categories, {len(tools)} tools"
                else:
                    return "FAIL", f"Cannot access tools registry - HTTP {response.status_code}"
            else:
                return "FAIL", f"Cannot access tool categories - HTTP {response.status_code}"
                
        except Exception as e:
            return "FAIL", f"Tool registration verification error: {e}"
    
    # ========================================
    # RAILWAY VERIFICATION CHECKS  
    # ========================================
    
    def verify_railway_backend(self) -> Tuple[str, str]:
        """Verify Railway backend deployment"""
        try:
            if not self.railway_backend_url:
                return "SKIP", "Railway backend URL not configured"
            
            # Test health endpoint
            response = requests.get(f"{self.railway_backend_url}/health", timeout=15)
            
            if response.status_code == 200:
                health_data = response.json()
                return "PASS", f"Railway backend healthy - {health_data.get('status', 'unknown')}"
            else:
                return "FAIL", f"Railway backend unhealthy - HTTP {response.status_code}"
                
        except Exception as e:
            return "FAIL", f"Railway backend error: {e}"
    
    def verify_railway_frontend(self) -> Tuple[str, str]:
        """Verify Railway frontend deployment"""
        try:
            if not self.railway_frontend_url:
                return "SKIP", "Railway frontend URL not configured"
            
            response = requests.get(self.railway_frontend_url, timeout=15)
            
            if response.status_code == 200:
                # Check if it's actually the Aeonforge frontend
                content = response.text.lower()
                if 'aeonforge' in content or 'ai development' in content:
                    return "PASS", "Railway frontend deployed and accessible"
                else:
                    return "WARNING", "Frontend accessible but content may not be correct"
            else:
                return "FAIL", f"Railway frontend not accessible - HTTP {response.status_code}"
                
        except Exception as e:
            return "FAIL", f"Railway frontend error: {e}"
    
    def verify_railway_environment(self) -> Tuple[str, str]:
        """Verify Railway environment variables and configuration"""
        try:
            if not self.railway_backend_url:
                return "SKIP", "Railway backend URL not configured"
            
            # Test environment endpoint (if exists)
            response = requests.get(f"{self.railway_backend_url}/health/detailed", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                environment = health_data.get('railway_health', {}).get('environment', 'unknown')
                services = health_data.get('railway_health', {}).get('services', {})
                
                healthy_services = sum(1 for status in services.values() if 'healthy' in str(status).lower())
                total_services = len(services)
                
                return "PASS", f"Railway environment: {environment}, Services: {healthy_services}/{total_services} healthy"
            else:
                return "WARNING", f"Cannot get detailed health info - HTTP {response.status_code}"
                
        except Exception as e:
            return "WARNING", f"Railway environment check error: {e}"
    
    # ========================================
    # INTEGRATION VERIFICATION CHECKS
    # ========================================
    
    def verify_end_to_end_integration(self) -> Tuple[str, str]:
        """Verify complete end-to-end system integration"""
        try:
            # Test tool execution pipeline
            if not self.railway_backend_url:
                return "SKIP", "Backend URL not configured for integration test"
            
            # Test a simple tool execution
            test_payload = {
                "tool_id": "universal_translator",
                "input_data": {"text": "Hello", "target_language": "es"},
                "user_id": "test_user"
            }
            
            response = requests.post(
                f"{self.railway_backend_url}/api/tools/execute",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return "PASS", f"End-to-end integration working - Tool execution successful"
            elif response.status_code == 404:
                return "WARNING", "Tool execution endpoint not found - may not be fully implemented"
            else:
                return "FAIL", f"End-to-end integration failed - HTTP {response.status_code}"
                
        except Exception as e:
            return "FAIL", f"Integration test error: {e}"
    
    def verify_tool_system_health(self) -> Tuple[str, str]:
        """Verify tool system is operational"""
        try:
            # Run local tool system health check
            from system_health_checks.quick_status_check import QuickStatusChecker
            
            checker = QuickStatusChecker()
            status_data, exit_code = checker.run_quick_check()
            
            if exit_code == 0:
                return "PASS", f"Tool system healthy - {status_data['success_rate']:.1f}% success rate"
            elif exit_code == 1:
                return "WARNING", f"Tool system has warnings - {status_data['success_rate']:.1f}% success rate"
            else:
                return "FAIL", f"Tool system critical issues - {status_data['success_rate']:.1f}% success rate"
                
        except Exception as e:
            return "FAIL", f"Tool system health check error: {e}"
    
    def verify_monitoring_system(self) -> Tuple[str, str]:
        """Verify monitoring and health check systems"""
        try:
            # Check if monitoring files exist
            monitoring_files = [
                'system_health_checks/comprehensive_inspection_system.py',
                'system_health_checks/quick_status_check.py',
                'deployment/production_monitoring.py'
            ]
            
            existing_files = []
            for file_path in monitoring_files:
                if os.path.exists(file_path):
                    existing_files.append(file_path)
            
            if len(existing_files) == len(monitoring_files):
                return "PASS", f"All {len(monitoring_files)} monitoring systems present"
            else:
                missing = set(monitoring_files) - set(existing_files)
                return "WARNING", f"Missing monitoring files: {', '.join(missing)}"
                
        except Exception as e:
            return "FAIL", f"Monitoring verification error: {e}"
    
    # ========================================
    # MAIN VERIFICATION RUNNER
    # ========================================
    
    def run_complete_verification(self) -> Dict[str, Any]:
        """Run complete deployment verification"""
        
        print("Starting Aeonforge Deployment Verification")
        print("=" * 60)
        print()
        
        # Define all verification checks
        verification_checks = [
            # GitHub Checks
            ("GitHub", "Repository Access", self.verify_github_repository),
            ("GitHub", "Actions Configuration", self.verify_github_actions),  
            ("GitHub", "Repository Structure", self.verify_github_repository_structure),
            
            # Supabase Checks
            ("Supabase", "Database Connection", self.verify_supabase_connection),
            ("Supabase", "Schema Verification", self.verify_supabase_schema),
            ("Supabase", "Tool Registration", self.verify_supabase_tool_registration),
            
            # Railway Checks
            ("Railway", "Backend Deployment", self.verify_railway_backend),
            ("Railway", "Frontend Deployment", self.verify_railway_frontend),
            ("Railway", "Environment Config", self.verify_railway_environment),
            
            # Integration Checks
            ("Integration", "End-to-End Test", self.verify_end_to_end_integration),
            ("Integration", "Tool System Health", self.verify_tool_system_health),
            ("Integration", "Monitoring Systems", self.verify_monitoring_system),
        ]
        
        # Run all checks
        for service, check_name, check_function in verification_checks:
            self.run_verification_check(service, check_name, check_function)
        
        # Calculate results
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.status == "PASS")
        failed_checks = sum(1 for r in self.results if r.status == "FAIL")
        warning_checks = sum(1 for r in self.results if r.status == "WARNING")
        skipped_checks = sum(1 for r in self.results if r.status == "SKIP")
        
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        total_time = time.time() - self.start_time
        
        # Determine overall status
        if failed_checks == 0 and warning_checks == 0:
            overall_status = "READY FOR PRODUCTION"
        elif failed_checks == 0:
            overall_status = "READY WITH WARNINGS"
        else:
            overall_status = "NOT READY - ISSUES FOUND"
        
        # Print summary
        print()
        print("=" * 60)
        print("DEPLOYMENT VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {overall_status}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {total_time:.2f} seconds")
        print()
        print(f"[PASS] Passed: {passed_checks}")
        print(f"[FAIL] Failed: {failed_checks}")
        print(f"[WARN] Warnings: {warning_checks}")
        print(f"[SKIP] Skipped: {skipped_checks}")
        print()
        
        # Show failed checks
        if failed_checks > 0:
            print("FAILED CHECKS:")
            for result in self.results:
                if result.status == "FAIL":
                    print(f"  * [{result.service}] {result.check_name}: {result.details}")
            print()
        
        # Show warnings
        if warning_checks > 0:
            print("WARNING CONDITIONS:")
            for result in self.results:
                if result.status == "WARNING":
                    print(f"  * [{result.service}] {result.check_name}: {result.details}")
            print()
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        if recommendations:
            print("RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"  * {rec}")
            print()
        
        print("=" * 60)
        
        # Save results to file
        self.save_verification_report(overall_status, success_rate, total_time)
        
        return {
            "overall_status": overall_status,
            "success_rate": success_rate,
            "total_checks": total_checks,
            "passed": passed_checks,
            "failed": failed_checks,
            "warnings": warning_checks,
            "skipped": skipped_checks,
            "duration": total_time,
            "results": [vars(r) for r in self.results],
            "recommendations": recommendations
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on verification results"""
        recommendations = []
        
        # Check for common issues
        github_failures = [r for r in self.results if r.service == "GitHub" and r.status == "FAIL"]
        if github_failures:
            recommendations.append("Fix GitHub repository configuration and Actions setup")
        
        supabase_failures = [r for r in self.results if r.service == "Supabase" and r.status == "FAIL"]  
        if supabase_failures:
            recommendations.append("Complete Supabase database setup and schema migration")
        
        railway_failures = [r for r in self.results if r.service == "Railway" and r.status == "FAIL"]
        if railway_failures:
            recommendations.append("Fix Railway deployment and environment configuration")
        
        integration_failures = [r for r in self.results if r.service == "Integration" and r.status == "FAIL"]
        if integration_failures:
            recommendations.append("Resolve integration issues between services")
        
        # Check for warnings
        warnings = [r for r in self.results if r.status == "WARNING"]
        if warnings:
            recommendations.append(f"Review and address {len(warnings)} warning conditions")
        
        # Environment-specific recommendations
        if not self.supabase_url:
            recommendations.append("Configure Supabase environment variables")
            
        if not self.railway_backend_url:
            recommendations.append("Configure Railway backend URL")
        
        return recommendations
    
    def save_verification_report(self, status: str, success_rate: float, duration: float):
        """Save verification report to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"deployment_verification_{timestamp}.json"
            filepath = os.path.join("deployment", filename)
            
            report_data = {
                "verification_id": f"DEPLOY_VERIFY_{timestamp}",
                "timestamp": datetime.now().isoformat(),
                "overall_status": status,
                "success_rate": success_rate,
                "duration": duration,
                "results": [vars(r) for r in self.results],
                "recommendations": self.generate_recommendations(),
                "environment": {
                    "github_repo": self.github_repo,
                    "supabase_configured": bool(self.supabase_url),
                    "railway_configured": bool(self.railway_backend_url)
                }
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"Verification report saved: {filepath}")
            
        except Exception as e:
            print(f"Warning: Could not save verification report: {e}")

def main():
    """Main execution function"""
    verifier = DeploymentVerificationSystem()
    results = verifier.run_complete_verification()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(2)  # Critical issues
    elif results["warnings"] > 0:
        sys.exit(1)  # Warnings
    else:
        sys.exit(0)  # All good

if __name__ == "__main__":
    main()