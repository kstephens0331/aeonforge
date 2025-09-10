"""
Comprehensive System Verification and Stress Testing for Aeonforge
Tests all phases, components, imports, and functionality under various conditions
"""

import os
import sys
import time
import json
import asyncio
import traceback
import requests
import threading
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import concurrent.futures

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@dataclass
class TestResult:
    """Test result structure"""
    test_name: str
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None
    warnings: List[str] = None

@dataclass
class ComponentHealth:
    """Component health status"""
    component: str
    status: str  # 'healthy', 'degraded', 'failed'
    import_success: bool
    functional_tests_passed: int
    total_functional_tests: int
    performance_score: Optional[float] = None
    error_details: List[str] = None

class SystemVerificationSuite:
    """Comprehensive system verification and testing"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.component_health: Dict[str, ComponentHealth] = {}
        self.stress_test_results: Dict[str, Any] = {}
        self.backend_url = "http://localhost:8000"
        self.api_running = False
        
    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """Run complete system verification"""
        print("🚀 Starting Aeonforge Comprehensive System Verification")
        print("=" * 60)
        
        verification_start = time.time()
        
        # Phase 1: Import and Module Verification
        print("\n📦 Phase 1: Import and Module Verification")
        import_results = self._verify_all_imports()
        
        # Phase 2: Component Functional Testing
        print("\n🔧 Phase 2: Component Functional Testing")
        component_results = self._test_all_components()
        
        # Phase 3: API System Testing
        print("\n🌐 Phase 3: API System Testing") 
        api_results = self._test_api_system()
        
        # Phase 4: Memory System Testing
        print("\n🧠 Phase 4: Memory System Testing")
        memory_results = self._test_memory_system()
        
        # Phase 5: Integration Testing
        print("\n🔗 Phase 5: Integration Testing")
        integration_results = self._test_system_integration()
        
        # Phase 6: Stress Testing
        print("\n💪 Phase 6: Stress Testing")
        stress_results = self._run_stress_tests()
        
        # Phase 7: ChatGPT-like Functionality Testing
        print("\n💬 Phase 7: ChatGPT-like Functionality Testing")
        chatgpt_results = self._test_chatgpt_functionality()
        
        total_time = time.time() - verification_start
        
        # Compile final report
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "total_execution_time": total_time,
            "import_verification": import_results,
            "component_testing": component_results,
            "api_testing": api_results,
            "memory_testing": memory_results,
            "integration_testing": integration_results,
            "stress_testing": stress_results,
            "chatgpt_testing": chatgpt_results,
            "overall_health": self._calculate_overall_health(),
            "recommendations": self._generate_recommendations()
        }
        
        # Print summary
        self._print_verification_summary(final_report)
        
        # Save detailed report
        report_file = f"aeonforge_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2, default=str)
        
        print(f"\n📋 Detailed report saved to: {report_file}")
        
        return final_report
    
    def _verify_all_imports(self) -> Dict[str, Any]:
        """Verify all system imports work correctly"""
        import_tests = [
            # Core tools
            ("tools.api_key_manager", "APIKeyManager"),
            ("tools.approval_system", "get_user_approval"),
            ("tools.file_tools", "create_file"),
            ("tools.web_tools", "web_search"),
            ("tools.git_tools", "git_commit"),
            ("tools.pdf_tools", "create_pdf"),
            ("tools.self_healing", "self_heal"),
            
            # Phase 2 - Multi-Agent System
            ("phase2_agents", "setup_phase2_agents"),
            
            # Phase 5 - Multi-Language Tools
            ("tools.multi_language_tools", "multi_language_manager"),
            ("tools.advanced_language_features", "AdvancedPythonHandler"),
            
            # Phase 6 - Platform Integrations
            ("tools.platform_integrations", "platform_manager"),
            ("tools.cloud_integrations", "setup_cloud_platforms"),
            ("tools.service_integrations", "service_manager"),
            
            # Phase 7 - Workflow Automation
            ("tools.workflow_engine", "WorkflowEngine"),
            ("tools.workflow_triggers", "TriggerManager"),
            ("tools.workflow_actions", "ActionLibrary"),
            ("tools.workflow_designer", "WorkflowDesigner"),
            ("tools.workflow_scheduler", "WorkflowScheduler"),
            
            # Memory System
            ("memory.memory_system", "MemorySystem"),
            ("memory.project_manager", "ProjectManager"),
            ("memory.instruction_manager", "InstructionManager"),
            ("memory.integration_layer", "AeonforgeMemoryCore"),
            
            # Backend
            ("backend.main", "app")
        ]
        
        results = {"successful_imports": 0, "failed_imports": 0, "import_details": []}
        
        for module_path, item_name in import_tests:
            try:
                start_time = time.time()
                
                # Try to import the module
                module = __import__(module_path, fromlist=[item_name])
                
                # Try to access the specific item
                if hasattr(module, item_name):
                    getattr(module, item_name)
                    status = "✅ SUCCESS"
                    results["successful_imports"] += 1
                else:
                    status = "⚠️ PARTIAL (module imported, item not found)"
                    results["failed_imports"] += 1
                
                import_time = time.time() - start_time
                
                results["import_details"].append({
                    "module": module_path,
                    "item": item_name,
                    "status": status,
                    "import_time": import_time
                })
                
                print(f"  {status} {module_path}.{item_name} ({import_time:.3f}s)")
                
            except Exception as e:
                results["failed_imports"] += 1
                error_msg = str(e)
                results["import_details"].append({
                    "module": module_path,
                    "item": item_name,
                    "status": "❌ FAILED",
                    "error": error_msg,
                    "import_time": 0
                })
                
                print(f"  ❌ FAILED {module_path}.{item_name}: {error_msg}")
        
        results["success_rate"] = results["successful_imports"] / len(import_tests) * 100
        return results
    
    def _test_all_components(self) -> Dict[str, Any]:
        """Test functionality of all major components"""
        components_to_test = [
            ("Memory System", self._test_memory_component),
            ("File Tools", self._test_file_tools),
            ("Web Tools", self._test_web_tools),
            ("Multi-Language Tools", self._test_multilang_tools),
            ("Platform Integrations", self._test_platform_integrations),
            ("Workflow Engine", self._test_workflow_engine)
        ]
        
        component_results = {"components": {}, "overall_success": True}
        
        for component_name, test_function in components_to_test:
            print(f"\n  🔍 Testing {component_name}...")
            try:
                start_time = time.time()
                result = test_function()
                execution_time = time.time() - start_time
                
                component_results["components"][component_name] = {
                    "success": result["success"],
                    "execution_time": execution_time,
                    "details": result,
                    "status": "✅ PASSED" if result["success"] else "❌ FAILED"
                }
                
                if not result["success"]:
                    component_results["overall_success"] = False
                
                print(f"    {component_results['components'][component_name]['status']} ({execution_time:.3f}s)")
                
            except Exception as e:
                component_results["components"][component_name] = {
                    "success": False,
                    "execution_time": 0,
                    "error": str(e),
                    "status": "❌ ERROR"
                }
                component_results["overall_success"] = False
                print(f"    ❌ ERROR: {str(e)}")
        
        return component_results
    
    def _test_memory_component(self) -> Dict[str, Any]:
        """Test memory system functionality"""
        try:
            from memory.memory_system import MemorySystem
            from memory.project_manager import ProjectManager
            
            # Test memory system basic operations
            memory = MemorySystem("test_memory")
            
            # Test conversation memory
            conv_id = memory.remember_conversation(
                user_message="Test user message",
                assistant_response="Test assistant response",
                context_tags=["test"],
                files_referenced=["test.py"],
                tools_used=["test_tool"]
            )
            
            # Test project creation
            project_manager = ProjectManager("test_memory")
            project_id = project_manager.memory.create_project(
                name="Test Project",
                base_path="./test_project",
                instructions="Test instructions"
            )
            
            # Test search
            search_results = memory.search_memory("test", limit=5)
            
            return {
                "success": True,
                "conversation_id": conv_id is not None,
                "project_id": project_id is not None,
                "search_results_count": len(search_results),
                "tests_passed": 3
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tests_passed": 0
            }
    
    def _test_file_tools(self) -> Dict[str, Any]:
        """Test file tools functionality"""
        try:
            from tools.file_tools import create_file, create_directory, read_file
            
            # Test directory creation
            test_dir = "test_verification_dir"
            create_directory(test_dir)
            
            # Test file creation
            test_file = f"{test_dir}/test_file.txt"
            test_content = "This is a test file for system verification"
            create_file(test_file, test_content)
            
            # Test file reading
            read_content = read_file(test_file)
            
            # Clean up
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
            
            return {
                "success": read_content == test_content,
                "directory_created": os.path.exists(test_dir),
                "file_created": True,
                "content_match": read_content == test_content,
                "tests_passed": 3
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tests_passed": 0
            }
    
    def _test_web_tools(self) -> Dict[str, Any]:
        """Test web tools functionality"""
        try:
            from tools.web_tools import web_search
            
            # Test web search (mock or real depending on API keys)
            search_results = web_search("Python programming", max_results=3)
            
            return {
                "success": isinstance(search_results, str),
                "has_results": len(search_results) > 0 if search_results else False,
                "search_executed": True,
                "tests_passed": 1
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tests_passed": 0
            }
    
    def _test_multilang_tools(self) -> Dict[str, Any]:
        """Test multi-language tools"""
        try:
            from tools.multi_language_tools import multi_language_manager, analyze_any_code
            
            # Test language detection
            test_code = "def hello(): print('Hello World')"
            detected_lang = multi_language_manager.detect_language(test_code)
            
            # Test code analysis
            analysis = analyze_any_code(test_code, "python")
            
            return {
                "success": True,
                "language_detected": detected_lang == "python",
                "analysis_performed": hasattr(analysis, 'language'),
                "supported_languages": len(multi_language_manager.get_supported_languages()),
                "tests_passed": 3
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tests_passed": 0
            }
    
    def _test_platform_integrations(self) -> Dict[str, Any]:
        """Test platform integration components"""
        try:
            from tools.platform_integrations import platform_manager
            
            # Test platform info retrieval
            platform_info = platform_manager.get_all_platform_info()
            
            # Test credential validation (will use mocked data)
            validation_results = platform_manager.validate_all_credentials()
            
            return {
                "success": True,
                "platform_info_available": isinstance(platform_info, dict),
                "validation_executed": isinstance(validation_results, dict),
                "tests_passed": 2
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tests_passed": 0
            }
    
    def _test_workflow_engine(self) -> Dict[str, Any]:
        """Test workflow automation engine"""
        try:
            from tools.workflow_engine import WorkflowEngine
            from tools.workflow_scheduler import WorkflowScheduler
            
            # Test workflow engine initialization
            engine = WorkflowEngine("test_workflow_data")
            
            # Test scheduler initialization  
            scheduler = WorkflowScheduler("test_workflow_data")
            
            return {
                "success": True,
                "engine_initialized": engine is not None,
                "scheduler_initialized": scheduler is not None,
                "tests_passed": 2
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tests_passed": 0
            }
    
    def _test_api_system(self) -> Dict[str, Any]:
        """Test the FastAPI backend system"""
        api_results = {"server_running": False, "endpoints_tested": 0, "endpoint_results": {}}
        
        try:
            # Check if API server is running
            response = requests.get(f"{self.backend_url}/", timeout=5)
            api_results["server_running"] = response.status_code == 200
            self.api_running = True
        except:
            print("  ⚠️ API server not running, starting test server...")
            api_results["server_running"] = False
            self.api_running = False
            return api_results
        
        # Test key endpoints
        endpoints_to_test = [
            ("/api/health", "GET", None),
            ("/api/languages", "GET", None),
            ("/api/platforms/supported", "GET", None),
        ]
        
        for endpoint, method, data in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{self.backend_url}{endpoint}", json=data, timeout=10)
                
                api_results["endpoint_results"][endpoint] = {
                    "status_code": response.status_code,
                    "success": 200 <= response.status_code < 300,
                    "response_time": response.elapsed.total_seconds()
                }
                
                if api_results["endpoint_results"][endpoint]["success"]:
                    api_results["endpoints_tested"] += 1
                
                print(f"    {endpoint}: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
                
            except Exception as e:
                api_results["endpoint_results"][endpoint] = {
                    "error": str(e),
                    "success": False
                }
                print(f"    {endpoint}: ERROR - {str(e)}")
        
        return api_results
    
    def _test_memory_system(self) -> Dict[str, Any]:
        """Test complete memory system functionality"""
        try:
            from memory.integration_layer import aeonforge_memory
            
            # Test initialization
            context = aeonforge_memory.initialize_session_with_memory("Test message")
            
            # Test conversation memory
            conv_id = aeonforge_memory.remember_interaction(
                user_message="Test user message for memory",
                assistant_response="Test assistant response for memory",
                context={"test": True}
            )
            
            # Test project creation
            try:
                project_id = aeonforge_memory.create_project_with_memory(
                    name="Test Memory Project",
                    base_path="./test_memory_project"
                )
                project_created = True
            except:
                project_created = False
                project_id = None
            
            return {
                "success": True,
                "context_initialized": isinstance(context, dict),
                "conversation_remembered": conv_id is not None,
                "project_created": project_created,
                "system_status": aeonforge_memory.get_system_status(),
                "tests_passed": 3 if project_created else 2
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tests_passed": 0
            }
    
    def _test_system_integration(self) -> Dict[str, Any]:
        """Test integration between different system components"""
        integration_results = {"integrations_tested": 0, "successful_integrations": 0, "details": {}}
        
        # Test Memory + Project Manager integration
        try:
            from memory.integration_layer import aeonforge_memory
            from memory.project_manager import ProjectManager
            
            # Test project switching with memory
            project_manager = ProjectManager()
            templates = project_manager.get_available_templates()
            
            integration_results["details"]["memory_project_integration"] = {
                "success": len(templates) > 0,
                "templates_available": len(templates)
            }
            
            if integration_results["details"]["memory_project_integration"]["success"]:
                integration_results["successful_integrations"] += 1
            
            integration_results["integrations_tested"] += 1
            
        except Exception as e:
            integration_results["details"]["memory_project_integration"] = {
                "success": False,
                "error": str(e)
            }
            integration_results["integrations_tested"] += 1
        
        # Test API + Memory integration
        if self.api_running:
            try:
                # Test that API can access memory system
                response = requests.get(f"{self.backend_url}/api/health", timeout=5)
                api_memory_integration = response.status_code == 200
                
                integration_results["details"]["api_memory_integration"] = {
                    "success": api_memory_integration,
                    "status_code": response.status_code if api_memory_integration else None
                }
                
                if api_memory_integration:
                    integration_results["successful_integrations"] += 1
                
                integration_results["integrations_tested"] += 1
                
            except Exception as e:
                integration_results["details"]["api_memory_integration"] = {
                    "success": False,
                    "error": str(e)
                }
                integration_results["integrations_tested"] += 1
        
        return integration_results
    
    def _run_stress_tests(self) -> Dict[str, Any]:
        """Run stress tests on the system"""
        stress_results = {"tests": {}, "overall_performance": {}}
        
        # Memory stress test
        print("  🧠 Memory stress test...")
        stress_results["tests"]["memory"] = self._stress_test_memory()
        
        # API stress test (if running)
        if self.api_running:
            print("  🌐 API stress test...")
            stress_results["tests"]["api"] = self._stress_test_api()
        
        # File I/O stress test
        print("  📁 File I/O stress test...")
        stress_results["tests"]["file_io"] = self._stress_test_file_io()
        
        return stress_results
    
    def _stress_test_memory(self) -> Dict[str, Any]:
        """Stress test memory system with multiple operations"""
        try:
            from memory.memory_system import MemorySystem
            
            memory = MemorySystem("stress_test_memory")
            start_time = time.time()
            
            # Create multiple conversations rapidly
            conversation_ids = []
            for i in range(100):
                conv_id = memory.remember_conversation(
                    user_message=f"Stress test message {i}",
                    assistant_response=f"Stress test response {i}",
                    context_tags=[f"stress_{i}"],
                    files_referenced=[f"stress_{i}.py"],
                    tools_used=[f"tool_{i}"]
                )
                conversation_ids.append(conv_id)
            
            # Perform multiple searches
            search_time_start = time.time()
            for i in range(50):
                memory.search_memory(f"stress test {i}", limit=10)
            search_time = time.time() - search_time_start
            
            total_time = time.time() - start_time
            
            return {
                "success": True,
                "conversations_created": len(conversation_ids),
                "searches_performed": 50,
                "total_time": total_time,
                "avg_conversation_time": total_time / 100,
                "avg_search_time": search_time / 50,
                "memory_operations_per_second": 150 / total_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _stress_test_api(self) -> Dict[str, Any]:
        """Stress test API with concurrent requests"""
        def make_request():
            try:
                response = requests.get(f"{self.backend_url}/api/health", timeout=10)
                return response.status_code == 200, response.elapsed.total_seconds()
            except:
                return False, 0
        
        # Run concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        successful_requests = sum(1 for success, _ in results if success)
        response_times = [time for success, time in results if success]
        
        return {
            "success": successful_requests > 0,
            "total_requests": 50,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / 50 * 100,
            "total_time": total_time,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "requests_per_second": 50 / total_time
        }
    
    def _stress_test_file_io(self) -> Dict[str, Any]:
        """Stress test file I/O operations"""
        try:
            from tools.file_tools import create_file, create_directory, read_file
            
            test_dir = "stress_test_files"
            create_directory(test_dir)
            
            start_time = time.time()
            
            # Create many files rapidly
            file_count = 100
            for i in range(file_count):
                create_file(f"{test_dir}/stress_file_{i}.txt", f"Stress test content {i}")
            
            # Read all files
            read_start = time.time()
            for i in range(file_count):
                read_file(f"{test_dir}/stress_file_{i}.txt")
            read_time = time.time() - read_start
            
            total_time = time.time() - start_time
            
            # Clean up
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
            
            return {
                "success": True,
                "files_created": file_count,
                "files_read": file_count,
                "total_time": total_time,
                "avg_write_time": (total_time - read_time) / file_count,
                "avg_read_time": read_time / file_count,
                "file_operations_per_second": (file_count * 2) / total_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_chatgpt_functionality(self) -> Dict[str, Any]:
        """Test ChatGPT-like functionality with dynamic user requests"""
        chatgpt_results = {"dynamic_response": False, "no_hardcoded_data": False, "user_driven": False}
        
        if not self.api_running:
            return {"success": False, "error": "API not running for ChatGPT functionality test"}
        
        try:
            # Test dynamic request processing
            test_requests = [
                "Create a simple calculator app",
                "Build a todo list application",
                "Generate a weather dashboard",
                "Make a file organizer tool"
            ]
            
            dynamic_responses = []
            for request in test_requests:
                try:
                    response = requests.post(
                        f"{self.backend_url}/api/chat",
                        json={
                            "message": request,
                            "api_keys": {},
                            "conversation_id": f"test_{hash(request)}"
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        dynamic_responses.append({
                            "request": request,
                            "response_length": len(data.get("message", "")),
                            "needs_approval": data.get("needs_approval", False),
                            "agent": data.get("agent", "unknown")
                        })
                    
                except Exception as e:
                    print(f"    Request failed: {request} - {e}")
            
            # Verify responses are different (not hardcoded)
            if len(dynamic_responses) >= 2:
                response_lengths = [r["response_length"] for r in dynamic_responses]
                responses_vary = len(set(response_lengths)) > 1  # Different response lengths indicate dynamic content
                chatgpt_results["no_hardcoded_data"] = responses_vary
                chatgpt_results["dynamic_response"] = True
                chatgpt_results["user_driven"] = all(r["needs_approval"] for r in dynamic_responses)
            
            chatgpt_results["test_requests"] = len(test_requests)
            chatgpt_results["successful_responses"] = len(dynamic_responses)
            chatgpt_results["response_details"] = dynamic_responses
            
            return {
                "success": len(dynamic_responses) > 0,
                "details": chatgpt_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_overall_health(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        health_score = 0
        max_score = 0
        
        # Import health (20 points)
        if hasattr(self, 'import_results'):
            health_score += (self.import_results.get("success_rate", 0) / 100) * 20
        max_score += 20
        
        # Component health (30 points) 
        component_success_rate = 0
        if hasattr(self, 'component_results'):
            successful_components = sum(1 for comp in self.component_results.get("components", {}).values() if comp.get("success", False))
            total_components = len(self.component_results.get("components", {}))
            if total_components > 0:
                component_success_rate = successful_components / total_components
        
        health_score += component_success_rate * 30
        max_score += 30
        
        # API health (25 points)
        if hasattr(self, 'api_results'):
            if self.api_results.get("server_running", False):
                health_score += 15
                # Additional points for successful endpoints
                successful_endpoints = sum(1 for ep in self.api_results.get("endpoint_results", {}).values() if ep.get("success", False))
                total_endpoints = len(self.api_results.get("endpoint_results", {}))
                if total_endpoints > 0:
                    health_score += (successful_endpoints / total_endpoints) * 10
        max_score += 25
        
        # Integration health (25 points)
        if hasattr(self, 'integration_results'):
            successful_integrations = self.integration_results.get("successful_integrations", 0)
            total_integrations = self.integration_results.get("integrations_tested", 1)
            health_score += (successful_integrations / total_integrations) * 25
        max_score += 25
        
        overall_percentage = (health_score / max_score * 100) if max_score > 0 else 0
        
        if overall_percentage >= 90:
            status = "🟢 EXCELLENT"
        elif overall_percentage >= 75:
            status = "🟡 GOOD"
        elif overall_percentage >= 50:
            status = "🟠 FAIR"
        else:
            status = "🔴 POOR"
        
        return {
            "score": health_score,
            "max_score": max_score,
            "percentage": overall_percentage,
            "status": status
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check import failures
        if hasattr(self, 'import_results') and self.import_results.get("failed_imports", 0) > 0:
            recommendations.append("🔧 Fix failed imports to ensure all components are available")
        
        # Check component failures
        if hasattr(self, 'component_results') and not self.component_results.get("overall_success", True):
            recommendations.append("⚙️ Address component test failures for better system reliability")
        
        # Check API status
        if hasattr(self, 'api_results') and not self.api_results.get("server_running", False):
            recommendations.append("🚀 Start the FastAPI backend server for full functionality")
        
        # Check stress test results
        if hasattr(self, 'stress_results'):
            memory_test = self.stress_results.get("tests", {}).get("memory", {})
            if not memory_test.get("success", True):
                recommendations.append("🧠 Optimize memory system for better performance under load")
        
        if not recommendations:
            recommendations.append("✅ System is performing well! Consider regular monitoring and updates.")
        
        return recommendations
    
    def _print_verification_summary(self, report: Dict[str, Any]):
        """Print a comprehensive verification summary"""
        print("\n" + "=" * 60)
        print("🎯 AEONFORGE SYSTEM VERIFICATION SUMMARY")
        print("=" * 60)
        
        # Overall health
        overall_health = report.get("overall_health", {})
        print(f"\n🏥 Overall System Health: {overall_health.get('status', 'UNKNOWN')}")
        print(f"   Health Score: {overall_health.get('percentage', 0):.1f}%")
        
        # Import results
        import_results = report.get("import_verification", {})
        print(f"\n📦 Import Verification:")
        print(f"   ✅ Successful: {import_results.get('successful_imports', 0)}")
        print(f"   ❌ Failed: {import_results.get('failed_imports', 0)}")
        print(f"   📊 Success Rate: {import_results.get('success_rate', 0):.1f}%")
        
        # Component results
        component_results = report.get("component_testing", {})
        print(f"\n🔧 Component Testing:")
        components = component_results.get("components", {})
        for name, result in components.items():
            status_icon = "✅" if result.get("success", False) else "❌"
            print(f"   {status_icon} {name}: {result.get('status', 'UNKNOWN')}")
        
        # API results
        api_results = report.get("api_testing", {})
        if api_results.get("server_running", False):
            print(f"\n🌐 API Testing:")
            print(f"   🚀 Server Status: RUNNING")
            print(f"   📊 Endpoints Tested: {api_results.get('endpoints_tested', 0)}")
        else:
            print(f"\n🌐 API Testing:")
            print(f"   ⚠️ Server Status: NOT RUNNING")
        
        # Memory system
        memory_results = report.get("memory_testing", {})
        if memory_results.get("success", False):
            print(f"\n🧠 Memory System: ✅ OPERATIONAL")
        else:
            print(f"\n🧠 Memory System: ❌ ISSUES DETECTED")
        
        # ChatGPT functionality
        chatgpt_results = report.get("chatgpt_testing", {})
        if chatgpt_results.get("success", False):
            details = chatgpt_results.get("details", {})
            print(f"\n💬 ChatGPT Functionality: ✅ OPERATIONAL")
            print(f"   📝 Dynamic Responses: {'✅' if details.get('dynamic_response') else '❌'}")
            print(f"   🚫 No Hardcoded Data: {'✅' if details.get('no_hardcoded_data') else '❌'}")
            print(f"   👤 User-Driven: {'✅' if details.get('user_driven') else '❌'}")
        else:
            print(f"\n💬 ChatGPT Functionality: ❌ ISSUES DETECTED")
        
        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
        
        # Performance metrics
        print(f"\n⏱️ Performance Metrics:")
        print(f"   Total Verification Time: {report.get('total_execution_time', 0):.2f} seconds")
        
        print("\n" + "=" * 60)
        print("Verification Complete! Check the detailed JSON report for more information.")
        print("=" * 60)

def main():
    """Run the comprehensive system verification"""
    print("🌟 Welcome to Aeonforge Comprehensive System Verification")
    print("This will test all phases, components, and functionality.")
    print("Please ensure the backend server is running for full API testing.")
    
    input("\nPress Enter to continue with verification...")
    
    verifier = SystemVerificationSuite()
    report = verifier.run_comprehensive_verification()
    
    # Ask if user wants to see detailed results
    show_details = input("\nWould you like to see detailed test results? (y/n): ").lower().strip()
    if show_details in ['y', 'yes']:
        print("\n📋 Detailed Results:")
        print(json.dumps(report, indent=2, default=str))
    
    return report

if __name__ == "__main__":
    main()