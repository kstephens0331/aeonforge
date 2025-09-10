#!/usr/bin/env python3
"""
Simple Test for Natural Language Processing Tools
===============================================

Quick validation of all 20 NLP tools to ensure proper imports and basic functionality.
"""

import sys
import os
import traceback

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_imports():
    """Test all tool imports"""
    print("Testing NLP Tool Imports...")
    
    try:
        from tools.natural_language import (
            # Core Tools (1-3)
            UniversalLanguageDetector, SmartTypoCorrector, SlangInterpreter,
            # Intelligence Tools (4-7)
            IntentRecognitionEngine, UniversalTranslator, AdvancedSentimentAnalyzer, ContextUnderstandingEngine,
            # Conversation Tools (8-10)
            ConversationFlowManager, MultilingualContentAdapter, SmartResponseGenerator,
            # Advanced Tools (11-15)
            ConversationalMemoryEngine, ContextualDialogueManager, PersonalizationEngine,
            MultilingualContextualizer, IntelligentResponseGenerator,
            # Real-Time Tools (16-20)
            RealTimeLanguageProcessor, AdaptiveLanguageLearner, CrossLinguisticIntelligence,
            ContextualMemoryManager, IntelligentConversationOrchestrator,
            # System functions
            get_tool_info, create_nlp_system
        )
        
        print("[PASS] All 20 NLP tools imported successfully!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        traceback.print_exc()
        return False

def test_tool_info():
    """Test tool info function"""
    print("\nTesting Tool Info...")
    
    try:
        from tools.natural_language import get_tool_info
        
        info = get_tool_info()
        print(f"Total tools: {info['total_tools']}")
        print(f"Categories: {info['categories']}")
        print(f"Capabilities: {len(info['capabilities'])} features")
        
        if info['total_tools'] == 20:
            print("[PASS] Tool info correct")
            return True
        else:
            print(f"[FAIL] Expected 20 tools, got {info['total_tools']}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Tool info error: {e}")
        traceback.print_exc()
        return False

def test_system_creation():
    """Test NLP system creation"""
    print("\nTesting System Creation...")
    
    try:
        from tools.natural_language import create_nlp_system
        
        system = create_nlp_system()
        
        if system['system_ready']:
            print(f"[PASS] System created with {system['tools_initialized']} tools")
            return True
        else:
            print("[FAIL] System not ready")
            return False
            
    except Exception as e:
        print(f"[FAIL] System creation error: {e}")
        traceback.print_exc()
        return False

def test_individual_tools():
    """Test individual tool instantiation"""
    print("\nTesting Individual Tools...")
    
    try:
        from tools.natural_language import (
            UniversalLanguageDetector, SmartTypoCorrector, SlangInterpreter,
            IntentRecognitionEngine, UniversalTranslator
        )
        
        # Test core tools
        detector = UniversalLanguageDetector()
        print("[PASS] Language Detector created")
        
        corrector = SmartTypoCorrector()
        print("[PASS] Typo Corrector created")
        
        slang = SlangInterpreter()
        print("[PASS] Slang Interpreter created")
        
        intent = IntentRecognitionEngine()
        print("[PASS] Intent Recognition created")
        
        translator = UniversalTranslator()
        print("[PASS] Universal Translator created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Individual tool test error: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality of a few key tools"""
    print("\nTesting Basic Functionality...")
    
    try:
        from tools.natural_language import UniversalLanguageDetector
        
        # Test language detection
        detector = UniversalLanguageDetector()
        
        # Simple test
        result = detector.detect_language("Hello, how are you?")
        print(f"Language detection result: {result}")
        
        if result and isinstance(result, dict):
            print("[PASS] Language detector working")
            return True
        else:
            print("[FAIL] Language detector not returning proper result")
            return False
            
    except Exception as e:
        print(f"[FAIL] Basic functionality test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Aeonforge NLP System - Simple Test Suite")
    print("=" * 50)
    
    tests = [
        ("Tool Imports", test_imports),
        ("Tool Info", test_tool_info),
        ("System Creation", test_system_creation),
        ("Individual Tools", test_individual_tools),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n[SUCCESS] All tests passed! NLP system is working correctly.")
    else:
        print(f"\n[WARNING] {len(results) - passed} tests failed. Check errors above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()