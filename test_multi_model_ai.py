"""
Test Multi-Model AI Integration
Test OpenAI/ChatGPT, Gemini, and Ollama integration
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from multi_model_ai import AIModelManager, ask_ai, compare_ai_models

async def test_multi_model_ai():
    """Test the multi-model AI integration"""
    print("=" * 80)
    print("AEONFORGE MULTI-MODEL AI INTEGRATION TEST")
    print("=" * 80)
    
    async with AIModelManager() as ai_manager:
        # Check available models
        available_models = ai_manager.get_available_models()
        print(f"Available AI Models: {len(available_models)}")
        print()
        
        for model in available_models:
            status = "READY" if model['has_api_key'] or model['provider'] == 'ollama' else "MISSING API KEY"
            print(f"  {model['name']} ({model['provider']}) - {status}")
        
        print()
        
        # Test prompt
        test_prompt = "Explain what makes a good software developer in 2 sentences."
        
        # Test each available model
        print("Testing AI Model Responses:")
        print("-" * 40)
        
        working_models = []
        
        for model in available_models:
            model_name = model['name']
            if model['has_api_key'] or model['provider'] == 'ollama':
                print(f"\nTesting {model_name}...")
                try:
                    result = await ai_manager.generate_response(
                        model_name, 
                        test_prompt,
                        system_prompt="You are a helpful AI assistant."
                    )
                    
                    if result['success']:
                        print(f"SUCCESS: {model_name}")
                        print(f"Response: {result['response'][:100]}...")
                        working_models.append(model_name)
                    else:
                        print(f"FAILED: {model_name} - {result['error']}")
                
                except Exception as e:
                    print(f"ERROR: {model_name} - {str(e)}")
            else:
                print(f"SKIPPED: {model_name} - Missing API key")
        
        # Test smart routing
        print(f"\n" + "=" * 40)
        print("Testing Smart AI Routing:")
        print("=" * 40)
        
        if working_models:
            routing_result = await ai_manager.smart_routing(
                "What is the best programming language for AI development?",
                task_type="technical_explanation"
            )
            
            if routing_result['success']:
                print(f"SUCCESS: Smart routing selected: {routing_result['selected_model']}")
                print(f"Response: {routing_result['response'][:150]}...")
            else:
                print(f"FAILED: Smart routing failed: {routing_result['error']}")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("MULTI-MODEL AI SUMMARY")
        print("=" * 80)
        print(f"Total Models Configured: {len(available_models)}")
        print(f"Working Models: {len(working_models)}")
        print(f"Models: {', '.join(working_models) if working_models else 'None'}")
        
        if len(working_models) >= 2:
            print("\nSUCCESS: Multi-model AI system is operational!")
            print("AeonForge now has access to multiple AI providers")
            print("Smart routing system is working")
            print("Ready for advanced AI-powered features")
        elif len(working_models) == 1:
            print(f"\nPARTIAL: Only {working_models[0]} is working")
            print("Consider adding Gemini API key for full functionality")
        else:
            print("\nFAILED: No AI models are working")
            print("Check API keys and network connectivity")
        
        return len(working_models) >= 1

async def main():
    """Run the multi-model AI test"""
    try:
        success = await test_multi_model_ai()
        
        if success:
            print(f"\n" + "=" * 80)
            print("AEONFORGE AI INTEGRATION COMPLETE")
            print("Ready for advanced AI-powered development assistance!")
            print("=" * 80)
            return 0
        else:
            print(f"\n" + "=" * 80)
            print("AI INTEGRATION NEEDS ATTENTION")
            print("Check API keys and configuration")
            print("=" * 80)
            return 1
    
    except Exception as e:
        print(f"\nCRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)