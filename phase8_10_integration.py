"""
Aeonforge Phase 8-10 Integration Layer
Complete integration of Advanced Database, Payment System, and AI Analytics
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import logging

# Phase imports
try:
    from phase8_database import get_database_manager, AdvancedDatabaseManager, DatabaseConfig
    from phase9_payments import get_payment_manager, PaymentManager, SubscriptionTier, PRICING_PLANS
    from phase10_ai_analytics import get_ai_orchestrator, AdvancedAIOrchestrator
    PHASES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Phase 8-10 modules not fully available: {e}")
    PHASES_AVAILABLE = False

# FastAPI integration
try:
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response models
if FASTAPI_AVAILABLE:
    class CreateUserRequest(BaseModel):
        email: str
        name: str
        metadata: Optional[Dict] = None
    
    class CreateSubscriptionRequest(BaseModel):
        user_id: str
        tier: str
        billing_period: str = "monthly"
        success_url: Optional[str] = None
        cancel_url: Optional[str] = None
    
    class AIRequestModel(BaseModel):
        user_id: str
        prompt: str
        request_type: str = "chat"
        model_preference: Optional[str] = None
        context: Optional[Dict] = None
    
    class AnalyticsRequest(BaseModel):
        user_id: Optional[str] = None
        days: int = 30
        metric_types: Optional[List[str]] = None

class AeonforgeEnterprisePlatform:
    """Complete enterprise platform integrating all phases"""
    
    def __init__(self):
        self.db_manager: Optional[AdvancedDatabaseManager] = None
        self.payment_manager: Optional[PaymentManager] = None
        self.ai_orchestrator: Optional[AdvancedAIOrchestrator] = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize all platform components"""
        if not PHASES_AVAILABLE:
            logger.error("Phase 8-10 modules not available")
            return False
        
        try:
            # Initialize database
            self.db_manager = await get_database_manager()
            logger.info("Database manager initialized")
            
            # Initialize payment system
            self.payment_manager = await get_payment_manager()
            logger.info("Payment manager initialized")
            
            # Initialize AI orchestrator
            self.ai_orchestrator = await get_ai_orchestrator()
            logger.info("AI orchestrator initialized")
            
            self.initialized = True
            logger.info("Enterprise platform fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Platform initialization failed: {e}")
            return False
    
    async def create_user_account(self, email: str, name: str, metadata: Dict = None) -> Dict[str, Any]:
        """Create complete user account with database and payment setup"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create user in payment system (includes Stripe customer)
            user_id = await self.payment_manager.create_user(email, name, metadata)
            
            if user_id:
                # Initialize user analytics
                await self.ai_orchestrator._record_analytics(
                    user_id, "user_creation", 1.0, {"email": email, "name": name}
                )
                
                logger.info(f"User account created successfully: {user_id}")
                return {
                    "success": True,
                    "user_id": user_id,
                    "message": "Account created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create user account"
                }
                
        except Exception as e:
            logger.error(f"User account creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_ai_request_with_limits(self, user_id: str, prompt: str, 
                                           request_type: str = "chat", 
                                           model_preference: str = None) -> Dict[str, Any]:
        """Process AI request with subscription limit checking"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Check user subscription and limits
            limits_check = await self.payment_manager.check_usage_limits(user_id, "api_calls_per_day")
            
            if not limits_check["allowed"]:
                return {
                    "success": False,
                    "error": limits_check["reason"],
                    "upgrade_required": True,
                    "available_plans": PRICING_PLANS
                }
            
            # Process AI request
            response = await self.ai_orchestrator.route_request(
                user_id=user_id,
                prompt=prompt,
                request_type=request_type,
                model_preference=model_preference
            )
            
            # Record usage if successful
            if response.get("success"):
                await self.payment_manager.record_usage(user_id, "api_calls", 1)
                
                # Store conversation in database
                conv_id = await self.db_manager.create_conversation(
                    user_id=user_id,
                    title=prompt[:50] + "..." if len(prompt) > 50 else prompt
                )
                
                # Add messages
                await self.db_manager.add_message(conv_id, "user", prompt)
                await self.db_manager.add_message(conv_id, "assistant", response.get("content", ""))
                
                # Store code generation if applicable
                if request_type == "code_generation" and response.get("content"):
                    await self.db_manager.store_code_generation(
                        project_id=None,  # Could be linked to a project
                        user_id=user_id,
                        request=prompt,
                        generated_code=response.get("content"),
                        language="auto-detected",
                        metadata={
                            "model": response.get("model_used"),
                            "tokens": response.get("tokens_used"),
                            "cost": response.get("cost")
                        }
                    )
                
                response["conversation_id"] = conv_id
            
            return response
            
        except Exception as e:
            logger.error(f"AI request processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_project_with_permissions(self, name: str, description: str, 
                                            owner_id: str, settings: Dict = None) -> Dict[str, Any]:
        """Create project with subscription tier permissions"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Check project limits
            limits_check = await self.payment_manager.check_usage_limits(owner_id, "projects")
            
            if not limits_check["allowed"]:
                return {
                    "success": False,
                    "error": limits_check["reason"],
                    "current_usage": limits_check["usage"],
                    "limit": limits_check["limit"],
                    "upgrade_required": True
                }
            
            # Create project
            project_id = await self.db_manager.create_project(name, description, owner_id, settings)
            
            if project_id:
                # Record project creation
                await self.payment_manager.record_usage(owner_id, "projects", 1)
                
                return {
                    "success": True,
                    "project_id": project_id,
                    "message": "Project created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create project"
                }
                
        except Exception as e:
            logger.error(f"Project creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user dashboard data"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get user info
            user = await self.payment_manager.get_user(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get usage statistics
            api_limits = await self.payment_manager.check_usage_limits(user_id, "api_calls_per_day")
            project_limits = await self.payment_manager.check_usage_limits(user_id, "projects")
            
            # Get AI analytics
            ai_analytics = await self.ai_orchestrator.get_ai_analytics(user_id, days=30)
            
            # Get database analytics
            db_analytics = await self.db_manager.get_analytics(days=30)
            
            # Get subscription info
            tier = SubscriptionTier(user["subscription_tier"])
            plan = PRICING_PLANS[tier]
            
            dashboard = {
                "user": user,
                "subscription": {
                    "tier": tier.value,
                    "plan_name": plan.name,
                    "features": plan.features,
                    "status": user["subscription_status"],
                    "end_date": user["subscription_end_date"]
                },
                "usage": {
                    "api_calls": {
                        "used": api_limits.get("usage", 0),
                        "limit": api_limits.get("limit", 0),
                        "remaining": api_limits.get("remaining", 0)
                    },
                    "projects": {
                        "used": project_limits.get("usage", 0),
                        "limit": project_limits.get("limit", 0),
                        "remaining": project_limits.get("remaining", 0)
                    }
                },
                "analytics": {
                    "ai": ai_analytics,
                    "database": db_analytics
                },
                "recent_activity": await self._get_recent_activity(user_id)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return {"error": str(e)}
    
    async def _get_recent_activity(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent user activity"""
        try:
            activities = []
            
            # Get recent conversations
            # This would be implemented with proper database queries
            # For now, returning sample data
            activities.append({
                "type": "conversation",
                "title": "Recent AI Chat",
                "timestamp": datetime.utcnow().isoformat(),
                "details": "Chat about Python development"
            })
            
            return activities
            
        except Exception as e:
            logger.error(f"Recent activity fetch failed: {e}")
            return []
    
    async def generate_comprehensive_report(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive platform analytics report"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get AI analytics report
            ai_report = await self.ai_orchestrator.generate_analytics_report(user_id, days)
            
            # Get billing analytics
            billing_analytics = await self.payment_manager.get_billing_analytics(days)
            
            # Get database analytics
            db_analytics = await self.db_manager.get_analytics(days=days)
            
            # Get performance insights
            performance_insights = await self.ai_orchestrator.get_performance_insights(days)
            
            comprehensive_report = {
                "report_id": ai_report["report_id"],
                "generated_at": ai_report["generated_at"],
                "period_days": days,
                "scope": "platform" if not user_id else f"user:{user_id}",
                "ai_analytics": ai_report["ai_analytics"],
                "billing_analytics": billing_analytics,
                "database_analytics": db_analytics,
                "performance_insights": performance_insights,
                "platform_summary": {
                    "total_users": billing_analytics.get("user_distribution", {}).get("total", 0),
                    "active_subscriptions": billing_analytics.get("active_subscriptions", 0),
                    "monthly_revenue": billing_analytics.get("mrr", 0.0),
                    "total_projects": db_analytics.get("total_projects", 0),
                    "total_conversations": db_analytics.get("total_conversations", 0),
                    "ai_requests": ai_report["ai_analytics"]["total_requests"],
                    "average_response_time": ai_report["ai_analytics"]["average_latency"]
                },
                "recommendations": [
                    *performance_insights.get("recommendations", []),
                    *performance_insights.get("optimization_suggestions", [])
                ]
            }
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"Comprehensive report generation failed: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive platform health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "overall_health": True
        }
        
        try:
            if self.initialized:
                # Check database
                try:
                    await self.db_manager.get_analytics(days=1)
                    health_status["components"]["database"] = {"status": "healthy", "latency_ms": 0}
                except Exception as e:
                    health_status["components"]["database"] = {"status": "unhealthy", "error": str(e)}
                    health_status["overall_health"] = False
                
                # Check payment system
                try:
                    analytics = await self.payment_manager.get_billing_analytics(days=1)
                    health_status["components"]["payments"] = {"status": "healthy", "active_subscriptions": analytics.get("active_subscriptions", 0)}
                except Exception as e:
                    health_status["components"]["payments"] = {"status": "unhealthy", "error": str(e)}
                    health_status["overall_health"] = False
                
                # Check AI system
                try:
                    ai_analytics = await self.ai_orchestrator.get_ai_analytics(days=1)
                    health_status["components"]["ai"] = {"status": "healthy", "models_available": len(self.ai_orchestrator.models)}
                except Exception as e:
                    health_status["components"]["ai"] = {"status": "unhealthy", "error": str(e)}
                    health_status["overall_health"] = False
            else:
                health_status["status"] = "initializing"
                health_status["overall_health"] = False
                
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["overall_health"] = False
            health_status["error"] = str(e)
        
        if not health_status["overall_health"]:
            health_status["status"] = "unhealthy"
        
        return health_status

