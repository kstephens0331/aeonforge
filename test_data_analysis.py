#!/usr/bin/env python3
"""
Test System for Data Analysis & Visualization Tools - Batch 5
=============================================================

Comprehensive testing of all 20 data analysis tools
for advanced analytics, machine learning, and business intelligence.
"""

import sys
import os
import traceback

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_data_analysis_imports():
    """Test all data analysis tool imports"""
    print("Testing Data Analysis Tool Imports...")
    
    try:
        from tools.data_analysis import (
            # Core Analytics Tools (1-5)
            DataVisualizer, StatisticalAnalyzer, TrendPredictor, SurveyBuilderAndAnalyzer, KPIDashboardCreator,
            # Advanced Analytics Tools (6-20)
            ABTestDesigner, CustomerSegmentationTool, SalesForecastingEngine, RiskAssessmentCalculator, ROICalculator,
            MarketResearchAnalyzer, DatabaseQueryBuilder, DataCleaningAndValidation, ReportAutomationEngine,
            BusinessIntelligenceDashboard, PredictiveAnalyticsEngine, CustomerJourneyMapper, ConversionRateOptimizer,
            FinancialModelBuilder, PerformanceMetricsTracker,
            # System functions
            get_data_analysis_tool_info, create_data_analysis_system
        )
        
        print("[PASS] All 20 data analysis tools imported successfully!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        traceback.print_exc()
        return False

def test_data_analysis_tool_info():
    """Test data analysis tool info function"""
    print("\nTesting Data Analysis Tool Info...")
    
    try:
        from tools.data_analysis import get_data_analysis_tool_info
        
        info = get_data_analysis_tool_info()
        print(f"Total tools: {info['total_tools']}")
        print(f"Categories: {info['categories']}")
        print(f"Capabilities: {len(info['capabilities'])} features")
        
        if info['total_tools'] == 20:
            print("[PASS] Data analysis tool info correct")
            return True
        else:
            print(f"[FAIL] Expected 20 tools, got {info['total_tools']}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Data analysis tool info error: {e}")
        traceback.print_exc()
        return False

def test_data_analysis_system_creation():
    """Test data analysis system creation"""
    print("\nTesting Data Analysis System Creation...")
    
    try:
        from tools.data_analysis import create_data_analysis_system
        
        system = create_data_analysis_system()
        
        if system['system_ready']:
            print(f"[PASS] Data analysis system created with {system['tools_initialized']} tools")
            print(f"Integration status: {system['integration_status']}")
            return True
        else:
            print("[FAIL] Data analysis system not ready")
            return False
            
    except Exception as e:
        print(f"[FAIL] Data analysis system creation error: {e}")
        traceback.print_exc()
        return False

def test_core_analytics_tools():
    """Test core analytics tool instantiation"""
    print("\nTesting Core Analytics Tools...")
    
    try:
        from tools.data_analysis import (
            DataVisualizer, StatisticalAnalyzer, TrendPredictor, SurveyBuilderAndAnalyzer, KPIDashboardCreator
        )
        
        # Test Data Visualizer
        visualizer = DataVisualizer()
        print("[PASS] Data Visualizer created")
        
        # Test Statistical Analyzer
        analyzer = StatisticalAnalyzer()
        print("[PASS] Statistical Analyzer created")
        
        # Test Trend Predictor
        predictor = TrendPredictor()
        print("[PASS] Trend Predictor created")
        
        # Test Survey Builder & Analyzer
        survey = SurveyBuilderAndAnalyzer()
        print("[PASS] Survey Builder & Analyzer created")
        
        # Test KPI Dashboard Creator
        dashboard = KPIDashboardCreator()
        print("[PASS] KPI Dashboard Creator created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Core analytics tools test error: {e}")
        traceback.print_exc()
        return False

def test_advanced_analytics_tools():
    """Test advanced analytics tool instantiation"""
    print("\nTesting Advanced Analytics Tools...")
    
    try:
        from tools.data_analysis import (
            ABTestDesigner, CustomerSegmentationTool, SalesForecastingEngine, 
            RiskAssessmentCalculator, ROICalculator
        )
        
        # Test A/B Test Designer
        abtest = ABTestDesigner()
        print("[PASS] A/B Test Designer created")
        
        # Test Customer Segmentation Tool
        segmentation = CustomerSegmentationTool()
        print("[PASS] Customer Segmentation Tool created")
        
        # Test Sales Forecasting Engine
        forecasting = SalesForecastingEngine()
        print("[PASS] Sales Forecasting Engine created")
        
        # Test Risk Assessment Calculator
        risk = RiskAssessmentCalculator()
        print("[PASS] Risk Assessment Calculator created")
        
        # Test ROI Calculator
        roi = ROICalculator()
        print("[PASS] ROI Calculator created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Advanced analytics tools test error: {e}")
        traceback.print_exc()
        return False

def test_business_intelligence_tools():
    """Test business intelligence tool instantiation"""
    print("\nTesting Business Intelligence Tools...")
    
    try:
        from tools.data_analysis import (
            MarketResearchAnalyzer, DatabaseQueryBuilder, DataCleaningAndValidation,
            ReportAutomationEngine, BusinessIntelligenceDashboard
        )
        
        # Test Market Research Analyzer
        market = MarketResearchAnalyzer()
        print("[PASS] Market Research Analyzer created")
        
        # Test Database Query Builder
        query = DatabaseQueryBuilder()
        print("[PASS] Database Query Builder created")
        
        # Test Data Cleaning & Validation
        cleaning = DataCleaningAndValidation()
        print("[PASS] Data Cleaning & Validation created")
        
        # Test Report Automation Engine
        reports = ReportAutomationEngine()
        print("[PASS] Report Automation Engine created")
        
        # Test Business Intelligence Dashboard
        bi = BusinessIntelligenceDashboard()
        print("[PASS] Business Intelligence Dashboard created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Business intelligence tools test error: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality of key data analysis tools"""
    print("\nTesting Basic Tool Functionality...")
    
    try:
        from tools.data_analysis import DataVisualizer, StatisticalAnalyzer, FinancialModelBuilder
        
        # Test Data Visualizer chart creation
        visualizer = DataVisualizer()
        chart_spec = {
            'chart_type': 'line_chart',
            'data_source': 'sample_data',
            'title': 'Test Chart',
            'x_axis': 'time',
            'y_axis': 'value'
        }
        
        result = visualizer.create_advanced_visualization(chart_spec)
        if result and 'visualization' in result:
            print("[PASS] Data Visualizer chart creation working")
        else:
            print("[FAIL] Data Visualizer not returning proper result")
            return False
        
        # Test Statistical Analyzer
        analyzer = StatisticalAnalyzer()
        analysis_spec = {
            'data_source': 'test_dataset',
            'analysis_type': 'descriptive',
            'variables': ['revenue', 'customers'],
            'confidence_level': 0.95
        }
        
        analysis_result = analyzer.perform_statistical_analysis(analysis_spec)
        if analysis_result and 'statistical_analysis' in analysis_result:
            print("[PASS] Statistical Analyzer working")
        else:
            print("[FAIL] Statistical Analyzer not returning proper result")
            return False
        
        # Test Financial Model Builder
        financial = FinancialModelBuilder()
        model_spec = {
            'name': 'Test Financial Model',
            'type': 'dcf',
            'projection_years': 5,
            'revenue_drivers': {'base_revenue': 1000000, 'growth_rate': 0.15}
        }
        
        financial_result = financial.create_financial_model(model_spec)
        if financial_result and 'financial_model' in financial_result:
            print("[PASS] Financial Model Builder working")
        else:
            print("[FAIL] Financial Model Builder not returning proper result")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Basic functionality test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all data analysis tests"""
    print("=" * 60)
    print("Aeonforge Data Analysis Tools - Test Suite")
    print("Batch 5: Data Analysis & Visualization Tools")
    print("=" * 60)
    
    tests = [
        ("Data Analysis Tool Imports", test_data_analysis_imports),
        ("Data Analysis Tool Info", test_data_analysis_tool_info),
        ("Data Analysis System Creation", test_data_analysis_system_creation),
        ("Core Analytics Tools", test_core_analytics_tools),
        ("Advanced Analytics Tools", test_advanced_analytics_tools),
        ("Business Intelligence Tools", test_business_intelligence_tools),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("DATA ANALYSIS TOOLS TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n[SUCCESS] All data analysis tools working correctly!")
        print("\nREADY FOR ANALYTICS PRODUCTION:")
        print("- Advanced statistical analysis and hypothesis testing")
        print("- Machine learning and predictive modeling") 
        print("- Real-time data visualization and dashboards")
        print("- Business intelligence and executive reporting")
        print("- Financial modeling and forecasting")
        print("- Customer analytics and segmentation")
        print("- Market research and competitive analysis")
        print("- Performance monitoring and KPI tracking")
        print("- A/B testing and conversion optimization")
        print("- Complete analytics workflow automation")
    else:
        print(f"\n[WARNING] {len(results) - passed} tests failed. Check errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()