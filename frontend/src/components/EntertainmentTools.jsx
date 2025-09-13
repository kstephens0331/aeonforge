import React, { useState } from 'react'
import axios from 'axios'

function EntertainmentTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('film')
  const [formData, setFormData] = useState({
    projectTitle: '',
    genre: '',
    targetAudience: '',
    budget: '',
    timeline: '',
    productionType: '',
    distributor: '',
    platform: '',
    contentRating: '',
    description: ''
  })
  const [analysis, setAnalysis] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  const entertainmentTools = {
    film: [
      { id: 'screenplay', title: 'Screenplay Analyzer', desc: 'Analyze screenplay structure, pacing, and character development' },
      { id: 'budget', title: 'Film Budget Calculator', desc: 'Estimate production costs for independent and studio films' },
      { id: 'casting', title: 'Casting Director Tools', desc: 'Character breakdowns and casting recommendations' },
      { id: 'location', title: 'Location Scout Assistant', desc: 'Find and evaluate filming locations with cost analysis' },
      { id: 'schedule', title: 'Production Scheduler', desc: 'Create optimized shooting schedules and call sheets' },
      { id: 'post', title: 'Post-Production Planner', desc: 'Plan editing workflow and post-production timeline' }
    ],
    music: [
      { id: 'composition', title: 'Music Composition Assistant', desc: 'Generate chord progressions and melody suggestions' },
      { id: 'arrangement', title: 'Song Arrangement Tool', desc: 'Structure songs and arrange instrumentation' },
      { id: 'mixing', title: 'Mix Engineering Guide', desc: 'Mixing techniques and audio processing recommendations' },
      { id: 'mastering', title: 'Mastering Checklist', desc: 'Professional mastering workflow and quality control' },
      { id: 'licensing', title: 'Music Licensing Calculator', desc: 'Calculate sync licensing fees and usage rights' },
      { id: 'distribution', title: 'Music Distribution Planner', desc: 'Plan digital releases across streaming platforms' }
    ],
    gaming: [
      { id: 'design', title: 'Game Design Document', desc: 'Create comprehensive game design specifications' },
      { id: 'mechanics', title: 'Game Mechanics Analyzer', desc: 'Balance and optimize gameplay mechanics' },
      { id: 'narrative', title: 'Interactive Story Builder', desc: 'Create branching narratives and dialogue trees' },
      { id: 'monetization', title: 'Game Monetization Strategy', desc: 'Design in-app purchases and revenue models' },
      { id: 'testing', title: 'QA Testing Framework', desc: 'Create testing protocols and bug tracking systems' },
      { id: 'marketing', title: 'Game Marketing Campaign', desc: 'Plan launch campaigns and community building' }
    ],
    streaming: [
      { id: 'content', title: 'Content Strategy Planner', desc: 'Plan streaming content calendar and themes' },
      { id: 'audience', title: 'Audience Analytics Tool', desc: 'Analyze viewer engagement and growth metrics' },
      { id: 'monetization', title: 'Stream Monetization Guide', desc: 'Optimize donations, sponsorships, and subscriptions' },
      { id: 'technical', title: 'Stream Setup Optimizer', desc: 'Configure OBS, audio, and streaming quality' },
      { id: 'brand', title: 'Brand Development Kit', desc: 'Create consistent branding across platforms' },
      { id: 'collaboration', title: 'Collaboration Manager', desc: 'Plan collabs and cross-platform promotions' }
    ],
    publishing: [
      { id: 'manuscript', title: 'Manuscript Evaluator', desc: 'Analyze plot structure and character development' },
      { id: 'editing', title: 'Editorial Planning Tool', desc: 'Plan developmental, copy, and line editing phases' },
      { id: 'formatting', title: 'Book Formatting Guide', desc: 'Format for print and digital publication' },
      { id: 'cover', title: 'Book Cover Designer', desc: 'Design guidelines and market analysis for covers' },
      { id: 'pricing', title: 'Book Pricing Strategy', desc: 'Optimize pricing across different markets and formats' },
      { id: 'marketing', title: 'Book Marketing Planner', desc: 'Launch campaigns and author platform building' }
    ],
    events: [
      { id: 'planning', title: 'Event Production Planner', desc: 'Plan concerts, festivals, and live entertainment' },
      { id: 'venue', title: 'Venue Selection Tool', desc: 'Evaluate venues for capacity, acoustics, and logistics' },
      { id: 'technical', title: 'Technical Rider Generator', desc: 'Create detailed technical requirements and riders' },
      { id: 'ticketing', title: 'Ticketing Strategy Tool', desc: 'Price tiers, sales phases, and revenue optimization' },
      { id: 'promotion', title: 'Event Promotion Planner', desc: 'Marketing campaigns and audience building strategies' },
      { id: 'logistics', title: 'Event Logistics Manager', desc: 'Coordinate setup, security, and vendor management' }
    ]
  }

  const generateEntertainmentAnalysis = async (toolId) => {
    setIsGenerating(true)
    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const tool = entertainmentTools[activeSection].find(t => t.id === toolId)
      
      const prompt = `As an entertainment industry expert, provide detailed analysis for: ${tool.title}

Project Details:
- Title: ${formData.projectTitle}
- Genre: ${formData.genre}
- Target Audience: ${formData.targetAudience}
- Budget: ${formData.budget}
- Timeline: ${formData.timeline}
- Production Type: ${formData.productionType}
- Distribution: ${formData.distributor}
- Platform: ${formData.platform}
- Content Rating: ${formData.contentRating}
- Description: ${formData.description}

Provide comprehensive analysis including:
1. Industry best practices and current trends
2. Specific recommendations based on project details
3. Budget considerations and cost optimization
4. Timeline and milestone planning
5. Market analysis and competitive landscape
6. Risk assessment and mitigation strategies
7. Success metrics and KPIs
8. Next steps and action items

Format as a professional entertainment industry report with specific, actionable recommendations.`

      const response = await axios.post(`${apiUrl}/chat/completions`, {
        model: serverInfo.default_model,
        messages: [{
          role: 'user',
          content: prompt
        }],
        max_tokens: 2000
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      setAnalysis(response.data.choices[0].message.content)
    } catch (error) {
      console.error('Error generating analysis:', error)
      setAnalysis('Error generating analysis. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const printReport = () => {
    const printWindow = window.open('', '_blank')
    printWindow.document.write(`
      <html>
        <head>
          <title>Entertainment Analysis Report</title>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
            .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }
            .content { white-space: pre-wrap; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>Entertainment Industry Analysis Report</h1>
            <p>Generated by AeonForge Entertainment Tools</p>
            <p>Date: ${new Date().toLocaleDateString()}</p>
          </div>
          <div class="content">${analysis}</div>
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
  }

  const sections = [
    { id: 'film', title: 'Film & TV', icon: '🎬' },
    { id: 'music', title: 'Music', icon: '🎵' },
    { id: 'gaming', title: 'Gaming', icon: '🎮' },
    { id: 'streaming', title: 'Streaming', icon: '📹' },
    { id: 'publishing', title: 'Publishing', icon: '📚' },
    { id: 'events', title: 'Live Events', icon: '🎭' }
  ]

  return (
    <div className="entertainment-tools">
      <div className="entertainment-header">
        <h1>🎬 Entertainment & Media Production Tools</h1>
        <p>Professional tools for film, music, gaming, streaming, publishing, and live events</p>
      </div>

      <div className="entertainment-form">
        <h3>Project Information</h3>
        <div className="form-grid">
          <input
            type="text"
            name="projectTitle"
            placeholder="Project Title"
            value={formData.projectTitle}
            onChange={handleInputChange}
          />
          <select
            name="genre"
            value={formData.genre}
            onChange={handleInputChange}
          >
            <option value="">Select Genre</option>
            <option value="action">Action</option>
            <option value="comedy">Comedy</option>
            <option value="drama">Drama</option>
            <option value="horror">Horror</option>
            <option value="documentary">Documentary</option>
            <option value="animation">Animation</option>
            <option value="sci-fi">Sci-Fi</option>
            <option value="romance">Romance</option>
            <option value="thriller">Thriller</option>
          </select>
          <select
            name="targetAudience"
            value={formData.targetAudience}
            onChange={handleInputChange}
          >
            <option value="">Target Audience</option>
            <option value="children">Children (G)</option>
            <option value="family">Family (PG)</option>
            <option value="teen">Teen (PG-13)</option>
            <option value="adult">Adult (R)</option>
            <option value="mature">Mature (18+)</option>
          </select>
          <input
            type="text"
            name="budget"
            placeholder="Budget Range"
            value={formData.budget}
            onChange={handleInputChange}
          />
          <input
            type="text"
            name="timeline"
            placeholder="Timeline/Deadline"
            value={formData.timeline}
            onChange={handleInputChange}
          />
          <select
            name="productionType"
            value={formData.productionType}
            onChange={handleInputChange}
          >
            <option value="">Production Type</option>
            <option value="independent">Independent</option>
            <option value="studio">Studio</option>
            <option value="streaming">Streaming Original</option>
            <option value="web-series">Web Series</option>
            <option value="short-film">Short Film</option>
          </select>
          <input
            type="text"
            name="distributor"
            placeholder="Distribution Platform"
            value={formData.distributor}
            onChange={handleInputChange}
          />
          <input
            type="text"
            name="platform"
            placeholder="Release Platform"
            value={formData.platform}
            onChange={handleInputChange}
          />
        </div>
        <textarea
          name="description"
          placeholder="Project description, goals, and specific requirements..."
          value={formData.description}
          onChange={handleInputChange}
          rows="3"
          style={{ width: '100%', marginTop: '15px' }}
        />
      </div>

      <div className="entertainment-navigation">
        {sections.map(section => (
          <button
            key={section.id}
            className={`entertainment-nav-btn ${activeSection === section.id ? 'active' : ''}`}
            onClick={() => setActiveSection(section.id)}
          >
            <div className="nav-icon">{section.icon}</div>
            <div className="nav-title">{section.title}</div>
          </button>
        ))}
      </div>

      <div className="entertainment-content">
        <div className="entertainment-section" data-section={activeSection}>
          <h3>{sections.find(s => s.id === activeSection)?.title} Tools</h3>
          
          <div className="entertainment-tools-grid">
            {entertainmentTools[activeSection].map(tool => (
              <div key={tool.id} className="entertainment-tool-card">
                <h4>{tool.title}</h4>
                <p>{tool.desc}</p>
                <button
                  className="generate-entertainment-btn"
                  onClick={() => generateEntertainmentAnalysis(tool.id)}
                  disabled={isGenerating}
                >
                  {isGenerating ? 'Generating...' : 'Generate Analysis'}
                </button>
              </div>
            ))}
          </div>
        </div>

        {analysis && (
          <div className="analysis-result" style={{ marginTop: '30px', padding: '25px', background: 'white', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ color: '#2c3e50', margin: 0 }}>Analysis Report</h3>
              <button onClick={printReport} style={{ padding: '8px 16px', background: '#3498db', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
                Print Report
              </button>
            </div>
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', color: '#333' }}>
              {analysis}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default EntertainmentTools