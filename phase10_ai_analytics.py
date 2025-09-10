"""
Aeonforge Phase 10 - Advanced AI Features & Analytics
Multi-Model AI Orchestration, Advanced Analytics, Performance Monitoring, and Intelligent Insights
"""

import os
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import asynccontextmanager
import time
import statistics

# AI and ML imports
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import matplotlib.pyplot as plt
    import seaborn as sns
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    ML_AVAILABLE = True
except ImportError:
    print("Warning: ML libraries not available. Install with: pip install scikit-learn matplotlib seaborn transformers torch")
    ML_AVAILABLE = False

# Database and payment integration
try:
    from phase8_database import get_database_manager, database_session, Base
    from phase9_payments import get_payment_manager, SubscriptionTier
    from sqlalchemy.orm import Mapped, mapped_column
    from sqlalchemy import String, DateTime, Text, Integer, Boolean, JSON, Float
    INTEGRATION_AVAILABLE = True
except ImportError:
    print("Warning: Phase 8/9 integration not available")
    INTEGRATION_AVAILABLE = False

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelType(Enum):
    """AI Model types supported"""
    LANGUAGE_MODEL = "language_model"
    CODE_GENERATOR = "code_generator"
    TEXT_ANALYZER = "text_analyzer"
    IMAGE_GENERATOR = "image_generator"
    EMBEDDING_MODEL = "embedding_model"

class AnalyticsMetric(Enum):
    """Analytics metrics tracked"""
    API_LATENCY = "api_latency"
    MODEL_ACCURACY = "model_accuracy"
    USER_SATISFACTION = "user_satisfaction"
    CODE_QUALITY = "code_quality"
    SYSTEM_PERFORMANCE = "system_performance"

@dataclass
class AIModelConfig:
    """AI Model configuration"""
    name: str
    model_type: AIModelType
    endpoint: str = ""
    api_key: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    enabled: bool = True
    cost_per_token: float = 0.0
    rate_limit: int = 60  # requests per minute

@dataclass
class AnalyticsEvent:
    """Analytics event structure"""
    event_id: str
    user_id: str
    event_type: str
    metric_name: str
    metric_value: float
    metadata: Dict[str, Any]
    timestamp: datetime

# Predefined AI models
AI_MODELS = {
    "gpt-4": AIModelConfig(
        name="GPT-4",
        model_type=AIModelType.LANGUAGE_MODEL,
        endpoint="https://api.openai.com/v1/chat/completions",
        max_tokens=8192,
        temperature=0.7,
        cost_per_token=0.00003
    ),
    "claude-3": AIModelConfig(
        name="Claude-3",
        model_type=AIModelType.LANGUAGE_MODEL,
        endpoint="https://api.anthropic.com/v1/messages",
        max_tokens=4096,
        temperature=0.7,
        cost_per_token=0.000015
    ),
    "codellama": AIModelConfig(
        name="CodeLlama",
        model_type=AIModelType.CODE_GENERATOR,
        endpoint="http://localhost:11434/api/generate",
        max_tokens=4096,
        temperature=0.1,
        cost_per_token=0.0  # Local model
    ),
    "ollama-llama3": AIModelConfig(
        name="Ollama Llama3",
        model_type=AIModelType.LANGUAGE_MODEL,
        endpoint="http://localhost:11434/api/generate",
        max_tokens=4096,
        temperature=0.7,
        cost_per_token=0.0  # Local model
    )
}

