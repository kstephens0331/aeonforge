import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import FileUpload from './FileUpload'
import '../styles/fileupload.css'

function ChatInterface({ currentChat, onUpdateChat, serverInfo }) {
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [pendingApproval, setPendingApproval] = useState(null)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [showFileUpload, setShowFileUpload] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [currentChat?.messages])

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [currentChat?.id])

  const sendMessage = async () => {
    if ((!inputMessage.trim() && selectedFiles.length === 0) || isLoading || !currentChat) return

    let content = inputMessage.trim()
    if (selectedFiles.length > 0) {
      const filesList = selectedFiles.map(f => `📎 ${f.name} (${formatFileSize(f.size)})`).join('\n')
      content = content ? `${content}\n\n**Attached Files:**\n${filesList}` : `**Attached Files:**\n${filesList}`
    }

    const baseId = Date.now()
    const userMessage = {
      id: baseId,
      type: 'user',
      content: content,
      files: selectedFiles,
      timestamp: new Date().toISOString()
    }

    // Add user message immediately
    const updatedMessages = [...currentChat.messages, userMessage]
    onUpdateChat({ messages: updatedMessages })

    // Clear input, files, and show loading
    setInputMessage('')
    setSelectedFiles([])
    setShowFileUpload(false)
    setIsLoading(true)

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      // Use the new secure /chat endpoint - no API keys needed on frontend
      const response = await axios.post(`${apiUrl}/chat`, {
        message: inputMessage.trim(),
        conversation_id: currentChat.id || 'main',
        model: serverInfo.default_model || 'gpt-3.5-turbo'
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const botMessage = {
        id: baseId + 1,
        type: 'agent',
        content: response.data.response,
        agent: response.data.model_used,
        timestamp: response.data.timestamp || new Date().toISOString()
      }

      const finalMessages = [...updatedMessages, botMessage]
      onUpdateChat({ messages: finalMessages })

      // Handle approval if needed
      if (response.data.needs_approval) {
        setPendingApproval({
          conversationId: currentChat.id,
          task: response.data.approval_task,
          details: response.data.approval_details
        })
      }

      // Update chat title if it's still "New Chat"
      if (currentChat.messages.length <= 1) {
        let title = inputMessage.trim() || 'File Upload'
        title = title.slice(0, 40) + (title.length > 40 ? '...' : '')
        onUpdateChat({ title })
      }

    } catch (error) {
      console.error('Error sending message:', error)
      
      const errorMessage = {
        id: baseId + 2,
        type: 'system',
        content: '❌ Error: Unable to connect to Aeonforge backend. Please ensure the backend server is running.',
        timestamp: new Date().toISOString()
      }

      const finalMessages = [...updatedMessages, errorMessage]
      onUpdateChat({ messages: finalMessages })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleFilesSelected = (files) => {
    setSelectedFiles(files)
  }

  const toggleFileUpload = () => {
    setShowFileUpload(!showFileUpload)
  }

  const handleApproval = async (approved) => {
    if (!pendingApproval) return

    setIsLoading(true)
    setPendingApproval(null)

    try { 
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await axios.post(`${apiUrl}/api/approval`, {
        conversation_id: pendingApproval.conversationId || 'main',
        approved: approved
      })

      const approvalMessage = {
        id: Date.now() + Math.random(), // Use random to avoid conflicts
        type: 'agent',
        content: response.data.message,
        agent: response.data.agent,
        timestamp: new Date().toISOString()
      }

      const updatedMessages = [...currentChat.messages, approvalMessage]
      onUpdateChat({ messages: updatedMessages })

    } catch (error) {
      console.error('Error handling approval:', error)
      
      const errorMessage = {
        id: Date.now() + Math.random(), // Use random to avoid conflicts
        type: 'system',
        content: '❌ Error processing approval. Please try again.',
        timestamp: new Date().toISOString()
      }

      const updatedMessages = [...currentChat.messages, errorMessage]
      onUpdateChat({ messages: updatedMessages })
    } finally {
      setIsLoading(false)
    }
  }

  if (!currentChat) {
    return (
      <div className="chat-interface">
        <div className="no-chat">
          <h3>Select a chat to get started</h3>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-interface">
      {/* Chat Header */}
      <div className="chat-interface-header">
        <h2>{currentChat.title}</h2>
        <div className="chat-info">
          <span className="message-count">{currentChat.messages.length} messages</span>
          <span className="last-updated">
            Updated {new Date(currentChat.updatedAt).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {currentChat.messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            {message.type === 'agent' && (
              <div className="message-avatar">
                {message.agent === 'project_manager' ? 'PM' :
                 message.agent === 'senior_developer' ? 'SD' :
                 message.agent === 'assistant' ? 'AI' : 'A'}
              </div>
            )}
            <div className="message-content">
              {message.agent && message.type === 'agent' && (
                <div className="message-header">
                  {message.agent === 'project_manager' ? 'Project Manager' :
                   message.agent === 'senior_developer' ? 'Senior Developer' :
                   message.agent === 'assistant' ? 'Assistant' :
                   message.agent}
                </div>
              )}
              <div dangerouslySetInnerHTML={{ 
                __html: message.content
                  .replace(/\n/g, '<br />')
                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/`(.*?)`/g, '<code>$1</code>')
              }} />
            </div>
          </div>
        ))}

        {/* Approval prompt */}
        {pendingApproval && (
          <div className="approval-prompt">
            <strong>🤖 Approval Required</strong>
            <p><strong>Task:</strong> {pendingApproval.task}</p>
            {pendingApproval.details && (
              <p><strong>Details:</strong> {pendingApproval.details}</p>
            )}
            
            <div className="approval-buttons">
              <button 
                className="approval-button approve"
                onClick={() => handleApproval(true)}
                disabled={isLoading}
              >
                ✅ Approve
              </button>
              <button 
                className="approval-button reject"
                onClick={() => handleApproval(false)}
                disabled={isLoading}
              >
                ❌ Reject
              </button>
            </div>
          </div>
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="loading">
            AI is thinking<span className="loading-dots"></span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* File Upload Section */}
      {showFileUpload && (
        <div className="chat-file-upload">
          <FileUpload
            onFilesSelected={handleFilesSelected}
            maxFiles={50}
            context="chat"
            disabled={isLoading || pendingApproval}
          />
        </div>
      )}

      {/* Input */}
      <div className="chat-input-container">
        {selectedFiles.length > 0 && (
          <div className="selected-files-preview">
            <div className="files-preview-header">
              <span>📎 {selectedFiles.length} file(s) selected</span>
              <button 
                className="clear-files-btn"
                onClick={() => setSelectedFiles([])}
                disabled={isLoading}
              >
                Clear
              </button>
            </div>
            <div className="files-preview-list">
              {selectedFiles.slice(0, 3).map((fileObj) => (
                <div key={fileObj.id} className="file-preview-item">
                  <span className="file-name">{fileObj.name}</span>
                  <span className="file-size">({formatFileSize(fileObj.size)})</span>
                </div>
              ))}
              {selectedFiles.length > 3 && (
                <div className="file-preview-item more-files">
                  +{selectedFiles.length - 3} more files
                </div>
              )}
            </div>
          </div>
        )}
        
        <div className="chat-input">
          <button
            className="attach-button"
            onClick={toggleFileUpload}
            disabled={isLoading || pendingApproval}
            title="Attach Files"
          >
            📎
          </button>
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Message AeonForge AI... (coding, research, medical questions, general knowledge)"
            disabled={isLoading || pendingApproval}
            rows={1}
          />
          <button
            className="send-button"
            onClick={sendMessage}
            disabled={(!inputMessage.trim() && selectedFiles.length === 0) || isLoading || pendingApproval}
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface