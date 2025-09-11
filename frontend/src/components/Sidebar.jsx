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

      {/* Server Info Section */}
      <div className="api-section">
        <button 
          className="api-toggle"
          onClick={() => setShowServerInfo(!showServerInfo)}
        >
          <span className="nav-icon">⚙️</span>
          Server Info
          <span className={`arrow ${showServerInfo ? 'up' : 'down'}`}>▼</span>
        </button>
        
        {showServerInfo && (
          <div className="api-keys">
            <div className="server-info-group">
              <label>Available Models: {serverInfo.models?.length || 0}</label>
              <div className="model-list">
                {serverInfo.models?.map(model => (
                  <div key={model} className="model-item">{model}</div>
                )) || <div className="model-item">Loading...</div>}
              </div>
            </div>
            
            <div className="server-info-group">
              <label>Default Model</label>
              <div className="model-item">{serverInfo.default_model || 'gpt-3.5-turbo'}</div>
            </div>
            
            <div className="server-info-group">
              <label>Features</label>
              <div className="feature-list">
                <div className="feature-item">
                  OpenAI: {serverInfo.features?.openai_available ? '✅' : '❌'}
                </div>
                <div className="feature-item">
                  Anthropic: {serverInfo.features?.anthropic_available ? '✅' : '❌'}
                </div>
                <div className="feature-item">
                  Search: {serverInfo.features?.search_available ? '✅' : '❌'}
                </div>
              </div>
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