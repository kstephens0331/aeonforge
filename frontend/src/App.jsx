import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './index.css'

// Import components
import Sidebar from './components/Sidebar'
import ChatInterface from './components/ChatInterface'
import ProjectsTab from './components/ProjectsTab'
import MedicalTool from './components/MedicalTool'

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [chats, setChats] = useState([])
  const [currentChatId, setCurrentChatId] = useState(null)
  // API keys are now handled server-side only for security
  const [serverInfo, setServerInfo] = useState({
    models: [],
    features: {},
    default_model: 'gpt-3.5-turbo'
  })

  // Initialize with first chat and fetch server capabilities
  useEffect(() => {
    if (chats.length === 0) {
      createNewChat()
    }
    fetchServerInfo()
  }, [])

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

  const createNewChat = () => {
    const now = Date.now()
    const newChatId = now.toString()
    const newChat = {
      id: newChatId,
      title: 'New Chat',
      messages: [{
        id: now + 1, // Ensure unique ID by adding 1
        type: 'system',
        content: 'Aeonforge AI Development System ready! Ask me anything - from coding projects to medical research.',
        timestamp: new Date().toISOString()
      }],
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


  return (
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
      />

      <div className="main-content">
        {activeTab === 'chat' && (
          <ChatInterface
            currentChat={getCurrentChat()}
            onUpdateChat={updateCurrentChat}
            serverInfo={serverInfo}
          />
        )}
        
        {activeTab === 'projects' && (
          <ProjectsTab serverInfo={serverInfo} />
        )}
        
        {activeTab === 'medical' && (
          <MedicalTool serverInfo={serverInfo} />
        )}
      </div>
    </div>
  )
}

export default App