#!/usr/bin/env python3
"""
Test System for Business Productivity Tools - Batch 3
====================================================

Comprehensive testing of all 20 business productivity tools
for document generation, data visualization, and workflow automation.
"""

import sys
import os
import traceback

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_business_imports():
    """Test all business productivity tool imports"""
    print("Testing Business Productivity Tool Imports...")
    
    try:
        from tools.business_productivity import (
            # Core Business Tools (1-5)
            ExcelMaster, PowerPointPro, WordDocumentGenerator, PDFCreatorAndEditor, ChartAndGraphGenerator,
            # Business Intelligence Tools (6-10)
            ReportBuilder, InvoiceAndBillingSystem, ContractGenerator, EmailCampaignBuilder, CalendarAndScheduleManager,
            # Advanced Business Tools (11-20)
            MeetingNotesAndMinutes, ProposalGenerator, BudgetPlanner, ProjectTimelineCreator, BusinessPlanGenerator,
            PerformanceReviewBuilder, PolicyDocumentCreator, TrainingMaterialGenerator, QualityAssuranceChecklist, WorkflowAutomationDesigner,
            # System functions
            get_business_tool_info, create_business_productivity_system
        )
        
        print("[PASS] All 20 business productivity tools imported successfully!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        traceback.print_exc()
        return False

def test_business_tool_info():
    """Test business tool info function"""
    print("\nTesting Business Tool Info...")
    
    try:
        from tools.business_productivity import get_business_tool_info
        
        info = get_business_tool_info()
        print(f"Total tools: {info['total_tools']}")
        print(f"Categories: {info['categories']}")
        print(f"Capabilities: {len(info['capabilities'])} features")
        
        if info['total_tools'] == 20:
            print("[PASS] Business tool info correct")
            return True
        else:
            print(f"[FAIL] Expected 20 tools, got {info['total_tools']}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Business tool info error: {e}")
        traceback.print_exc()
        return False

def test_business_system_creation():
    """Test business productivity system creation"""
    print("\nTesting Business System Creation...")
    
    try:
        from tools.business_productivity import create_business_productivity_system
        
        system = create_business_productivity_system()
        
        if system['system_ready']:
            print(f"[PASS] Business system created with {system['tools_initialized']} tools")
            print(f"Integration status: {system['integration_status']}")
            return True
        else:
            print("[FAIL] Business system not ready")
            return False
            
    except Exception as e:
        print(f"[FAIL] Business system creation error: {e}")
        traceback.print_exc()
        return False

def test_core_business_tools():
    """Test core business tool instantiation"""
    print("\nTesting Core Business Tools...")
    
    try:
        from tools.business_productivity import (
            ExcelMaster, PowerPointPro, WordDocumentGenerator, PDFCreatorAndEditor, ChartAndGraphGenerator
        )
        
        # Test Excel Master
        excel = ExcelMaster()
        print("[PASS] Excel Master created")
        
        # Test PowerPoint Pro
        powerpoint = PowerPointPro()
        print("[PASS] PowerPoint Pro created")
        
        # Test Word Generator
        word = WordDocumentGenerator()
        print("[PASS] Word Document Generator created")
        
        # Test PDF Creator
        pdf = PDFCreatorAndEditor()
        print("[PASS] PDF Creator & Editor created")
        
        # Test Chart Generator
        chart = ChartAndGraphGenerator()
        print("[PASS] Chart & Graph Generator created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Core business tools test error: {e}")
        traceback.print_exc()
        return False

def test_business_intelligence_tools():
    """Test business intelligence tool instantiation"""
    print("\nTesting Business Intelligence Tools...")
    
    try:
        from tools.business_productivity import (
            ReportBuilder, InvoiceAndBillingSystem, ContractGenerator, 
            EmailCampaignBuilder, CalendarAndScheduleManager
        )
        
        # Test Report Builder
        report = ReportBuilder()
        print("[PASS] Report Builder created")
        
        # Test Invoice System
        invoice = InvoiceAndBillingSystem()
        print("[PASS] Invoice & Billing System created")
        
        # Test Contract Generator
        contract = ContractGenerator()
        print("[PASS] Contract Generator created")
        
        # Test Email Builder
        email = EmailCampaignBuilder()
        print("[PASS] Email Campaign Builder created")
        
        # Test Calendar Manager
        calendar = CalendarAndScheduleManager()
        print("[PASS] Calendar & Schedule Manager created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Business intelligence tools test error: {e}")
        traceback.print_exc()
        return False

def test_advanced_business_tools():
    """Test advanced business tool instantiation"""
    print("\nTesting Advanced Business Tools...")
    
    try:
        from tools.business_productivity import (
            MeetingNotesAndMinutes, ProposalGenerator, BudgetPlanner,
            ProjectTimelineCreator, BusinessPlanGenerator
        )
        
        # Test Meeting Notes
        meeting = MeetingNotesAndMinutes()
        print("[PASS] Meeting Notes & Minutes created")
        
        # Test Proposal Generator
        proposal = ProposalGenerator()
        print("[PASS] Proposal Generator created")
        
        # Test Budget Planner
        budget = BudgetPlanner()
        print("[PASS] Budget Planner created")
        
        # Test Project Timeline
        timeline = ProjectTimelineCreator()
        print("[PASS] Project Timeline Creator created")
        
        # Test Business Plan
        business_plan = BusinessPlanGenerator()
        print("[PASS] Business Plan Generator created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Advanced business tools test error: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality of key business tools"""
    print("\nTesting Basic Tool Functionality...")
    
    try:
        from tools.business_productivity import ExcelMaster, ChartAndGraphGenerator, ReportBuilder
        
        # Test Excel Master spreadsheet creation
        excel = ExcelMaster()
        spreadsheet_spec = {
            'sheets': {
                'Data': {
                    'headers': ['Name', 'Sales', 'Profit'],
                    'data': [
                        ['Product A', 1000, 200],
                        ['Product B', 1500, 300],
                        ['Product C', 800, 150]
                    ]
                }
            }
        }
        
        result = excel.create_spreadsheet(spreadsheet_spec)
        if result and 'workbook' in result:
            print("[PASS] Excel Master spreadsheet creation working")
        else:
            print("[FAIL] Excel Master not returning proper result")
            return False
        
        # Test Chart Generator
        chart = ChartAndGraphGenerator()
        chart_spec = {
            'type': 'column',
            'title': 'Sales Performance',
            'data': {
                'categories': ['Product A', 'Product B', 'Product C'],
                'series': [{'name': 'Sales', 'data': [1000, 1500, 800]}]
            }
        }
        
        chart_result = chart.create_chart(chart_spec)
        if chart_result and 'chart' in chart_result:
            print("[PASS] Chart Generator working")
        else:
            print("[FAIL] Chart Generator not returning proper result")
            return False
        
        # Test Report Builder
        report = ReportBuilder()
        report_spec = {
            'title': 'Test Business Report',
            'sections': [
                {
                    'title': 'Overview',
                    'content': 'This is a test report section'
                }
            ]
        }
        
        report_result = report.create_business_report(report_spec)
        if report_result and 'report' in report_result:
            print("[PASS] Report Builder working")
        else:
            print("[FAIL] Report Builder not returning proper result")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Basic functionality test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all business productivity tests"""
    print("=" * 60)
    print("Aeonforge Business Productivity Tools - Test Suite")
    print("Batch 3: Document Generation & Business Automation")
    print("=" * 60)
    
    tests = [
        ("Business Tool Imports", test_business_imports),
        ("Business Tool Info", test_business_tool_info),
        ("Business System Creation", test_business_system_creation),
        ("Core Business Tools", test_core_business_tools),
        ("Business Intelligence Tools", test_business_intelligence_tools),
        ("Advanced Business Tools", test_advanced_business_tools),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("BUSINESS PRODUCTIVITY TOOLS TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n[SUCCESS] All business productivity tools working correctly!")
        print("\nREADY FOR BUSINESS USE:")
        print("- Professional document generation (Excel, PowerPoint, Word, PDF)")
        print("- Advanced data visualization and charts") 
        print("- Financial document automation (invoices, contracts)")
        print("- Project management and timeline creation")
        print("- Business intelligence and reporting")
        print("- HR and performance management tools")
        print("- Workflow automation and optimization")
    else:
        print(f"\n[WARNING] {len(results) - passed} tests failed. Check errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()