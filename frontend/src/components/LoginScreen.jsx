import React, { useState } from 'react'
import './LoginScreen.css'

function LoginScreen({ onLogin, onSignup }) {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      if (isLogin) {
        await onLogin(formData.email, formData.password)
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match')
          setIsLoading(false)
          return
        }
        await onSignup(formData.email, formData.password, formData.name)
      }
    } catch (err) {
      setError(err.message || 'Authentication failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="login-screen">
      <div className="login-container">
        <div className="login-header">
          <h1>🚀 AeonForge</h1>
          <p>AI Development Platform</p>
        </div>

        <div className="login-tabs">
          <button 
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button 
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {!isLogin && (
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required={!isLogin}
                placeholder="Enter your full name"
              />
            </div>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              placeholder="Enter your password"
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required={!isLogin}
                placeholder="Confirm your password"
              />
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading ? '⏳ Processing...' : (isLogin ? 'Login' : 'Create Account')}
          </button>
        </form>

        <div className="login-footer">
          <div className="free-tier-info">
            <h3>🆓 Start Free</h3>
            <p>• 5 AI messages per day</p>
            <p>• Basic chat functionality</p>
            <p>• No file uploads</p>
            <p>• Community support</p>
          </div>
          
          <div className="premium-info">
            <h3>⭐ Premium Plans</h3>
            <p>• Standard ($10/mo): 100 messages/day</p>
            <p>• Pro ($15/mo): Unlimited messages</p>
            <p>• Enterprise ($50/mo): 2 seats + team features</p>
            <p>• All AI models (GPT-4, Claude, Gemini)</p>
            <p>• File uploads & project management</p>
            <p>• Medical research tools</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginScreen