import React, { useState } from 'react'
import axios from 'axios'

function MarketingTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('strategy')
  const [marketingData, setMarketingData] = useState({
    businessName: '',
    industry: '',
    targetAudience: '',
    budget: '',
    goals: '',
    currentChannels: '',
    geography: '',
    competitorAnalysis: ''
  })
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedContent, setGeneratedContent] = useState('')

  const sections = {
    strategy: {
      title: 'Marketing Strategy',
      icon: '📊',
      tools: [
        { id: 'marketing_plan', name: 'Marketing Plan', description: 'Comprehensive marketing strategy and roadmap' },
        { id: 'target_audience', name: 'Target Audience Analysis', description: 'Customer persona and segmentation analysis' },
        { id: 'competitor_analysis', name: 'Competitor Analysis', description: 'Competitive landscape and positioning' },
        { id: 'brand_strategy', name: 'Brand Strategy', description: 'Brand positioning and messaging framework' },
        { id: 'marketing_mix', name: 'Marketing Mix (4Ps)', description: 'Product, Price, Place, Promotion analysis' },
        { id: 'market_research', name: 'Market Research', description: 'Industry trends and market opportunities' }
      ]
    },
    content: {
      title: 'Content Creation',
      icon: '✍️',
      tools: [
        { id: 'content_calendar', name: 'Content Calendar', description: 'Social media and blog content scheduling' },
        { id: 'blog_posts', name: 'Blog Post Generator', description: 'SEO-optimized blog content creation' },
        { id: 'social_posts', name: 'Social Media Posts', description: 'Platform-specific social content' },
        { id: 'email_campaigns', name: 'Email Campaigns', description: 'Newsletter and drip campaign content' },
        { id: 'ad_copy', name: 'Ad Copy Generator', description: 'Compelling advertising copy and headlines' },
        { id: 'video_scripts', name: 'Video Scripts', description: 'YouTube and social video scripts' }
      ]
    },
    social: {
      title: 'Social Media Management',
      icon: '📱',
      tools: [
        { id: 'social_strategy', name: 'Social Media Strategy', description: 'Platform-specific growth strategies' },
        { id: 'hashtag_research', name: 'Hashtag Research', description: 'Trending and niche hashtag discovery' },
        { id: 'influencer_outreach', name: 'Influencer Outreach', description: 'Influencer collaboration templates' },
        { id: 'social_analytics', name: 'Social Analytics', description: 'Performance tracking and optimization' },
        { id: 'community_management', name: 'Community Management', description: 'Engagement and response strategies' },
        { id: 'viral_content', name: 'Viral Content Ideas', description: 'Trending content concept generation' }
      ]
    },
    advertising: {
      title: 'Digital Advertising',
      icon: '🎯',
      tools: [
        { id: 'google_ads', name: 'Google Ads Campaigns', description: 'Search and display ad campaign setup' },
        { id: 'facebook_ads', name: 'Facebook Ads Manager', description: 'Meta advertising campaign optimization' },
        { id: 'linkedin_ads', name: 'LinkedIn Ads', description: 'B2B advertising campaign strategies' },
        { id: 'youtube_ads', name: 'YouTube Advertising', description: 'Video advertising campaign creation' },
        { id: 'retargeting', name: 'Retargeting Campaigns', description: 'Pixel-based remarketing strategies' },
        { id: 'ad_optimization', name: 'Ad Optimization', description: 'A/B testing and performance improvement' }
      ]
    },
    analytics: {
      title: 'Analytics & Optimization',
      icon: '📈',
      tools: [
        { id: 'conversion_tracking', name: 'Conversion Tracking', description: 'Goal setup and attribution modeling' },
        { id: 'funnel_analysis', name: 'Funnel Analysis', description: 'Customer journey optimization' },
        { id: 'roi_calculator', name: 'Marketing ROI Calculator', description: 'Campaign profitability analysis' },
        { id: 'attribution_modeling', name: 'Attribution Modeling', description: 'Multi-touch attribution analysis' },
        { id: 'performance_reports', name: 'Performance Reports', description: 'Automated marketing dashboards' },
        { id: 'growth_hacking', name: 'Growth Hacking', description: 'Viral coefficient and growth strategies' }
      ]
    },
    automation: {
      title: 'Marketing Automation',
      icon: '🤖',
      tools: [
        { id: 'drip_campaigns', name: 'Drip Campaigns', description: 'Automated email nurture sequences' },
        { id: 'lead_scoring', name: 'Lead Scoring', description: 'Prospect qualification automation' },
        { id: 'chatbot_flows', name: 'Chatbot Flows', description: 'Customer service automation scripts' },
        { id: 'workflow_automation', name: 'Workflow Automation', description: 'Marketing process optimization' },
        { id: 'personalization', name: 'Content Personalization', description: 'Dynamic content delivery systems' },
        { id: 'trigger_campaigns', name: 'Trigger Campaigns', description: 'Behavioral marketing automation' }
      ]
    }
  }

  const generateMarketingContent = async (toolId) => {
    setIsGenerating(true)

    const prompts = {
      marketing_plan: `Create a comprehensive marketing plan for ${marketingData.businessName || 'the business'} in the ${marketingData.industry || 'specified'} industry. Include: Situation Analysis, Target Market Definition, Marketing Objectives, Strategy & Tactics, Budget Allocation, Implementation Timeline, and Success Metrics.`,
      
      target_audience: `Develop detailed customer personas for ${marketingData.businessName || 'the business'}. Include: Demographics, Psychographics, Buying Behavior, Pain Points, Communication Preferences, Customer Journey Mapping, and Segmentation Strategy.`,
      
      competitor_analysis: `Perform comprehensive competitor analysis including: Direct and Indirect Competitors, SWOT Analysis, Pricing Strategies, Marketing Tactics, Market Share, Competitive Advantages, and Positioning Opportunities.`,
      
      content_calendar: `Create a 3-month content calendar with: Daily Social Media Posts, Weekly Blog Topics, Email Campaign Schedule, Seasonal Content Themes, Trending Hashtags, and Cross-Platform Content Strategy.`,
      
      blog_posts: `Generate 10 SEO-optimized blog post ideas with full outlines for ${marketingData.industry || 'the industry'}. Include: Target Keywords, Headlines, Meta Descriptions, Content Structure, Internal Linking Strategy, and Call-to-Action suggestions.`,
      
      social_posts: `Create 30 days of social media content including: Platform-specific posts (Facebook, Instagram, Twitter, LinkedIn), Engaging captions, Relevant hashtags, Visual content ideas, and Engagement strategies.`,
      
      google_ads: `Design Google Ads campaign structure with: Keyword Research, Ad Group Organization, Compelling Ad Copy, Landing Page Recommendations, Bidding Strategies, and Performance Tracking Setup.`,
      
      email_campaigns: `Create email marketing campaign sequences including: Welcome Series, Nurture Campaigns, Product Launches, Re-engagement Campaigns, Subject Line Variations, and A/B Testing Strategies.`,
      
      social_strategy: `Develop platform-specific social media strategies for: Content Pillars, Posting Frequency, Engagement Tactics, Growth Strategies, Community Building, and Influencer Partnerships.`,
      
      conversion_tracking: `Setup comprehensive conversion tracking including: Goal Configuration, Attribution Models, Customer Journey Mapping, ROI Calculations, and Performance Dashboards.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are a digital marketing expert and growth strategist. ${prompts[toolId] || 'Generate comprehensive marketing strategy and actionable recommendations.'} 

Business Information:
- Business Name: ${marketingData.businessName || 'Not specified'}
- Industry: ${marketingData.industry || 'Not specified'}
- Target Audience: ${marketingData.targetAudience || 'Not specified'}
- Monthly Budget: ${marketingData.budget || 'Not specified'}
- Marketing Goals: ${marketingData.goals || 'Not specified'}
- Current Channels: ${marketingData.currentChannels || 'Not specified'}
- Geographic Area: ${marketingData.geography || 'Not specified'}

Requirements:
1. Use current digital marketing best practices
2. Include specific, actionable recommendations
3. Provide measurable KPIs and success metrics
4. Include budget allocation and ROI projections
5. Format professionally with clear sections
6. Add implementation timelines and priorities
7. Include competitive advantages and differentiation
8. Provide both organic and paid strategies

Create comprehensive marketing materials that can be implemented immediately for business growth.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `marketing_${toolId}_${Date.now()}`,
        model: 'gpt-3.5-turbo'
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      setGeneratedContent(response.data.response)
      
      // Open content in new window
      const newWindow = window.open()
      newWindow.document.write(`
        <html>
          <head>
            <title>Marketing Strategy - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 3px solid #e74c3c; padding-bottom: 15px; }
              .business-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #e74c3c; }
              .strategy-section { background: #fef9e7; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .action-items { background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .kpi-box { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #64b5f6; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #e74c3c; color: white; }
              .highlight { background: #ffecb3; font-weight: bold; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="business-info">
              <strong>Business:</strong> ${marketingData.businessName || 'Not specified'}<br>
              <strong>Industry:</strong> ${marketingData.industry || 'Not specified'}<br>
              <strong>Target Audience:</strong> ${marketingData.targetAudience || 'Not specified'}<br>
              <strong>Budget:</strong> ${marketingData.budget || 'Not specified'}<br>
              <strong>Generated:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #e74c3c; color: white; border: none; border-radius: 4px;">Print Strategy</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating marketing content:', error)
      setGeneratedContent('Error generating content. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="marketing-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="marketing-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="marketing-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-content-btn"
                onClick={() => generateMarketingContent(tool.id)}
                disabled={isGenerating}
              >
                {isGenerating ? '⏳ Generating...' : '🚀 Generate Content'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="marketing-tools">
      <div className="marketing-header">
        <h1>📢 Marketing & Social Media Tools</h1>
        <p>Complete digital marketing automation and growth optimization platform</p>
      </div>

      <div className="marketing-form">
        <h3>Business & Campaign Information</h3>
        <div className="form-grid">
          <input
            type="text"
            placeholder="Business Name"
            value={marketingData.businessName}
            onChange={(e) => setMarketingData({...marketingData, businessName: e.target.value})}
          />
          <input
            type="text"
            placeholder="Industry/Niche"
            value={marketingData.industry}
            onChange={(e) => setMarketingData({...marketingData, industry: e.target.value})}
          />
          <input
            type="text"
            placeholder="Target Audience"
            value={marketingData.targetAudience}
            onChange={(e) => setMarketingData({...marketingData, targetAudience: e.target.value})}
          />
          <select
            value={marketingData.budget}
            onChange={(e) => setMarketingData({...marketingData, budget: e.target.value})}
          >
            <option value="">Monthly Marketing Budget</option>
            <option value="under-1k">Under $1,000</option>
            <option value="1k-5k">$1,000 - $5,000</option>
            <option value="5k-10k">$5,000 - $10,000</option>
            <option value="10k-25k">$10,000 - $25,000</option>
            <option value="25k-50k">$25,000 - $50,000</option>
            <option value="over-50k">Over $50,000</option>
          </select>
          <input
            type="text"
            placeholder="Marketing Goals"
            value={marketingData.goals}
            onChange={(e) => setMarketingData({...marketingData, goals: e.target.value})}
          />
          <input
            type="text"
            placeholder="Current Marketing Channels"
            value={marketingData.currentChannels}
            onChange={(e) => setMarketingData({...marketingData, currentChannels: e.target.value})}
          />
          <input
            type="text"
            placeholder="Geographic Target Area"
            value={marketingData.geography}
            onChange={(e) => setMarketingData({...marketingData, geography: e.target.value})}
          />
        </div>
      </div>

      <div className="marketing-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`marketing-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="marketing-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default MarketingTools