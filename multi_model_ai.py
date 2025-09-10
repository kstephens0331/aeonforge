"""
AeonForge Multi-Model AI Integration System
Support for OpenAI/ChatGPT, Google Gemini, and other AI models
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """Supported AI model providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"

@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    provider: ModelProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    rate_limit: int = 10  # requests per minute

class AIModelManager:
    """Manages multiple AI model integrations"""
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiters: Dict[str, Dict] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available AI models"""
        # OpenAI/ChatGPT
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.models['gpt-4'] = ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                api_key=openai_key,
                base_url="https://api.openai.com/v1",
                max_tokens=4096
            )
            self.models['gpt-3.5-turbo'] = ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                api_key=openai_key,
                base_url="https://api.openai.com/v1",
                max_tokens=4096
            )
        
        # Google Gemini
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key and gemini_key != 'placeholder_for_gemini_key':
            self.models['gemini-1.5-flash'] = ModelConfig(
                provider=ModelProvider.GEMINI,
                model_name="gemini-1.5-flash",
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta",
                max_tokens=8192
            )
            self.models['gemini-1.5-pro'] = ModelConfig(
                provider=ModelProvider.GEMINI,
                model_name="gemini-1.5-pro",
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta",
                max_tokens=8192
            )
        
        # Local Ollama (existing)
        self.models['llama3'] = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="llama3:8b",
            base_url="http://localhost:11434",
            max_tokens=4096
        )
        
        logger.info(f"Initialized {len(self.models)} AI models: {list(self.models.keys())}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def generate_response(self, model_name: str, prompt: str, 
                              system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Generate response from specified model"""
        if model_name not in self.models:
            return {
                'success': False,
                'error': f'Model {model_name} not available',
                'available_models': list(self.models.keys())
            }
        
        config = self.models[model_name]
        
        try:
            if config.provider == ModelProvider.OPENAI:
                return await self._openai_request(config, prompt, system_prompt, **kwargs)
            elif config.provider == ModelProvider.GEMINI:
                return await self._gemini_request(config, prompt, system_prompt, **kwargs)
            elif config.provider == ModelProvider.OLLAMA:
                return await self._ollama_request(config, prompt, system_prompt, **kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Provider {config.provider.value} not implemented'
                }
        
        except Exception as e:
            logger.error(f"Error with model {model_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model': model_name
            }
    
    async def _openai_request(self, config: ModelConfig, prompt: str, 
                             system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Make request to OpenAI API"""
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }
        
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        payload = {
            'model': config.model_name,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', config.max_tokens),
            'temperature': kwargs.get('temperature', config.temperature),
        }
        
        url = f"{config.base_url}/chat/completions"
        
        async with self.session.post(url, headers=headers, json=payload, 
                                   timeout=config.timeout) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'success': True,
                    'response': data['choices'][0]['message']['content'],
                    'model': config.model_name,
                    'usage': data.get('usage', {}),
                    'provider': 'openai'
                }
            else:
                error_text = await response.text()
                return {
                    'success': False,
                    'error': f'OpenAI API error: {response.status} - {error_text}',
                    'model': config.model_name
                }
    
    async def _gemini_request(self, config: ModelConfig, prompt: str, 
                             system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Make request to Google Gemini API"""
        # Combine system prompt and user prompt for Gemini
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            'contents': [{
                'parts': [{'text': full_prompt}]
            }],
            'generationConfig': {
                'maxOutputTokens': kwargs.get('max_tokens', config.max_tokens),
                'temperature': kwargs.get('temperature', config.temperature),
            }
        }
        
        url = f"{config.base_url}/models/{config.model_name}:generateContent?key={config.api_key}"
        
        async with self.session.post(url, json=payload, 
                                   timeout=config.timeout) as response:
            if response.status == 200:
                data = await response.json()
                if 'candidates' in data and data['candidates']:
                    content = data['candidates'][0]['content']['parts'][0]['text']
                    return {
                        'success': True,
                        'response': content,
                        'model': config.model_name,
                        'usage': data.get('usageMetadata', {}),
                        'provider': 'gemini'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No response generated by Gemini',
                        'model': config.model_name
                    }
            else:
                error_text = await response.text()
                return {
                    'success': False,
                    'error': f'Gemini API error: {response.status} - {error_text}',
                    'model': config.model_name
                }
    
    async def _ollama_request(self, config: ModelConfig, prompt: str, 
                             system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Make request to Ollama API"""
        payload = {
            'model': config.model_name,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': kwargs.get('temperature', config.temperature),
                'num_predict': kwargs.get('max_tokens', config.max_tokens)
            }
        }
        
        if system_prompt:
            payload['system'] = system_prompt
        
        url = f"{config.base_url}/api/generate"
        
        try:
            async with self.session.post(url, json=payload, 
                                       timeout=config.timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'success': True,
                        'response': data.get('response', ''),
                        'model': config.model_name,
                        'provider': 'ollama'
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'Ollama API error: {response.status} - {error_text}',
                        'model': config.model_name
                    }
        except aiohttp.ClientConnectorError:
            return {
                'success': False,
                'error': 'Ollama server not available - make sure Ollama is running',
                'model': config.model_name
            }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        return [
            {
                'name': name,
                'provider': config.provider.value,
                'model_name': config.model_name,
                'max_tokens': config.max_tokens,
                'has_api_key': config.api_key is not None
            }
            for name, config in self.models.items()
        ]
    
    async def compare_models(self, prompt: str, model_names: List[str] = None, 
                           system_prompt: str = None) -> Dict[str, Any]:
        """Compare responses from multiple models"""
        if model_names is None:
            model_names = list(self.models.keys())
        
        tasks = []
        for model_name in model_names:
            if model_name in self.models:
                task = self.generate_response(model_name, prompt, system_prompt)
                tasks.append((model_name, task))
        
        results = {}
        for model_name, task in tasks:
            try:
                result = await task
                results[model_name] = result
            except Exception as e:
                results[model_name] = {
                    'success': False,
                    'error': str(e),
                    'model': model_name
                }
        
        return {
            'prompt': prompt,
            'system_prompt': system_prompt,
            'results': results,
            'models_tested': len(results)
        }
    
    async def smart_routing(self, prompt: str, task_type: str = "general", 
                          system_prompt: str = None) -> Dict[str, Any]:
        """Intelligently route requests to the best model for the task"""
        # Model routing logic based on task type
        routing_rules = {
            'code_analysis': ['gpt-4', 'gemini-1.5-pro', 'gpt-3.5-turbo', 'llama3'],
            'creative_writing': ['gpt-4', 'gemini-1.5-pro', 'gpt-3.5-turbo'],
            'technical_explanation': ['gpt-4', 'gemini-1.5-pro', 'gpt-3.5-turbo'],
            'quick_response': ['gpt-3.5-turbo', 'gemini-1.5-flash', 'llama3'],
            'vision_analysis': ['gemini-1.5-pro', 'gpt-4'],
            'general': ['gpt-4', 'gemini-1.5-pro', 'gpt-3.5-turbo', 'llama3']
        }
        
        preferred_models = routing_rules.get(task_type, routing_rules['general'])
        
        # Try models in preference order
        for model_name in preferred_models:
            if model_name in self.models:
                result = await self.generate_response(model_name, prompt, system_prompt)
                if result['success']:
                    result['selected_model'] = model_name
                    result['task_type'] = task_type
                    return result
        
        return {
            'success': False,
            'error': 'No available models could handle the request',
            'task_type': task_type,
            'tried_models': preferred_models
        }

# Global AI manager instance
ai_manager = None

async def get_ai_manager() -> AIModelManager:
    """Get the global AI model manager"""
    global ai_manager
    if ai_manager is None:
        ai_manager = AIModelManager()
    return ai_manager

# Convenience functions
async def ask_ai(prompt: str, model: str = None, system_prompt: str = None, **kwargs) -> str:
    """Simple function to ask AI and get response"""
    async with AIModelManager() as manager:
        if model:
            result = await manager.generate_response(model, prompt, system_prompt, **kwargs)
        else:
            result = await manager.smart_routing(prompt, system_prompt=system_prompt, **kwargs)
        
        if result['success']:
            return result['response']
        else:
            return f"Error: {result['error']}"

async def compare_ai_models(prompt: str, models: List[str] = None) -> Dict[str, Any]:
    """Compare responses from multiple AI models"""
    async with AIModelManager() as manager:
        return await manager.compare_models(prompt, models)

# Export main classes and functions
__all__ = [
    'AIModelManager', 'ModelProvider', 'ModelConfig',
    'get_ai_manager', 'ask_ai', 'compare_ai_models'
]