import React, { useState, useEffect } from 'react'
import axios from 'axios'
import RealTimeChart from './RealTimeChart'
import NotificationSystem from './NotificationSystem'
import AdvancedSearch from './AdvancedSearch'
import './SystemDashboard.css'

function SystemDashboard() {
  const [systemStatus, setSystemStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSystemStatus()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchSystemStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchSystemStatus = async () => {
    try {
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/system/status`;
      const response = await axios.get(apiUrl)
      setSystemStatus(response.data)
      setError(null)
    } catch (error) {
      console.error('Error fetching system status:', error)
      setError('Failed to fetch system status')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="system-dashboard">
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <p>Loading system status...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="system-dashboard">
        <div className="dashboard-error">
          <h3>⚠️ System Status Error</h3>
          <p>{error}</p>
          <button onClick={fetchSystemStatus} className="retry-btn">
            🔄 Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="system-dashboard">
      <NotificationSystem />
      <div className="dashboard-header">
        <h1>🚀 AeonForge Enterprise Dashboard</h1>
        <div className="status-indicator">
          <span className={`status-badge ${systemStatus?.status?.toLowerCase()}`}>
            {systemStatus?.status || 'Unknown'}
          </span>
        </div>
      </div>

      <AdvancedSearch 
        onSearch={(searchData) => {
          console.log('Search performed:', searchData)
        }}
        placeholder="Search code, models, projects, team members..."
      />

      <div className="dashboard-grid">
        {/* System Overview Card */}
        <div className="dashboard-card system-overview">
          <div className="card-header">
            <h3>📊 System Overview</h3>
            <span className="version-badge">v{systemStatus?.version}</span>
          </div>
          <div className="card-content">
            <div className="stat-item">
              <span className="stat-label">System:</span>
              <span className="stat-value">{systemStatus?.system}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Last Updated:</span>
              <span className="stat-value">
                {systemStatus?.timestamp ? new Date(systemStatus.timestamp).toLocaleString() : 'N/A'}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Enterprise Features:</span>
              <span className={`stat-value ${systemStatus?.enterprise_features ? 'enabled' : 'disabled'}`}>
                {systemStatus?.enterprise_features ? '✅ Active' : '⚠️ Disabled'}
              </span>
            </div>
          </div>
        </div>

        {/* AI Orchestrator Card */}
        {systemStatus?.ai_orchestrator && (
          <div className="dashboard-card ai-orchestrator">
            <div className="card-header">
              <h3>🤖 AI Orchestrator</h3>
              <span className={`health-badge ${systemStatus.ai_orchestrator.system_health?.toLowerCase()}`}>
                {systemStatus.ai_orchestrator.system_health}
              </span>
            </div>
            <div className="card-content">
              <div className="stat-grid">
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.ai_orchestrator.total_models}</span>
                  <span className="stat-label">Models</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.ai_orchestrator.active_models}</span>
                  <span className="stat-label">Active</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.ai_orchestrator.total_requests}</span>
                  <span className="stat-label">Requests</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">
                    {(systemStatus.ai_orchestrator.success_rate * 100).toFixed(1)}%
                  </span>
                  <span className="stat-label">Success Rate</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Collaboration Engine Card */}
        {systemStatus?.collaboration && (
          <div className="dashboard-card collaboration">
            <div className="card-header">
              <h3>👥 Collaboration Engine</h3>
              <span className={`health-badge ${systemStatus.collaboration.system_health?.toLowerCase()}`}>
                {systemStatus.collaboration.system_health}
              </span>
            </div>
            <div className="card-content">
              <div className="stat-grid">
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.collaboration.active_sessions}</span>
                  <span className="stat-label">Active Sessions</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.collaboration.active_users}</span>
                  <span className="stat-label">Active Users</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.collaboration.messages_sent}</span>
                  <span className="stat-label">Messages</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.collaboration.ai_interactions}</span>
                  <span className="stat-label">AI Interactions</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Code Intelligence Card */}
        {systemStatus?.code_intelligence && (
          <div className="dashboard-card code-intelligence">
            <div className="card-header">
              <h3>💡 Code Intelligence</h3>
              <span className={`health-badge ${systemStatus.code_intelligence.system_health?.toLowerCase()}`}>
                {systemStatus.code_intelligence.system_health}
              </span>
            </div>
            <div className="card-content">
              <div className="stat-grid">
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.code_intelligence.code_generated}</span>
                  <span className="stat-label">Code Generated</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.code_intelligence.lines_generated}</span>
                  <span className="stat-label">Lines of Code</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{systemStatus.code_intelligence.languages_supported}</span>
                  <span className="stat-label">Languages</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">
                    {systemStatus.code_intelligence.average_quality_score?.toFixed(1) || 'N/A'}
                  </span>
                  <span className="stat-label">Avg Quality</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Performance Metrics Card */}
        <div className="dashboard-card performance-metrics">
          <div className="card-header">
            <h3>📈 Performance Metrics</h3>
          </div>
          <div className="card-content">
            <div className="metrics-grid">
              <RealTimeChart 
                title="CPU Usage" 
                chartType="line" 
                height={120}
                color="#00d4ff"
                realTimeUpdate={true}
              />
              <RealTimeChart 
                title="Memory Usage" 
                chartType="line" 
                height={120}
                color="#ff00ff"
                realTimeUpdate={true}
              />
              <RealTimeChart 
                title="Network I/O" 
                chartType="bar" 
                height={120}
                color="#00ff88"
                realTimeUpdate={true}
              />
              <RealTimeChart 
                title="API Response Time" 
                chartType="line" 
                height={120}
                color="#ffc107"
                realTimeUpdate={true}
              />
            </div>
          </div>
        </div>

        {/* Quick Actions Card */}
        <div className="dashboard-card quick-actions">
          <div className="card-header">
            <h3>⚡ Quick Actions</h3>
          </div>
          <div className="card-content">
            <div className="action-buttons">
              <button className="action-btn primary">
                🚀 Generate Code
              </button>
              <button className="action-btn secondary">
                👥 Start Collaboration
              </button>
              <button className="action-btn tertiary">
                📊 View Analytics
              </button>
              <button className="action-btn quaternary">
                ⚙️ System Settings
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-footer">
        <p>Last refreshed: {new Date().toLocaleTimeString()}</p>
        <button onClick={fetchSystemStatus} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>
    </div>
  )
}

export default SystemDashboard