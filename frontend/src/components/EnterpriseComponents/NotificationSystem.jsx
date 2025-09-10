import React, { useState, useEffect } from 'react'
import './NotificationSystem.css'

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState([])
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      generateMockNotification()
    }, 8000)

    return () => clearInterval(interval)
  }, [])

  const notificationTypes = [
    {
      type: 'success',
      icon: '✅',
      titles: ['Code Generated Successfully', 'Model Training Complete', 'Deployment Successful', 'Test Suite Passed'],
      messages: [
        'Generated 150 lines of optimized Python code',
        'AI model training completed with 94.2% accuracy',
        'Application deployed to production environment',
        'All 47 test cases passed successfully'
      ]
    },
    {
      type: 'warning',
      icon: '⚠️',
      titles: ['High CPU Usage Detected', 'Memory Usage Alert', 'API Rate Limit Approaching'],
      messages: [
        'CPU usage at 85% - consider scaling resources',
        'Memory usage at 78% of allocated capacity',
        'API requests approaching rate limit threshold'
      ]
    },
    {
      type: 'info',
      icon: '💡',
      titles: ['New Feature Available', 'System Update', 'Performance Improvement'],
      messages: [
        'Advanced code refactoring tools now available',
        'System updated to v2.1.0 with enhanced AI capabilities',
        'Response times improved by 23% with latest optimizations'
      ]
    },
    {
      type: 'collaboration',
      icon: '👥',
      titles: ['New Team Member', 'Collaboration Request', 'Code Review Ready'],
      messages: [
        'Sarah Johnson joined your development team',
        'Mike Chen requested collaboration on React components',
        'Pull request #127 is ready for code review'
      ]
    }
  ]

  const generateMockNotification = () => {
    const typeData = notificationTypes[Math.floor(Math.random() * notificationTypes.length)]
    const titleIndex = Math.floor(Math.random() * typeData.titles.length)
    const messageIndex = Math.floor(Math.random() * typeData.messages.length)

    const notification = {
      id: Date.now() + Math.random(),
      type: typeData.type,
      icon: typeData.icon,
      title: typeData.titles[titleIndex],
      message: typeData.messages[messageIndex],
      timestamp: new Date(),
      isRead: false
    }

    setNotifications(prev => [notification, ...prev.slice(0, 9)])
    setIsVisible(true)

    setTimeout(() => {
      setIsVisible(false)
    }, 4000)
  }

  const markAsRead = (id) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, isRead: true } : notif
      )
    )
  }

  const dismissNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id))
  }

  const clearAllNotifications = () => {
    setNotifications([])
  }

  const unreadCount = notifications.filter(notif => !notif.isRead).length

  return (
    <div className="notification-system">
      <button 
        className={`notification-trigger ${unreadCount > 0 ? 'has-unread' : ''}`}
        onClick={() => setIsVisible(!isVisible)}
      >
        🔔
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount}</span>
        )}
      </button>

      {isVisible && (
        <div className="notification-panel">
          <div className="notification-header">
            <h3>Notifications</h3>
            <div className="notification-actions">
              {notifications.length > 0 && (
                <button 
                  className="clear-all-btn"
                  onClick={clearAllNotifications}
                  title="Clear all notifications"
                >
                  🗑️
                </button>
              )}
              <button 
                className="close-btn"
                onClick={() => setIsVisible(false)}
                title="Close notifications"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="notification-list">
            {notifications.length === 0 ? (
              <div className="no-notifications">
                <div className="empty-state">
                  <span>🔕</span>
                  <p>No notifications</p>
                  <small>You're all caught up!</small>
                </div>
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${notification.type} ${notification.isRead ? 'read' : 'unread'}`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="notification-icon">
                    {notification.icon}
                  </div>
                  
                  <div className="notification-content">
                    <div className="notification-title">
                      {notification.title}
                    </div>
                    <div className="notification-message">
                      {notification.message}
                    </div>
                    <div className="notification-time">
                      {notification.timestamp.toLocaleTimeString()}
                    </div>
                  </div>

                  <button
                    className="dismiss-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      dismissNotification(notification.id)
                    }}
                    title="Dismiss notification"
                  >
                    ✕
                  </button>
                </div>
              ))
            )}
          </div>

          <div className="notification-footer">
            <small>Real-time system notifications</small>
          </div>
        </div>
      )}
    </div>
  )
}

export default NotificationSystem