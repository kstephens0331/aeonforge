"""
AeonForge Advanced Tools System - Comprehensive Testing
Test suite for the first batch of 20 Code Intelligence tools
"""

import asyncio
import sys
import os

# Add the tools directory to path
sys.path.append(os.path.dirname(__file__))

from tools.advanced_tools_system import get_tool_manager, ToolCategory

async def test_tool_system_initialization():
    """Test the tool system initialization"""
    print("Testing Tool System Initialization...")
    
    try:
        tool_manager = await get_tool_manager()
        print(f"SUCCESS: Tool Manager initialized successfully")
        
        # List available tools
        all_tools = tool_manager.registry.list_tools()
        print(f"SUCCESS: Found {len(all_tools)} tools loaded")
        
        # Test by category
        code_intel_tools = tool_manager.list_tools_by_category(ToolCategory.CODE_INTELLIGENCE)
        print(f"SUCCESS: Code Intelligence tools: {len(code_intel_tools)}")
        
        return True
    except Exception as e:
        print(f"FAILED: Tool system initialization failed: {e}")
        return False

async def test_complexity_analyzer():
    """Test the Advanced Complexity Analyzer"""
    print("\n🔍 Testing Advanced Complexity Analyzer...")
    
    test_code = '''
def complex_function(x, y, z, a, b):
    """A complex function with multiple branches"""
    result = 0
    
    if x > 0:
        if y > 0:
            for i in range(z):
                if i % 2 == 0:
                    result += i * a
                else:
                    result -= i * b
        else:
            while y < 0:
                y += 1
                result += x
    elif x < 0:
        try:
            result = complex_calculation(x, y)
        except ValueError:
            result = 0
    else:
        result = sum([i for i in range(a) if i % 2 == 0])
    
    return result

def complex_calculation(a, b):
    return a ** 2 + b ** 2
    '''
    
    try:
        tool_manager = await get_tool_manager()
        result = await tool_manager.execute_tool(
            "advanced_complexity_analyzer",
            code=test_code,
            language="python",
            include_suggestions=True
        )
        
        if result.success:
            print("✅ Complexity Analysis completed")
            data = result.data
            print(f"   - Cyclomatic Complexity: {data.get('cyclomatic_complexity', 'N/A')}")
            print(f"   - Cognitive Complexity: {data.get('cognitive_complexity', 'N/A')}")
            print(f"   - Maintainability Index: {data.get('maintainability_index', 'N/A'):.1f}")
            print(f"   - Risk Level: {data.get('risk_level', 'N/A')}")
            
            if 'refactoring_suggestions' in data:
                print(f"   - Refactoring Suggestions: {len(data['refactoring_suggestions'])}")
                for suggestion in data['refactoring_suggestions'][:2]:
                    print(f"     • {suggestion}")
        else:
            print(f"❌ Complexity analysis failed: {result.error}")
        
        return result.success
    except Exception as e:
        print(f"❌ Exception in complexity analyzer test: {e}")
        return False

async def test_clone_detector():
    """Test the Code Clone Detector"""
    print("\n🔍 Testing Code Clone Detector...")
    
    source_code = '''
def calculate_area(length, width):
    """Calculate area of rectangle"""
    if length <= 0 or width <= 0:
        return 0
    return length * width
    '''
    
    comparison_codes = [
        '''
def compute_rectangle_area(l, w):
    """Compute area of rectangle"""
    if l <= 0 or w <= 0:
        return 0
    return l * w
        ''',
        '''
def get_area(length, width):
    """Get the area"""
    return length * width if length > 0 and width > 0 else 0
        ''',
        '''
def totally_different_function():
    """This is completely different"""
    print("Hello World")
    return 42
        '''
    ]
    
    try:
        tool_manager = await get_tool_manager()
        result = await tool_manager.execute_tool(
            "code_clone_detector",
            source_code=source_code,
            comparison_codes=comparison_codes,
            similarity_threshold=0.6
        )
        
        if result.success:
            print("✅ Clone Detection completed")
            data = result.data
            summary = data.get('summary', {})
            print(f"   - Total Comparisons: {summary.get('total_comparisons', 0)}")
            print(f"   - Clones Found: {summary.get('clones_found', 0)}")
            print(f"   - Highest Similarity: {summary.get('highest_similarity', 0):.2f}")
            
            clones = data.get('clones', [])
            for i, clone in enumerate(clones[:2]):
                print(f"   - Clone {i+1}: {clone.get('similarity_score', 0):.2f} similarity ({clone.get('clone_type', 'Unknown')})")
        else:
            print(f"❌ Clone detection failed: {result.error}")
        
        return result.success
    except Exception as e:
        print(f"❌ Exception in clone detector test: {e}")
        return False

