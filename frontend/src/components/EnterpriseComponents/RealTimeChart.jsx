import React, { useState, useEffect, useRef } from 'react'
import './RealTimeChart.css'

const RealTimeChart = ({ 
  title, 
  data = [], 
  chartType = 'line',
  height = 200,
  color = '#00d4ff',
  realTimeUpdate = true,
  maxDataPoints = 50 
}) => {
  const [chartData, setChartData] = useState(data)
  const [isAnimating, setIsAnimating] = useState(false)
  const chartRef = useRef(null)
  const animationRef = useRef(null)

  useEffect(() => {
    if (realTimeUpdate && data.length > 0) {
      setIsAnimating(true)
      setTimeout(() => setIsAnimating(false), 300)
      
      setChartData(prevData => {
        const newData = [...prevData, ...data].slice(-maxDataPoints)
        return newData
      })
    }
  }, [data, realTimeUpdate, maxDataPoints])

  useEffect(() => {
    if (realTimeUpdate) {
      const interval = setInterval(() => {
        const newValue = Math.random() * 100 + Math.sin(Date.now() / 1000) * 20
        setChartData(prevData => {
          const newData = [...prevData, { 
            timestamp: new Date(), 
            value: newValue,
            id: Date.now()
          }].slice(-maxDataPoints)
          return newData
        })
        setIsAnimating(true)
        setTimeout(() => setIsAnimating(false), 300)
      }, 2000)

      return () => clearInterval(interval)
    }
  }, [realTimeUpdate, maxDataPoints])

  const renderLineChart = () => {
    if (chartData.length < 2) return null

    const maxValue = Math.max(...chartData.map(d => d.value))
    const minValue = Math.min(...chartData.map(d => d.value))
    const range = maxValue - minValue || 1

    const points = chartData.map((point, index) => {
      const x = (index / (chartData.length - 1)) * 100
      const y = 100 - ((point.value - minValue) / range) * 80 - 10
      return `${x},${y}`
    }).join(' ')

    const path = `M ${points.replace(/,/g, ' L ').substring(2)}`

    return (
      <svg className="chart-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
        <defs>
          <linearGradient id={`gradient-${title}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.3"/>
            <stop offset="100%" stopColor={color} stopOpacity="0.05"/>
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <path
          d={`${path} L 100,100 L 0,100 Z`}
          fill={`url(#gradient-${title})`}
          className="chart-area"
        />
        
        <path
          d={path}
          fill="none"
          stroke={color}
          strokeWidth="0.5"
          filter="url(#glow)"
          className={`chart-line ${isAnimating ? 'animating' : ''}`}
        />
        
        {chartData.slice(-1).map((point, index) => {
          const x = 100
          const y = 100 - ((point.value - minValue) / range) * 80 - 10
          return (
            <circle
              key={point.id || index}
              cx={x}
              cy={y}
              r="0.8"
              fill={color}
              className={`chart-point ${isAnimating ? 'pulse' : ''}`}
            />
          )
        })}
      </svg>
    )
  }

  const renderBarChart = () => {
    if (chartData.length === 0) return null

    const maxValue = Math.max(...chartData.map(d => d.value))
    const recentData = chartData.slice(-10)

    return (
      <div className="bar-chart-container">
        {recentData.map((point, index) => {
          const height = (point.value / maxValue) * 100
          return (
            <div
              key={point.id || index}
              className={`chart-bar ${isAnimating && index === recentData.length - 1 ? 'new-bar' : ''}`}
              style={{
                height: `${height}%`,
                background: `linear-gradient(0deg, ${color}, ${color}80)`,
                animationDelay: `${index * 50}ms`
              }}
              title={`Value: ${point.value.toFixed(1)}`}
            />
          )
        })}
      </div>
    )
  }

  const getCurrentValue = () => {
    if (chartData.length === 0) return '0'
    return chartData[chartData.length - 1].value.toFixed(1)
  }

  const getTrend = () => {
    if (chartData.length < 2) return 'neutral'
    const recent = chartData.slice(-5)
    const average = recent.reduce((sum, point) => sum + point.value, 0) / recent.length
    const current = chartData[chartData.length - 1].value
    
    if (current > average * 1.05) return 'up'
    if (current < average * 0.95) return 'down'
    return 'neutral'
  }

  const trend = getTrend()

  return (
    <div className={`real-time-chart ${isAnimating ? 'updating' : ''}`} ref={chartRef}>
      <div className="chart-header">
        <h4 className="chart-title">{title}</h4>
        <div className="chart-indicators">
          <span className={`trend-indicator ${trend}`}>
            {trend === 'up' && '📈'}
            {trend === 'down' && '📉'}
            {trend === 'neutral' && '➡️'}
          </span>
          <span className="current-value" style={{ color }}>
            {getCurrentValue()}
          </span>
        </div>
      </div>
      
      <div className="chart-content" style={{ height: `${height}px` }}>
        {chartType === 'line' ? renderLineChart() : renderBarChart()}
        
        {chartData.length === 0 && (
          <div className="chart-empty">
            <div className="loading-dots">
              <div></div>
              <div></div>
              <div></div>
            </div>
            <p>Waiting for data...</p>
          </div>
        )}
      </div>
      
      {realTimeUpdate && (
        <div className="chart-footer">
          <div className="live-indicator">
            <div className="pulse-dot"></div>
            <span>Live</span>
          </div>
          <span className="data-points">{chartData.length}/{maxDataPoints} points</span>
        </div>
      )}
    </div>
  )
}

export default RealTimeChart