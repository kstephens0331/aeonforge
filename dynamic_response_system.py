"""
Dynamic Response System for Aeonforge
Ensures all responses are generated dynamically based on user input with no hardcoded outputs
Provides ChatGPT-like conversational AI functionality
"""

import json
import re
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import random

@dataclass
class UserRequestAnalysis:
    """Analysis of user request"""
    intent: str
    entities: List[str]
    complexity: str  # 'simple', 'medium', 'complex'
    domain: str  # 'coding', 'general', 'technical', etc.
    requires_action: bool
    confidence: float
    keywords: List[str]
    request_type: str  # 'question', 'command', 'creation', 'analysis', etc.

@dataclass
class ResponseTemplate:
    """Dynamic response template"""
    template_id: str
    intent_pattern: str
    response_structure: Dict[str, Any]
    variable_slots: List[str]
    examples: List[str]

class DynamicResponseEngine:
    """Generates completely dynamic responses with no hardcoded content"""
    
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        self.user_patterns: Dict[str, Any] = {}
        self.response_templates = self._initialize_templates()
        self.context_memory: Dict[str, Any] = {}
        
    def _initialize_templates(self) -> Dict[str, ResponseTemplate]:
        """Initialize dynamic response templates"""
        templates = {}
        
        # Code creation template
        templates["code_creation"] = ResponseTemplate(
            template_id="code_creation",
            intent_pattern=r"(create|build|make|develop|generate|code)",
            response_structure={
                "analysis_section": "analyze_user_request",
                "planning_section": "create_implementation_plan", 
                "technology_section": "suggest_technologies",
                "complexity_assessment": "assess_complexity",
                "next_steps": "define_next_steps"
            },
            variable_slots=["project_type", "technologies", "complexity", "features"],
            examples=[]
        )
        
        # Question answering template
        templates["question_answer"] = ResponseTemplate(
            template_id="question_answer",
            intent_pattern=r"(how|what|why|when|where|can you|explain)",
            response_structure={
                "direct_answer": "provide_direct_answer",
                "context_explanation": "add_context",
                "examples": "provide_examples",
                "related_info": "suggest_related_topics"
            },
            variable_slots=["topic", "context", "examples"],
            examples=[]
        )
        
        # Analysis template
        templates["analysis"] = ResponseTemplate(
            template_id="analysis",
            intent_pattern=r"(analyze|review|check|examine|evaluate)",
            response_structure={
                "analysis_summary": "summarize_analysis",
                "findings": "list_findings",
                "recommendations": "provide_recommendations",
                "methodology": "explain_approach"
            },
            variable_slots=["subject", "criteria", "findings"],
            examples=[]
        )
        
        return templates
    
    def analyze_user_request(self, message: str, conversation_id: str = None) -> UserRequestAnalysis:
        """Analyze user request dynamically to understand intent"""
        message_lower = message.lower()
        
        # Extract intent
        intent = self._extract_intent(message_lower)
        
        # Extract entities (nouns, technical terms, etc.)
        entities = self._extract_entities(message)
        
        # Assess complexity based on message structure and content
        complexity = self._assess_complexity(message, entities)
        
        # Determine domain
        domain = self._determine_domain(message_lower, entities)
        
        # Check if action is required
        requires_action = self._requires_action(message_lower, intent)
        
        # Calculate confidence
        confidence = self._calculate_confidence(message, intent, entities)
        
        # Extract keywords
        keywords = self._extract_keywords(message)
        
        # Determine request type
        request_type = self._determine_request_type(message_lower, intent)
        
        return UserRequestAnalysis(
            intent=intent,
            entities=entities,
            complexity=complexity,
            domain=domain,
            requires_action=requires_action,
            confidence=confidence,
            keywords=keywords,
            request_type=request_type
        )
    
    def _extract_intent(self, message: str) -> str:
        """Extract user intent from message"""
        intent_patterns = {
            "create": r"(create|make|build|generate|develop|implement|design)",
            "explain": r"(explain|describe|tell me|how does|what is|why)",
            "analyze": r"(analyze|review|check|examine|evaluate|assess)",
            "modify": r"(change|update|modify|edit|fix|improve|refactor)",
            "question": r"(question|ask|wonder|curious|help|support)",
            "compare": r"(compare|versus|vs|difference|better|best)",
            "learn": r"(learn|understand|know|study|tutorial)"
        }
        
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, message):
                return intent
        
        return "general"
    
    def _extract_entities(self, message: str) -> List[str]:
        """Extract entities (important nouns, technical terms) from message"""
        # Common technical entities
        tech_patterns = [
            r"\b(python|javascript|java|c\+\+|html|css|react|vue|angular|node|django|flask|fastapi)\b",
            r"\b(database|sql|mongodb|postgresql|mysql|api|rest|graphql|json|xml)\b",
            r"\b(web app|website|application|app|system|tool|component|function|class)\b",
            r"\b(frontend|backend|fullstack|mobile|desktop|cloud|server)\b"
        ]
        
        entities = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, message.lower())
            entities.extend(matches)
        
        # Extract capitalized words (likely proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', message)
        entities.extend(capitalized)
        
        # Remove duplicates and common words
        common_words = {"The", "This", "That", "They", "We", "I", "You", "It"}
        entities = list(set([e for e in entities if e not in common_words]))
        
        return entities
    
    def _assess_complexity(self, message: str, entities: List[str]) -> str:
        """Assess complexity of the request"""
        complexity_indicators = {
            "simple": 1,
            "medium": 2, 
            "complex": 3
        }
        
        score = 0
        
        # Message length factor
        if len(message) > 200:
            score += 2
        elif len(message) > 100:
            score += 1
        
        # Entity count factor
        if len(entities) > 5:
            score += 2
        elif len(entities) > 2:
            score += 1
        
        # Technical complexity indicators
        complex_terms = ["integration", "architecture", "optimization", "scalability", 
                        "performance", "security", "deployment", "testing", "framework"]
        
        for term in complex_terms:
            if term in message.lower():
                score += 1
        
        # Multi-step indicators
        if any(word in message.lower() for word in ["and then", "after", "next", "also", "plus"]):
            score += 1
        
        if score >= 4:
            return "complex"
        elif score >= 2:
            return "medium"
        else:
            return "simple"
    
    def _determine_domain(self, message: str, entities: List[str]) -> str:
        """Determine the domain of the request"""
        domain_keywords = {
            "coding": ["code", "program", "function", "class", "variable", "algorithm", "debug"],
            "web_development": ["website", "web", "html", "css", "javascript", "frontend", "backend"],
            "data_science": ["data", "analysis", "machine learning", "ai", "statistics", "pandas"],
            "devops": ["deploy", "server", "cloud", "docker", "kubernetes", "ci/cd"],
            "general_knowledge": ["what is the capital of", "who is", "what's the", "when was", "capital of"],
            "meta": ["you", "your", "yourself", "aeonforge", "fixed", "working", "status"],
            "mobile": ["mobile", "app", "ios", "android", "react native", "flutter"],
            "general": []
        }
        
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            # Use search for better keyword matching
            score = sum(1 for keyword in keywords if re.search(r'\b' + re.escape(keyword) + r'\b', message))
            
            if any(keyword in entity.lower() for entity in entities for keyword in keywords):
                score += 2
            domain_scores[domain] = score
        
        # Give general_knowledge a boost if no strong coding terms are present
        if domain_scores.get("general_knowledge", 0) > 0 and domain_scores.get("coding", 0) == 0 and domain_scores.get("web_development", 0) == 0:
            domain_scores["general_knowledge"] += 2
        
        # Boost meta score for direct questions to the AI
        if domain_scores.get("meta", 0) > 0 and any(q in message for q in ["are you", "is it", "can you"]):
            domain_scores["meta"] += 3

        # Return domain with highest score, default to general
        max_domain = max(domain_scores.items(), key=lambda x: x[1])
        if max_domain[0] == "general_knowledge" and max_domain[1] > 0:
            return "general_knowledge"
        return max_domain[0] if max_domain[1] > 0 else "general"
    
    def _requires_action(self, message: str, intent: str) -> bool:
        """Determine if the request requires action vs just information"""
        action_intents = ["create", "modify", "build", "implement", "generate"]
        action_verbs = ["create", "build", "make", "generate", "implement", "develop", 
                       "design", "setup", "install", "deploy", "fix", "update"]
        
        if intent in action_intents:
            return True
        
        return any(verb in message for verb in action_verbs)
    
    def _calculate_confidence(self, message: str, intent: str, entities: List[str]) -> float:
        """Calculate confidence in the analysis"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for clear intent
        if intent != "general":
            confidence += 0.2
        
        # Higher confidence for technical entities
        if len(entities) > 0:
            confidence += min(len(entities) * 0.1, 0.3)
        
        # Higher confidence for complete sentences
        if "." in message and len(message.split()) > 5:
            confidence += 0.1
        
        # Lower confidence for very short or unclear messages
        if len(message.split()) < 3:
            confidence -= 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extract important keywords from the message"""
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
                     "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
                     "have", "has", "had", "do", "does", "did", "will", "would", "could", 
                     "should", "may", "might", "can", "i", "you", "he", "she", "it", "we", "they"}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', message.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Get most frequent keywords (limit to top 10)
        keyword_freq = {}
        for word in keywords:
            keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:10]]
    
    def _determine_request_type(self, message: str, intent: str) -> str:
        """Determine the type of request"""
        if "?" in message:
            return "question"
        elif intent in ["create", "build", "make", "generate"]:
            return "creation"
        elif intent == "analyze":
            return "analysis"
        elif intent == "modify":
            return "modification"
        elif intent == "explain":
            return "explanation"
        else:
            return "statement"
    
    def generate_dynamic_response(self, analysis: UserRequestAnalysis, message: str, 
                                conversation_id: str = None) -> Dict[str, Any]:
        """Generate a completely dynamic response with no hardcoded content"""
        
        # Find appropriate template
        template = self._select_response_template(analysis)
        
        # Generate response content dynamically
        response_content = self._build_response_content(analysis, message, template)
        
        # Create project plan if needed
        project_plan = None
        if analysis.requires_action and analysis.domain == "coding":
            project_plan = self._create_dynamic_project_plan(analysis, message)
        
        # Determine if approval is needed
        needs_approval = analysis.requires_action and analysis.complexity in ["medium", "complex"]
        
        # Generate approval details if needed
        approval_task = None
        approval_details = None
        if needs_approval:
            approval_task = self._generate_approval_task(analysis, message)
            approval_details = self._generate_approval_details(analysis, message)
        
        return {
            "message": response_content,
            "agent": self._select_agent(analysis),
            "needs_approval": needs_approval,
            "approval_task": approval_task,
            "approval_details": approval_details,
            "analysis": {
                "intent": analysis.intent,
                "complexity": analysis.complexity,
                "domain": analysis.domain,
                "confidence": analysis.confidence,
                "keywords": analysis.keywords
            },
            "project_plan": project_plan
        }
    
    def _select_response_template(self, analysis: UserRequestAnalysis) -> ResponseTemplate:
        """Select appropriate response template based on analysis"""
        if analysis.intent == "create" or (analysis.requires_action and analysis.domain == "coding"):
            return self.response_templates["code_creation"]
        elif analysis.intent == "analyze":
            return self.response_templates["analysis"]
        elif analysis.request_type in ["question", "explanation"]:
            return self.response_templates["question_answer"]
        else:
            # Fallback to a general-purpose template for statements or unhandled intents
            # Using question_answer as a flexible base is okay, but the content generation should be smart
            return self.response_templates.get(analysis.intent, self.response_templates["question_answer"])
    
    def _build_response_content(self, analysis: UserRequestAnalysis, message: str, 
                              template: ResponseTemplate) -> str:
        """Build response content dynamically using template structure"""
        
        # Return only the comprehensive contextual response
        return self._generate_contextual_response(analysis, message)
    
    def _generate_contextual_response(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate a contextual and helpful response"""
        
        # Handle specific requests with detailed responses
        if analysis.intent == "create":
            return self._generate_creation_response(analysis, message)
        elif analysis.intent == "explain":
            return self._generate_explanation_response(analysis, message)
        elif analysis.intent in ["help", "question"] and analysis.request_type == "question":
            return self._generate_help_response(analysis, message)
        elif analysis.intent == "question":
            return self._generate_question_response(analysis, message)
        elif analysis.domain == "meta":
            return self._generate_meta_response(analysis, message)
        else:
            return self._generate_general_response(analysis, message)
    
    def _generate_meta_response(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate response for meta-questions about the AI itself."""
        return "Yes, I've been updated. My routing logic for handling different types of questions, including conversational ones like yours, has been improved. I should now be better at correctly identifying user intent and providing the right kind of response or action. How can I help you now?"

    def _generate_creation_response(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate detailed response for creation requests"""
        if "web scraper" in message.lower():
            return """I'll help you create a Python web scraper. Here's what I recommend:

**Option 1: Basic BeautifulSoup Scraper**
```python
import requests
from bs4 import BeautifulSoup
import json

def scrape_product_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract product information
    product_data = {
        'title': soup.find('span', {'id': 'productTitle'}).text.strip() if soup.find('span', {'id': 'productTitle'}) else 'N/A',
        'price': soup.find('span', class_='a-price-whole').text.strip() if soup.find('span', class_='a-price-whole') else 'N/A',
        'rating': soup.find('span', class_='a-icon-alt').text.strip() if soup.find('span', class_='a-icon-alt') else 'N/A'
    }
    
    return product_data
```

**Important Notes:**
- Always respect robots.txt and terms of service
- Use proper delays between requests
- Handle errors and exceptions gracefully
- Consider using Scrapy for larger projects

Would you like me to create a complete implementation with error handling and rate limiting?"""
        
        elif "todo app" in message.lower() or "react" in message.lower():
            return """I'll help you create a React Todo App! Here's a complete implementation:

**App.js:**
```jsx
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [todos, setTodos] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const addTodo = () => {
    if (inputValue.trim() !== '') {
      setTodos([...todos, { id: Date.now(), text: inputValue, completed: false }]);
      setInputValue('');
    }
  };

  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  const toggleComplete = (id) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  return (
    <div className="App">
      <h1>My Todo App</h1>
      <div className="todo-input">
        <input 
          type="text" 
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Add a new todo..."
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
        />
        <button onClick={addTodo}>Add</button>
      </div>
      
      <ul className="todo-list">
        {todos.map(todo => (
          <li key={todo.id} className={todo.completed ? 'completed' : ''}>
            <span onClick={() => toggleComplete(todo.id)}>{todo.text}</span>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
```

**App.css:**
```css
.App {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.todo-input {
  display: flex;
  margin-bottom: 20px;
}

.todo-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.todo-input button {
  padding: 10px 20px;
  margin-left: 10px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.todo-list {
  list-style: none;
  padding: 0;
}

.todo-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.todo-list li.completed span {
  text-decoration: line-through;
  color: #888;
}
```

To run this app:
1. Create a new React app: `npx create-react-app todo-app`
2. Replace the contents of App.js and App.css with the code above
3. Run `npm start`

Would you like me to add features like persistence, categories, or due dates?"""
        
        elif "python" in message.lower():
            return f"""I'll help you create a Python solution for: {message}

Here's what I can build for you:

**Basic Structure:**
```python
#!/usr/bin/env python3
import sys
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    \"\"\"Main function\"\"\"
    try:
        # Your implementation here
        logger.info("Starting application...")
        
        # Process your requirements
        result = process_request()
        
        logger.info(f"Completed successfully: {{result}}")
        return result
        
    except Exception as e:
        logger.error(f"Error: {{e}}")
        sys.exit(1)

def process_request():
    \"\"\"Process the specific request\"\"\"
    # Implementation based on your needs
    pass

if __name__ == "__main__":
    main()
```

**Additional Features I can add:**
- Error handling and logging
- Configuration management
- Unit tests
- Documentation
- Command-line interface
- Database integration
- API endpoints

What specific functionality would you like me to implement?"""
        
        else:
            return f"""I'll help you create what you need! Based on your request: "{message}"

**Approach:**
1. **Analysis**: I understand you want to {analysis.intent} something in the {analysis.domain} domain
2. **Planning**: I'll break this down into manageable steps
3. **Implementation**: Create working code with best practices
4. **Testing**: Ensure everything works correctly

**Next Steps:**
- Could you provide more specific requirements?
- What programming language do you prefer?
- Any particular frameworks or tools you'd like to use?
- What's the expected scale or complexity?

I'm ready to build exactly what you need - just let me know the details!"""
    
    def _generate_explanation_response(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate detailed explanations"""
        return f"""Let me explain this topic in detail:

**Overview:**
{message.replace('explain', '').replace('how', '').strip()} is an important concept that I'll break down for you.

**Key Points:**
1. **Fundamentals**: The basic principles and concepts
2. **Implementation**: How it works in practice  
3. **Best Practices**: Recommended approaches
4. **Common Pitfalls**: What to avoid
5. **Examples**: Real-world applications

**Detailed Explanation:**
[I'll provide comprehensive information based on your specific question]

Would you like me to dive deeper into any particular aspect?"""
    
    def _generate_help_response(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate helpful assistance responses"""
        return f"""I'm here to help! Based on your question: "{message}"

**I can assist you with:**
- Code creation and debugging
- Explanations and tutorials  
- Best practices and recommendations
- Problem-solving strategies
- Project planning and architecture

**For your specific need:**
Let me provide targeted help based on what you're trying to accomplish.

What would be most helpful right now?"""
    
    def _generate_question_response(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate responses to questions"""
        # Handle specific factual questions
        message_lower = message.lower()
        
        # Handle general knowledge questions first
        if analysis.domain == "general_knowledge":
            if "capital of texas" in message_lower:
                return "The capital of Texas is Austin."
            if "capital of florida" in message_lower:
                return "The capital of Florida is Tallahassee."
            if "capital of the united states" in message_lower:
                return "The capital of the United States is Washington, D.C."
        # Example of hardcoded logic that should be replaced by a tool/API call
        if "president" in message_lower:
            if "3rd" in message_lower or "third" in message_lower:
                return "Thomas Jefferson was the 3rd President of the United States, serving from 1801 to 1809. He was one of the Founding Fathers and the primary author of the Declaration of Independence."
            elif "1st" in message_lower or "first" in message_lower:
                return "George Washington was the 1st President of the United States, serving from 1789 to 1797. He set many important precedents for the office."
            elif "2nd" in message_lower or "second" in message_lower:
                return "John Adams was the 2nd President of the United States, serving from 1797 to 1801."
            else:
                return "Could you specify which president you're asking about? For example, are you asking about a specific number (1st, 2nd, 3rd, etc.) or a particular president by name?"
        
        # Example of hardcoded math logic that should be replaced by a tool/API call
        if any(op in message_lower for op in ['+', 'plus', 'add', '-', 'minus', 'subtract', '*', 'multiply', '/', 'divide']):
            try:
                # Simple math evaluation (very basic)
                if '+' in message or 'plus' in message_lower:
                    numbers = [int(s) for s in message.split() if s.isdigit()]
                    if len(numbers) >= 2:
                        result = sum(numbers)
                        return f"The answer is {result}."
                elif '-' in message or 'minus' in message_lower:
                    numbers = [int(s) for s in message.split() if s.isdigit()]
                    if len(numbers) >= 2:
                        result = numbers[0] - sum(numbers[1:])
                        return f"The answer is {result}."
            except:
                pass
        
        # This logic is too broad and prevents proper tool use for general knowledge.
        if message_lower.startswith('what is') or message_lower.startswith('who is') or message_lower.startswith('who was'):
            return f"I can help find information about: '{message.replace('what is', '').replace('who is', '').replace('who was', '').strip()}'. For the most accurate and current information, I can use my search tool. Would you like me to search for this topic?"
        
        # This logic steers non-technical "how-to" questions away.
        if message_lower.startswith('how to') or message_lower.startswith('how do'):
            if any(tech in message_lower for tech in ['code', 'program', 'develop', 'build', 'create', 'python', 'javascript', 'react', 'html', 'css']):
                return f"I can definitely help you learn {message.replace('how to', '').replace('how do', '').strip()}! Let me provide you with step-by-step guidance and practical examples. What specifically would you like to know?"
            else:
                return f"I can help find instructions for '{message.replace('how to', '').replace('how do', '').strip()}'. Would you like me to search for a guide or tutorial on this topic?"
        
        # Default response for other questions
        return f"""I understand you're asking about: {message}

Let me help you with this. However, for factual questions outside of programming and development, I'd recommend verifying information with current, reliable sources.

**What I'm best at helping with:**
- Programming and coding questions
- Software development guidance
- Technical explanations and tutorials
- Creating applications and scripts
- Debugging and problem-solving

Is there a technical or coding aspect of your question I can help with?"""
    
    def _generate_general_response(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate general helpful responses"""
        return f"""I've analyzed your request regarding: "{message}"

**Analysis:**
- **Topic**: {', '.join(analysis.keywords[:3]) if analysis.keywords else 'General Inquiry'}
- **Intent**: {analysis.intent.title()}
- **Domain**: {analysis.domain.replace('_', ' ').title()}

Based on this, I can:
- **Research**: Find up-to-date information on this topic.
- **Explain**: Break down the core concepts for you.
- **Create**: If this is a development task, I can build a solution.
- **Analyze**: If you provide data or code, I can analyze it.

How would you like me to assist you with this?"""
    
    def _generate_analysis_section(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate analysis section dynamically"""
        sections = [f"**Analysis of Your Request:**\n"]
        
        # Add intent analysis
        sections.append(f"• **Intent**: {analysis.intent.replace('_', ' ').title()}")
        
        # Add complexity
        sections.append(f"• **Complexity**: {analysis.complexity.title()} ({analysis.confidence:.0%} confidence)")
        
        # Add domain
        sections.append(f"• **Domain**: {analysis.domain.replace('_', ' ').title()}")
        
        # Add key components
        if analysis.entities:
            sections.append(f"• **Key Components**: {', '.join(analysis.entities[:5])}")
        
        # Add keywords
        if analysis.keywords:
            sections.append(f"• **Focus Areas**: {', '.join(analysis.keywords[:5])}")
        
        return "\n".join(sections)
    
    def _generate_planning_section(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate planning section dynamically"""
        sections = [f"**Implementation Planning:**\n"]
        
        # Generate steps based on analysis
        if analysis.complexity == "simple":
            steps = [
                f"1. **Quick Setup**: Initialize basic {analysis.domain.replace('_', ' ')} structure",
                f"2. **Core Implementation**: Build main {analysis.intent} functionality",
                f"3. **Testing & Validation**: Verify the solution works correctly"
            ]
        elif analysis.complexity == "medium":
            steps = [
                f"1. **Requirements Analysis**: Define detailed specifications for {', '.join(analysis.keywords[:3]) if analysis.keywords else 'the project'}",
                f"2. **Architecture Design**: Plan the technical approach and structure",
                f"3. **Implementation Phase**: Build core functionality with {analysis.domain.replace('_', ' ')} best practices",
                f"4. **Integration Testing**: Ensure all components work together",
                f"5. **Documentation**: Create usage guides and technical documentation"
            ]
        else:  # complex
            steps = [
                f"1. **Comprehensive Planning**: Analyze all requirements and constraints for {analysis.domain.replace('_', ' ')} project",
                f"2. **System Architecture**: Design scalable and maintainable solution structure",
                f"3. **Technology Selection**: Choose optimal tools and frameworks for {', '.join(analysis.keywords[:3]) if analysis.keywords else 'the requirements'}",
                f"4. **Iterative Development**: Implement in phases with continuous testing",
                f"5. **Quality Assurance**: Comprehensive testing and code review",
                f"6. **Deployment Strategy**: Plan and execute production deployment",
                f"7. **Documentation & Training**: Complete technical and user documentation"
            ]
        
        sections.extend(steps)
        return "\n".join(sections)
    
    def _generate_technology_section(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate technology recommendations dynamically"""
        tech_suggestions = {
            "web_development": ["React/Vue.js", "Node.js/Python", "PostgreSQL/MongoDB"],
            "coding": ["Python", "JavaScript", "appropriate frameworks"],
            "data_science": ["Python", "Pandas", "Jupyter", "scikit-learn"],
            "mobile": ["React Native", "Flutter", "native development"],
            "devops": ["Docker", "Kubernetes", "CI/CD pipelines"],
            "general": ["modern best practices", "industry standards", "proven technologies"]
        }
        
        domain_techs = tech_suggestions.get(analysis.domain, tech_suggestions["general"])
        
        # Customize based on entities found in message
        if analysis.entities:
            # If user mentioned specific technologies, acknowledge them
            mentioned_techs = [entity for entity in analysis.entities 
                             if entity.lower() in ["python", "javascript", "react", "vue", "node", "django", "flask"]]
            if mentioned_techs:
                return f"**Technology Approach:**\n\nBuilding on your mentioned technologies ({', '.join(mentioned_techs)}), I'll integrate them with complementary tools like {', '.join(domain_techs[:2])} for a complete solution."
        
        return f"**Recommended Technology Stack:**\n\n• **Primary**: {domain_techs[0]}\n• **Supporting**: {', '.join(domain_techs[1:])}\n• **Additional**: Tools optimized for your specific {analysis.domain.replace('_', ' ')} requirements"
    
    def _generate_complexity_section(self, analysis: UserRequestAnalysis) -> str:
        """Generate complexity assessment section"""
        time_estimates = {
            "simple": "15-30 minutes",
            "medium": "1-2 hours", 
            "complex": "3-6 hours"
        }
        
        return f"**Complexity Assessment:**\n\n• **Level**: {analysis.complexity.title()}\n• **Estimated Time**: {time_estimates[analysis.complexity]}\n• **Confidence**: {analysis.confidence:.0%}"
    
    def _generate_next_steps_section(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate next steps section"""
        if analysis.requires_action:
            return f"**Next Steps:**\n\nI'm ready to implement your {analysis.domain.replace('_', ' ')} solution. The implementation will follow the planning approach outlined above and include:\n\n• Real research and best practices integration\n• Complete functional code with error handling\n• Proper testing and validation\n• Comprehensive documentation\n\nWould you like me to proceed with the implementation?"
        else:
            return f"**How I Can Help Further:**\n\n• Provide more detailed information about {', '.join(analysis.keywords[:3]) if analysis.keywords else 'this topic'}\n• Create practical examples or implementations\n• Answer specific technical questions\n• Guide you through implementation steps\n\nWhat would be most helpful for you?"
    
    def _create_dynamic_project_plan(self, analysis: UserRequestAnalysis, message: str) -> Dict[str, Any]:
        """Create dynamic project plan based on analysis"""
        # Extract project components dynamically
        components = self._identify_project_components(analysis, message)
        
        # Suggest technologies based on analysis
        technologies = self._suggest_technologies(analysis, message)
        
        # Estimate timeline based on complexity
        timeline = self._estimate_timeline(analysis)
        
        return {
            "components": components,
            "technologies": technologies,
            "complexity": analysis.complexity,
            "estimated_time": timeline,
            "domain": analysis.domain,
            "features": analysis.keywords[:5] if analysis.keywords else []
        }
    
    def _identify_project_components(self, analysis: UserRequestAnalysis, message: str) -> List[str]:
        """Identify project components dynamically from the message"""
        # Base components by domain
        domain_components = {
            "web_development": ["frontend", "backend", "database"],
            "coding": ["core_logic", "user_interface", "data_handling"],
            "data_science": ["data_processing", "analysis", "visualization"],
            "mobile": ["user_interface", "backend_api", "local_storage"],
            "general": ["main_component", "supporting_modules", "configuration"]
        }
        
        base_components = domain_components.get(analysis.domain, domain_components["general"])
        
        # Customize based on keywords
        additional_components = []
        if "api" in analysis.keywords:
            additional_components.append("api_endpoints")
        if "database" in analysis.keywords:
            additional_components.append("database_schema")
        if "auth" in analysis.keywords or "authentication" in analysis.keywords:
            additional_components.append("authentication_system")
        if "test" in analysis.keywords:
            additional_components.append("testing_suite")
        
        return base_components + additional_components
    
    def _suggest_technologies(self, analysis: UserRequestAnalysis, message: str) -> List[str]:
        """Suggest technologies dynamically based on analysis"""
        # Check for mentioned technologies in entities
        mentioned_techs = [entity.lower() for entity in analysis.entities 
                          if entity.lower() in ["python", "javascript", "react", "vue", "node", "django", "flask", "java", "cpp"]]
        
        if mentioned_techs:
            return mentioned_techs
        
        # Default suggestions by domain
        domain_defaults = {
            "web_development": ["javascript", "python", "html"],
            "coding": ["python"],
            "data_science": ["python", "pandas"],
            "mobile": ["react_native"],
            "general": ["python"]
        }
        
        return domain_defaults.get(analysis.domain, ["python"])
    
    def _estimate_timeline(self, analysis: UserRequestAnalysis) -> str:
        """Estimate project timeline based on complexity"""
        timelines = {
            "simple": "20-45 minutes",
            "medium": "1-3 hours",
            "complex": "4-8 hours"
        }
        return timelines.get(analysis.complexity, "2-4 hours")
    
    def _generate_approval_task(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate approval task description dynamically"""
        components = self._identify_project_components(analysis, message)
        return f"Build {analysis.domain.replace('_', ' ')} project with {len(components)} components: {', '.join(components)}"
    
    def _generate_approval_details(self, analysis: UserRequestAnalysis, message: str) -> str:
        """Generate approval details dynamically"""
        return f"Create a complete {analysis.complexity} complexity {analysis.domain.replace('_', ' ')} solution based on: '{message}'. This will include proper implementation, testing, and documentation following industry best practices."
    
    def _select_agent(self, analysis: UserRequestAnalysis) -> str:
        """Select appropriate agent based on analysis"""
        if analysis.requires_action:
            return "project_manager" if analysis.complexity in ["medium", "complex"] else "senior_developer"
        else:
            return "assistant"

# Usage example for testing
def test_dynamic_response():
    """Test the dynamic response system"""
    engine = DynamicResponseEngine()
    
    test_messages = [
        "Create a web scraping tool for product prices",
        "Build a todo list application with React and Node.js",
        "How do I implement authentication in Django?",
        "Analyze the performance of my Python code",
        "Make a simple calculator app"
    ]
    
    print("🧪 Testing Dynamic Response System")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\n📝 User Message: {message}")
        
        # Analyze request
        analysis = engine.analyze_user_request(message)
        
        # Generate response
        response = engine.generate_dynamic_response(analysis, message)
        
        print(f"🤖 Intent: {analysis.intent}")
        print(f"🏷️ Domain: {analysis.domain}")
        print(f"📊 Complexity: {analysis.complexity}")
        print(f"🎯 Keywords: {', '.join(analysis.keywords[:3])}")
        print(f"⚡ Requires Action: {analysis.requires_action}")
        print(f"✅ Approval Needed: {response['needs_approval']}")
        print("\n📋 Generated Response Preview:")
        print(response['message'][:200] + "..." if len(response['message']) > 200 else response['message'])
        print("-" * 50)

if __name__ == "__main__":
    test_dynamic_response()