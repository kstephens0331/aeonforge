import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import FileUpload from './FileUpload'
import MedicalEducation from './MedicalEducation'
import '../styles/fileupload.css'

function MedicalTool({ apiKeys }) {
  const [activeMode, setActiveMode] = useState('research')
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [searchHistory, setSearchHistory] = useState([])
  const [savedResearch, setSavedResearch] = useState([])
  const [selectedFiles, setSelectedFiles] = useState([])
  const [showFileUpload, setShowFileUpload] = useState(false)
  
  const modes = {
    research: {
      title: 'Medical Research',
      icon: '🔬',
      description: 'Access NIH databases, PubMed, clinical trials, and medical literature'
    },
    diagnosis: {
      title: 'Diagnostic Assistant',
      icon: '🩺',
      description: 'Symptom analysis and differential diagnosis support'
    },
    education: {
      title: 'Interactive Study',
      icon: '📚',
      description: 'Upload content and get AI-generated questions for personalized learning'
    },
    clinical: {
      title: 'Clinical Guidelines',
      icon: '📋',
      description: 'Treatment protocols, drug interactions, and clinical decision support'
    }
  }

  useEffect(() => {
    loadSearchHistory()
    loadSavedResearch()
  }, [])

  const loadSearchHistory = () => {
    const saved = localStorage.getItem('medical-search-history')
    if (saved) {
      setSearchHistory(JSON.parse(saved))
    }
  }

  const loadSavedResearch = () => {
    const saved = localStorage.getItem('medical-saved-research')
    if (saved) {
      setSavedResearch(JSON.parse(saved))
    }
  }

  const saveToHistory = (query, results) => {
    const entry = {
      id: Date.now(),
      query,
      mode: activeMode,
      timestamp: new Date().toISOString(),
      resultCount: results?.sources?.length || 0
    }
    
    const updated = [entry, ...searchHistory.slice(0, 49)] // Keep last 50
    setSearchHistory(updated)
    localStorage.setItem('medical-search-history', JSON.stringify(updated))
  }

  const saveResearch = (title, content) => {
    const entry = {
      id: Date.now(),
      title,
      content,
      mode: activeMode,
      query: query,
      timestamp: new Date().toISOString()
    }
    
    const updated = [entry, ...savedResearch]
    setSavedResearch(updated)
    localStorage.setItem('medical-saved-research', JSON.stringify(updated))
  }

  const performMedicalSearch = async () => {
    if (!query.trim() && selectedFiles.length === 0) return

    setIsLoading(true)
    setResults(null)

    try {
      // Prepare form data for file upload
      const formData = new FormData()
      let searchQuery = query.trim()
      
      if (selectedFiles.length > 0) {
        const filesList = selectedFiles.map(f => `📎 ${f.name} (${(f.size / 1024 / 1024).toFixed(2)} MB)`).join('\n')
        searchQuery = searchQuery ? `${searchQuery}\n\nMedical Files for Analysis:\n${filesList}` : `Medical Files for Analysis:\n${filesList}`
        
        // Add files to form data
        selectedFiles.forEach((fileObj, index) => {
          formData.append(`file_${index}`, fileObj.file)
        })
        formData.append('file_count', selectedFiles.length.toString())
      } else {
        formData.append('file_count', '0')
      }
      
      formData.append('mode', activeMode)
      formData.append('query', searchQuery)
      formData.append('apiKeys', JSON.stringify(apiKeys))

      // Simulate medical research - in real implementation, this would call specialized medical APIs
      const response = await axios.post('http://localhost:8000/api/medical-search', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      setResults(response.data)
      saveToHistory(searchQuery, response.data)
      
      // Clear files after successful search
      setSelectedFiles([])
      setShowFileUpload(false)

    } catch (error) {
      console.error('Medical search error:', error)
      
      // Fallback to regular web search with medical focus
      try {
        // Prepare fallback form data
        const fallbackFormData = new FormData()
        let fallbackMessage = `Medical ${activeMode} search: ${query}. Please provide comprehensive medical information, research findings, and relevant studies.`
        
        if (selectedFiles.length > 0) {
          const filesList = selectedFiles.map(f => `📎 ${f.name}`).join('\n')
          fallbackMessage += `\n\nAnalyze these medical files:\n${filesList}`
          
          selectedFiles.forEach((fileObj, index) => {
            fallbackFormData.append(`file_${index}`, fileObj.file)
          })
          fallbackFormData.append('file_count', selectedFiles.length.toString())
        } else {
          fallbackFormData.append('file_count', '0')
        }
        
        fallbackFormData.append('message', fallbackMessage)
        fallbackFormData.append('conversation_id', `medical_${Date.now()}`)
        fallbackFormData.append('api_keys', JSON.stringify(apiKeys))

        const fallbackResponse = await axios.post('http://localhost:8000/api/chat', fallbackFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        const mockResults = {
          query: searchQuery,
          mode: activeMode,
          summary: fallbackResponse.data.message,
          sources: [
            {
              title: 'Medical Research Results',
              content: fallbackResponse.data.message,
              source: 'AeonForge Medical AI',
              relevance: 95
            }
          ],
          suggestions: [
            `Related ${activeMode} topics for "${query}"`,
            `Clinical trials related to "${query}"`,
            `Recent studies on "${query}"`
          ]
        }

        setResults(mockResults)
        saveToHistory(searchQuery, mockResults)
        
        // Clear files after fallback search
        setSelectedFiles([])
        setShowFileUpload(false)

      } catch (fallbackError) {
        console.error('Fallback search error:', fallbackError)
        
        setResults({
          query: searchQuery,
          mode: activeMode,
          error: 'Unable to perform medical search. Please check your connection and API keys.',
          sources: []
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  const getPlaceholderText = () => {
    switch (activeMode) {
      case 'research':
        return 'e.g., "Latest research on CRISPR gene therapy", "COVID-19 treatment protocols"'
      case 'diagnosis':
        return 'e.g., "Chest pain with shortness of breath", "Differential diagnosis for headache"'
      case 'education':
        return 'e.g., "Cardiology case studies", "Pharmacology study guide for beta blockers"'
      case 'clinical':
        return 'e.g., "Hypertension treatment guidelines", "Drug interactions with warfarin"'
      default:
        return 'Enter your medical query...'
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      performMedicalSearch()
    }
  }

  const handleFilesSelected = (files) => {
    setSelectedFiles(files)
  }

  const toggleFileUpload = () => {
    setShowFileUpload(!showFileUpload)
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  return (
    <div className="medical-tool">
      {/* Header */}
      <div className="medical-header">
        <div className="header-content">
          <h1>🏥 Medical Research & Education Tool</h1>
          <p>AI-powered medical research, diagnosis support, and educational resources</p>
        </div>
      </div>

      {/* Mode Selection */}
      <div className="medical-modes">
        {Object.entries(modes).map(([key, mode]) => (
          <button
            key={key}
            className={`mode-button ${activeMode === key ? 'active' : ''}`}
            onClick={() => setActiveMode(key)}
          >
            <span className="mode-icon">{mode.icon}</span>
            <div className="mode-content">
              <div className="mode-title">{mode.title}</div>
              <div className="mode-description">{mode.description}</div>
            </div>
          </button>
        ))}
      </div>

      {/* File Upload Section */}
      {showFileUpload && (
        <div className="medical-file-upload">
          <FileUpload
            onFilesSelected={handleFilesSelected}
            maxFiles={50}
            context="medical"
            disabled={isLoading}
          />
        </div>
      )}

      {/* Search Interface */}
      <div className="medical-search">
        <div className="search-container">
          {selectedFiles.length > 0 && (
            <div className="selected-files-preview">
              <div className="files-preview-header">
                <span>📎 {selectedFiles.length} medical file(s) selected for analysis</span>
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
          
          <div className="search-input-group">
            <button
              className="attach-button"
              onClick={toggleFileUpload}
              disabled={isLoading}
              title="Upload Medical Files"
            >
              📎
            </button>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={getPlaceholderText()}
              rows={3}
              disabled={isLoading}
            />
            <button
              className="search-button"
              onClick={performMedicalSearch}
              disabled={(!query.trim() && selectedFiles.length === 0) || isLoading}
            >
              {isLoading ? '⏳' : '🔍'} Search
            </button>
          </div>
          
          <div className="search-info">
            <span className="current-mode">
              {modes[activeMode].icon} {modes[activeMode].title} Mode
            </span>
            {apiKeys.nih ? (
              <span className="api-status connected">🟢 NIH/PubMed Connected</span>
            ) : (
              <span className="api-status disconnected">🔴 NIH/PubMed API Key Required</span>
            )}
          </div>
        </div>
      </div>

      <div className="medical-content">
        {/* Education Mode - Special Component */}
        {activeMode === 'education' ? (
          <MedicalEducation apiKeys={apiKeys} />
        ) : (
          <div className="medical-results">
          {isLoading && (
            <div className="loading-medical">
              <div className="loading-spinner"></div>
              <p>Searching medical databases...</p>
            </div>
          )}

          {results && (
            <div className="results-container">
              <div className="results-header">
                <h3>
                  {modes[results.mode].icon} {modes[results.mode].title} Results
                </h3>
                <div className="results-meta">
                  <span>Query: "{results.query}"</span>
                  <button
                    className="save-research-btn"
                    onClick={() => saveResearch(results.query, results)}
                  >
                    💾 Save Research
                  </button>
                </div>
              </div>

              {results.error ? (
                <div className="results-error">
                  <p>{results.error}</p>
                </div>
              ) : (
                <>
                  {results.summary && (
                    <div className="results-summary">
                      <h4>Summary</h4>
                      <div 
                        dangerouslySetInnerHTML={{
                          __html: results.summary
                            .replace(/\n/g, '<br />')
                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        }}
                      />
                    </div>
                  )}

                  {results.sources && results.sources.length > 0 && (
                    <div className="results-sources">
                      <h4>Sources ({results.sources.length})</h4>
                      {results.sources.map((source, index) => (
                        <div key={index} className="source-item">
                          <div className="source-header">
                            <h5>{source.title}</h5>
                            {source.relevance && (
                              <span className="relevance">{source.relevance}% relevant</span>
                            )}
                          </div>
                          <div className="source-content">
                            {source.content}
                          </div>
                          <div className="source-meta">
                            <span className="source-name">{source.source}</span>
                            {source.date && (
                              <span className="source-date">{source.date}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {results.suggestions && results.suggestions.length > 0 && (
                    <div className="results-suggestions">
                      <h4>Related Searches</h4>
                      <div className="suggestion-list">
                        {results.suggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            className="suggestion-item"
                            onClick={() => setQuery(suggestion)}
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
          </div>
        )}

        {/* Sidebar - Hide when in education mode */}
        {activeMode !== 'education' && (
        <div className="medical-sidebar">
          {/* Search History */}
          <div className="sidebar-section">
            <h4>Recent Searches</h4>
            <div className="history-list">
              {searchHistory.slice(0, 10).map((item) => (
                <div
                  key={item.id}
                  className="history-item"
                  onClick={() => setQuery(item.query)}
                >
                  <div className="history-query">
                    {modes[item.mode].icon} {item.query}
                  </div>
                  <div className="history-meta">
                    {formatTimestamp(item.timestamp)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Saved Research */}
          <div className="sidebar-section">
            <h4>Saved Research</h4>
            <div className="saved-list">
              {savedResearch.slice(0, 5).map((item) => (
                <div key={item.id} className="saved-item">
                  <div className="saved-title">
                    {modes[item.mode].icon} {item.title}
                  </div>
                  <div className="saved-meta">
                    {formatTimestamp(item.timestamp)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Medical Resources */}
          <div className="sidebar-section">
            <h4>Quick Resources</h4>
            <div className="resource-links">
              <a href="#" className="resource-link">
                📚 Medical Textbooks
              </a>
              <a href="#" className="resource-link">
                🧬 Drug Database
              </a>
              <a href="#" className="resource-link">
                🏥 Clinical Calculators
              </a>
              <a href="#" className="resource-link">
                📊 Medical Statistics
              </a>
            </div>
          </div>
        </div>
        )}
      </div>
    </div>
  )
}

export default MedicalTool