# Global platform instance
enterprise_platform = AeonforgeEnterprisePlatform()

async def get_enterprise_platform() -> AeonforgeEnterprisePlatform:
    """Get the global enterprise platform instance"""
    if not enterprise_platform.initialized:
        await enterprise_platform.initialize()
    return enterprise_platform

# FastAPI integration routes
if FASTAPI_AVAILABLE:
    def create_enterprise_api() -> FastAPI:
        """Create FastAPI application with enterprise endpoints"""
        app = FastAPI(
            title="Aeonforge Enterprise API",
            description="Complete AI Development Platform with Advanced Features",
            version="3.0.0"
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.post("/api/v3/users")
        async def create_user(request: CreateUserRequest):
            platform = await get_enterprise_platform()
            return await platform.create_user_account(
                email=request.email,
                name=request.name,
                metadata=request.metadata
            )
        
        @app.post("/api/v3/ai/chat")
        async def ai_chat(request: AIRequestModel):
            platform = await get_enterprise_platform()
            return await platform.process_ai_request_with_limits(
                user_id=request.user_id,
                prompt=request.prompt,
                request_type=request.request_type,
                model_preference=request.model_preference
            )
        
        @app.post("/api/v3/projects")
        async def create_project(name: str, description: str, owner_id: str, settings: Dict = None):
            platform = await get_enterprise_platform()
            return await platform.create_project_with_permissions(name, description, owner_id, settings)
        
        @app.get("/api/v3/users/{user_id}/dashboard")
        async def get_dashboard(user_id: str):
            platform = await get_enterprise_platform()
            return await platform.get_user_dashboard(user_id)
        
        @app.post("/api/v3/subscriptions")
        async def create_subscription(request: CreateSubscriptionRequest):
            platform = await get_enterprise_platform()
            return await platform.payment_manager.create_checkout_session(
                user_id=request.user_id,
                tier=SubscriptionTier(request.tier),
                billing_period=request.billing_period,
                success_url=request.success_url,
                cancel_url=request.cancel_url
            )
        
        @app.get("/api/v3/analytics")
        async def get_analytics(request: AnalyticsRequest):
            platform = await get_enterprise_platform()
            return await platform.generate_comprehensive_report(request.user_id, request.days)
        
        @app.get("/api/v3/health")
        async def health_check():
            platform = await get_enterprise_platform()
            return await platform.health_check()
        
        @app.get("/api/v3/pricing")
        async def get_pricing():
            return {"plans": {tier.value: asdict(plan) for tier, plan in PRICING_PLANS.items()}}
        
        return app

# Export main classes and functions
__all__ = [
    'AeonforgeEnterprisePlatform',
    'get_enterprise_platform',
    'create_enterprise_api',
    'enterprise_platform'
]

if __name__ == "__main__":
    # Test the enterprise platform
    async def test_enterprise_platform():
        platform = AeonforgeEnterprisePlatform()
        
        # Initialize platform
        success = await platform.initialize()
        if success:
            print("Enterprise platform initialized successfully!")
            
            # Test user creation
            user_result = await platform.create_user_account(
                email="enterprise@test.com",
                name="Enterprise Test User"
            )
            print("User creation:", user_result)
            
            if user_result.get("success"):
                user_id = user_result["user_id"]
                
                # Test AI request
                ai_result = await platform.process_ai_request_with_limits(
                    user_id=user_id,
                    prompt="Create a React component for user authentication"
                )
                print("AI request:", ai_result.get("success", False))
                
                # Test dashboard
                dashboard = await platform.get_user_dashboard(user_id)
                print("Dashboard loaded:", "user" in dashboard)
                
                # Test health check
                health = await platform.health_check()
                print("Health check:", health["status"])
                
        else:
            print("Enterprise platform initialization failed")
    
    # Run test
    asyncio.run(test_enterprise_platform())