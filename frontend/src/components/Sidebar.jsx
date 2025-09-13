import React, { useState } from 'react'

function Sidebar({ 
  chats, 
  currentChatId, 
  activeTab, 
  onTabChange, 
  onNewChat, 
  onSelectChat, 
  onDeleteChat,
  serverInfo
}) {
  const [showServerInfo, setShowServerInfo] = useState(false)

  const formatChatTitle = (chat) => {
    if (chat.messages.length > 1) {
      const firstUserMessage = chat.messages.find(m => m.type === 'user')
      if (firstUserMessage) {
        return firstUserMessage.content.slice(0, 40) + (firstUserMessage.content.length > 40 ? '...' : '')
      }
    }
    return 'New Chat'
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInHours = (now - date) / (1000 * 60 * 60)
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
    } else if (diffInHours < 7 * 24) {
      return date.toLocaleDateString('en-US', { weekday: 'short' })
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      })
    }
  }

  return (
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <h1>AeonForge</h1>
        <p>AI Development System</p>
      </div>

      {/* Navigation Tabs */}
      <div className="sidebar-nav">
        <button 
          className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => onTabChange('chat')}
        >
          <span className="nav-icon">💬</span>
          Chat
        </button>
        <button 
          className={`nav-tab ${activeTab === 'projects' ? 'active' : ''}`}
          onClick={() => onTabChange('projects')}
        >
          <span className="nav-icon">📁</span>
          Projects
        </button>
        <button 
          className={`nav-tab ${activeTab === 'medical' ? 'active' : ''}`}
          onClick={() => onTabChange('medical')}
        >
          <span className="nav-icon">🏥</span>
          Medical
        </button>
        <button 
          className={`nav-tab ${activeTab === 'personal' ? 'active' : ''}`}
          onClick={() => onTabChange('personal')}
        >
          <span className="nav-icon">🌟</span>
          Personal
        </button>
        <button 
          className={`nav-tab ${activeTab === 'legal' ? 'active' : ''}`}
          onClick={() => onTabChange('legal')}
        >
          <span className="nav-icon">⚖️</span>
          Legal
        </button>
        <button 
          className={`nav-tab ${activeTab === 'business' ? 'active' : ''}`}
          onClick={() => onTabChange('business')}
        >
          <span className="nav-icon">🏢</span>
          Business
        </button>
        <button 
          className={`nav-tab ${activeTab === 'realestate' ? 'active' : ''}`}
          onClick={() => onTabChange('realestate')}
        >
          <span className="nav-icon">🏠</span>
          Real Estate
        </button>
        <button 
          className={`nav-tab ${activeTab === 'marketing' ? 'active' : ''}`}
          onClick={() => onTabChange('marketing')}
        >
          <span className="nav-icon">📢</span>
          Marketing
        </button>
        <button 
          className={`nav-tab ${activeTab === 'tax' ? 'active' : ''}`}
          onClick={() => onTabChange('tax')}
        >
          <span className="nav-icon">🧮</span>
          Tax
        </button>
        <button 
          className={`nav-tab ${activeTab === 'education' ? 'active' : ''}`}
          onClick={() => onTabChange('education')}
        >
          <span className="nav-icon">🎓</span>
          Education
        </button>
        <button 
          className={`nav-tab ${activeTab === 'construction' ? 'active' : ''}`}
          onClick={() => onTabChange('construction')}
        >
          <span className="nav-icon">🏗️</span>
          Construction
        </button>
        <button 
          className={`nav-tab ${activeTab === 'retail' ? 'active' : ''}`}
          onClick={() => onTabChange('retail')}
        >
          <span className="nav-icon">🛒</span>
          Retail
        </button>
        <button 
          className={`nav-tab ${activeTab === 'agriculture' ? 'active' : ''}`}
          onClick={() => onTabChange('agriculture')}
        >
          <span className="nav-icon">🌾</span>
          Agriculture
        </button>
      </div>

      {/* Chat Section - Expanded */}
      {activeTab === 'chat' && (
        <div className="chat-section expanded">
          <div className="chat-header">
            <button className="new-chat-btn" onClick={onNewChat}>
              <span>➕</span>
              New Chat
            </button>
            <div className="chat-count">
              {chats.length} conversation{chats.length !== 1 ? 's' : ''}
            </div>
          </div>
          
          <div className="chat-list expanded">
            {chats.length === 0 ? (
              <div className="empty-chat-list">
                <p>No conversations yet</p>
                <p>Start your first chat!</p>
              </div>
            ) : (
              chats.map((chat) => (
                <div
                  key={chat.id}
                  className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                  onClick={() => onSelectChat(chat.id)}
                >
                  <div className="chat-content">
                    <div className="chat-title">{formatChatTitle(chat)}</div>
                    <div className="chat-meta">
                      <span className="chat-time">{formatTime(chat.updatedAt)}</span>
                      <span className="message-count">{chat.messages.length} msgs</span>
                    </div>
                  </div>
                  <button
                    className="delete-chat-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteChat(chat.id)
                    }}
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Status Section */}
      <div className="status-section">
        <div className="status-header">
          <div className="status-indicator">
            <div className="status-dot active"></div>
            <span>System Online</span>
          </div>
          <button 
            className="status-toggle"
            onClick={() => setShowServerInfo(!showServerInfo)}
          >
            <span className={`arrow ${showServerInfo ? 'up' : 'down'}`}>▼</span>
          </button>
        </div>
        
        {showServerInfo && (
          <div className="status-details">
            <div className="feature-status">
              <div className="feature-item">
                <span className="feature-label">AI Chat</span>
                <span className="feature-status-icon">
                  {serverInfo.features?.openai_available || serverInfo.features?.anthropic_available || serverInfo.features?.google_available ? '✅' : '❌'}
                </span>
              </div>
              <div className="feature-item">
                <span className="feature-label">OpenAI</span>
                <span className="feature-status-icon">
                  {serverInfo.features?.openai_available ? '✅' : '❌'}
                </span>
              </div>
              <div className="feature-item">
                <span className="feature-label">Anthropic</span>
                <span className="feature-status-icon">
                  {serverInfo.features?.anthropic_available ? '✅' : '❌'}
                </span>
              </div>
              <div className="feature-item">
                <span className="feature-label">Google</span>
                <span className="feature-status-icon">
                  {serverInfo.features?.google_available ? '✅' : '❌'}
                </span>
              </div>
              <div className="feature-item">
                <span className="feature-label">Web Search</span>
                <span className="feature-status-icon">
                  {serverInfo.features?.search_available ? '✅' : '❌'}
                </span>
              </div>
              <div className="feature-item">
                <span className="feature-label">NIH/PubMed</span>
                <span className="feature-status-icon">
                  {serverInfo.features?.nih_available ? '✅' : '❌'}
                </span>
              </div>
              <div className="feature-item">
                <span className="feature-label">File Upload</span>
                <span className="feature-status-icon">✅</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Sidebar