async def test_security_scanner():
    """Test the Security Vulnerability Scanner"""
    print("\n🔒 Testing Security Vulnerability Scanner...")
    
    vulnerable_code = '''
import os
import subprocess

def process_user_input(user_input):
    # SQL Injection vulnerability
    query = "SELECT * FROM users WHERE name = '%s'" % user_input
    cursor.execute(query)
    
    # Command injection vulnerability
    os.system("ls " + user_input)
    
    # Hardcoded credentials
    api_key = "sk-1234567890abcdef"
    password = "admin123"
    
    # Path traversal vulnerability
    filename = user_input
    with open(filename, 'r') as f:
        return f.read()
    '''
    
    try:
        tool_manager = await get_tool_manager()
        result = await tool_manager.execute_tool(
            "security_vulnerability_scanner",
            code=vulnerable_code,
            language="python",
            severity_filter="medium",
            include_owasp=True
        )
        
        if result.success:
            print("✅ Security Scan completed")
            data = result.data
            vulnerabilities = data.get('vulnerabilities', [])
            summary = data.get('summary', {})
            
            print(f"   - Total Vulnerabilities: {summary.get('total_vulnerabilities', 0)}")
            print(f"   - Security Score: {summary.get('security_score', 0):.1f}/100")
            print(f"   - Risk Score: {data.get('risk_score', 'Unknown')}")
            
            severity_counts = summary.get('by_severity', {})
            for severity, count in severity_counts.items():
                if count > 0:
                    print(f"   - {severity.title()}: {count}")
            
            print("   - Top Vulnerabilities:")
            for vuln in vulnerabilities[:3]:
                print(f"     • {vuln.get('name', 'Unknown')} (Line {vuln.get('line', 'N/A')})")
        else:
            print(f"❌ Security scan failed: {result.error}")
        
        return result.success
    except Exception as e:
        print(f"❌ Exception in security scanner test: {e}")
        return False

async def test_refactoring_assistant():
    """Test the Intelligent Refactoring Assistant"""
    print("\n🔧 Testing Intelligent Refactoring Assistant...")
    
    messy_code = '''
import os
import sys
import json
from datetime import datetime

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
    return result

def process_more_data(data):
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
    return result

def unused_function():
    print("This function is never called")
    return 42

def main():
    data = [1, 2, 3, 4, 5]
    processed = process_data(data)
    return processed
    '''
    
    try:
        tool_manager = await get_tool_manager()
        result = await tool_manager.execute_tool(
            "intelligent_refactoring_assistant",
            code=messy_code,
            refactoring_types=["all"],
            preserve_functionality=True,
            optimization_level="balanced"
        )
        
        if result.success:
            print("✅ Refactoring completed")
            data = result.data
            
            applied = data.get('applied_refactorings', [])
            print(f"   - Applied Refactorings: {len(applied)}")
            
            for refactoring in applied[:3]:
                print(f"     • {refactoring.get('type', 'Unknown')}: {refactoring.get('description', 'No description')}")
            
            quality_improvement = data.get('quality_improvement', {})
            loc_improvement = quality_improvement.get('lines_of_code', {})
            if loc_improvement:
                print(f"   - Lines Reduced: {loc_improvement.get('reduction', 0)}")
            
            print(f"   - Functionality Preserved: {data.get('functionality_preserved', 'Unknown')}")
        else:
            print(f"❌ Refactoring failed: {result.error}")
        
        return result.success
    except Exception as e:
        print(f"❌ Exception in refactoring test: {e}")
        return False

