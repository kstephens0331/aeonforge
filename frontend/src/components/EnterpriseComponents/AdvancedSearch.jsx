import React, { useState, useEffect, useRef } from 'react'
import './AdvancedSearch.css'

const AdvancedSearch = ({ onSearch, placeholder = "Search across all enterprise features..." }) => {
  const [query, setQuery] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  const [searchHistory, setSearchHistory] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [selectedFilter, setSelectedFilter] = useState('all')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState([])
  
  const searchRef = useRef(null)
  const inputRef = useRef(null)

  const searchFilters = [
    { id: 'all', label: 'All', icon: '🔍' },
    { id: 'code', label: 'Code', icon: '💻' },
    { id: 'models', label: 'AI Models', icon: '🤖' },
    { id: 'projects', label: 'Projects', icon: '📁' },
    { id: 'users', label: 'Team Members', icon: '👥' },
    { id: 'files', label: 'Files', icon: '📄' },
    { id: 'documentation', label: 'Docs', icon: '📖' }
  ]

  const searchSuggestions = [
    'Python code generation',
    'React component templates',
    'API integration patterns',
    'Database optimization',
    'Machine learning models',
    'Team collaboration tools',
    'Project deployment guides',
    'Security best practices',
    'Performance monitoring',
    'Code review workflows'
  ]

  const mockResults = {
    code: [
      { type: 'code', title: 'Authentication Service', description: 'JWT-based authentication with refresh tokens', language: 'Python', matches: 5 },
      { type: 'code', title: 'React Dashboard Component', description: 'Enterprise dashboard with real-time updates', language: 'JavaScript', matches: 3 },
      { type: 'code', title: 'Database Migration Script', description: 'PostgreSQL schema migration utilities', language: 'SQL', matches: 2 }
    ],
    models: [
      { type: 'model', title: 'Code Generation Model', description: 'Fine-tuned LLM for enterprise code generation', accuracy: 94.2, matches: 8 },
      { type: 'model', title: 'Documentation AI', description: 'Automated documentation generation from code', accuracy: 89.7, matches: 4 }
    ],
    projects: [
      { type: 'project', title: 'E-commerce Platform', description: 'Full-stack enterprise e-commerce solution', status: 'Active', matches: 12 },
      { type: 'project', title: 'AI Analytics Dashboard', description: 'Real-time analytics with ML insights', status: 'In Development', matches: 7 }
    ],
    users: [
      { type: 'user', title: 'Sarah Johnson', description: 'Senior Full-Stack Developer', role: 'Developer', matches: 3 },
      { type: 'user', title: 'Mike Chen', description: 'ML Engineer & AI Specialist', role: 'AI Engineer', matches: 6 }
    ]
  }

  useEffect(() => {
    const saved = localStorage.getItem('aeonforge_search_history')
    if (saved) {
      setSearchHistory(JSON.parse(saved))
    }
  }, [])

  useEffect(() => {
    if (query.length > 0) {
      const filtered = searchSuggestions.filter(suggestion =>
        suggestion.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 5)
      setSuggestions(filtered)
    } else {
      setSuggestions([])
    }
  }, [query])

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return

    setIsLoading(true)
    
    // Add to search history
    const newHistory = [searchQuery, ...searchHistory.filter(h => h !== searchQuery)].slice(0, 10)
    setSearchHistory(newHistory)
    localStorage.setItem('aeonforge_search_history', JSON.stringify(newHistory))

    // Mock search delay
    setTimeout(() => {
      const mockSearchResults = []
      
      if (selectedFilter === 'all') {
        Object.values(mockResults).forEach(categoryResults => {
          mockSearchResults.push(...categoryResults.filter(item => 
            item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.description.toLowerCase().includes(searchQuery.toLowerCase())
          ))
        })
      } else {
        const categoryResults = mockResults[selectedFilter] || []
        mockSearchResults.push(...categoryResults.filter(item => 
          item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.description.toLowerCase().includes(searchQuery.toLowerCase())
        ))
      }

      setResults(mockSearchResults.slice(0, 20))
      setIsLoading(false)
      
      if (onSearch) {
        onSearch({ query: searchQuery, filter: selectedFilter, results: mockSearchResults })
      }
    }, 800)

    setIsExpanded(true)
    setSuggestions([])
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
    if (e.key === 'Escape') {
      setIsExpanded(false)
      setQuery('')
      setSuggestions([])
    }
  }

  const selectSuggestion = (suggestion) => {
    setQuery(suggestion)
    handleSearch(suggestion)
  }

  const clearSearch = () => {
    setQuery('')
    setResults([])
    setIsExpanded(false)
    setSuggestions([])
  }

  const getResultIcon = (type) => {
    switch (type) {
      case 'code': return '💻'
      case 'model': return '🤖'
      case 'project': return '📁'
      case 'user': return '👥'
      default: return '📄'
    }
  }

  const getResultBadge = (item) => {
    switch (item.type) {
      case 'code':
        return <span className="result-badge language">{item.language}</span>
      case 'model':
        return <span className="result-badge accuracy">{item.accuracy}% Accuracy</span>
      case 'project':
        return <span className="result-badge status">{item.status}</span>
      case 'user':
        return <span className="result-badge role">{item.role}</span>
      default:
        return null
    }
  }

  return (
    <div className={`advanced-search ${isExpanded ? 'expanded' : ''}`} ref={searchRef}>
      <div className="search-container">
        <div className="search-input-container">
          <div className="search-icon">🔍</div>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={() => setIsExpanded(true)}
            placeholder={placeholder}
            className="search-input"
          />
          {query && (
            <button className="clear-search" onClick={clearSearch}>
              ✕
            </button>
          )}
        </div>

        {/* Search Filters */}
        <div className="search-filters">
          {searchFilters.map(filter => (
            <button
              key={filter.id}
              className={`filter-btn ${selectedFilter === filter.id ? 'active' : ''}`}
              onClick={() => setSelectedFilter(filter.id)}
            >
              <span className="filter-icon">{filter.icon}</span>
              <span className="filter-label">{filter.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Search Dropdown */}
      {isExpanded && (
        <div className="search-dropdown">
          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="search-section">
              <div className="section-header">
                <span>💡 Suggestions</span>
              </div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-item"
                  onClick={() => selectSuggestion(suggestion)}
                >
                  <span className="suggestion-icon">🔍</span>
                  <span className="suggestion-text">{suggestion}</span>
                </button>
              ))}
            </div>
          )}

          {/* Search History */}
          {searchHistory.length > 0 && suggestions.length === 0 && query === '' && (
            <div className="search-section">
              <div className="section-header">
                <span>🕒 Recent Searches</span>
                <button 
                  className="clear-history"
                  onClick={() => {
                    setSearchHistory([])
                    localStorage.removeItem('aeonforge_search_history')
                  }}
                >
                  Clear
                </button>
              </div>
              {searchHistory.slice(0, 5).map((item, index) => (
                <button
                  key={index}
                  className="history-item"
                  onClick={() => selectSuggestion(item)}
                >
                  <span className="history-icon">🕒</span>
                  <span className="history-text">{item}</span>
                </button>
              ))}
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="search-loading">
              <div className="loading-spinner-small"></div>
              <span>Searching across enterprise resources...</span>
            </div>
          )}

          {/* Search Results */}
          {results.length > 0 && !isLoading && (
            <div className="search-section">
              <div className="section-header">
                <span>📊 Results ({results.length})</span>
              </div>
              {results.map((result, index) => (
                <div key={index} className={`result-item ${result.type}`}>
                  <div className="result-icon">{getResultIcon(result.type)}</div>
                  <div className="result-content">
                    <div className="result-title">{result.title}</div>
                    <div className="result-description">{result.description}</div>
                    <div className="result-meta">
                      {getResultBadge(result)}
                      <span className="result-matches">{result.matches} matches</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* No Results */}
          {results.length === 0 && !isLoading && query.length > 2 && (
            <div className="search-empty">
              <div className="empty-icon">🔍</div>
              <div className="empty-title">No results found</div>
              <div className="empty-description">
                Try adjusting your search terms or filters
              </div>
            </div>
          )}
        </div>
      )}

      {/* Backdrop */}
      {isExpanded && (
        <div 
          className="search-backdrop"
          onClick={() => setIsExpanded(false)}
        />
      )}
    </div>
  )
}

export default AdvancedSearch