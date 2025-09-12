import React, { useState } from 'react'
import axios from 'axios'

function RealEstateTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('analysis')
  const [propertyData, setPropertyData] = useState({
    address: '',
    price: '',
    propertyType: '',
    sqft: '',
    bedrooms: '',
    bathrooms: '',
    yearBuilt: '',
    rentAmount: '',
    marketArea: ''
  })
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState('')

  const sections = {
    analysis: {
      title: 'Property Analysis',
      icon: '🏠',
      tools: [
        { id: 'property_valuation', name: 'Property Valuation', description: 'Comprehensive market value analysis using comparables' },
        { id: 'investment_analysis', name: 'Investment Analysis', description: 'ROI, cash flow, and return calculations' },
        { id: 'rental_analysis', name: 'Rental Analysis', description: 'Rental income potential and market rates' },
        { id: 'flip_analysis', name: 'Fix & Flip Analysis', description: 'Rehab costs and profit projections' },
        { id: 'cash_flow', name: 'Cash Flow Analysis', description: 'Monthly income vs expenses breakdown' },
        { id: 'market_analysis', name: 'Market Analysis', description: 'Local market trends and forecasts' }
      ]
    },
    financing: {
      title: 'Financing & Mortgages',
      icon: '🏦',
      tools: [
        { id: 'mortgage_calculator', name: 'Mortgage Calculator', description: 'Payment calculations and amortization schedules' },
        { id: 'refinance_analysis', name: 'Refinance Analysis', description: 'Break-even and savings calculations' },
        { id: 'loan_comparison', name: 'Loan Comparison', description: 'Compare different mortgage options' },
        { id: 'qualification', name: 'Qualification Analysis', description: 'Income and debt-to-income requirements' },
        { id: 'closing_costs', name: 'Closing Costs', description: 'Estimate total transaction costs' },
        { id: 'pmi_analysis', name: 'PMI Analysis', description: 'Private mortgage insurance calculations' }
      ]
    },
    investment: {
      title: 'Investment Strategies',
      icon: '📈',
      tools: [
        { id: 'brrrr_strategy', name: 'BRRRR Strategy', description: 'Buy, Rehab, Rent, Refinance, Repeat analysis' },
        { id: 'wholesale_analysis', name: 'Wholesale Analysis', description: 'Assignment contracts and profit margins' },
        { id: 'reit_analysis', name: 'REIT Analysis', description: 'Real Estate Investment Trust evaluation' },
        { id: 'syndication', name: 'Syndication Analysis', description: 'Group investment structure and returns' },
        { id: 'tax_benefits', name: 'Tax Benefits', description: 'Depreciation, deductions, and 1031 exchanges' },
        { id: 'portfolio_analysis', name: 'Portfolio Analysis', description: 'Multi-property investment tracking' }
      ]
    },
    commercial: {
      title: 'Commercial Real Estate',
      icon: '🏢',
      tools: [
        { id: 'cap_rate', name: 'Cap Rate Analysis', description: 'Capitalization rate calculations' },
        { id: 'noi_analysis', name: 'NOI Analysis', description: 'Net Operating Income breakdown' },
        { id: 'dcf_analysis', name: 'DCF Analysis', description: 'Discounted Cash Flow valuation' },
        { id: 'lease_analysis', name: 'Lease Analysis', description: 'Commercial lease terms and valuations' },
        { id: 'market_rent', name: 'Market Rent Analysis', description: 'Commercial rental rate comparisons' },
        { id: 'vacancy_analysis', name: 'Vacancy Analysis', description: 'Market vacancy rates and impact' }
      ]
    },
    development: {
      title: 'Development & Construction',
      icon: '🏗️',
      tools: [
        { id: 'development_analysis', name: 'Development Analysis', description: 'Land development feasibility studies' },
        { id: 'construction_costs', name: 'Construction Costs', description: 'Building cost estimates and timelines' },
        { id: 'permit_analysis', name: 'Permit Analysis', description: 'Zoning and permit requirements' },
        { id: 'subdivision', name: 'Subdivision Analysis', description: 'Land subdivision profitability' },
        { id: 'spec_building', name: 'Spec Building', description: 'Speculative construction analysis' },
        { id: 'infill_development', name: 'Infill Development', description: 'Urban infill project analysis' }
      ]
    },
    legal: {
      title: 'Legal & Documentation',
      icon: '📋',
      tools: [
        { id: 'purchase_agreement', name: 'Purchase Agreement', description: 'Real estate purchase contracts' },
        { id: 'lease_agreement', name: 'Lease Agreement', description: 'Residential and commercial leases' },
        { id: 'deed_forms', name: 'Deed Forms', description: 'Property transfer documentation' },
        { id: 'disclosure_forms', name: 'Disclosure Forms', description: 'Property condition disclosures' },
        { id: 'hoa_analysis', name: 'HOA Analysis', description: 'Homeowners association document review' },
        { id: 'title_analysis', name: 'Title Analysis', description: 'Title search and insurance review' }
      ]
    }
  }

  const generateRealEstateAnalysis = async (toolId) => {
    setIsAnalyzing(true)

    const prompts = {
      property_valuation: `Perform comprehensive property valuation analysis for ${propertyData.address || 'the subject property'}. Include: Comparative Market Analysis (CMA), Adjusted Sales Price, Price per Square Foot Analysis, Market Appreciation Trends, Property Condition Adjustments, and Final Market Value Range.`,
      
      investment_analysis: `Create detailed investment analysis including: Purchase Price Analysis, Down Payment Requirements, Financing Scenarios, Cash-on-Cash Return, Total Return on Investment (ROI), Internal Rate of Return (IRR), Net Present Value (NPV), Payback Period, and 10-year projection scenarios.`,
      
      rental_analysis: `Analyze rental income potential with: Market Rent Comparables, Rental Yield Calculations, Gross Rent Multiplier, Vacancy Rate Impact, Property Management Costs, Maintenance Reserves, Cash Flow Projections, and Annual Rent Escalation Scenarios.`,
      
      cash_flow: `Generate comprehensive cash flow analysis with: Monthly Rental Income, Operating Expenses (Taxes, Insurance, Maintenance, Management), Debt Service Payments, Cash Flow Before Taxes, Tax Benefits (Depreciation, Interest Deduction), Cash Flow After Taxes, and Break-even Analysis.`,
      
      mortgage_calculator: `Calculate mortgage scenarios including: Principal & Interest Payments, Amortization Schedule, Total Interest Paid, Monthly Payment Breakdown, Different Loan Terms Comparison (15 vs 30 year), PMI Calculations, and Prepayment Impact Analysis.`,
      
      brrrr_strategy: `Analyze BRRRR strategy with: Initial Purchase Analysis, Rehab Cost Estimates, After Repair Value (ARV), Refinance Scenarios, Cash Left in Deal, Infinite Return Calculations, and Cycle Repeat Projections.`,
      
      cap_rate: `Perform capitalization rate analysis including: Net Operating Income Calculation, Cap Rate Derivation, Market Cap Rate Comparisons, Cap Rate Impact on Value, Sensitivity Analysis, and Investment Grade Assessment.`,
      
      development_analysis: `Create development feasibility study with: Land Acquisition Costs, Site Preparation Expenses, Construction Costs, Soft Costs (Permits, Professional Fees), Financing Costs, Sales/Lease Projections, Timeline Analysis, and Profit Margin Calculations.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are a real estate investment expert and licensed appraiser. ${prompts[toolId] || 'Generate comprehensive real estate analysis with professional recommendations.'} 

Property Details:
- Address: ${propertyData.address || 'Not specified'}
- Price: ${propertyData.price || 'Not specified'}
- Property Type: ${propertyData.propertyType || 'Not specified'}
- Square Footage: ${propertyData.sqft || 'Not specified'}
- Bedrooms: ${propertyData.bedrooms || 'Not specified'}
- Bathrooms: ${propertyData.bathrooms || 'Not specified'}
- Year Built: ${propertyData.yearBuilt || 'Not specified'}
- Current/Expected Rent: ${propertyData.rentAmount || 'Not specified'}
- Market Area: ${propertyData.marketArea || 'Not specified'}

Requirements:
1. Use current market data and trends
2. Include detailed financial calculations
3. Provide risk assessment and mitigation strategies
4. Include comparable properties analysis
5. Format with professional real estate terminology
6. Add investment recommendations and action items
7. Include market timing considerations
8. Provide both conservative and optimistic scenarios

Create a comprehensive, actionable real estate analysis that investors can use for decision-making.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `realestate_${toolId}_${Date.now()}`,
        model: 'gpt-3.5-turbo'
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      setAnalysisResult(response.data.response)
      
      // Open analysis in new window
      const newWindow = window.open()
      newWindow.document.write(`
        <html>
          <head>
            <title>Real Estate Analysis - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 3px solid #27ae60; padding-bottom: 15px; }
              .property-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #27ae60; }
              .financial-summary { background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .risk-warning { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #ffeaa7; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #27ae60; color: white; }
              .highlight { background: #d4edda; font-weight: bold; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="property-info">
              <strong>Property:</strong> ${propertyData.address || 'Not specified'}<br>
              <strong>Price:</strong> ${propertyData.price || 'Not specified'}<br>
              <strong>Type:</strong> ${propertyData.propertyType || 'Not specified'}<br>
              <strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #27ae60; color: white; border: none; border-radius: 4px;">Print Analysis</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating real estate analysis:', error)
      setAnalysisResult('Error generating analysis. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="realestate-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="realestate-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="realestate-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-analysis-btn"
                onClick={() => generateRealEstateAnalysis(tool.id)}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? '⏳ Analyzing...' : '🏠 Generate Analysis'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="realestate-tools">
      <div className="realestate-header">
        <h1>🏠 Real Estate & Investment Tools</h1>
        <p>Professional real estate analysis, investment calculations, and market research</p>
      </div>

      <div className="realestate-form">
        <h3>Property Information</h3>
        <div className="form-grid">
          <input
            type="text"
            placeholder="Property Address"
            value={propertyData.address}
            onChange={(e) => setPropertyData({...propertyData, address: e.target.value})}
          />
          <input
            type="text"
            placeholder="Purchase/List Price"
            value={propertyData.price}
            onChange={(e) => setPropertyData({...propertyData, price: e.target.value})}
          />
          <select
            value={propertyData.propertyType}
            onChange={(e) => setPropertyData({...propertyData, propertyType: e.target.value})}
          >
            <option value="">Property Type</option>
            <option value="single-family">Single Family</option>
            <option value="condo">Condominium</option>
            <option value="townhouse">Townhouse</option>
            <option value="duplex">Duplex</option>
            <option value="multi-family">Multi-Family</option>
            <option value="commercial">Commercial</option>
            <option value="land">Land</option>
          </select>
          <input
            type="text"
            placeholder="Square Footage"
            value={propertyData.sqft}
            onChange={(e) => setPropertyData({...propertyData, sqft: e.target.value})}
          />
          <input
            type="text"
            placeholder="Bedrooms"
            value={propertyData.bedrooms}
            onChange={(e) => setPropertyData({...propertyData, bedrooms: e.target.value})}
          />
          <input
            type="text"
            placeholder="Bathrooms"
            value={propertyData.bathrooms}
            onChange={(e) => setPropertyData({...propertyData, bathrooms: e.target.value})}
          />
          <input
            type="text"
            placeholder="Year Built"
            value={propertyData.yearBuilt}
            onChange={(e) => setPropertyData({...propertyData, yearBuilt: e.target.value})}
          />
          <input
            type="text"
            placeholder="Monthly Rent"
            value={propertyData.rentAmount}
            onChange={(e) => setPropertyData({...propertyData, rentAmount: e.target.value})}
          />
          <input
            type="text"
            placeholder="Market Area/Neighborhood"
            value={propertyData.marketArea}
            onChange={(e) => setPropertyData({...propertyData, marketArea: e.target.value})}
          />
        </div>
      </div>

      <div className="realestate-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`realestate-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="realestate-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default RealEstateTools