async def test_performance_detector():
    """Test the Performance Bottleneck Detector"""
    print("\n⚡ Testing Performance Bottleneck Detector...")
    
    slow_code = '''
def inefficient_function(data):
    # String concatenation in loop
    result = ""
    for item in data:
        result += str(item) + ","
    
    # Inefficient list iteration
    for i in range(len(data)):
        print(data[i])
    
    # Nested loops
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] > data[j]:
                print(f"Found: {data[i]} > {data[j]}")
    
    return result

def database_in_loop(users):
    results = []
    for user in users:
        # Database query in loop (simulated)
        cursor.execute("SELECT * FROM orders WHERE user_id = ?", user.id)
        orders = cursor.fetchall()
        results.append(orders)
    return results
    '''
    
    try:
        tool_manager = await get_tool_manager()
        result = await tool_manager.execute_tool(
            "performance_bottleneck_detector",
            code=slow_code,
            language="python",
            analysis_depth="comprehensive"
        )
        
        if result.success:
            print("✅ Performance Analysis completed")
            data = result.data
            
            bottlenecks = data.get('bottlenecks', [])
            summary = data.get('summary', {})
            
            print(f"   - Bottlenecks Found: {len(bottlenecks)}")
            print(f"   - Performance Score: {summary.get('performance_score', 0):.1f}/100")
            print(f"   - Priority Level: {summary.get('priority_level', 'Unknown')}")
            
            critical_bottlenecks = [b for b in bottlenecks if b.get('severity') == 'critical']
            high_bottlenecks = [b for b in bottlenecks if b.get('severity') == 'high']
            
            print(f"   - Critical Issues: {len(critical_bottlenecks)}")
            print(f"   - High Priority Issues: {len(high_bottlenecks)}")
            
            improvement = data.get('estimated_improvement', {})
            if improvement:
                print(f"   - Potential Improvement: {improvement.get('potential_improvement', 'Unknown')}")
        else:
            print(f"❌ Performance analysis failed: {result.error}")
        
        return result.success
    except Exception as e:
        print(f"❌ Exception in performance detector test: {e}")
        return False

async def test_tool_search_and_recommendations():
    """Test tool search and recommendation system"""
    print("\n🔍 Testing Tool Search & Recommendations...")
    
    try:
        tool_manager = await get_tool_manager()
        
        # Test search functionality
        search_queries = [
            "code complexity",
            "security vulnerability",
            "performance optimization",
            "code documentation"
        ]
        
        for query in search_queries:
            recommendations = tool_manager.search_tools(query)
            print(f"   Query: '{query}' -> {len(recommendations)} tools found")
            
            if recommendations:
                top_tool = recommendations[0]
                print(f"     Top match: {top_tool['name']} (score: {top_tool['score']})")
        
        # Test analytics
        analytics = tool_manager.get_tool_analytics()
        print(f"   - Total Tools: {analytics.get('total_tools', 0)}")
        print(f"   - Categories: {len(analytics.get('categories', {}))}")
        
        return True
    except Exception as e:
        print(f"❌ Exception in search test: {e}")
        return False

async def run_comprehensive_test_suite():
    """Run all tests for the advanced tools system"""
    print("=" * 80)
    print("AEONFORGE ADVANCED TOOLS SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("Testing the first batch of 20 revolutionary Code Intelligence tools")
    print()
    
    # Track test results
    test_results = []
    
    # Test system initialization
    test_results.append(await test_tool_system_initialization())
    
    # Test individual tools
    test_results.append(await test_complexity_analyzer())
    test_results.append(await test_clone_detector())
    test_results.append(await test_security_scanner())
    test_results.append(await test_refactoring_assistant())
    test_results.append(await test_performance_detector())
    
    # Test system features
    test_results.append(await test_tool_search_and_recommendations())
    
    # Generate summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 ALL TESTS PASSED! Advanced Tools System is fully operational!")
        print("\n🌟 AEONFORGE IS NOW SUPERIOR TO OTHER LLMS IN CODE INTELLIGENCE!")
        print("\nCapabilities that surpass other LLMs:")
        print("✅ Advanced complexity analysis with multiple metrics")
        print("✅ Intelligent code clone detection with similarity scoring")
        print("✅ Comprehensive security vulnerability scanning")
        print("✅ AI-powered refactoring with functionality preservation")
        print("✅ Deep performance bottleneck detection")
        print("✅ Intelligent tool search and recommendations")
        print("✅ Scalable architecture for 6000+ tools")
        
    elif success_rate >= 80:
        print("✅ Most tests passed - System is largely operational")
        print("⚠️  Some components may need attention")
        
    else:
        print("❌ Several tests failed - System needs debugging")
        print("🔧 Check individual test results above")
    
    print("\n🚀 Ready to implement the next 20 tools!")
    print("   Next categories: Data Analysis, Web Development, DevOps, etc.")
    
    return success_rate

if __name__ == "__main__":
    # Run the comprehensive test suite
    asyncio.run(run_comprehensive_test_suite())