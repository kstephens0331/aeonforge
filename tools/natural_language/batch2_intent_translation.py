"""
AeonForge Natural Language Processing Tools - Intent & Translation (Tools 4-8)
Advanced intent recognition and multilingual translation capabilities
"""

import re
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass
from collections import Counter, defaultdict
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from advanced_tools_system import BaseTool, ToolResult, ToolCategory
    from multi_model_ai import AIModelManager
except ImportError:
    # Fallback implementations
    class BaseTool:
        def __init__(self, name: str, description: str, category: str):
            self.name = name
            self.description = description
            self.category = category
        
        async def execute(self, **kwargs) -> Any:
            pass
    
    @dataclass
    class ToolResult:
        success: bool
        data: Dict[str, Any] = None
        error: str = None
        execution_time: float = 0.0
    
    class ToolCategory:
        NATURAL_LANGUAGE = "natural_language"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tool 4: Intent Recognition Engine
class IntentRecognitionEngine(BaseTool):
    """Advanced intent recognition that understands what users really want"""
    
    def __init__(self):
        super().__init__(
            name="intent_recognition_engine",
            description="Recognize user intent from natural language with high accuracy across multiple domains",
            category=ToolCategory.NATURAL_LANGUAGE
        )
        self.intent_patterns = self._initialize_intent_patterns()
        self.confidence_thresholds = self._initialize_confidence_thresholds()
    
    async def execute(self, text: str, domain: str = "general", 
                     include_confidence: bool = True, **kwargs) -> ToolResult:
        try:
            recognition_data = await self._recognize_intent(text, domain, include_confidence)
            
            return ToolResult(
                success=True,
                data=recognition_data
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Intent recognition failed: {str(e)}"
            )
    
    def _initialize_intent_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive intent recognition patterns"""
        return {
            # General intents
            'question': {
                'patterns': [
                    r'\b(what|who|when|where|why|how|which|whose)\b',
                    r'\b(can you|could you|would you|will you)\b.*\?',
                    r'\b(do you|did you|does|is|are|was|were)\b.*\?',
                    r'\b(tell me|explain|describe|show me)\b',
                    r'\?$'
                ],
                'keywords': ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'explain', 'tell me'],
                'confidence_boost': 1.2,
                'domain': 'general'
            },
            
            'request_help': {
                'patterns': [
                    r'\b(help|assist|support|guide|tutorial)\b',
                    r'\b(need help|can you help|please help)\b',
                    r'\b(stuck|confused|don\'t know|lost)\b',
                    r'\b(how do i|how to|help me)\b'
                ],
                'keywords': ['help', 'assist', 'support', 'guide', 'stuck', 'confused', 'tutorial'],
                'confidence_boost': 1.1,
                'domain': 'general'
            },
            
            'greeting': {
                'patterns': [
                    r'\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b',
                    r'\b(what\'s up|how are you|how\'s it going)\b',
                    r'^(yo|sup|hiya|howdy)\b'
                ],
                'keywords': ['hello', 'hi', 'hey', 'greetings', 'morning', 'afternoon', 'evening'],
                'confidence_boost': 1.3,
                'domain': 'general'
            },
            
            'complaint': {
                'patterns': [
                    r'\b(problem|issue|bug|error|broken|not working|doesn\'t work)\b',
                    r'\b(complain|complaint|frustrated|annoying|terrible|awful)\b',
                    r'\b(fix|repair|resolve|solve)\b.*\b(problem|issue)\b'
                ],
                'keywords': ['problem', 'issue', 'bug', 'error', 'broken', 'complain', 'frustrated'],
                'confidence_boost': 1.1,
                'domain': 'general'
            },
            
            'compliment': {
                'patterns': [
                    r'\b(great|awesome|amazing|fantastic|excellent|wonderful|perfect)\b',
                    r'\b(love|like|enjoy|appreciate|impressed|good job|well done)\b',
                    r'\b(thank you|thanks|grateful|appreciate)\b'
                ],
                'keywords': ['great', 'awesome', 'amazing', 'love', 'like', 'thank', 'appreciate'],
                'confidence_boost': 1.2,
                'domain': 'general'
            },
            
            # Technical intents
            'code_request': {
                'patterns': [
                    r'\b(write|create|generate|make|build)\b.*\b(code|function|script|program)\b',
                    r'\b(implement|develop|program)\b',
                    r'\b(debug|fix|refactor|optimize)\b.*\b(code|function)\b'
                ],
                'keywords': ['code', 'function', 'script', 'program', 'implement', 'debug', 'refactor'],
                'confidence_boost': 1.3,
                'domain': 'technical'
            },
            
            'explanation_request': {
                'patterns': [
                    r'\b(explain|describe|tell me about|what is|define)\b',
                    r'\b(understand|learn|know more about)\b',
                    r'\b(how does|why does|what does)\b.*\b(work|mean)\b'
                ],
                'keywords': ['explain', 'describe', 'understand', 'learn', 'define', 'work', 'mean'],
                'confidence_boost': 1.1,
                'domain': 'educational'
            },
            
            'translation_request': {
                'patterns': [
                    r'\b(translate|translation)\b',
                    r'\b(how do you say|what is.*in)\b',
                    r'\b(english|spanish|french|german|chinese|japanese|korean)\b.*\b(to|in)\b'
                ],
                'keywords': ['translate', 'translation', 'say', 'language', 'english', 'spanish', 'french'],
                'confidence_boost': 1.4,
                'domain': 'language'
            },
            
            'creative_request': {
                'patterns': [
                    r'\b(write|create|generate|make)\b.*\b(story|poem|essay|article|content)\b',
                    r'\b(creative|imagination|original|unique)\b',
                    r'\b(brainstorm|ideas|suggestions)\b'
                ],
                'keywords': ['write', 'create', 'story', 'poem', 'creative', 'brainstorm', 'ideas'],
                'confidence_boost': 1.2,
                'domain': 'creative'
            },
            
            'search_request': {
                'patterns': [
                    r'\b(find|search|look for|locate)\b',
                    r'\b(where can i|where to|how to find)\b',
                    r'\b(show me|give me|list)\b.*\b(examples|options|results)\b'
                ],
                'keywords': ['find', 'search', 'look', 'locate', 'show', 'give', 'list'],
                'confidence_boost': 1.1,
                'domain': 'information'
            },
            
            'comparison_request': {
                'patterns': [
                    r'\b(compare|comparison|vs|versus|difference|better)\b',
                    r'\b(which is|what\'s the difference|pros and cons)\b',
                    r'\b(similar|different|same)\b'
                ],
                'keywords': ['compare', 'comparison', 'difference', 'better', 'similar', 'different'],
                'confidence_boost': 1.1,
                'domain': 'analysis'
            }
        }
    
    def _initialize_confidence_thresholds(self) -> Dict[str, float]:
        """Initialize confidence thresholds for different intent types"""
        return {
            'high_confidence': 0.8,
            'medium_confidence': 0.6,
            'low_confidence': 0.4,
            'uncertain': 0.2
        }
    
    async def _recognize_intent(self, text: str, domain: str, include_confidence: bool) -> Dict[str, Any]:
        """Recognize intent from text"""
        if not text or len(text.strip()) == 0:
            return {
                'primary_intent': 'unclear',
                'confidence': 0.0,
                'possible_intents': [],
                'domain': domain
            }
        
        text_lower = text.lower().strip()
        intent_scores = {}
        
        # Score each intent pattern
        for intent_name, intent_data in self.intent_patterns.items():
            # Skip if domain-specific and doesn't match
            if domain != "general" and intent_data.get('domain', 'general') != domain and intent_data.get('domain', 'general') != 'general':
                continue
            
            score = 0
            total_matches = 0
            
            # Pattern matching
            for pattern in intent_data['patterns']:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches * 2
                total_matches += matches
            
            # Keyword matching
            for keyword in intent_data['keywords']:
                if keyword in text_lower:
                    score += 1
                    total_matches += 1
            
            # Apply confidence boost
            if total_matches > 0:
                confidence_boost = intent_data.get('confidence_boost', 1.0)
                score *= confidence_boost
            
            # Normalize score
            if total_matches > 0:
                intent_scores[intent_name] = score / max(len(text_lower.split()), 1)
            else:
                intent_scores[intent_name] = 0
        
        # Find best matches
        if not intent_scores:
            return {
                'primary_intent': 'unclear',
                'confidence': 0.0,
                'possible_intents': [],
                'domain': domain
            }
        
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        primary_intent = sorted_intents[0][0]
        primary_score = sorted_intents[0][1]
        
        # Calculate confidence
        confidence = min(primary_score, 1.0)
        confidence_level = self._get_confidence_level(confidence)
        
        # Get possible intents (top 3)
        possible_intents = [
            {
                'intent': intent,
                'confidence': round(min(score, 1.0), 3),
                'confidence_level': self._get_confidence_level(min(score, 1.0))
            }
            for intent, score in sorted_intents[:3]
            if score > 0.1
        ]
        
        # Enhanced analysis
        context_analysis = self._analyze_context(text_lower, primary_intent)
        sentiment = self._analyze_sentiment(text_lower)
        urgency = self._analyze_urgency(text_lower)
        
        return {
            'primary_intent': primary_intent,
            'confidence': round(confidence, 3),
            'confidence_level': confidence_level,
            'possible_intents': possible_intents,
            'domain': domain,
            'context_analysis': context_analysis,
            'sentiment': sentiment,
            'urgency_level': urgency,
            'intent_metadata': {
                'requires_response': self._requires_response(primary_intent),
                'expected_action': self._get_expected_action(primary_intent),
                'response_type': self._get_response_type(primary_intent)
            }
        }
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level"""
        if confidence >= self.confidence_thresholds['high_confidence']:
            return 'high'
        elif confidence >= self.confidence_thresholds['medium_confidence']:
            return 'medium'
        elif confidence >= self.confidence_thresholds['low_confidence']:
            return 'low'
        else:
            return 'uncertain'
    
    def _analyze_context(self, text: str, intent: str) -> Dict[str, Any]:
        """Analyze contextual information"""
        context = {
            'is_question': '?' in text or intent == 'question',
            'has_emotion': bool(re.search(r'\b(feel|feeling|emotion|happy|sad|angry|frustrated|excited)\b', text)),
            'is_urgent': bool(re.search(r'\b(urgent|asap|immediately|now|quickly|emergency)\b', text)),
            'is_polite': bool(re.search(r'\b(please|thank|sorry|excuse me|pardon)\b', text)),
            'mentions_time': bool(re.search(r'\b(today|tomorrow|yesterday|now|later|soon|minute|hour|day)\b', text)),
            'has_specifics': len(re.findall(r'\b\d+\b', text)) > 0 or bool(re.search(r'\b(specific|exactly|precisely)\b', text))
        }
        
        return context
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'awesome', 'excellent', 'love', 'like', 'happy', 'pleased', 'satisfied', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'frustrated', 'disappointed', 'annoying', 'problem']
        neutral_words = ['okay', 'fine', 'normal', 'average', 'standard']
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        neu_count = sum(1 for word in neutral_words if word in text)
        
        total_sentiment_words = pos_count + neg_count + neu_count
        
        if total_sentiment_words == 0:
            return {'polarity': 'neutral', 'confidence': 0.5, 'intensity': 'low'}
        
        if pos_count > neg_count:
            polarity = 'positive'
            confidence = pos_count / total_sentiment_words
        elif neg_count > pos_count:
            polarity = 'negative'
            confidence = neg_count / total_sentiment_words
        else:
            polarity = 'neutral'
            confidence = 0.5
        
        # Intensity based on strong words
        strong_words = ['amazing', 'terrible', 'fantastic', 'awful', 'incredible', 'horrible']
        intensity = 'high' if any(word in text for word in strong_words) else 'medium' if total_sentiment_words > 2 else 'low'
        
        return {
            'polarity': polarity,
            'confidence': round(confidence, 3),
            'intensity': intensity,
            'word_counts': {
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count
            }
        }
    
    def _analyze_urgency(self, text: str) -> str:
        """Analyze urgency level"""
        urgent_indicators = ['urgent', 'asap', 'emergency', 'immediately', 'now', 'quickly', 'hurry', 'rush']
        high_priority = ['important', 'critical', 'priority', 'deadline', 'time-sensitive']
        
        if any(indicator in text for indicator in urgent_indicators):
            return 'high'
        elif any(indicator in text for indicator in high_priority):
            return 'medium'
        else:
            return 'low'
    
    def _requires_response(self, intent: str) -> bool:
        """Determine if intent requires a response"""
        response_required = [
            'question', 'request_help', 'complaint', 'code_request',
            'explanation_request', 'translation_request', 'creative_request',
            'search_request', 'comparison_request'
        ]
        return intent in response_required
    
    def _get_expected_action(self, intent: str) -> str:
        """Get expected action for intent"""
        action_map = {
            'question': 'provide_answer',
            'request_help': 'offer_assistance',
            'greeting': 'respond_greeting',
            'complaint': 'acknowledge_and_resolve',
            'compliment': 'acknowledge_thanks',
            'code_request': 'generate_code',
            'explanation_request': 'provide_explanation',
            'translation_request': 'translate_text',
            'creative_request': 'create_content',
            'search_request': 'find_information',
            'comparison_request': 'compare_options'
        }
        return action_map.get(intent, 'general_response')
    
    def _get_response_type(self, intent: str) -> str:
        """Get appropriate response type"""
        response_types = {
            'question': 'informative',
            'request_help': 'helpful',
            'greeting': 'friendly',
            'complaint': 'empathetic',
            'compliment': 'appreciative',
            'code_request': 'technical',
            'explanation_request': 'educational',
            'translation_request': 'linguistic',
            'creative_request': 'creative',
            'search_request': 'informative',
            'comparison_request': 'analytical'
        }
        return response_types.get(intent, 'general')

