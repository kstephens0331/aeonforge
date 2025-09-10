"""
Aeonforge Phase 9 - Payment & Subscription System
Stripe Integration, User Management, SaaS Features with AI-Enhanced Business Intelligence
"""

import os
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import asynccontextmanager

# Payment processing imports
try:
    import stripe
    from stripe import StripeError
    STRIPE_AVAILABLE = True
except ImportError:
    print("Warning: Stripe not available. Install with: pip install stripe")
    STRIPE_AVAILABLE = False

# Database integration
try:
    from phase8_database import get_database_manager, database_session
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
    from sqlalchemy import String, DateTime, Text, Integer, Boolean, JSON, Float, Enum as SQLEnum
    DATABASE_AVAILABLE = True
except ImportError:
    print("Warning: Phase 8 database not available")
    DATABASE_AVAILABLE = False

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stripe configuration
if STRIPE_AVAILABLE:
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_key_here')

class SubscriptionTier(Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"

@dataclass
class PricingPlan:
    """Pricing plan configuration"""
    tier: SubscriptionTier
    name: str
    price_monthly: float
    price_yearly: float
    features: List[str]
    limits: Dict[str, int]
    stripe_price_id_monthly: str = ""
    stripe_price_id_yearly: str = ""

# Define pricing tiers
PRICING_PLANS = {
    SubscriptionTier.FREE: PricingPlan(
        tier=SubscriptionTier.FREE,
        name="Free",
        price_monthly=0.0,
        price_yearly=0.0,
        features=[
            "Basic AI assistance",
            "5 projects",
            "Community support",
            "Basic templates"
        ],
        limits={
            "projects": 5,
            "api_calls_per_day": 100,
            "storage_gb": 1,
            "team_members": 1
        }
    ),
    SubscriptionTier.BASIC: PricingPlan(
        tier=SubscriptionTier.BASIC,
        name="Basic",
        price_monthly=29.99,
        price_yearly=299.99,
        features=[
            "Advanced AI assistance",
            "50 projects",
            "Email support",
            "Advanced templates",
            "Git integration",
            "PDF generation"
        ],
        limits={
            "projects": 50,
            "api_calls_per_day": 1000,
            "storage_gb": 10,
            "team_members": 5
        },
        stripe_price_id_monthly="price_basic_monthly",
        stripe_price_id_yearly="price_basic_yearly"
    ),
    SubscriptionTier.PRO: PricingPlan(
        tier=SubscriptionTier.PRO,
        name="Pro",
        price_monthly=99.99,
        price_yearly=999.99,
        features=[
            "All Basic features",
            "Unlimited projects",
            "Priority support",
            "Custom templates",
            "Advanced analytics",
            "Team collaboration",
            "API access",
            "Multi-model AI"
        ],
        limits={
            "projects": -1,  # Unlimited
            "api_calls_per_day": 10000,
            "storage_gb": 100,
            "team_members": 25
        },
        stripe_price_id_monthly="price_pro_monthly",
        stripe_price_id_yearly="price_pro_yearly"
    ),
    SubscriptionTier.ENTERPRISE: PricingPlan(
        tier=SubscriptionTier.ENTERPRISE,
        name="Enterprise",
        price_monthly=499.99,
        price_yearly=4999.99,
        features=[
            "All Pro features",
            "Custom deployment",
            "Dedicated support",
            "SLA guarantees",
            "White-label options",
            "Custom integrations",
            "Advanced security",
            "Compliance tools"
        ],
        limits={
            "projects": -1,
            "api_calls_per_day": -1,  # Unlimited
            "storage_gb": -1,
            "team_members": -1
        },
        stripe_price_id_monthly="price_enterprise_monthly",
        stripe_price_id_yearly="price_enterprise_yearly"
    )
}

if DATABASE_AVAILABLE:
    from phase8_database import Base
    
    class User(Base):
        """User data model with subscription info"""
        __tablename__ = "users"
        
        id: Mapped[str] = mapped_column(String, primary_key=True)
        email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
        name: Mapped[str] = mapped_column(String(255), nullable=False)
        stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255))
        subscription_tier: Mapped[str] = mapped_column(String(50), default="free")
        subscription_status: Mapped[str] = mapped_column(String(50), default="active")
        subscription_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        user_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    class Subscription(Base):
        """Subscription data model"""
        __tablename__ = "subscriptions"
        
        id: Mapped[str] = mapped_column(String, primary_key=True)
        user_id: Mapped[str] = mapped_column(String(255), nullable=False)
        stripe_subscription_id: Mapped[str] = mapped_column(String(255), nullable=False)
        tier: Mapped[str] = mapped_column(String(50), nullable=False)
        status: Mapped[str] = mapped_column(String(50), nullable=False)
        current_period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
        current_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
        canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        user_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    class Payment(Base):
        """Payment transaction model"""
        __tablename__ = "payments"
        
        id: Mapped[str] = mapped_column(String, primary_key=True)
        user_id: Mapped[str] = mapped_column(String(255), nullable=False)
        stripe_payment_intent_id: Mapped[str] = mapped_column(String(255), nullable=False)
        amount: Mapped[float] = mapped_column(Float, nullable=False)
        currency: Mapped[str] = mapped_column(String(3), default="usd")
        status: Mapped[str] = mapped_column(String(50), nullable=False)
        description: Mapped[Optional[str]] = mapped_column(Text)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        user_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    class UsageMetrics(Base):
        """User usage tracking"""
        __tablename__ = "usage_metrics"
        
        id: Mapped[str] = mapped_column(String, primary_key=True)
        user_id: Mapped[str] = mapped_column(String(255), nullable=False)
        metric_type: Mapped[str] = mapped_column(String(100), nullable=False)  # api_calls, storage, projects
        metric_value: Mapped[int] = mapped_column(Integer, nullable=False)
        recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        user_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

class PaymentManager:
    """Advanced payment and subscription management system"""
    
    def __init__(self):
        self.stripe_available = STRIPE_AVAILABLE
        self.db_available = DATABASE_AVAILABLE
        
    async def create_user(self, email: str, name: str, metadata: Dict = None) -> str:
        """Create a new user account"""
        user_id = str(uuid.uuid4())
        
        if not self.db_available:
            logger.error("Database not available for user creation")
            return None
            
        # Create Stripe customer
        stripe_customer_id = None
        if self.stripe_available:
            try:
                customer = stripe.Customer.create(
                    email=email,
                    name=name,
                    metadata=metadata or {}
                )
                stripe_customer_id = customer.id
                logger.info(f"Created Stripe customer: {stripe_customer_id}")
            except StripeError as e:
                logger.error(f"Stripe customer creation failed: {e}")
        
        # Create user in database
        async with database_session() as session:
            user = User(
                id=user_id,
                email=email,
                name=name,
                stripe_customer_id=stripe_customer_id,
                subscription_tier=SubscriptionTier.FREE.value,
                metadata=metadata or {}
            )
            session.add(user)
            await session.commit()
            
        logger.info(f"Created user: {user_id}")
        return user_id
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user information"""
        if not self.db_available:
            return None
            
        async with database_session() as session:
            user = await session.get(User, user_id)
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "subscription_tier": user.subscription_tier,
                    "subscription_status": user.subscription_status,
                    "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
                    "created_at": user.created_at.isoformat(),
                    "metadata": user.metadata,
                    "is_active": user.is_active
                }
        return None
    
    async def create_checkout_session(self, user_id: str, tier: SubscriptionTier, 
                                    billing_period: str = "monthly", 
                                    success_url: str = None, 
                                    cancel_url: str = None) -> Dict:
        """Create Stripe checkout session for subscription"""
        if not self.stripe_available:
            return {"error": "Payment processing not available"}
            
        user = await self.get_user(user_id)
        if not user:
            return {"error": "User not found"}
            
        plan = PRICING_PLANS.get(tier)
        if not plan:
            return {"error": "Invalid subscription tier"}
            
        price_id = plan.stripe_price_id_yearly if billing_period == "yearly" else plan.stripe_price_id_monthly
        
        try:
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=user.get("stripe_customer_id"),
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url or 'https://your-app.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url or 'https://your-app.com/cancel',
                metadata={
                    'user_id': user_id,
                    'tier': tier.value,
                    'billing_period': billing_period
                }
            )
            
            return {
                "session_id": session.id,
                "url": session.url,
                "session": session
            }
            
        except StripeError as e:
            logger.error(f"Checkout session creation failed: {e}")
            return {"error": str(e)}
    
    async def handle_subscription_created(self, stripe_subscription: Dict) -> bool:
        """Handle successful subscription creation"""
        try:
            user_id = stripe_subscription.get("metadata", {}).get("user_id")
            if not user_id:
                logger.error("No user_id in subscription metadata")
                return False
                
            # Create subscription record
            subscription_id = str(uuid.uuid4())
            
            async with database_session() as session:
                subscription = Subscription(
                    id=subscription_id,
                    user_id=user_id,
                    stripe_subscription_id=stripe_subscription["id"],
                    tier=stripe_subscription.get("metadata", {}).get("tier", "basic"),
                    status=stripe_subscription["status"],
                    current_period_start=datetime.fromtimestamp(stripe_subscription["current_period_start"]),
                    current_period_end=datetime.fromtimestamp(stripe_subscription["current_period_end"]),
                    metadata=stripe_subscription.get("metadata", {})
                )
                session.add(subscription)
                
                # Update user
                user = await session.get(User, user_id)
                if user:
                    user.subscription_tier = subscription.tier
                    user.subscription_status = "active"
                    user.subscription_end_date = subscription.current_period_end
                    user.updated_at = datetime.utcnow()
                
                await session.commit()
                
            logger.info(f"Subscription created: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Subscription creation handling failed: {e}")
            return False
    
    async def handle_subscription_updated(self, stripe_subscription: Dict) -> bool:
        """Handle subscription updates"""
        try:
            subscription_id = stripe_subscription["id"]
            
            async with database_session() as session:
                from sqlalchemy import select
                
                # Find subscription
                stmt = select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
                result = await session.execute(stmt)
                subscription = result.scalar_one_or_none()
                
                if subscription:
                    subscription.status = stripe_subscription["status"]
                    subscription.current_period_start = datetime.fromtimestamp(stripe_subscription["current_period_start"])
                    subscription.current_period_end = datetime.fromtimestamp(stripe_subscription["current_period_end"])
                    subscription.updated_at = datetime.utcnow()
                    
                    if stripe_subscription["status"] == "canceled":
                        subscription.canceled_at = datetime.utcnow()
                    
                    # Update user
                    user = await session.get(User, subscription.user_id)
                    if user:
                        user.subscription_status = stripe_subscription["status"]
                        user.subscription_end_date = subscription.current_period_end
                        user.updated_at = datetime.utcnow()
                    
                    await session.commit()
                    logger.info(f"Subscription updated: {subscription.id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Subscription update handling failed: {e}")
            
        return False
    
    async def cancel_subscription(self, user_id: str) -> bool:
        """Cancel user subscription"""
        if not self.stripe_available:
            return False
            
        user = await self.get_user(user_id)
        if not user:
            return False
            
        try:
            # Find active subscription
            async with database_session() as session:
                from sqlalchemy import select
                
                stmt = select(Subscription).where(
                    Subscription.user_id == user_id,
                    Subscription.status == "active"
                )
                result = await session.execute(stmt)
                subscription = result.scalar_one_or_none()
                
                if subscription:
                    # Cancel in Stripe
                    stripe.Subscription.delete(subscription.stripe_subscription_id)
                    
                    # Update database
                    subscription.status = "canceled"
                    subscription.canceled_at = datetime.utcnow()
                    subscription.updated_at = datetime.utcnow()
                    
                    await session.commit()
                    logger.info(f"Canceled subscription for user: {user_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Subscription cancellation failed: {e}")
            
        return False
    
    async def check_usage_limits(self, user_id: str, metric_type: str) -> Dict[str, Any]:
        """Check if user has exceeded usage limits"""
        user = await self.get_user(user_id)
        if not user:
            return {"allowed": False, "reason": "User not found"}
            
        tier = SubscriptionTier(user["subscription_tier"])
        plan = PRICING_PLANS[tier]
        
        # Check subscription status
        if user["subscription_status"] != "active" and tier != SubscriptionTier.FREE:
            return {"allowed": False, "reason": "Subscription inactive"}
            
        # Get usage limits
        limit = plan.limits.get(metric_type, 0)
        if limit == -1:  # Unlimited
            return {"allowed": True, "limit": -1, "usage": 0}
            
        # Get current usage
        current_usage = await self._get_current_usage(user_id, metric_type)
        
        return {
            "allowed": current_usage < limit,
            "limit": limit,
            "usage": current_usage,
            "remaining": max(0, limit - current_usage)
        }
    
    async def record_usage(self, user_id: str, metric_type: str, amount: int = 1):
        """Record usage metrics"""
        if not self.db_available:
            return
            
        metric_id = str(uuid.uuid4())
        
        async with database_session() as session:
            usage = UsageMetrics(
                id=metric_id,
                user_id=user_id,
                metric_type=metric_type,
                metric_value=amount
            )
            session.add(usage)
            await session.commit()
    
    async def _get_current_usage(self, user_id: str, metric_type: str) -> int:
        """Get current usage for a specific metric"""
        if not self.db_available:
            return 0
            
        async with database_session() as session:
            from sqlalchemy import select, func
            
            today = datetime.utcnow().date()
            
            if metric_type == "api_calls_per_day":
                # Daily usage
                stmt = select(func.sum(UsageMetrics.metric_value)).where(
                    UsageMetrics.user_id == user_id,
                    UsageMetrics.metric_type == "api_calls",
                    func.date(UsageMetrics.recorded_at) == today
                )
            elif metric_type == "projects":
                # Total projects
                from phase8_database import Project
                stmt = select(func.count(Project.id)).where(
                    Project.owner_id == user_id,
                    Project.is_active == True
                )
            else:
                # Other metrics
                stmt = select(func.sum(UsageMetrics.metric_value)).where(
                    UsageMetrics.user_id == user_id,
                    UsageMetrics.metric_type == metric_type
                )
                
            result = await session.execute(stmt)
            usage = result.scalar()
            return usage or 0
    
    async def get_billing_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get billing and subscription analytics"""
        analytics = {
            "total_revenue": 0.0,
            "active_subscriptions": 0,
            "subscription_breakdown": {},
            "churn_rate": 0.0,
            "mrr": 0.0,  # Monthly Recurring Revenue
            "arr": 0.0,  # Annual Recurring Revenue
            "user_distribution": {}
        }
        
        if not self.db_available:
            return analytics
            
        async with database_session() as session:
            from sqlalchemy import select, func
            
            # Active subscriptions by tier
            stmt = select(
                User.subscription_tier,
                func.count(User.id).label('count')
            ).where(
                User.subscription_status == "active",
                User.is_active == True
            ).group_by(User.subscription_tier)
            
            result = await session.execute(stmt)
            for row in result:
                tier = row.subscription_tier
                count = row.count
                analytics["subscription_breakdown"][tier] = count
                analytics["active_subscriptions"] += count
                
                # Calculate revenue
                plan = PRICING_PLANS.get(SubscriptionTier(tier))
                if plan and plan.price_monthly > 0:
                    monthly_revenue = plan.price_monthly * count
                    analytics["mrr"] += monthly_revenue
                    analytics["arr"] += monthly_revenue * 12
            
            # Total revenue from payments
            payments_sum = await session.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.status == "completed",
                    Payment.created_at >= datetime.utcnow() - timedelta(days=days)
                )
            )
            analytics["total_revenue"] = payments_sum.scalar() or 0.0
            
            # User distribution
            user_count = await session.execute(select(func.count(User.id)))
            analytics["user_distribution"]["total"] = user_count.scalar()
            
        return analytics
    
    def get_pricing_plans(self) -> Dict[str, Dict]:
        """Get all available pricing plans"""
        return {tier.value: asdict(plan) for tier, plan in PRICING_PLANS.items()}
    
    async def process_webhook(self, event_type: str, data: Dict) -> bool:
        """Process Stripe webhook events"""
        try:
            if event_type == "customer.subscription.created":
                return await self.handle_subscription_created(data)
            elif event_type == "customer.subscription.updated":
                return await self.handle_subscription_updated(data)
            elif event_type == "invoice.payment_succeeded":
                return await self._handle_payment_succeeded(data)
            elif event_type == "invoice.payment_failed":
                return await self._handle_payment_failed(data)
            else:
                logger.info(f"Unhandled webhook event: {event_type}")
                return True
                
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return False
    
    async def _handle_payment_succeeded(self, invoice_data: Dict) -> bool:
        """Handle successful payment"""
        try:
            customer_id = invoice_data.get("customer")
            amount_paid = invoice_data.get("amount_paid", 0) / 100  # Convert from cents
            
            # Find user by Stripe customer ID
            async with database_session() as session:
                from sqlalchemy import select
                
                stmt = select(User).where(User.stripe_customer_id == customer_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    # Record payment
                    payment_id = str(uuid.uuid4())
                    payment = Payment(
                        id=payment_id,
                        user_id=user.id,
                        stripe_payment_intent_id=invoice_data.get("payment_intent", ""),
                        amount=amount_paid,
                        status="completed",
                        description=f"Subscription payment - {invoice_data.get('billing_reason', 'subscription_cycle')}",
                        metadata={"invoice_id": invoice_data.get("id")}
                    )
                    session.add(payment)
                    await session.commit()
                    
                    logger.info(f"Payment recorded: {payment_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Payment success handling failed: {e}")
            
        return False
    
    async def _handle_payment_failed(self, invoice_data: Dict) -> bool:
        """Handle failed payment"""
        try:
            customer_id = invoice_data.get("customer")
            
            # Find user and update subscription status
            async with database_session() as session:
                from sqlalchemy import select
                
                stmt = select(User).where(User.stripe_customer_id == customer_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    # Update user status
                    user.subscription_status = "past_due"
                    user.updated_at = datetime.utcnow()
                    
                    # Record failed payment
                    payment_id = str(uuid.uuid4())
                    payment = Payment(
                        id=payment_id,
                        user_id=user.id,
                        stripe_payment_intent_id=invoice_data.get("payment_intent", ""),
                        amount=invoice_data.get("amount_due", 0) / 100,
                        status="failed",
                        description=f"Failed payment - {invoice_data.get('billing_reason', 'subscription_cycle')}",
                        metadata={"invoice_id": invoice_data.get("id")}
                    )
                    session.add(payment)
                    await session.commit()
                    
                    logger.warning(f"Payment failed for user: {user.id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Payment failure handling failed: {e}")
            
        return False

# Global payment manager instance
payment_manager = PaymentManager()

async def get_payment_manager() -> PaymentManager:
    """Get the global payment manager instance"""
    return payment_manager

# Export main classes and functions
__all__ = [
    'PaymentManager',
    'SubscriptionTier',
    'PaymentStatus', 
    'PricingPlan',
    'PRICING_PLANS',
    'User',
    'Subscription',
    'Payment',
    'UsageMetrics',
    'get_payment_manager',
    'payment_manager'
]

if __name__ == "__main__":
    # Test the payment system
    async def test_payment_system():
        manager = PaymentManager()
        
        # Test user creation
        user_id = await manager.create_user(
            email="test@example.com",
            name="Test User",
            metadata={"source": "test"}
        )
        
        if user_id:
            print(f"Created test user: {user_id}")
            
            # Test usage limits
            limits = await manager.check_usage_limits(user_id, "projects")
            print("Usage limits:", limits)
            
            # Test pricing plans
            plans = manager.get_pricing_plans()
            print("Available plans:", list(plans.keys()))
            
            # Test analytics
            analytics = await manager.get_billing_analytics()
            print("Billing analytics:", analytics)
        else:
            print("Failed to create test user")
    
    # Run test
    asyncio.run(test_payment_system())