if INTEGRATION_AVAILABLE:
    class AIRequest(Base):
        """AI request tracking"""
        __tablename__ = "ai_requests"
        
        id: Mapped[str] = mapped_column(String, primary_key=True)
        user_id: Mapped[str] = mapped_column(String(255), nullable=False)
        model_name: Mapped[str] = mapped_column(String(100), nullable=False)
        request_type: Mapped[str] = mapped_column(String(50), nullable=False)
        prompt: Mapped[str] = mapped_column(Text, nullable=False)
        response: Mapped[Optional[str]] = mapped_column(Text)
        tokens_used: Mapped[int] = mapped_column(Integer, default=0)
        cost: Mapped[float] = mapped_column(Float, default=0.0)
        latency_ms: Mapped[int] = mapped_column(Integer, default=0)
        success: Mapped[bool] = mapped_column(Boolean, default=True)
        error_message: Mapped[Optional[str]] = mapped_column(Text)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        ai_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    class AnalyticsData(Base):
        """Analytics data storage"""
        __tablename__ = "analytics_data"
        
        id: Mapped[str] = mapped_column(String, primary_key=True)
        user_id: Mapped[Optional[str]] = mapped_column(String(255))
        metric_type: Mapped[str] = mapped_column(String(100), nullable=False)
        metric_name: Mapped[str] = mapped_column(String(200), nullable=False)
        metric_value: Mapped[float] = mapped_column(Float, nullable=False)
        aggregation_period: Mapped[str] = mapped_column(String(50), default="daily")  # hourly, daily, weekly, monthly
        recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        ai_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    class ModelPerformance(Base):
        """Model performance tracking"""
        __tablename__ = "model_performance"
        
        id: Mapped[str] = mapped_column(String, primary_key=True)
        model_name: Mapped[str] = mapped_column(String(100), nullable=False)
        performance_metric: Mapped[str] = mapped_column(String(100), nullable=False)
        score: Mapped[float] = mapped_column(Float, nullable=False)
        test_set_size: Mapped[int] = mapped_column(Integer, default=0)
        evaluation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        ai_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