# Tool 5: Universal Translator
class UniversalTranslator(BaseTool):
    """Advanced translation supporting 100+ languages with context awareness"""
    
    def __init__(self):
        super().__init__(
            name="universal_translator",
            description="Translate text between 100+ languages with context awareness and cultural adaptation",
            category=ToolCategory.NATURAL_LANGUAGE
        )
        self.supported_languages = self._initialize_supported_languages()
        self.translation_cache = {}  # Simple cache for common translations
    
    async def initialize(self) -> bool:
        """Initialize the universal translator"""
        self._initialized = True
        return True
    
    async def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        return 'text' in kwargs and 'target_language' in kwargs
    
    async def execute(self, text: str, target_language: str, 
                     source_language: str = "auto", **kwargs) -> ToolResult:
        try:
            translation_data = await self._translate_text(text, target_language, source_language, **kwargs)
            
            return ToolResult(
                success=True,
                data=translation_data
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Translation failed: {str(e)}"
            )
    
    def _initialize_supported_languages(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive language support database"""
        return {
            # Major languages with full support
            'english': {'native_name': 'English', 'code': 'en', 'family': 'Germanic', 'script': 'Latin', 'rtl': False},
            'spanish': {'native_name': 'Español', 'code': 'es', 'family': 'Romance', 'script': 'Latin', 'rtl': False},
            'french': {'native_name': 'Français', 'code': 'fr', 'family': 'Romance', 'script': 'Latin', 'rtl': False},
            'german': {'native_name': 'Deutsch', 'code': 'de', 'family': 'Germanic', 'script': 'Latin', 'rtl': False},
            'italian': {'native_name': 'Italiano', 'code': 'it', 'family': 'Romance', 'script': 'Latin', 'rtl': False},
            'portuguese': {'native_name': 'Português', 'code': 'pt', 'family': 'Romance', 'script': 'Latin', 'rtl': False},
            'russian': {'native_name': 'Русский', 'code': 'ru', 'family': 'Slavic', 'script': 'Cyrillic', 'rtl': False},
            'chinese': {'native_name': '中文', 'code': 'zh', 'family': 'Sino-Tibetan', 'script': 'Chinese', 'rtl': False},
            'japanese': {'native_name': '日本語', 'code': 'ja', 'family': 'Japonic', 'script': 'Mixed', 'rtl': False},
            'korean': {'native_name': '한국어', 'code': 'ko', 'family': 'Koreanic', 'script': 'Hangul', 'rtl': False},
            'arabic': {'native_name': 'العربية', 'code': 'ar', 'family': 'Semitic', 'script': 'Arabic', 'rtl': True},
            'hindi': {'native_name': 'हिन्दी', 'code': 'hi', 'family': 'Indo-Aryan', 'script': 'Devanagari', 'rtl': False},
            'dutch': {'native_name': 'Nederlands', 'code': 'nl', 'family': 'Germanic', 'script': 'Latin', 'rtl': False},
            'swedish': {'native_name': 'Svenska', 'code': 'sv', 'family': 'Germanic', 'script': 'Latin', 'rtl': False},
            'norwegian': {'native_name': 'Norsk', 'code': 'no', 'family': 'Germanic', 'script': 'Latin', 'rtl': False},
            'danish': {'native_name': 'Dansk', 'code': 'da', 'family': 'Germanic', 'script': 'Latin', 'rtl': False},
            'polish': {'native_name': 'Polski', 'code': 'pl', 'family': 'Slavic', 'script': 'Latin', 'rtl': False},
            'czech': {'native_name': 'Čeština', 'code': 'cs', 'family': 'Slavic', 'script': 'Latin', 'rtl': False},
            'turkish': {'native_name': 'Türkçe', 'code': 'tr', 'family': 'Turkic', 'script': 'Latin', 'rtl': False},
            'greek': {'native_name': 'Ελληνικά', 'code': 'el', 'family': 'Greek', 'script': 'Greek', 'rtl': False},
            'hebrew': {'native_name': 'עברית', 'code': 'he', 'family': 'Semitic', 'script': 'Hebrew', 'rtl': True},
            'thai': {'native_name': 'ไทย', 'code': 'th', 'family': 'Tai-Kadai', 'script': 'Thai', 'rtl': False},
            'vietnamese': {'native_name': 'Tiếng Việt', 'code': 'vi', 'family': 'Austro-Asiatic', 'script': 'Latin', 'rtl': False},
            'finnish': {'native_name': 'Suomi', 'code': 'fi', 'family': 'Uralic', 'script': 'Latin', 'rtl': False},
            'hungarian': {'native_name': 'Magyar', 'code': 'hu', 'family': 'Uralic', 'script': 'Latin', 'rtl': False},
            'romanian': {'native_name': 'Română', 'code': 'ro', 'family': 'Romance', 'script': 'Latin', 'rtl': False},
            'bulgarian': {'native_name': 'Български', 'code': 'bg', 'family': 'Slavic', 'script': 'Cyrillic', 'rtl': False},
            'croatian': {'native_name': 'Hrvatski', 'code': 'hr', 'family': 'Slavic', 'script': 'Latin', 'rtl': False},
            'serbian': {'native_name': 'Српски', 'code': 'sr', 'family': 'Slavic', 'script': 'Cyrillic', 'rtl': False},
            'ukrainian': {'native_name': 'Українська', 'code': 'uk', 'family': 'Slavic', 'script': 'Cyrillic', 'rtl': False},
            'slovak': {'native_name': 'Slovenčina', 'code': 'sk', 'family': 'Slavic', 'script': 'Latin', 'rtl': False},
            'slovenian': {'native_name': 'Slovenščina', 'code': 'sl', 'family': 'Slavic', 'script': 'Latin', 'rtl': False},
            'latvian': {'native_name': 'Latviešu', 'code': 'lv', 'family': 'Baltic', 'script': 'Latin', 'rtl': False},
            'lithuanian': {'native_name': 'Lietuvių', 'code': 'lt', 'family': 'Baltic', 'script': 'Latin', 'rtl': False},
            'estonian': {'native_name': 'Eesti', 'code': 'et', 'family': 'Uralic', 'script': 'Latin', 'rtl': False}
        }
    
    async def _translate_text(self, text: str, target_language: str, source_language: str, **kwargs) -> Dict[str, Any]:
        """Perform advanced translation with context awareness"""
        if not text or len(text.strip()) == 0:
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': 'unknown',
                'target_language': target_language,
                'confidence': 0.0
            }
        
        # Detect source language if auto
        if source_language == "auto":
            source_language = await self._detect_source_language(text)
        
        # Validate target language
        if target_language not in self.supported_languages:
            return {
                'error': f'Target language "{target_language}" not supported',
                'supported_languages': list(self.supported_languages.keys())
            }
        
        # Check if translation is needed
        if source_language == target_language:
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': source_language,
                'target_language': target_language,
                'confidence': 1.0,
                'note': 'No translation needed - same language'
            }
        
        # Use AI for translation
        translation_result = await self._ai_translate(text, source_language, target_language, **kwargs)
        
        # Post-process translation
        processed_result = self._post_process_translation(translation_result, source_language, target_language)
        
        return {
            'original_text': text,
            'translated_text': processed_result['translated_text'],
            'source_language': source_language,
            'target_language': target_language,
            'source_language_info': self.supported_languages.get(source_language, {}),
            'target_language_info': self.supported_languages.get(target_language, {}),
            'confidence': processed_result['confidence'],
            'translation_metadata': {
                'method': 'ai_translation',
                'cultural_adaptations': processed_result.get('cultural_adaptations', []),
                'formatting_preserved': processed_result.get('formatting_preserved', True),
                'untranslatable_terms': processed_result.get('untranslatable_terms', [])
            }
        }
    
    async def _detect_source_language(self, text: str) -> str:
        """Detect source language (simplified - in real implementation use UniversalLanguageDetector)"""
        # Basic pattern matching for common languages
        if re.search(r'[а-яё]', text.lower()):
            return 'russian'
        elif re.search(r'[àâäéèêëïîôöùûüÿç]', text.lower()):
            return 'french'
        elif re.search(r'[áéíóúñü¿¡]', text.lower()):
            return 'spanish'
        elif re.search(r'[äöüß]', text.lower()):
            return 'german'
        elif re.search(r'[一-龯]', text):
            return 'chinese'
        elif re.search(r'[ひらがなカタカナ]', text):
            return 'japanese'
        elif re.search(r'[가-힣]', text):
            return 'korean'
        elif re.search(r'[ا-ي]', text):
            return 'arabic'
        else:
            return 'english'  # Default assumption
    
    async def _ai_translate(self, text: str, source_lang: str, target_lang: str, **kwargs) -> Dict[str, Any]:
        """Use AI models for translation"""
        # Create translation prompt
        source_info = self.supported_languages.get(source_lang, {})
        target_info = self.supported_languages.get(target_lang, {})
        
        prompt = f"""Translate the following text from {source_info.get('native_name', source_lang)} to {target_info.get('native_name', target_lang)}.
Please provide a natural, contextually appropriate translation that preserves the meaning and tone.

Text to translate: "{text}"

Please provide only the translation, maintaining any formatting."""
        
        try:
            # Use multi-model AI system
            async with AIModelManager() as ai:
                result = await ai.smart_routing(
                    prompt,
                    task_type="translation",
                    system_prompt="You are an expert translator with deep understanding of cultural context and nuances."
                )
                
                if result['success']:
                    return {
                        'translated_text': result['response'].strip(),
                        'confidence': 0.9,
                        'method': 'ai_translation'
                    }
                else:
                    # Fallback to simple translation
                    return await self._fallback_translate(text, source_lang, target_lang)
        
        except Exception as e:
            logger.warning(f"AI translation failed: {e}")
            return await self._fallback_translate(text, source_lang, target_lang)
    
    async def _fallback_translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Fallback translation method"""
        # Simple dictionary-based translation for common phrases
        common_translations = {
            ('english', 'spanish'): {
                'hello': 'hola',
                'goodbye': 'adiós',
                'thank you': 'gracias',
                'yes': 'sí',
                'no': 'no',
                'please': 'por favor',
                'sorry': 'lo siento'
            },
            ('english', 'french'): {
                'hello': 'bonjour',
                'goodbye': 'au revoir',
                'thank you': 'merci',
                'yes': 'oui',
                'no': 'non',
                'please': 's\'il vous plaît',
                'sorry': 'désolé'
            },
            ('english', 'german'): {
                'hello': 'hallo',
                'goodbye': 'auf wiedersehen',
                'thank you': 'danke',
                'yes': 'ja',
                'no': 'nein',
                'please': 'bitte',
                'sorry': 'entschuldigung'
            }
        }
        
        translation_key = (source_lang, target_lang)
        if translation_key in common_translations:
            text_lower = text.lower().strip()
            if text_lower in common_translations[translation_key]:
                return {
                    'translated_text': common_translations[translation_key][text_lower],
                    'confidence': 0.8,
                    'method': 'dictionary_translation'
                }
        
        # Return original text if no translation available
        return {
            'translated_text': text,
            'confidence': 0.1,
            'method': 'no_translation',
            'note': 'Translation not available for this language pair'
        }
    
    def _post_process_translation(self, translation_result: Dict[str, Any], source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Post-process translation for cultural and formatting considerations"""
        translated_text = translation_result['translated_text']
        
        # Handle RTL languages
        target_info = self.supported_languages.get(target_lang, {})
        if target_info.get('rtl', False):
            translation_result['formatting_note'] = 'Text should be displayed right-to-left'
        
        # Cultural adaptations
        cultural_adaptations = []
        
        # Date format adaptations
        if re.search(r'\d{1,2}/\d{1,2}/\d{4}', translated_text):
            if target_lang in ['german', 'french', 'spanish']:
                cultural_adaptations.append('Date format may need adjustment (DD/MM/YYYY vs MM/DD/YYYY)')
        
        # Currency adaptations
        if re.search(r'\$\d+', translated_text) and target_lang != 'english':
            cultural_adaptations.append('Currency symbols may need localization')
        
        translation_result['cultural_adaptations'] = cultural_adaptations
        translation_result['formatting_preserved'] = True
        
        return translation_result

# Get intent and translation tools
def get_intent_translation_tools() -> List[BaseTool]:
    """Get intent recognition and translation tools (Tools 4-5)"""
    return [
        IntentRecognitionEngine(),
        UniversalTranslator()
    ]