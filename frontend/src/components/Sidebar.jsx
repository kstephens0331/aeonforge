import React, { useState } from 'react'

function Sidebar({ 
  chats, 
  currentChatId, 
  activeTab, 
  onTabChange, 
  onNewChat, 
  onSelectChat, 
  onDeleteChat,
  apiKeys,
  onApiKeyChange 
}) {
  const [showApiKeys, setShowApiKeys] = useState(false)

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
      </div>

      {/* Chat Section */}
      {activeTab === 'chat' && (
        <div className="chat-section">
          <div className="chat-header">
            <button className="new-chat-btn" onClick={onNewChat}>
              <span>➕</span>
              New Chat
            </button>
          </div>
          
          <div className="chat-list">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                onClick={() => onSelectChat(chat.id)}
              >
                <div className="chat-content">
                  <div className="chat-title">{formatChatTitle(chat)}</div>
                  <div className="chat-time">{formatTime(chat.updatedAt)}</div>
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
            ))}
          </div>
        </div>
      )}

      {/* API Keys Section */}
      <div className="api-section">
        <button 
          className="api-toggle"
          onClick={() => setShowApiKeys(!showApiKeys)}
        >
          <span className="nav-icon">🔑</span>
          API Keys
          <span className={`arrow ${showApiKeys ? 'up' : 'down'}`}>▼</span>
        </button>
        
        {showApiKeys && (
          <div className="api-keys">
            <div className="api-key-group">
              <label>SerpAPI Key</label>
              <input
                type="password"
                value={apiKeys.serpapi}
                onChange={(e) => onApiKeyChange('serpapi', e.target.value)}
                placeholder="Web search & research"
              />
            </div>
            
            <div className="api-key-group">
              <label>NIH/PubMed Key</label>
              <input
                type="password"
                value={apiKeys.nih}
                onChange={(e) => onApiKeyChange('nih', e.target.value)}
                placeholder="Medical research access"
              />
            </div>
          </div>
        )}
      </div>

      {/* Status Indicator */}
      <div className="status-section">
        <div className="status-indicator">
          <div className="status-dot active"></div>
          <span>System Online</span>
        </div>
      </div>
    </div>
  )
}

export default Sidebar