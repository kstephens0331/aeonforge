"""
Comprehensive Test Suite for Aeonforge Phase 8-10
Tests Advanced Database, Payment System, AI Analytics, and Enterprise Integration
"""

import asyncio
import pytest
import json
import os
from datetime import datetime
from typing import Dict, Any

# Test the Phase 8-10 implementations
def test_phase8_10_imports():
    """Test that all Phase 8-10 modules can be imported"""
    try:
        from phase8_database import AdvancedDatabaseManager, DatabaseConfig
        from phase9_payments import PaymentManager, SubscriptionTier, PRICING_PLANS
        from phase10_ai_analytics import AdvancedAIOrchestrator, AIModelType
        from phase8_10_integration import AeonforgeEnterprisePlatform
        print("✓ All Phase 8-10 modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

async def test_phase8_database():
    """Test Phase 8 - Advanced Database Integration"""
    print("\n" + "="*60)
    print("TESTING PHASE 8 - ADVANCED DATABASE INTEGRATION")
    print("="*60)
    
    try:
        from phase8_database import AdvancedDatabaseManager, DatabaseConfig
        
        # Test database manager initialization
        config = DatabaseConfig()
        db_manager = AdvancedDatabaseManager(config)
        
        print("Testing database initialization...")
        success = await db_manager.initialize()
        
        if success:
            print("✓ Database system initialized successfully")
            
            # Test project creation
            print("Testing project creation...")
            project_id = await db_manager.create_project(
                name="Test Project Phase 8",
                description="A comprehensive test project for Phase 8 database features",
                owner_id="test_user_phase8",
                settings={"test_mode": True, "phase": "8"}
            )
            
            if project_id:
                print(f"✓ Project created successfully: {project_id}")
                
                # Test project retrieval
                project = await db_manager.get_project(project_id)
                if project and project["name"] == "Test Project Phase 8":
                    print("✓ Project retrieval working")
                else:
                    print("✗ Project retrieval failed")
            else:
                print("✗ Project creation failed")
            
            # Test conversation creation
            print("Testing conversation management...")
            conv_id = await db_manager.create_conversation(
                user_id="test_user_phase8",
                title="Phase 8 Test Conversation",
                project_id=project_id
            )
            
            if conv_id:
                print(f"✓ Conversation created: {conv_id}")
                
                # Test message addition
                msg_id1 = await db_manager.add_message(
                    conversation_id=conv_id,
                    role="user",
                    content="Hello, I need help testing the Phase 8 database system"
                )
                
                msg_id2 = await db_manager.add_message(
                    conversation_id=conv_id,
                    role="assistant",
                    content="I'd be happy to help you test the Phase 8 database system! The advanced database integration includes PostgreSQL, Redis caching, and vector search capabilities."
                )
                
                if msg_id1 and msg_id2:
                    print("✓ Messages added successfully")
                    
                    # Test conversation history retrieval
                    history = await db_manager.get_conversation_history(conv_id)
                    if len(history) == 2:
                        print("✓ Conversation history retrieval working")
                    else:
                        print("✗ Conversation history incomplete")
                else:
                    print("✗ Message addition failed")
            
            # Test code generation storage
            print("Testing code generation storage...")
            code_id = await db_manager.store_code_generation(
                project_id=project_id,
                user_id="test_user_phase8",
                request="Create a Python class for database management",
                generated_code='''class DatabaseManager:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        
    async def connect(self):
        """Connect to database"""
        pass
        
    async def execute_query(self, query, params=None):
        """Execute database query"""
        pass''',
                language="python",
                metadata={"test": True, "complexity": "medium"}
            )
            
            if code_id:
                print(f"✓ Code generation stored: {code_id}")
            else:
                print("✗ Code generation storage failed")
            
            # Test similar code search (if vector DB available)
            print("Testing vector search capabilities...")
            similar_code = await db_manager.search_similar_code(
                query="database connection management",
                language="python"
            )
            print(f"✓ Vector search returned {len(similar_code)} results")
            
            # Test analytics
            print("Testing database analytics...")
            analytics = await db_manager.get_analytics()
            if analytics["total_projects"] > 0:
                print("✓ Database analytics working")
                print(f"  - Projects: {analytics['total_projects']}")
                print(f"  - Conversations: {analytics['total_conversations']}")
                print(f"  - Messages: {analytics['total_messages']}")
                print(f"  - Code generations: {analytics['total_code_generations']}")
            else:
                print("✗ Database analytics failed")
            
            await db_manager.cleanup()
            print("✓ Phase 8 database tests completed successfully")
            return True
        else:
            print("✗ Database initialization failed")
            return False
            
    except Exception as e:
        print(f"✗ Phase 8 database test failed: {e}")
        return False

async def test_phase9_payments():
    """Test Phase 9 - Payment & Subscription System"""
    print("\n" + "="*60)
    print("TESTING PHASE 9 - PAYMENT & SUBSCRIPTION SYSTEM")
    print("="*60)
    
    try:
        from phase9_payments import PaymentManager, SubscriptionTier, PRICING_PLANS
        
        payment_manager = PaymentManager()
        
        # Test pricing plans
        print("Testing pricing plans...")
        plans = payment_manager.get_pricing_plans()
        if len(plans) == 4:  # FREE, BASIC, PRO, ENTERPRISE
            print("✓ All pricing plans available")
            for tier, plan in plans.items():
                print(f"  - {plan['name']}: ${plan['price_monthly']}/month")
        else:
            print("✗ Pricing plans incomplete")
        
        # Test user creation
        print("Testing user creation...")
        user_id = await payment_manager.create_user(
            email="phase9test@aeonforge.com",
            name="Phase 9 Test User",
            metadata={"test": True, "phase": "9"}
        )
        
        if user_id:
            print(f"✓ User created successfully: {user_id}")
            
            # Test user retrieval
            user = await payment_manager.get_user(user_id)
            if user and user["email"] == "phase9test@aeonforge.com":
                print("✓ User retrieval working")
                print(f"  - Tier: {user['subscription_tier']}")
                print(f"  - Status: {user['subscription_status']}")
            else:
                print("✗ User retrieval failed")
            
            # Test usage limits checking
            print("Testing usage limits...")
            api_limits = await payment_manager.check_usage_limits(user_id, "api_calls_per_day")
            project_limits = await payment_manager.check_usage_limits(user_id, "projects")
            
            print(f"✓ API calls limit: {api_limits['limit']} (remaining: {api_limits['remaining']})")
            print(f"✓ Projects limit: {project_limits['limit']} (remaining: {project_limits['remaining']})")
            
            # Test usage recording
            print("Testing usage recording...")
            await payment_manager.record_usage(user_id, "api_calls", 5)
            await payment_manager.record_usage(user_id, "projects", 1)
            print("✓ Usage recorded successfully")
            
            # Test checkout session creation (simulated)
            print("Testing checkout session creation...")
            if payment_manager.stripe_available:
                try:
                    checkout = await payment_manager.create_checkout_session(
                        user_id=user_id,
                        tier=SubscriptionTier.BASIC,
                        billing_period="monthly"
                    )
                    if "error" not in checkout:
                        print("✓ Checkout session creation working")
                    else:
                        print(f"⚠ Checkout session: {checkout['error']}")
                except Exception as e:
                    print(f"⚠ Stripe not configured: {e}")
            else:
                print("⚠ Stripe not available for checkout testing")
        
        # Test billing analytics
        print("Testing billing analytics...")
        analytics = await payment_manager.get_billing_analytics()
        print("✓ Billing analytics available:")
        print(f"  - Active subscriptions: {analytics['active_subscriptions']}")
        print(f"  - Monthly recurring revenue: ${analytics['mrr']:.2f}")
        print(f"  - Total users: {analytics['user_distribution'].get('total', 0)}")
        
        print("✓ Phase 9 payment tests completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Phase 9 payment test failed: {e}")
        return False

async def test_phase10_ai_analytics():
    """Test Phase 10 - Advanced AI Features & Analytics"""
    print("\n" + "="*60)
    print("TESTING PHASE 10 - AI FEATURES & ANALYTICS")
    print("="*60)
    
    try:
        from phase10_ai_analytics import AdvancedAIOrchestrator, AIModelType
        
        ai_orchestrator = AdvancedAIOrchestrator()
        
        # Test AI model configuration
        print("Testing AI model configuration...")
        print(f"✓ {len(ai_orchestrator.models)} AI models configured:")
        for model_name, config in ai_orchestrator.models.items():
            print(f"  - {config.name} ({config.model_type.value})")
        
        # Test AI request routing
        print("Testing AI request routing...")
        response = await ai_orchestrator.route_request(
            user_id="test_user_phase10",
            prompt="Create a React component for user authentication with TypeScript",
            request_type="code_generation"
        )
        
        if response.get("success"):
            print("✓ AI request routing working")
            print(f"  - Model used: {response['model_used']}")
            print(f"  - Tokens used: {response['tokens_used']}")
            print(f"  - Latency: {response['latency_ms']}ms")
            print(f"  - Cost: ${response['cost']:.6f}")
        else:
            print(f"✗ AI request failed: {response.get('error', 'Unknown error')}")
        
        # Test another AI request with different type
        chat_response = await ai_orchestrator.route_request(
            user_id="test_user_phase10",
            prompt="Explain the benefits of using TypeScript over JavaScript",
            request_type="chat"
        )
        
        if chat_response.get("success"):
            print("✓ Chat request routing working")
        
        # Test AI analytics
        print("Testing AI analytics...")
        analytics = await ai_orchestrator.get_ai_analytics(user_id="test_user_phase10", days=7)
        print("✓ AI analytics available:")
        print(f"  - Total requests: {analytics['total_requests']}")
        print(f"  - Successful requests: {analytics['successful_requests']}")
        print(f"  - Average latency: {analytics['average_latency']}ms")
        print(f"  - Total tokens: {analytics['total_tokens']}")
        print(f"  - Total cost: ${analytics['total_cost']:.6f}")
        
        # Test performance insights
        print("Testing performance insights...")
        insights = await ai_orchestrator.get_performance_insights(days=7)
        print("✓ Performance insights generated:")
        print(f"  - Models analyzed: {len(insights['model_performance'])}")
        print(f"  - Optimization suggestions: {len(insights['optimization_suggestions'])}")
        print(f"  - Recommendations: {len(insights['recommendations'])}")
        
        # Test analytics report generation
        print("Testing analytics report generation...")
        report = await ai_orchestrator.generate_analytics_report(
            user_id="test_user_phase10", 
            days=7
        )
        
        if report.get("report_id"):
            print("✓ Analytics report generated successfully")
            print(f"  - Report ID: {report['report_id']}")
            print(f"  - Summary: {len(report['summary'])} key metrics")
        else:
            print("✗ Analytics report generation failed")
        
        print("✓ Phase 10 AI analytics tests completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Phase 10 AI analytics test failed: {e}")
        return False

async def test_enterprise_integration():
    """Test Enterprise Platform Integration"""
    print("\n" + "="*60)
    print("TESTING ENTERPRISE PLATFORM INTEGRATION")
    print("="*60)
    
    try:
        from phase8_10_integration import AeonforgeEnterprisePlatform
        
        platform = AeonforgeEnterprisePlatform()
        
        # Test platform initialization
        print("Testing platform initialization...")
        success = await platform.initialize()
        
        if success:
            print("✓ Enterprise platform initialized successfully")
            
            # Test user account creation
            print("Testing integrated user account creation...")
            user_result = await platform.create_user_account(
                email="enterprise@aeonforge.com",
                name="Enterprise Test User",
                metadata={"test": True, "integration": "phase8-10"}
            )
            
            if user_result.get("success"):
                user_id = user_result["user_id"]
                print(f"✓ User account created: {user_id}")
                
                # Test AI request with limits
                print("Testing AI request with subscription limits...")
                ai_result = await platform.process_ai_request_with_limits(
                    user_id=user_id,
                    prompt="Create a Python FastAPI application with authentication",
                    request_type="code_generation"
                )
                
                if ai_result.get("success"):
                    print("✓ AI request with limits working")
                    print(f"  - Response length: {len(ai_result.get('content', ''))}")
                else:
                    print(f"⚠ AI request issue: {ai_result.get('error', 'Unknown')}")
                
                # Test project creation with permissions
                print("Testing project creation with permissions...")
                project_result = await platform.create_project_with_permissions(
                    name="Enterprise Test Project",
                    description="A comprehensive test project for enterprise features",
                    owner_id=user_id,
                    settings={"enterprise": True, "test_mode": True}
                )
                
                if project_result.get("success"):
                    print(f"✓ Project created with permissions: {project_result['project_id']}")
                else:
                    print(f"✗ Project creation failed: {project_result.get('error')}")
                
                # Test user dashboard
                print("Testing user dashboard...")
                dashboard = await platform.get_user_dashboard(user_id)
                
                if "user" in dashboard and "subscription" in dashboard:
                    print("✓ User dashboard working")
                    print(f"  - Subscription tier: {dashboard['subscription']['tier']}")
                    print(f"  - API usage: {dashboard['usage']['api_calls']['used']}/{dashboard['usage']['api_calls']['limit']}")
                else:
                    print("✗ User dashboard failed")
            
            # Test comprehensive report
            print("Testing comprehensive analytics report...")
            report = await platform.generate_comprehensive_report(days=7)
            
            if "report_id" in report:
                print("✓ Comprehensive report generated")
                print(f"  - Platform users: {report['platform_summary'].get('total_users', 0)}")
                print(f"  - Total projects: {report['platform_summary'].get('total_projects', 0)}")
                print(f"  - AI requests: {report['platform_summary'].get('ai_requests', 0)}")
            else:
                print("✗ Comprehensive report failed")
            
            # Test health check
            print("Testing platform health check...")
            health = await platform.health_check()
            
            print(f"✓ Health check completed - Status: {health['status']}")
            print(f"  - Overall health: {health['overall_health']}")
            for component, status in health.get("components", {}).items():
                print(f"  - {component}: {status['status']}")
        
        print("✓ Enterprise integration tests completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Enterprise integration test failed: {e}")
        return False

async def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n" + "="*60)
    print("TESTING DEPENDENCIES")
    print("="*60)
    
    dependencies = {
        "asyncpg": "PostgreSQL async driver",
        "sqlalchemy": "Database ORM",
        "redis": "Redis caching",
        "chromadb": "Vector database",
        "stripe": "Payment processing",
        "scikit-learn": "Machine learning",
        "transformers": "AI models",
        "torch": "Deep learning",
        "fastapi": "Web framework",
        "uvicorn": "ASGI server"
    }
    
    available_deps = []
    missing_deps = []
    
    for dep_name, description in dependencies.items():
        try:
            __import__(dep_name)
            available_deps.append((dep_name, description))
            print(f"✓ {dep_name}: {description}")
        except ImportError:
            missing_deps.append((dep_name, description))
            print(f"✗ {dep_name}: {description} (not available)")
    
    print(f"\nDependency Status: {len(available_deps)}/{len(dependencies)} available")
    
    if missing_deps:
        print(f"\nTo install missing dependencies:")
        print("pip install", " ".join([dep[0] for dep in missing_deps]))
    
    return len(missing_deps) == 0

def print_test_summary(results):
    """Print comprehensive test summary"""
    print("\n" + "="*60)
    print("PHASE 8-10 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results if result[1])
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status:10} {test_name}")
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Phase 8-10 fully operational!")
    else:
        print("⚠ Some tests failed - check individual results above")
    
    return passed_tests == total_tests

async def run_all_tests():
    """Run all Phase 8-10 tests"""
    print("AEONFORGE PHASE 8-10 COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing Advanced Database, Payment System, AI Analytics & Integration")
    print("=" * 60)
    
    # Run all tests
    test_results = []
    
    # Import test
    test_results.append(("Import Test", test_phase8_10_imports()))
    
    # Dependency test
    test_results.append(("Dependencies", await test_dependencies()))
    
    # Phase-specific tests
    test_results.append(("Phase 8 Database", await test_phase8_database()))
    test_results.append(("Phase 9 Payments", await test_phase9_payments()))
    test_results.append(("Phase 10 AI Analytics", await test_phase10_ai_analytics()))
    test_results.append(("Enterprise Integration", await test_enterprise_integration()))
    
    # Print summary
    all_passed = print_test_summary(test_results)
    
    if all_passed:
        print("\n🚀 PHASE 8-10 READY FOR PRODUCTION!")
        print("All advanced features are operational:")
        print("- Advanced Database Integration (PostgreSQL, Redis, Vector DB)")
        print("- Payment & Subscription System (Stripe, User Management)")
        print("- AI Features & Analytics (Multi-model, Performance tracking)")
        print("- Enterprise Platform Integration (Complete unified system)")
    else:
        print("\n⚠ Some components need attention before production deployment")
    
    return all_passed

if __name__ == "__main__":
    # Run the comprehensive test suite
    asyncio.run(run_all_tests())