class AdvancedAIOrchestrator:
    """Advanced AI orchestration and analytics system"""
    
    def __init__(self):
        self.models = AI_MODELS.copy()
        self.ml_available = ML_AVAILABLE
        self.integration_available = INTEGRATION_AVAILABLE
        self.embedder = None
        self.tokenizer = None
        self._performance_cache = {}
        
        # Initialize ML models if available
        if self.ml_available:
            self._initialize_ml_models()
    
    def _initialize_ml_models(self):
        """Initialize ML models for analytics"""
        try:
            # Initialize embedding model for semantic analysis
            if torch.cuda.is_available():
                self.embedder = pipeline("feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2", device=0)
            else:
                self.embedder = pipeline("feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2")
                
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.warning(f"ML model initialization failed: {e}")
            self.ml_available = False
    
    async def route_request(self, user_id: str, prompt: str, request_type: str = "chat", 
                          model_preference: str = None, context: Dict = None) -> Dict[str, Any]:
        """Intelligently route AI requests to optimal models"""
        start_time = time.time()
        
        # Determine best model for request
        selected_model = await self._select_optimal_model(prompt, request_type, model_preference, user_id)
        
        if not selected_model:
            return {"error": "No suitable model available", "success": False}
        
        # Check user limits
        usage_allowed = await self._check_user_limits(user_id, selected_model)
        if not usage_allowed["allowed"]:
            return {"error": usage_allowed["reason"], "success": False}
        
        # Generate response
        try:
            response = await self._generate_response(selected_model, prompt, context or {})
            
            # Calculate metrics
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            tokens_used = self._estimate_tokens(prompt + response.get("content", ""))
            cost = self._calculate_cost(selected_model, tokens_used)
            
            # Record request
            await self._record_ai_request(
                user_id=user_id,
                model_name=selected_model,
                request_type=request_type,
                prompt=prompt,
                response=response.get("content", ""),
                tokens_used=tokens_used,
                cost=cost,
                latency_ms=latency_ms,
                success=True
            )
            
            # Record analytics
            await self._record_analytics(user_id, AnalyticsMetric.API_LATENCY, latency_ms)
            
            return {
                "success": True,
                "content": response.get("content", ""),
                "model_used": selected_model,
                "tokens_used": tokens_used,
                "cost": cost,
                "latency_ms": latency_ms,
                "metadata": response.get("metadata", {})
            }
            
        except Exception as e:
            # Record failed request
            await self._record_ai_request(
                user_id=user_id,
                model_name=selected_model,
                request_type=request_type,
                prompt=prompt,
                success=False,
                error_message=str(e),
                latency_ms=int((time.time() - start_time) * 1000)
            )
            
            logger.error(f"AI request failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _select_optimal_model(self, prompt: str, request_type: str, 
                                  model_preference: str, user_id: str) -> Optional[str]:
        """Select the optimal model based on various factors"""
        
        # Use preference if specified and available
        if model_preference and model_preference in self.models:
            if self.models[model_preference].enabled:
                return model_preference
        
        # Analyze prompt to determine best model type
        if request_type == "code_generation" or self._is_code_related(prompt):
            # Prefer code-specific models
            code_models = [name for name, config in self.models.items() 
                          if config.model_type == AIModelType.CODE_GENERATOR and config.enabled]
            if code_models:
                return await self._select_by_performance(code_models, "code_quality")
        
        # For general language tasks
        language_models = [name for name, config in self.models.items() 
                          if config.model_type == AIModelType.LANGUAGE_MODEL and config.enabled]
        
        if language_models:
            return await self._select_by_performance(language_models, "overall_quality")
        
        return None
    
    async def _select_by_performance(self, model_candidates: List[str], metric: str) -> str:
        """Select model based on performance metrics"""
        if not self.integration_available:
            return model_candidates[0] if model_candidates else None
        
        best_model = None
        best_score = -1
        
        for model_name in model_candidates:
            score = await self._get_model_performance_score(model_name, metric)
            if score > best_score:
                best_score = score
                best_model = model_name
        
        return best_model or (model_candidates[0] if model_candidates else None)
    
    async def _get_model_performance_score(self, model_name: str, metric: str) -> float:
        """Get cached or calculated performance score for a model"""
        cache_key = f"{model_name}_{metric}"
        
        if cache_key in self._performance_cache:
            cache_time, score = self._performance_cache[cache_key]
            if datetime.utcnow() - cache_time < timedelta(hours=1):
                return score
        
        if not self.integration_available:
            return 0.7  # Default score
        
        try:
            async with database_session() as session:
                from sqlalchemy import select, func, desc
                
                # Get recent performance data
                stmt = select(func.avg(ModelPerformance.score)).where(
                    ModelPerformance.model_name == model_name,
                    ModelPerformance.performance_metric == metric,
                    ModelPerformance.evaluation_date >= datetime.utcnow() - timedelta(days=7)
                )
                
                result = await session.execute(stmt)
                score = result.scalar() or 0.7
                
                # Cache the result
                self._performance_cache[cache_key] = (datetime.utcnow(), score)
                return score
                
        except Exception as e:
            logger.error(f"Performance score lookup failed: {e}")
            return 0.7
    
    def _is_code_related(self, prompt: str) -> bool:
        """Determine if prompt is code-related"""
        code_keywords = [
            "function", "class", "import", "def ", "var ", "let ", "const ",
            "public class", "private ", "protected ", "async ", "await ",
            "console.log", "print(", "return ", "if ", "for ", "while ",
            "try ", "catch ", "exception", "debug", "test", "unit test",
            "algorithm", "data structure", "api", "database", "sql",
            "html", "css", "javascript", "python", "java", "c++", "react",
            "component", "props", "state", "render", "useEffect", "useState"
        ]
        
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in code_keywords)
    
    async def _check_user_limits(self, user_id: str, model_name: str) -> Dict[str, Any]:
        """Check if user can make request with selected model"""
        if not self.integration_available:
            return {"allowed": True}
        
        try:
            payment_manager = await get_payment_manager()
            limits = await payment_manager.check_usage_limits(user_id, "api_calls_per_day")
            
            if not limits["allowed"]:
                return {"allowed": False, "reason": f"Daily API limit exceeded ({limits['limit']})"}
            
            # Check model-specific limits for premium models
            model_config = self.models.get(model_name)
            if model_config and model_config.cost_per_token > 0:
                # Premium model - check subscription tier
                user = await payment_manager.get_user(user_id)
                if user:
                    tier = SubscriptionTier(user["subscription_tier"])
                    if tier == SubscriptionTier.FREE:
                        return {"allowed": False, "reason": "Premium models require paid subscription"}
            
            return {"allowed": True}
            
        except Exception as e:
            logger.error(f"Limit checking failed: {e}")
            return {"allowed": True}  # Allow on error
    
    async def _generate_response(self, model_name: str, prompt: str, context: Dict) -> Dict[str, Any]:
        """Generate response using selected model"""
        model_config = self.models[model_name]
        
        # Simulate different model responses based on type
        if "gpt" in model_name.lower():
            return await self._call_openai_api(model_config, prompt, context)
        elif "claude" in model_name.lower():
            return await self._call_anthropic_api(model_config, prompt, context)
        elif "ollama" in model_name.lower() or "llama" in model_name.lower():
            return await self._call_ollama_api(model_config, prompt, context)
        else:
            return await self._call_generic_api(model_config, prompt, context)
    
    async def _call_openai_api(self, config: AIModelConfig, prompt: str, context: Dict) -> Dict[str, Any]:
        """Call OpenAI API (simulated)"""
        # In a real implementation, this would call the actual OpenAI API
        response = f"[GPT-4 Response] Based on your request: {prompt[:100]}..., here's a comprehensive solution."
        
        return {
            "content": response,
            "metadata": {
                "model": config.name,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            }
        }
    
    async def _call_anthropic_api(self, config: AIModelConfig, prompt: str, context: Dict) -> Dict[str, Any]:
        """Call Anthropic Claude API (simulated)"""
        response = f"[Claude-3 Response] I understand you're looking for help with: {prompt[:100]}... Let me provide a detailed analysis."
        
        return {
            "content": response,
            "metadata": {
                "model": config.name,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            }
        }
    
    async def _call_ollama_api(self, config: AIModelConfig, prompt: str, context: Dict) -> Dict[str, Any]:
        """Call Ollama local API (simulated)"""
        response = f"[{config.name} Response] Processing your request about: {prompt[:100]}... Here's my analysis based on local processing."
        
        return {
            "content": response,
            "metadata": {
                "model": config.name,
                "local": True,
                "temperature": config.temperature
            }
        }
    
    async def _call_generic_api(self, config: AIModelConfig, prompt: str, context: Dict) -> Dict[str, Any]:
        """Call generic API endpoint"""
        response = f"[{config.name} Response] Your request has been processed: {prompt[:100]}..."
        
        return {
            "content": response,
            "metadata": {
                "model": config.name,
                "endpoint": config.endpoint
            }
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def _calculate_cost(self, model_name: str, tokens: int) -> float:
        """Calculate cost for model usage"""
        model_config = self.models.get(model_name)
        if model_config:
            return tokens * model_config.cost_per_token
        return 0.0
    
    async def _record_ai_request(self, user_id: str, model_name: str, request_type: str,
                               prompt: str, response: str = "", tokens_used: int = 0,
                               cost: float = 0.0, latency_ms: int = 0, success: bool = True,
                               error_message: str = None):
        """Record AI request for analytics"""
        if not self.integration_available:
            return
        
        try:
            async with database_session() as session:
                ai_request = AIRequest(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    model_name=model_name,
                    request_type=request_type,
                    prompt=prompt,
                    response=response,
                    tokens_used=tokens_used,
                    cost=cost,
                    latency_ms=latency_ms,
                    success=success,
                    error_message=error_message
                )
                session.add(ai_request)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to record AI request: {e}")
    
    async def _record_analytics(self, user_id: str, metric: AnalyticsMetric, value: float, 
                              metadata: Dict = None):
        """Record analytics data"""
        if not self.integration_available:
            return
        
        try:
            async with database_session() as session:
                analytics = AnalyticsData(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    metric_type=metric.value,
                    metric_name=metric.value,
                    metric_value=value,
                    metadata=metadata or {}
                )
                session.add(analytics)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to record analytics: {e}")
    
    async def get_ai_analytics(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive AI usage analytics"""
        analytics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_latency": 0.0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "model_usage": {},
            "request_types": {},
            "daily_usage": {},
            "performance_metrics": {}
        }
        
        if not self.integration_available:
            return analytics
        
        try:
            async with database_session() as session:
                from sqlalchemy import select, func, and_
                
                # Base query conditions
                base_conditions = [
                    AIRequest.created_at >= datetime.utcnow() - timedelta(days=days)
                ]
                if user_id:
                    base_conditions.append(AIRequest.user_id == user_id)
                
                # Total requests
                total_requests = await session.execute(
                    select(func.count(AIRequest.id)).where(and_(*base_conditions))
                )
                analytics["total_requests"] = total_requests.scalar() or 0
                
                # Success/failure counts
                successful = await session.execute(
                    select(func.count(AIRequest.id)).where(
                        and_(*base_conditions, AIRequest.success == True)
                    )
                )
                analytics["successful_requests"] = successful.scalar() or 0
                analytics["failed_requests"] = analytics["total_requests"] - analytics["successful_requests"]
                
                # Average latency
                avg_latency = await session.execute(
                    select(func.avg(AIRequest.latency_ms)).where(
                        and_(*base_conditions, AIRequest.success == True)
                    )
                )
                analytics["average_latency"] = round(avg_latency.scalar() or 0.0, 2)
                
                # Token and cost totals
                token_sum = await session.execute(
                    select(func.sum(AIRequest.tokens_used)).where(and_(*base_conditions))
                )
                analytics["total_tokens"] = token_sum.scalar() or 0
                
                cost_sum = await session.execute(
                    select(func.sum(AIRequest.cost)).where(and_(*base_conditions))
                )
                analytics["total_cost"] = round(cost_sum.scalar() or 0.0, 4)
                
                # Model usage breakdown
                model_usage = await session.execute(
                    select(
                        AIRequest.model_name,
                        func.count(AIRequest.id).label('count'),
                        func.sum(AIRequest.tokens_used).label('tokens'),
                        func.sum(AIRequest.cost).label('cost')
                    ).where(and_(*base_conditions)).group_by(AIRequest.model_name)
                )
                
                for row in model_usage:
                    analytics["model_usage"][row.model_name] = {
                        "requests": row.count,
                        "tokens": row.tokens or 0,
                        "cost": round(row.cost or 0.0, 4)
                    }
                
                # Request type breakdown
                request_types = await session.execute(
                    select(
                        AIRequest.request_type,
                        func.count(AIRequest.id).label('count')
                    ).where(and_(*base_conditions)).group_by(AIRequest.request_type)
                )
                
                for row in request_types:
                    analytics["request_types"][row.request_type] = row.count
                
        except Exception as e:
            logger.error(f"Analytics query failed: {e}")
        
        return analytics
    
    async def get_performance_insights(self, days: int = 7) -> Dict[str, Any]:
        """Get AI performance insights and recommendations"""
        insights = {
            "model_performance": {},
            "optimization_suggestions": [],
            "cost_analysis": {},
            "quality_metrics": {},
            "recommendations": []
        }
        
        if not self.integration_available:
            return insights
        
        try:
            # Get recent performance data
            analytics = await self.get_ai_analytics(days=days)
            
            # Analyze model performance
            for model_name, usage in analytics["model_usage"].items():
                if usage["requests"] > 0:
                    avg_cost_per_request = usage["cost"] / usage["requests"]
                    avg_tokens_per_request = usage["tokens"] / usage["requests"]
                    
                    insights["model_performance"][model_name] = {
                        "avg_cost_per_request": round(avg_cost_per_request, 4),
                        "avg_tokens_per_request": round(avg_tokens_per_request, 2),
                        "efficiency_score": self._calculate_efficiency_score(usage)
                    }
            
            # Generate optimization suggestions
            insights["optimization_suggestions"] = self._generate_optimization_suggestions(analytics)
            
            # Cost analysis
            insights["cost_analysis"] = self._analyze_costs(analytics)
            
            # Quality metrics (would be enhanced with real feedback data)
            insights["quality_metrics"] = await self._get_quality_metrics(days)
            
            # Generate recommendations
            insights["recommendations"] = self._generate_recommendations(insights)
            
        except Exception as e:
            logger.error(f"Performance insights failed: {e}")
        
        return insights
    
    def _calculate_efficiency_score(self, usage: Dict) -> float:
        """Calculate efficiency score for a model"""
        # Simple efficiency calculation based on cost and token ratio
        if usage["tokens"] > 0:
            cost_per_token = usage["cost"] / usage["tokens"]
            # Lower cost per token = higher efficiency (inverted and normalized)
            return max(0.0, min(1.0, 1.0 - (cost_per_token * 10000)))
        return 0.5
    
    def _generate_optimization_suggestions(self, analytics: Dict) -> List[str]:
        """Generate optimization suggestions based on analytics"""
        suggestions = []
        
        # High latency suggestion
        if analytics["average_latency"] > 5000:  # 5 seconds
            suggestions.append("Consider using faster models or implementing caching for improved response times")
        
        # High cost suggestion
        if analytics["total_cost"] > 100:  # $100
            suggestions.append("Consider using more cost-effective models for routine tasks")
        
        # Low success rate
        success_rate = analytics["successful_requests"] / max(analytics["total_requests"], 1)
        if success_rate < 0.95:
            suggestions.append("Review error patterns and implement better error handling")
        
        return suggestions
    
    def _analyze_costs(self, analytics: Dict) -> Dict[str, Any]:
        """Analyze cost patterns"""
        cost_analysis = {
            "daily_average": analytics["total_cost"] / 30 if analytics["total_cost"] > 0 else 0,
            "most_expensive_model": "",
            "cost_per_success": 0.0
        }
        
        # Find most expensive model
        max_cost = 0
        for model, usage in analytics["model_usage"].items():
            if usage["cost"] > max_cost:
                max_cost = usage["cost"]
                cost_analysis["most_expensive_model"] = model
        
        # Cost per successful request
        if analytics["successful_requests"] > 0:
            cost_analysis["cost_per_success"] = round(
                analytics["total_cost"] / analytics["successful_requests"], 4
            )
        
        return cost_analysis
    
    async def _get_quality_metrics(self, days: int) -> Dict[str, Any]:
        """Get quality metrics (placeholder for real implementation)"""
        # In a real system, this would analyze user feedback, task completion rates, etc.
        return {
            "average_user_rating": 4.2,
            "task_completion_rate": 0.87,
            "user_satisfaction": 0.85
        }
    
    def _generate_recommendations(self, insights: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Performance recommendations
        if insights["cost_analysis"]["daily_average"] > 10:
            recommendations.append("Consider implementing usage quotas to control costs")
        
        # Model recommendations
        best_model = max(
            insights["model_performance"].items(),
            key=lambda x: x[1]["efficiency_score"],
            default=(None, None)
        )
        if best_model[0]:
            recommendations.append(f"Consider using {best_model[0]} more frequently for better efficiency")
        
        return recommendations
    
    async def generate_analytics_report(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "period_days": days,
            "user_id": user_id,
            "ai_analytics": await self.get_ai_analytics(user_id, days),
            "performance_insights": await self.get_performance_insights(days),
            "summary": {}
        }
        
        # Generate summary
        ai_analytics = report["ai_analytics"]
        performance_insights = report["performance_insights"]
        
        report["summary"] = {
            "total_ai_interactions": ai_analytics["total_requests"],
            "success_rate": round(
                ai_analytics["successful_requests"] / max(ai_analytics["total_requests"], 1), 3
            ),
            "average_response_time": f"{ai_analytics['average_latency']}ms",
            "total_cost": f"${ai_analytics['total_cost']:.4f}",
            "most_used_model": max(
                ai_analytics["model_usage"].items(),
                key=lambda x: x[1]["requests"],
                default=("N/A", {"requests": 0})
            )[0],
            "key_recommendations": performance_insights["recommendations"][:3]
        }
        
        return report

# Global AI orchestrator instance
ai_orchestrator = AdvancedAIOrchestrator()

async def get_ai_orchestrator() -> AdvancedAIOrchestrator:
    """Get the global AI orchestrator instance"""
    return ai_orchestrator

# Export main classes and functions
__all__ = [
    'AdvancedAIOrchestrator',
    'AIModelConfig',
    'AIModelType',
    'AnalyticsMetric',
    'AnalyticsEvent',
    'AIRequest',
    'AnalyticsData',
    'ModelPerformance',
    'get_ai_orchestrator',
    'ai_orchestrator'
]

if __name__ == "__main__":
    # Test the AI orchestration system
    async def test_ai_system():
        orchestrator = AdvancedAIOrchestrator()
        
        # Test AI request routing
        response = await orchestrator.route_request(
            user_id="test_user_123",
            prompt="Create a Python function that calculates fibonacci numbers",
            request_type="code_generation"
        )
        
        print("AI Response:", response)
        
        # Test analytics
        analytics = await orchestrator.get_ai_analytics(user_id="test_user_123", days=7)
        print("\\nAI Analytics:", analytics)
        
        # Test performance insights
        insights = await orchestrator.get_performance_insights()
        print("\\nPerformance Insights:", insights)
        
        # Generate report
        report = await orchestrator.generate_analytics_report(user_id="test_user_123")
        print("\\nAnalytics Report Summary:", report["summary"])
    
    # Run test
    asyncio.run(test_ai_system())