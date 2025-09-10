"""
AeonForge Natural Language Processing Tools - Advanced NLP (Tools 6-15)
Advanced NLP capabilities including sentiment, context, and conversation analysis
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

# Tool 6: Advanced Sentiment Analyzer
class AdvancedSentimentAnalyzer(BaseTool):
    """Comprehensive sentiment analysis with emotion detection and cultural sensitivity"""
    
    def __init__(self):
        super().__init__(
            name="advanced_sentiment_analyzer",
            description="Advanced sentiment analysis with emotion detection, intensity, and cultural context",
            category=ToolCategory.NATURAL_LANGUAGE
        )
        self.emotion_lexicon = self._initialize_emotion_lexicon()
        self.cultural_modifiers = self._initialize_cultural_modifiers()
    
    async def execute(self, text: str, language: str = "auto", 
                     include_emotions: bool = True, **kwargs) -> ToolResult:
        try:
            sentiment_data = await self._analyze_sentiment(text, language, include_emotions)
            
            return ToolResult(
                success=True,
                data=sentiment_data
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Sentiment analysis failed: {str(e)}"
            )
    
    def _initialize_emotion_lexicon(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive emotion and sentiment lexicon"""
        return {
            # Primary emotions with intensity and context
            'joy': {
                'words': ['happy', 'joy', 'delighted', 'ecstatic', 'cheerful', 'glad', 'pleased', 'content', 'elated', 'blissful', 'euphoric', 'overjoyed', 'thrilled', 'excited'],
                'intensity_low': ['content', 'pleased', 'glad'],
                'intensity_medium': ['happy', 'cheerful', 'delighted'],
                'intensity_high': ['ecstatic', 'elated', 'euphoric', 'overjoyed', 'thrilled'],
                'valence': 0.8,
                'arousal': 0.6
            },
            'sadness': {
                'words': ['sad', 'depressed', 'melancholy', 'gloomy', 'dejected', 'mournful', 'sorrowful', 'despondent', 'downhearted', 'blue', 'miserable', 'heartbroken', 'devastated'],
                'intensity_low': ['blue', 'downhearted', 'gloomy'],
                'intensity_medium': ['sad', 'melancholy', 'dejected'],
                'intensity_high': ['depressed', 'devastated', 'heartbroken', 'miserable'],
                'valence': -0.8,
                'arousal': -0.3
            },
            'anger': {
                'words': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'rage', 'outraged', 'livid', 'enraged', 'irate', 'frustrated', 'aggravated', 'incensed'],
                'intensity_low': ['annoyed', 'irritated', 'frustrated'],
                'intensity_medium': ['angry', 'mad', 'aggravated'],
                'intensity_high': ['furious', 'outraged', 'livid', 'enraged', 'incensed'],
                'valence': -0.7,
                'arousal': 0.8
            },
            'fear': {
                'words': ['scared', 'afraid', 'fearful', 'terrified', 'petrified', 'horrified', 'alarmed', 'worried', 'anxious', 'nervous', 'apprehensive', 'panicked'],
                'intensity_low': ['worried', 'nervous', 'apprehensive'],
                'intensity_medium': ['scared', 'afraid', 'anxious'],
                'intensity_high': ['terrified', 'petrified', 'horrified', 'panicked'],
                'valence': -0.6,
                'arousal': 0.7
            },
            'surprise': {
                'words': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'astounded', 'bewildered', 'startled', 'flabbergasted', 'dumbfounded'],
                'intensity_low': ['surprised', 'startled'],
                'intensity_medium': ['amazed', 'astonished', 'bewildered'],
                'intensity_high': ['shocked', 'stunned', 'flabbergasted', 'dumbfounded'],
                'valence': 0.1,
                'arousal': 0.8
            },
            'disgust': {
                'words': ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated', 'appalled', 'grossed', 'repelled'],
                'intensity_low': ['grossed', 'repelled'],
                'intensity_medium': ['disgusted', 'repulsed'],
                'intensity_high': ['revolted', 'sickened', 'nauseated', 'appalled'],
                'valence': -0.7,
                'arousal': 0.5
            },
            'trust': {
                'words': ['trust', 'confident', 'secure', 'assured', 'certain', 'believing', 'faithful', 'loyal', 'devoted'],
                'intensity_low': ['believing', 'faithful'],
                'intensity_medium': ['trust', 'confident', 'secure'],
                'intensity_high': ['assured', 'certain', 'devoted'],
                'valence': 0.6,
                'arousal': 0.2
            },
            'anticipation': {
                'words': ['excited', 'eager', 'hopeful', 'expectant', 'anticipating', 'looking forward', 'optimistic'],
                'intensity_low': ['hopeful', 'expectant'],
                'intensity_medium': ['excited', 'eager', 'optimistic'],
                'intensity_high': ['anticipating', 'looking forward'],
                'valence': 0.5,
                'arousal': 0.6
            }
        }
    
    def _initialize_cultural_modifiers(self) -> Dict[str, Dict[str, float]]:
        """Initialize cultural context modifiers for sentiment interpretation"""
        return {
            'understatement_cultures': {
                'languages': ['english_uk', 'japanese', 'korean'],
                'modifier': 1.3,  # Multiply sentiment intensity
                'note': 'These cultures often understate emotions'
            },
            'expressive_cultures': {
                'languages': ['spanish', 'italian', 'arabic'],
                'modifier': 0.8,  # Reduce sentiment intensity slightly
                'note': 'These cultures often express emotions more openly'
            },
            'context_dependent': {
                'languages': ['chinese', 'japanese', 'korean'],
                'modifier': 1.0,
                'note': 'Sentiment heavily depends on context and relationships'
            }
        }
    
    async def _analyze_sentiment(self, text: str, language: str, include_emotions: bool) -> Dict[str, Any]:
        """Perform comprehensive sentiment analysis"""
        if not text or len(text.strip()) == 0:
            return {
                'text': text,
                'sentiment': 'neutral',
                'confidence': 0.0,
                'polarity': 0.0,
                'emotions': {}
            }
        
        text_clean = text.lower().strip()
        
        # Basic sentiment analysis
        sentiment_scores = self._calculate_sentiment_scores(text_clean)
        
        # Emotion detection if requested
        emotions = {}
        if include_emotions:
            emotions = self._detect_emotions(text_clean)
        
        # Cultural adjustment
        if language != "auto":
            sentiment_scores = self._apply_cultural_adjustment(sentiment_scores, language)
        
        # Advanced analysis
        intensity = self._calculate_intensity(text_clean, emotions)
        subjectivity = self._calculate_subjectivity(text_clean)
        confidence = self._calculate_confidence(sentiment_scores, emotions)
        
        # Determine overall sentiment
        overall_sentiment = self._determine_sentiment(sentiment_scores['polarity'])
        
        return {
            'text': text,
            'sentiment': overall_sentiment,
            'confidence': round(confidence, 3),
            'polarity': round(sentiment_scores['polarity'], 3),
            'subjectivity': round(subjectivity, 3),
            'intensity': round(intensity, 3),
            'emotions': emotions,
            'detailed_scores': {
                'positive_score': round(sentiment_scores['positive'], 3),
                'negative_score': round(sentiment_scores['negative'], 3),
                'neutral_score': round(sentiment_scores['neutral'], 3)
            },
            'language': language,
            'analysis_metadata': {
                'emotion_words_found': sum(len(emotion_data.get('found_words', [])) for emotion_data in emotions.values()),
                'sentiment_indicators': sentiment_scores.get('indicators', 0),
                'cultural_adjustment_applied': language != 'auto'
            }
        }
    
    def _calculate_sentiment_scores(self, text: str) -> Dict[str, Any]:
        """Calculate basic sentiment scores"""
        # Positive indicators
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'perfect',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'delighted', 'thrilled',
            'best', 'better', 'superior', 'outstanding', 'brilliant', 'magnificent', 'spectacular',
            'beautiful', 'gorgeous', 'stunning', 'incredible', 'remarkable', 'extraordinary'
        ]
        
        # Negative indicators
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'dislike', 'despise',
            'angry', 'frustrated', 'annoyed', 'disappointed', 'sad', 'depressed', 'upset',
            'worst', 'worse', 'inferior', 'pathetic', 'useless', 'worthless', 'failure',
            'ugly', 'hideous', 'revolting', 'sickening', 'appalling', 'dreadful'
        ]
        
        # Intensifiers
        intensifiers = ['very', 'extremely', 'incredibly', 'absolutely', 'totally', 'completely', 'utterly']
        
        # Negators
        negators = ['not', 'no', 'never', 'none', 'nobody', 'nothing', 'nowhere', 'neither', "don't", "won't", "can't"]
        
        words = text.split()
        positive_score = 0
        negative_score = 0
        indicator_count = 0
        
        for i, word in enumerate(words):
            # Check for negation
            is_negated = i > 0 and words[i-1] in negators
            
            # Check for intensification
            intensity_multiplier = 1.0
            if i > 0 and words[i-1] in intensifiers:
                intensity_multiplier = 1.5
            
            # Calculate scores
            if word in positive_words:
                score = intensity_multiplier
                if is_negated:
                    negative_score += score
                else:
                    positive_score += score
                indicator_count += 1
            
            elif word in negative_words:
                score = intensity_multiplier
                if is_negated:
                    positive_score += score
                else:
                    negative_score += score
                indicator_count += 1
        
        # Normalize scores
        total_words = len(words)
        if total_words > 0:
            positive_score /= total_words
            negative_score /= total_words
        
        # Calculate polarity
        polarity = positive_score - negative_score
        neutral_score = 1 - abs(polarity)
        
        return {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': neutral_score,
            'polarity': polarity,
            'indicators': indicator_count
        }
    
    def _detect_emotions(self, text: str) -> Dict[str, Any]:
        """Detect specific emotions in text"""
        detected_emotions = {}
        words = text.split()
        
        for emotion_name, emotion_data in self.emotion_lexicon.items():
            found_words = []
            total_intensity = 0
            emotion_count = 0
            
            for word in words:
                if word in emotion_data['words']:
                    found_words.append(word)
                    emotion_count += 1
                    
                    # Determine intensity
                    if word in emotion_data.get('intensity_high', []):
                        total_intensity += 3
                    elif word in emotion_data.get('intensity_medium', []):
                        total_intensity += 2
                    elif word in emotion_data.get('intensity_low', []):
                        total_intensity += 1
                    else:
                        total_intensity += 2  # Default medium intensity
            
            if emotion_count > 0:
                # Calculate emotion score
                avg_intensity = total_intensity / emotion_count
                presence_score = emotion_count / len(words)  # Frequency in text
                
                detected_emotions[emotion_name] = {
                    'score': round(min(presence_score * avg_intensity, 1.0), 3),
                    'intensity': round(avg_intensity, 1),
                    'found_words': found_words,
                    'valence': emotion_data['valence'],
                    'arousal': emotion_data['arousal']
                }
        
        return detected_emotions
    
    def _apply_cultural_adjustment(self, sentiment_scores: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Apply cultural context adjustments to sentiment scores"""
        for culture_type, culture_data in self.cultural_modifiers.items():
            if language in culture_data['languages']:
                modifier = culture_data['modifier']
                
                # Apply modifier to polarity
                sentiment_scores['polarity'] *= modifier
                
                # Ensure bounds
                sentiment_scores['polarity'] = max(-1.0, min(1.0, sentiment_scores['polarity']))
                
                break
        
        return sentiment_scores
    
    def _calculate_intensity(self, text: str, emotions: Dict[str, Any]) -> float:
        """Calculate emotional intensity"""
        # Check for intensity markers
        intensity_markers = {
            'very': 1.5, 'extremely': 2.0, 'incredibly': 1.8, 'absolutely': 1.7,
            'totally': 1.6, 'completely': 1.8, 'utterly': 1.9, 'so': 1.3,
            'really': 1.4, 'quite': 1.2, 'pretty': 1.1, 'rather': 1.1
        }
        
        intensity_score = 1.0
        words = text.split()
        
        for word in words:
            if word in intensity_markers:
                intensity_score = max(intensity_score, intensity_markers[word])
        
        # Factor in emotion intensity
        if emotions:
            avg_emotion_intensity = sum(emotion['intensity'] for emotion in emotions.values()) / len(emotions)
            intensity_score *= (1 + avg_emotion_intensity / 10)
        
        return min(intensity_score, 3.0)  # Cap at 3.0
    
    def _calculate_subjectivity(self, text: str) -> float:
        """Calculate subjectivity (objective vs subjective)"""
        subjective_indicators = [
            'i think', 'i believe', 'in my opinion', 'i feel', 'seems', 'appears',
            'probably', 'maybe', 'perhaps', 'might', 'could', 'would', 'should',
            'beautiful', 'ugly', 'good', 'bad', 'amazing', 'terrible', 'love', 'hate'
        ]
        
        objective_indicators = [
            'according to', 'research shows', 'data indicates', 'studies show',
            'fact', 'evidence', 'proven', 'documented', 'measured', 'calculated'
        ]
        
        subjective_count = sum(1 for indicator in subjective_indicators if indicator in text)
        objective_count = sum(1 for indicator in objective_indicators if indicator in text)
        
        total_indicators = subjective_count + objective_count
        if total_indicators == 0:
            return 0.5  # Neutral
        
        return subjective_count / total_indicators
    
    def _calculate_confidence(self, sentiment_scores: Dict[str, Any], emotions: Dict[str, Any]) -> float:
        """Calculate confidence in sentiment analysis"""
        # Base confidence on number of sentiment indicators
        indicator_confidence = min(sentiment_scores.get('indicators', 0) * 0.1, 0.8)
        
        # Boost confidence if emotions are detected
        emotion_confidence = 0.1 if emotions else 0.0
        
        # Boost confidence for clear polarity
        polarity_confidence = abs(sentiment_scores['polarity']) * 0.2
        
        return min(indicator_confidence + emotion_confidence + polarity_confidence, 1.0)
    
    def _determine_sentiment(self, polarity: float) -> str:
        """Determine overall sentiment label"""
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'

# Tool 7: Context Understanding Engine  
class ContextUnderstandingEngine(BaseTool):
    """Advanced context understanding for maintaining conversation coherence"""
    
    def __init__(self):
        super().__init__(
            name="context_understanding_engine",
            description="Understand and maintain context across conversations and documents",
            category=ToolCategory.NATURAL_LANGUAGE
        )
        self.context_memory = {}
        self.reference_patterns = self._initialize_reference_patterns()
    
    async def execute(self, text: str, conversation_id: str = None, 
                     include_references: bool = True, **kwargs) -> ToolResult:
        try:
            context_data = await self._analyze_context(text, conversation_id, include_references)
            
            return ToolResult(
                success=True,
                data=context_data
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Context analysis failed: {str(e)}"
            )
    
    def _initialize_reference_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting references and context clues"""
        return {
            'temporal_references': [
                r'\b(now|then|before|after|earlier|later|yesterday|today|tomorrow)\b',
                r'\b(first|second|third|next|previous|last|finally)\b',
                r'\b(while|when|during|since|until)\b'
            ],
            'demonstrative_references': [
                r'\b(this|that|these|those|here|there)\b',
                r'\b(above|below|following|preceding)\b',
                r'\b(such|said|aforementioned)\b'
            ],
            'personal_references': [
                r'\b(he|she|it|they|him|her|them)\b',
                r'\b(his|her|its|their|theirs)\b',
                r'\b(himself|herself|itself|themselves)\b'
            ],
            'topic_transitions': [
                r'\b(speaking of|regarding|concerning|about)\b',
                r'\b(by the way|incidentally|meanwhile)\b',
                r'\b(however|but|although|despite)\b',
                r'\b(also|additionally|furthermore|moreover)\b'
            ],
            'comparative_references': [
                r'\b(compared to|versus|rather than|instead of)\b',
                r'\b(similar to|like|unlike|different from)\b',
                r'\b(better|worse|same|equal)\b'
            ]
        }
    
    async def _analyze_context(self, text: str, conversation_id: str, include_references: bool) -> Dict[str, Any]:
        """Analyze context and references in text"""
        if not text or len(text.strip()) == 0:
            return {
                'text': text,
                'context_score': 0.0,
                'references': [],
                'conversation_id': conversation_id
            }
        
        # Initialize conversation memory if needed
        if conversation_id and conversation_id not in self.context_memory:
            self.context_memory[conversation_id] = {
                'messages': [],
                'entities': set(),
                'topics': [],
                'context_stack': []
            }
        
        references = []
        if include_references:
            references = self._extract_references(text)
        
        # Analyze context elements
        context_elements = self._identify_context_elements(text)
        topic_analysis = self._analyze_topic_continuity(text, conversation_id)
        entity_tracking = self._track_entities(text, conversation_id)
        
        # Update conversation memory
        if conversation_id:
            self._update_conversation_memory(conversation_id, text, context_elements, entity_tracking)
        
        # Calculate context coherence score
        context_score = self._calculate_context_score(references, context_elements, conversation_id)
        
        return {
            'text': text,
            'conversation_id': conversation_id,
            'context_score': round(context_score, 3),
            'references': references,
            'context_elements': context_elements,
            'topic_analysis': topic_analysis,
            'entity_tracking': entity_tracking,
            'coherence_indicators': self._get_coherence_indicators(text, conversation_id),
            'context_recommendations': self._generate_context_recommendations(references, context_elements)
        }
    
    def _extract_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract various types of references from text"""
        references = []
        text_lower = text.lower()
        
        for ref_type, patterns in self.reference_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    references.append({
                        'type': ref_type,
                        'text': match.group(),
                        'position': {'start': match.start(), 'end': match.end()},
                        'confidence': 0.8
                    })
        
        # Sort by position
        references.sort(key=lambda x: x['position']['start'])
        return references
    
    def _identify_context_elements(self, text: str) -> Dict[str, Any]:
        """Identify various context elements"""
        elements = {
            'has_questions': bool(re.search(r'\?', text)),
            'has_imperatives': bool(re.search(r'\b(please|help|do|make|create|show)\b', text.lower())),
            'has_conditionals': bool(re.search(r'\b(if|unless|provided|assuming)\b', text.lower())),
            'has_temporal_context': bool(re.search(r'\b(when|before|after|while|during)\b', text.lower())),
            'has_causal_relationships': bool(re.search(r'\b(because|since|due to|as a result)\b', text.lower())),
            'has_comparisons': bool(re.search(r'\b(than|compared|versus|like|similar)\b', text.lower())),
            'sentence_count': len(re.findall(r'[.!?]+', text)),
            'complexity_level': self._assess_complexity(text)
        }
        
        return elements
    
    def _analyze_topic_continuity(self, text: str, conversation_id: str) -> Dict[str, Any]:
        """Analyze topic continuity and transitions"""
        current_topics = self._extract_topics(text)
        
        if conversation_id and conversation_id in self.context_memory:
            previous_topics = self.context_memory[conversation_id].get('topics', [])
            
            # Calculate topic overlap
            if previous_topics:
                last_topics = previous_topics[-1] if previous_topics else []
                overlap = len(set(current_topics) & set(last_topics))
                continuity_score = overlap / max(len(current_topics), len(last_topics), 1)
            else:
                continuity_score = 0.0
            
            return {
                'current_topics': current_topics,
                'previous_topics': previous_topics[-3:] if len(previous_topics) > 0 else [],  # Last 3
                'continuity_score': round(continuity_score, 3),
                'topic_shift_detected': continuity_score < 0.3,
                'new_topics_introduced': list(set(current_topics) - set(last_topics) if previous_topics else current_topics)
            }
        
        return {
            'current_topics': current_topics,
            'previous_topics': [],
            'continuity_score': 1.0,
            'topic_shift_detected': False,
            'new_topics_introduced': current_topics
        }
    
    def _track_entities(self, text: str, conversation_id: str) -> Dict[str, Any]:
        """Track named entities and their references"""
        # Simple entity extraction (in real implementation, use NER)
        entities = {
            'people': re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text),  # Names
            'places': re.findall(r'\b[A-Z][a-z]+(?:ville|town|city|berg|burg)\b', text),  # Places
            'organizations': re.findall(r'\b[A-Z][A-Z]+\b', text),  # Acronyms
            'dates': re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', text),  # Dates
            'numbers': re.findall(r'\b\d+\b', text)  # Numbers
        }
        
        # Update conversation memory
        if conversation_id and conversation_id in self.context_memory:
            memory = self.context_memory[conversation_id]
            for entity_type, entity_list in entities.items():
                memory['entities'].update(entity_list)
        
        return {
            'current_entities': entities,
            'entity_count': sum(len(entity_list) for entity_list in entities.values()),
            'new_entities': self._identify_new_entities(entities, conversation_id)
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text (simplified)"""
        # In a real implementation, this would use more sophisticated topic modeling
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter out common words
        stopwords = {
            'that', 'this', 'with', 'from', 'they', 'been', 'have', 'their',
            'said', 'each', 'which', 'what', 'there', 'then', 'when', 'where',
            'will', 'more', 'some', 'like', 'into', 'him', 'her', 'two', 'its'
        }
        
        content_words = [word for word in words if word not in stopwords]
        
        # Return most frequent words as topics
        word_freq = Counter(content_words)
        return [word for word, count in word_freq.most_common(5)]
    
    def _assess_complexity(self, text: str) -> str:
        """Assess text complexity level"""
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
        
        complex_words = len(re.findall(r'\b\w{8,}\b', text))
        total_words = len(text.split())
        complexity_ratio = complex_words / max(total_words, 1)
        
        if avg_sentence_length > 20 or complexity_ratio > 0.3:
            return 'high'
        elif avg_sentence_length > 15 or complexity_ratio > 0.2:
            return 'medium'
        else:
            return 'low'
    
    def _update_conversation_memory(self, conversation_id: str, text: str, context_elements: Dict, entities: Dict):
        """Update conversation memory with new information"""
        memory = self.context_memory[conversation_id]
        
        # Add message
        memory['messages'].append({
            'text': text,
            'timestamp': asyncio.get_event_loop().time(),
            'context_elements': context_elements
        })
        
        # Keep only last 10 messages
        if len(memory['messages']) > 10:
            memory['messages'] = memory['messages'][-10:]
        
        # Update topics
        current_topics = self._extract_topics(text)
        memory['topics'].append(current_topics)
        
        # Keep only last 5 topic sets
        if len(memory['topics']) > 5:
            memory['topics'] = memory['topics'][-5:]
    
    def _identify_new_entities(self, current_entities: Dict, conversation_id: str) -> Dict[str, List[str]]:
        """Identify entities that are new to the conversation"""
        if not conversation_id or conversation_id not in self.context_memory:
            return current_entities
        
        known_entities = self.context_memory[conversation_id]['entities']
        new_entities = {}
        
        for entity_type, entity_list in current_entities.items():
            new_entities[entity_type] = [entity for entity in entity_list if entity not in known_entities]
        
        return new_entities
    
    def _calculate_context_score(self, references: List[Dict], context_elements: Dict, conversation_id: str) -> float:
        """Calculate overall context coherence score"""
        score = 0.5  # Base score
        
        # Boost for references
        score += len(references) * 0.05
        
        # Boost for context elements
        element_count = sum(1 for v in context_elements.values() if isinstance(v, bool) and v)
        score += element_count * 0.1
        
        # Boost for conversation continuity
        if conversation_id and conversation_id in self.context_memory:
            memory = self.context_memory[conversation_id]
            if len(memory['messages']) > 1:
                score += 0.2  # Bonus for ongoing conversation
        
        return min(score, 1.0)
    
    def _get_coherence_indicators(self, text: str, conversation_id: str) -> Dict[str, Any]:
        """Get indicators of text coherence"""
        return {
            'has_clear_structure': bool(re.search(r'\b(first|second|finally|in conclusion)\b', text.lower())),
            'uses_transitions': bool(re.search(r'\b(however|therefore|meanwhile|furthermore)\b', text.lower())),
            'maintains_topic': conversation_id in self.context_memory if conversation_id else False,
            'appropriate_length': 10 <= len(text.split()) <= 100,
            'clear_intent': bool(re.search(r'[.!?]$', text.strip()))
        }
    
    def _generate_context_recommendations(self, references: List[Dict], context_elements: Dict) -> List[str]:
        """Generate recommendations for improving context clarity"""
        recommendations = []
        
        if not references:
            recommendations.append("Consider adding connecting words to improve flow")
        
        if not context_elements.get('has_questions') and not context_elements.get('has_imperatives'):
            recommendations.append("Text could benefit from clearer intent indicators")
        
        if context_elements.get('complexity_level') == 'high':
            recommendations.append("Consider simplifying sentence structure for better clarity")
        
        return recommendations

# Get advanced NLP tools (6-7 so far, will continue with 8-15)
def get_advanced_nlp_tools() -> List[BaseTool]:
    """Get advanced NLP tools (Tools 6-7)"""
    return [
        AdvancedSentimentAnalyzer(),
        ContextUnderstandingEngine()
    ]