import React, { useState } from 'react'
import axios from 'axios'

function BusinessTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('planning')
  const [businessData, setBusinessData] = useState({
    companyName: '',
    industry: '',
    targetMarket: '',
    revenue: '',
    funding: ''
  })
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState('')

  const sections = {
    planning: {
      title: 'Business Planning',
      icon: '📋',
      tools: [
        { id: 'business_plan', name: 'Complete Business Plan', description: 'Comprehensive business plan with financial projections' },
        { id: 'executive_summary', name: 'Executive Summary', description: 'Compelling executive summary for investors' },
        { id: 'market_analysis', name: 'Market Analysis', description: 'Industry and competitive analysis' },
        { id: 'financial_projections', name: 'Financial Projections', description: '5-year financial forecasts and models' },
        { id: 'swot_analysis', name: 'SWOT Analysis', description: 'Strengths, weaknesses, opportunities, threats' },
        { id: 'risk_assessment', name: 'Risk Assessment', description: 'Business risk evaluation and mitigation' }
      ]
    },
    funding: {
      title: 'Funding & Investment',
      icon: '💰',
      tools: [
        { id: 'pitch_deck', name: 'Investor Pitch Deck', description: 'Professional investor presentation' },
        { id: 'valuation', name: 'Company Valuation', description: 'Business valuation using multiple methods' },
        { id: 'term_sheet', name: 'Investment Term Sheet', description: 'VC/Angel investor terms template' },
        { id: 'cap_table', name: 'Capitalization Table', description: 'Equity ownership and dilution modeling' },
        { id: 'due_diligence', name: 'Due Diligence Package', description: 'Complete investor due diligence materials' },
        { id: 'grant_proposal', name: 'Grant Proposal', description: 'Government and private grant applications' }
      ]
    },
    operations: {
      title: 'Operations & Management',
      icon: '⚙️',
      tools: [
        { id: 'org_chart', name: 'Organizational Chart', description: 'Company structure and reporting lines' },
        { id: 'job_descriptions', name: 'Job Descriptions', description: 'Comprehensive role definitions' },
        { id: 'employee_handbook', name: 'Employee Handbook', description: 'HR policies and procedures' },
        { id: 'vendor_analysis', name: 'Vendor Analysis', description: 'Supplier evaluation and selection' },
        { id: 'process_optimization', name: 'Process Optimization', description: 'Workflow and efficiency improvements' },
        { id: 'quality_systems', name: 'Quality Management', description: 'QA/QC systems and procedures' }
      ]
    },
    marketing: {
      title: 'Marketing & Sales',
      icon: '📢',
      tools: [
        { id: 'marketing_plan', name: 'Marketing Plan', description: 'Comprehensive marketing strategy' },
        { id: 'competitor_analysis', name: 'Competitor Analysis', description: 'Competitive landscape assessment' },
        { id: 'pricing_strategy', name: 'Pricing Strategy', description: 'Optimal pricing models and strategies' },
        { id: 'sales_funnel', name: 'Sales Funnel', description: 'Customer acquisition and conversion' },
        { id: 'brand_strategy', name: 'Brand Strategy', description: 'Brand positioning and messaging' },
        { id: 'digital_marketing', name: 'Digital Marketing', description: 'Online marketing campaigns' }
      ]
    },
    financial: {
      title: 'Financial Management',
      icon: '📊',
      tools: [
        { id: 'cash_flow', name: 'Cash Flow Analysis', description: 'Working capital and cash management' },
        { id: 'budget_planning', name: 'Budget Planning', description: 'Annual budgets and variance analysis' },
        { id: 'cost_analysis', name: 'Cost Analysis', description: 'Cost structure optimization' },
        { id: 'break_even', name: 'Break-Even Analysis', description: 'Profitability thresholds' },
        { id: 'roi_calculator', name: 'ROI Calculator', description: 'Return on investment analysis' },
        { id: 'tax_planning', name: 'Tax Planning', description: 'Business tax optimization strategies' }
      ]
    },
    legal: {
      title: 'Legal & Compliance',
      icon: '⚖️',
      tools: [
        { id: 'business_structure', name: 'Business Structure', description: 'Entity selection and formation' },
        { id: 'contract_templates', name: 'Contract Templates', description: 'Standard business agreements' },
        { id: 'compliance_checklist', name: 'Compliance Checklist', description: 'Regulatory requirements' },
        { id: 'ip_protection', name: 'IP Protection', description: 'Intellectual property strategy' },
        { id: 'licensing', name: 'Licensing Requirements', description: 'Business permits and licenses' },
        { id: 'insurance_needs', name: 'Insurance Analysis', description: 'Business insurance requirements' }
      ]
    }
  }

  const generateBusinessDocument = async (toolId) => {
    setIsAnalyzing(true)

    const prompts = {
      business_plan: `Generate a comprehensive business plan for ${businessData.companyName || 'a new business'} in the ${businessData.industry || 'specified'} industry. Include: Executive Summary, Company Description, Market Analysis, Organization & Management, Service/Product Line, Marketing & Sales, Funding Request, Financial Projections, and Implementation Timeline.`,
      
      pitch_deck: `Create a compelling investor pitch deck outline for ${businessData.companyName || 'a startup'}. Include: Problem Statement, Solution, Market Opportunity, Business Model, Competition, Traction, Team, Financial Projections, Funding Ask, and Use of Funds. Make it investor-ready with compelling narratives.`,
      
      market_analysis: `Perform comprehensive market analysis for ${businessData.industry || 'the specified industry'}. Include: Market Size (TAM/SAM/SOM), Growth Trends, Customer Segments, Competitive Landscape, Market Drivers, Barriers to Entry, and Key Success Factors.`,
      
      financial_projections: `Create 5-year financial projections including: Income Statement, Cash Flow Statement, Balance Sheet, Break-even Analysis, Key Financial Ratios, Sensitivity Analysis, and Assumptions. Use realistic growth rates and industry benchmarks.`,
      
      swot_analysis: `Conduct detailed SWOT analysis for ${businessData.companyName || 'the business'}. Analyze internal Strengths and Weaknesses, external Opportunities and Threats. Provide strategic recommendations based on findings.`,
      
      valuation: `Perform comprehensive business valuation using multiple methods: DCF Analysis, Comparable Company Analysis, Asset-Based Valuation, and Market Multiple approaches. Include sensitivity analysis and valuation range.`,
      
      marketing_plan: `Develop complete marketing plan including: Situation Analysis, Target Market Definition, Positioning Strategy, Marketing Mix (4Ps), Digital Marketing Strategy, Budget Allocation, KPIs, and Implementation Timeline.`,
      
      cash_flow: `Create cash flow analysis with: Monthly cash flow projections, Working capital requirements, Seasonal variations, Cash conversion cycle, Financing needs, and Cash management strategies.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are a business strategy expert and consultant. ${prompts[toolId] || 'Generate comprehensive business analysis and recommendations.'} 

Company Details:
- Name: ${businessData.companyName || 'Not specified'}
- Industry: ${businessData.industry || 'Not specified'}
- Target Market: ${businessData.targetMarket || 'Not specified'}
- Revenue Stage: ${businessData.revenue || 'Not specified'}
- Funding Status: ${businessData.funding || 'Not specified'}

Requirements:
1. Provide actionable insights and recommendations
2. Use industry best practices and benchmarks
3. Include specific metrics and KPIs
4. Format professionally with clear sections
5. Add implementation timelines where applicable
6. Include risk factors and mitigation strategies
7. Provide competitive advantages and differentiation

Create a comprehensive, professional document that can be used immediately for business decision-making.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `business_${toolId}_${Date.now()}`,
        model: 'gpt-3.5-turbo'
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      setAnalysisResult(response.data.response)
      
      // Open document in new window
      const newWindow = window.open()
      newWindow.document.write(`
        <html>
          <head>
            <title>Business Analysis - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
              .header-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
              .section { margin: 30px 0; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #f2f2f2; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="header-info">
              <strong>Company:</strong> ${businessData.companyName || 'Not specified'}<br>
              <strong>Industry:</strong> ${businessData.industry || 'Not specified'}<br>
              <strong>Generated:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px;">Print Document</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating business document:', error)
      setAnalysisResult('Error generating document. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="business-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="business-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="business-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-analysis-btn"
                onClick={() => generateBusinessDocument(tool.id)}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? '⏳ Generating...' : '🚀 Generate Analysis'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="business-tools">
      <div className="business-header">
        <h1>🏢 Business & Startup Tools</h1>
        <p>Comprehensive business planning, analysis, and growth tools</p>
      </div>

      <div className="business-form">
        <h3>Business Information</h3>
        <div className="form-grid">
          <input
            type="text"
            placeholder="Company Name"
            value={businessData.companyName}
            onChange={(e) => setBusinessData({...businessData, companyName: e.target.value})}
          />
          <input
            type="text"
            placeholder="Industry"
            value={businessData.industry}
            onChange={(e) => setBusinessData({...businessData, industry: e.target.value})}
          />
          <input
            type="text"
            placeholder="Target Market"
            value={businessData.targetMarket}
            onChange={(e) => setBusinessData({...businessData, targetMarket: e.target.value})}
          />
          <select
            value={businessData.revenue}
            onChange={(e) => setBusinessData({...businessData, revenue: e.target.value})}
          >
            <option value="">Revenue Stage</option>
            <option value="pre-revenue">Pre-Revenue</option>
            <option value="under-100k">Under $100K</option>
            <option value="100k-1m">$100K - $1M</option>
            <option value="1m-10m">$1M - $10M</option>
            <option value="over-10m">Over $10M</option>
          </select>
          <select
            value={businessData.funding}
            onChange={(e) => setBusinessData({...businessData, funding: e.target.value})}
          >
            <option value="">Funding Stage</option>
            <option value="bootstrapped">Bootstrapped</option>
            <option value="pre-seed">Pre-Seed</option>
            <option value="seed">Seed</option>
            <option value="series-a">Series A</option>
            <option value="series-b">Series B+</option>
            <option value="established">Established</option>
          </select>
        </div>
      </div>

      <div className="business-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`business-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="business-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default BusinessTools