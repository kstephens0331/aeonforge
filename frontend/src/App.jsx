import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './index.css'
import './sidebar-enhancements.css'
import './styles/brand.css'
import './styles/personal-tools.css'

// Import components
import Sidebar from './components/Sidebar'
import ChatInterface from './components/ChatInterface'
import ProjectsTab from './components/ProjectsTab'
import MedicalTool from './components/MedicalTool'
import PersonalTools from './components/PersonalTools'
import LoginScreen from './components/LoginScreen'
import SubscriptionModal from './components/SubscriptionModal'

function App() {
  // Authentication state
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false)
  const [authToken, setAuthToken] = useState(localStorage.getItem('aeonforge_token'))
  
  // App state
  const [activeTab, setActiveTab] = useState('chat')
  const [chats, setChats] = useState([])
  const [currentChatId, setCurrentChatId] = useState(null)
  
  // API keys are now handled server-side only for security
  const [serverInfo, setServerInfo] = useState({
    models: [],
    features: {},
    default_model: 'gpt-3.5-turbo'
  })

  // Initialize authentication and app data
  useEffect(() => {
    checkAuthStatus()
    fetchServerInfo()
  }, [])

  useEffect(() => {
    if (isAuthenticated && chats.length === 0) {
      createNewChat()
    }
  }, [isAuthenticated])

  const checkAuthStatus = async () => {
    if (authToken) {
      try {
        const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
        const response = await axios.get(`${apiUrl}/auth/verify`, {
          headers: { Authorization: `Bearer ${authToken}` }
        })
        setUser(response.data.user)
        setIsAuthenticated(true)
      } catch (error) {
        localStorage.removeItem('aeonforge_token')
        setAuthToken(null)
        setIsAuthenticated(false)
      }
    }
  }

  const fetchServerInfo = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      
      // Fetch server capabilities
      const [statusResponse, modelsResponse] = await Promise.all([
        axios.get(`${apiUrl}/`),
        axios.get(`${apiUrl}/models`).catch(() => ({ data: { available_models: [] } }))
      ])
      
      setServerInfo({
        models: modelsResponse.data.available_models || [],
        features: statusResponse.data.features || {},
        default_model: statusResponse.data.features?.default_model || 'gpt-3.5-turbo'
      })
    } catch (error) {
      console.warn('Could not fetch server info:', error)
    }
  }

  // Authentication functions
  const handleLogin = async (email, password) => {
    const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const response = await axios.post(`${apiUrl}/auth/login`, { email, password })
    
    const { token, user: userData } = response.data
    localStorage.setItem('aeonforge_token', token)
    setAuthToken(token)
    setUser(userData)
    setIsAuthenticated(true)
    
    // Show subscription modal for free users
    if (userData.plan === 'free' && userData.dailyUsage >= 3) {
      setShowSubscriptionModal(true)
    }
  }

  const handleSignup = async (email, password, name) => {
    const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const response = await axios.post(`${apiUrl}/auth/signup`, { email, password, name })
    
    const { token, user: userData } = response.data
    localStorage.setItem('aeonforge_token', token)
    setAuthToken(token)
    setUser(userData)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('aeonforge_token')
    setAuthToken(null)
    setUser(null)
    setIsAuthenticated(false)
    setChats([])
    setCurrentChatId(null)
  }

  const handleUpgrade = async (stripePriceId, planKey) => {
    const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const response = await axios.post(`${apiUrl}/payments/create-checkout`, {
      priceId: stripePriceId,
      plan: planKey
    }, {
      headers: { Authorization: `Bearer ${authToken}` }
    })
    
    // Redirect to Stripe checkout
    window.location.href = response.data.checkoutUrl
  }

  const createNewChat = () => {
    const now = Date.now()
    const newChatId = now.toString()
    const newChat = {
      id: newChatId,
      title: 'New Chat',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    setChats(prev => [newChat, ...prev])
    setCurrentChatId(newChatId)
  }

  const selectChat = (chatId) => {
    setCurrentChatId(chatId)
  }

  const getCurrentChat = () => {
    return chats.find(chat => chat.id === currentChatId) || null
  }

  const updateCurrentChat = (updates) => {
    setChats(prev => prev.map(chat => 
      chat.id === currentChatId 
        ? { ...chat, ...updates, updatedAt: new Date().toISOString() }
        : chat
    ))
  }

  const deleteChat = (chatId) => {
    setChats(prev => prev.filter(chat => chat.id !== chatId))
    if (currentChatId === chatId) {
      const remainingChats = chats.filter(chat => chat.id !== chatId)
      if (remainingChats.length > 0) {
        setCurrentChatId(remainingChats[0].id)
      } else {
        createNewChat()
      }
    }
  }


  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return (
      <LoginScreen 
        onLogin={handleLogin}
        onSignup={handleSignup}
      />
    )
  }

  // Main app for authenticated users
  return (
    <>
      <div className="app-container">
        <Sidebar
          chats={chats}
          currentChatId={currentChatId}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onNewChat={createNewChat}
          onSelectChat={selectChat}
          onDeleteChat={deleteChat}
          serverInfo={serverInfo}
          user={user}
          onLogout={handleLogout}
          onShowSubscription={() => setShowSubscriptionModal(true)}
        />

        <div className="main-content">
          {activeTab === 'chat' && (
            <ChatInterface
              currentChat={getCurrentChat()}
              onUpdateChat={updateCurrentChat}
              serverInfo={serverInfo}
              user={user}
              authToken={authToken}
              onShowSubscription={() => setShowSubscriptionModal(true)}
            />
          )}
          
          {activeTab === 'projects' && ['standard', 'pro', 'enterprise'].includes(user?.plan) && (
            <ProjectsTab 
              serverInfo={serverInfo} 
              user={user}
              authToken={authToken}
            />
          )}
          
          {activeTab === 'projects' && user?.plan === 'free' && (
            <div className="upgrade-required">
              <h2>🔒 Premium Feature</h2>
              <p>Project management requires a Standard, Pro, or Enterprise subscription</p>
              <button onClick={() => setShowSubscriptionModal(true)}>
                Upgrade Now
              </button>
            </div>
          )}
          
          {activeTab === 'medical' && ['pro', 'enterprise'].includes(user?.plan) && (
            <MedicalTool 
              serverInfo={serverInfo}
              user={user}
              authToken={authToken}
            />
          )}
          
          {activeTab === 'medical' && ['free', 'standard'].includes(user?.plan) && (
            <div className="upgrade-required">
              <h2>🔒 Premium Feature</h2>
              <p>Medical research tools require a Pro or Enterprise subscription</p>
              <button onClick={() => setShowSubscriptionModal(true)}>
                Upgrade Now
              </button>
            </div>
          )}
          
          {activeTab === 'personal' && (
            <PersonalTools 
              serverInfo={serverInfo}
              user={user}
              authToken={authToken}
            />
          )}
        </div>
      </div>

      {/* Subscription Modal */}
      <SubscriptionModal
        isOpen={showSubscriptionModal}
        onClose={() => setShowSubscriptionModal(false)}
        user={user}
        onUpgrade={handleUpgrade}
      />
    </>
  )
}

export default App