import React, { useState } from 'react'
import './SubscriptionModal.css'

function SubscriptionModal({ isOpen, onClose, user, onUpgrade }) {
  const [selectedPlan, setSelectedPlan] = useState('pro')
  const [isLoading, setIsLoading] = useState(false)

  const plans = {
    free: {
      name: 'Free Tier',
      price: 0,
      period: 'forever',
      features: [
        '5 AI messages per day',
        'Basic GPT-3.5 model only',
        'No file uploads',
        'Community support',
        'Rate limited API calls'
      ],
      limitations: [
        'Daily usage resets at midnight',
        'No premium models',
        'Basic features only'
      ],
      color: '#64748b',
      current: user?.plan === 'free'
    },
    standard: {
      name: 'Standard',
      price: 10,
      period: 'month',
      features: [
        '100 AI messages per day',
        'GPT-4 & Claude models',
        'Basic file uploads',
        'Email support',
        'Standard API access'
      ],
      color: '#10b981',
      stripePriceId: 'price_standard_monthly',
      current: user?.plan === 'standard'
    },
    pro: {
      name: 'Pro',
      price: 15,
      period: 'month',
      features: [
        'Unlimited AI messages',
        'All AI models (GPT-4, Claude, Gemini)',
        'File uploads & analysis',
        'Project management tools',
        'Priority email support',
        'Priority API access'
      ],
      popular: true,
      color: '#667eea',
      stripePriceId: 'price_pro_monthly',
      current: user?.plan === 'pro'
    },
    enterprise: {
      name: 'Enterprise',
      price: 50,
      period: 'month',
      subtitle: '2 seats included',
      features: [
        'Everything in Pro',
        '2 team seats included',
        '$15 per additional seat',
        'Medical research tools',
        'Advanced analytics',
        'Custom integrations',
        'Phone support',
        'Dedicated account manager',
        'SLA guarantees'
      ],
      color: '#f59e0b',
      stripePriceId: 'price_enterprise_monthly',
      current: user?.plan === 'enterprise'
    }
  }

  const handleUpgrade = async (planKey) => {
    if (planKey === 'free') return

    setIsLoading(true)
    try {
      await onUpgrade(plans[planKey].stripePriceId, planKey)
    } catch (error) {
      console.error('Upgrade failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="subscription-modal-overlay" onClick={onClose}>
      <div className="subscription-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Choose Your Plan</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="usage-warning">
          <div className="warning-box">
            <h3>🚨 Free Tier Limitations</h3>
            <p>You have <strong>{user?.dailyUsage || 0}/5</strong> free messages today</p>
            <p>Upgrade now for unlimited access to all features!</p>
          </div>
        </div>

        <div className="plans-grid">
          {Object.entries(plans).map(([key, plan]) => (
            <div 
              key={key} 
              className={`plan-card ${plan.popular ? 'popular' : ''} ${plan.current ? 'current' : ''}`}
              style={{ borderColor: plan.color }}
            >
              {plan.popular && <div className="popular-badge">Most Popular</div>}
              {plan.current && <div className="current-badge">Current Plan</div>}
              
              <div className="plan-header">
                <h3 style={{ color: plan.color }}>{plan.name}</h3>
                <div className="plan-price">
                  <span className="price">${plan.price}</span>
                  <span className="period">/{plan.period}</span>
                </div>
                {plan.subtitle && (
                  <div className="plan-subtitle">
                    {plan.subtitle}
                  </div>
                )}
              </div>

              <div className="plan-features">
                <h4>Features:</h4>
                {plan.features.map((feature, index) => (
                  <div key={index} className="feature">
                    <span className="check">✅</span>
                    {feature}
                  </div>
                ))}
                
                {plan.limitations && (
                  <>
                    <h4>Limitations:</h4>
                    {plan.limitations.map((limitation, index) => (
                      <div key={index} className="limitation">
                        <span className="warning">⚠️</span>
                        {limitation}
                      </div>
                    ))}
                  </>
                )}
              </div>

              <button
                className="plan-button"
                style={{ 
                  backgroundColor: plan.color,
                  opacity: plan.current ? 0.6 : 1 
                }}
                disabled={plan.current || isLoading}
                onClick={() => handleUpgrade(key)}
              >
                {plan.current ? 'Current Plan' : 
                 key === 'free' ? 'Downgrade' :
                 isLoading ? 'Processing...' : 'Upgrade Now'}
              </button>
            </div>
          ))}
        </div>

        <div className="modal-footer">
          <p>💳 Secure payment powered by Stripe</p>
          <p>🔄 Cancel anytime • 💰 30-day money-back guarantee</p>
        </div>
      </div>
    </div>
  )
}

export default SubscriptionModal