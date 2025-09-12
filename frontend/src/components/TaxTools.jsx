import React, { useState } from 'react'
import axios from 'axios'

function TaxTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('preparation')
  const [taxData, setTaxData] = useState({
    filingStatus: '',
    income: '',
    state: '',
    businessType: '',
    dependents: '',
    deductions: '',
    investments: '',
    realEstate: '',
    taxYear: new Date().getFullYear().toString()
  })
  const [isCalculating, setIsCalculating] = useState(false)
  const [taxResult, setTaxResult] = useState('')

  const sections = {
    preparation: {
      title: 'Tax Preparation',
      icon: '📋',
      tools: [
        { id: 'tax_return_1040', name: 'Form 1040 Preparation', description: 'Complete individual tax return preparation' },
        { id: 'business_tax_return', name: 'Business Tax Returns', description: 'LLC, Corp, Partnership, and Schedule C' },
        { id: 'amended_return', name: 'Amended Returns', description: 'Form 1040X and error corrections' },
        { id: 'extension_filing', name: 'Extension Filing', description: 'Form 4868 automatic extension requests' },
        { id: 'quarterly_estimates', name: 'Quarterly Estimates', description: 'Form 1040ES estimated tax payments' },
        { id: 'tax_organizer', name: 'Tax Document Organizer', description: 'Complete tax preparation checklist' }
      ]
    },
    deductions: {
      title: 'Deductions & Credits',
      icon: '💰',
      tools: [
        { id: 'itemized_deductions', name: 'Itemized Deductions', description: 'Schedule A optimization analysis' },
        { id: 'business_deductions', name: 'Business Deductions', description: 'Schedule C expense optimization' },
        { id: 'tax_credits', name: 'Tax Credits Finder', description: 'All available federal and state credits' },
        { id: 'charitable_deductions', name: 'Charitable Deductions', description: 'Donation optimization strategies' },
        { id: 'home_office', name: 'Home Office Deduction', description: 'Form 8829 calculations' },
        { id: 'vehicle_deductions', name: 'Vehicle Deductions', description: 'Business use of auto calculations' }
      ]
    },
    planning: {
      title: 'Tax Planning',
      icon: '📊',
      tools: [
        { id: 'tax_projection', name: 'Tax Projection', description: 'Year-end tax liability estimates' },
        { id: 'withholding_calculator', name: 'Withholding Calculator', description: 'W-4 optimization analysis' },
        { id: 'retirement_planning', name: 'Retirement Tax Planning', description: 'IRA, 401k, and distribution strategies' },
        { id: 'capital_gains', name: 'Capital Gains Planning', description: 'Investment tax optimization' },
        { id: 'entity_selection', name: 'Business Entity Selection', description: 'Tax-efficient business structure analysis' },
        { id: 'year_end_moves', name: 'Year-End Tax Moves', description: 'December tax optimization strategies' }
      ]
    },
    business: {
      title: 'Business Tax Tools',
      icon: '🏢',
      tools: [
        { id: 'payroll_tax', name: 'Payroll Tax Calculator', description: 'Employment tax calculations' },
        { id: 'sales_tax', name: 'Sales Tax Compliance', description: 'Multi-state sales tax analysis' },
        { id: 'business_credits', name: 'Business Tax Credits', description: 'R&D, Work Opportunity, and other credits' },
        { id: 'depreciation', name: 'Depreciation Calculator', description: 'MACRS, Section 179, and Bonus depreciation' },
        { id: 'inventory_methods', name: 'Inventory Tax Methods', description: 'FIFO, LIFO, and uniform capitalization' },
        { id: 'international_tax', name: 'International Tax', description: 'Foreign income and FBAR compliance' }
      ]
    },
    audit: {
      title: 'Audit & Compliance',
      icon: '🔍',
      tools: [
        { id: 'audit_risk', name: 'Audit Risk Assessment', description: 'IRS audit probability analysis' },
        { id: 'audit_prep', name: 'Audit Preparation', description: 'Documentation and response strategies' },
        { id: 'penalty_calculator', name: 'Penalty Calculator', description: 'IRS penalties and interest calculations' },
        { id: 'installment_agreement', name: 'Installment Agreements', description: 'Payment plan optimization' },
        { id: 'offer_in_compromise', name: 'Offer in Compromise', description: 'Tax debt settlement analysis' },
        { id: 'statute_limitations', name: 'Statute of Limitations', description: 'Collection and assessment periods' }
      ]
    },
    state: {
      title: 'State & Local Tax',
      icon: '🏛️',
      tools: [
        { id: 'state_tax_calc', name: 'State Tax Calculator', description: 'All 50 state tax calculations' },
        { id: 'multi_state', name: 'Multi-State Returns', description: 'Non-resident and part-year filings' },
        { id: 'salt_deduction', name: 'SALT Deduction', description: 'State and local tax deduction optimization' },
        { id: 'property_tax', name: 'Property Tax Appeals', description: 'Assessment challenge strategies' },
        { id: 'nexus_analysis', name: 'Nexus Analysis', description: 'State tax filing requirements' },
        { id: 'residency_planning', name: 'Residency Planning', description: 'State tax residency optimization' }
      ]
    }
  }

  const generateTaxAnalysis = async (toolId) => {
    setIsCalculating(true)

    const prompts = {
      tax_return_1040: `Prepare comprehensive Form 1040 analysis with: Income Reporting, Deduction Optimization, Tax Credits Analysis, Tax Liability Calculation, Refund/Payment Due, and Filing Strategy recommendations.`,
      
      itemized_deductions: `Analyze itemized deductions vs standard deduction with: Medical Expenses, State/Local Tax Deduction, Mortgage Interest, Charitable Contributions, Miscellaneous Deductions, and optimization strategies for maximum tax benefit.`,
      
      business_deductions: `Optimize business deductions including: Office Expenses, Equipment Purchases, Travel & Entertainment, Professional Services, Insurance, Marketing Costs, Section 179 Elections, and audit-safe documentation requirements.`,
      
      tax_projection: `Calculate year-end tax projections with: Income Forecasting, Quarterly Payment Analysis, Withholding Optimization, Tax Planning Opportunities, Estimated Tax Requirements, and December tax moves.`,
      
      retirement_planning: `Analyze retirement tax strategies including: Traditional vs Roth IRA Analysis, 401k Contribution Optimization, Distribution Planning, Tax-Deferred Growth Projections, RMD Calculations, and succession planning.`,
      
      capital_gains: `Optimize capital gains taxation with: Short vs Long-term Analysis, Tax-Loss Harvesting, Section 1031 Exchanges, Installment Sale Benefits, Net Investment Income Tax, and portfolio tax efficiency.`,
      
      payroll_tax: `Calculate payroll tax obligations including: Federal Withholding, Social Security/Medicare Tax, State Withholding, Unemployment Tax, Worker Classification, and quarterly deposit requirements.`,
      
      audit_risk: `Assess IRS audit risk factors including: Income Level Analysis, Deduction Ratios, Red Flag Identification, Industry Benchmarks, Historical Audit Rates, and risk mitigation strategies.`,
      
      state_tax_calc: `Calculate multi-state tax obligations including: Resident vs Non-resident Status, Allocation and Apportionment, Tax Credits, Reciprocity Agreements, and compliance requirements.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are a Certified Public Accountant and tax expert. ${prompts[toolId] || 'Provide comprehensive tax analysis and optimization recommendations.'} 

Taxpayer Information:
- Filing Status: ${taxData.filingStatus || 'Not specified'}
- Annual Income: ${taxData.income || 'Not specified'}
- State: ${taxData.state || 'Not specified'}
- Business Type: ${taxData.businessType || 'Not specified'}
- Dependents: ${taxData.dependents || 'Not specified'}
- Current Deductions: ${taxData.deductions || 'Not specified'}
- Investment Income: ${taxData.investments || 'Not specified'}
- Real Estate: ${taxData.realEstate || 'Not specified'}
- Tax Year: ${taxData.taxYear}

Requirements:
1. Use current tax law and rates for ${taxData.taxYear}
2. Provide specific calculations and dollar amounts
3. Include federal and state tax implications
4. Identify all available deductions and credits
5. Format as professional tax analysis document
6. Add compliance and audit considerations
7. Include planning opportunities for next year
8. Provide both current year and multi-year strategies

IMPORTANT DISCLAIMER: This is for informational purposes only. Always consult a qualified tax professional for specific tax advice.

Create comprehensive tax analysis that maximizes tax savings while ensuring full compliance.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `tax_${toolId}_${Date.now()}`,
        model: 'gpt-3.5-turbo'
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      setTaxResult(response.data.response)
      
      // Open analysis in new window
      const newWindow = window.open()
      newWindow.document.write(`
        <html>
          <head>
            <title>Tax Analysis - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 3px solid #16a085; padding-bottom: 15px; }
              .tax-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #16a085; }
              .calculation-box { background: #e8f8f5; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .warning-box { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #ffeaa7; }
              .savings-highlight { background: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #c3e6cb; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #16a085; color: white; }
              .tax-amount { font-weight: bold; font-size: 1.2em; }
              .disclaimer { background: #f8d7da; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #f5c6cb; font-size: 0.9em; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="tax-info">
              <strong>Taxpayer:</strong> ${taxData.filingStatus || 'Not specified'}<br>
              <strong>Income:</strong> ${taxData.income || 'Not specified'}<br>
              <strong>State:</strong> ${taxData.state || 'Not specified'}<br>
              <strong>Tax Year:</strong> ${taxData.taxYear}<br>
              <strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <div class="disclaimer">
              <strong>DISCLAIMER:</strong> This analysis is for informational purposes only and does not constitute professional tax advice. 
              Tax laws are complex and change frequently. Always consult with a qualified tax professional or CPA before making tax decisions.
            </div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #16a085; color: white; border: none; border-radius: 4px;">Print Analysis</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating tax analysis:', error)
      setTaxResult('Error generating tax analysis. Please try again.')
    } finally {
      setIsCalculating(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="tax-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="tax-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="tax-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-tax-btn"
                onClick={() => generateTaxAnalysis(tool.id)}
                disabled={isCalculating}
              >
                {isCalculating ? '⏳ Calculating...' : '🧮 Generate Analysis'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="tax-tools">
      <div className="tax-header">
        <h1>🧮 Tax Preparation & Optimization</h1>
        <p>Professional tax preparation, planning, and compliance tools</p>
        <div className="tax-disclaimer">
          <strong>⚠️ Tax Disclaimer:</strong> These tools provide general tax information only. 
          Always consult a qualified tax professional for specific tax advice.
        </div>
      </div>

      <div className="tax-form">
        <h3>Tax Information</h3>
        <div className="form-grid">
          <select
            value={taxData.filingStatus}
            onChange={(e) => setTaxData({...taxData, filingStatus: e.target.value})}
          >
            <option value="">Filing Status</option>
            <option value="single">Single</option>
            <option value="married-joint">Married Filing Jointly</option>
            <option value="married-separate">Married Filing Separately</option>
            <option value="head-household">Head of Household</option>
            <option value="qualifying-widow">Qualifying Widow(er)</option>
          </select>
          <input
            type="text"
            placeholder="Annual Income"
            value={taxData.income}
            onChange={(e) => setTaxData({...taxData, income: e.target.value})}
          />
          <input
            type="text"
            placeholder="State"
            value={taxData.state}
            onChange={(e) => setTaxData({...taxData, state: e.target.value})}
          />
          <select
            value={taxData.businessType}
            onChange={(e) => setTaxData({...taxData, businessType: e.target.value})}
          >
            <option value="">Business Type</option>
            <option value="none">No Business</option>
            <option value="sole-proprietor">Sole Proprietor</option>
            <option value="llc">LLC</option>
            <option value="s-corp">S-Corporation</option>
            <option value="c-corp">C-Corporation</option>
            <option value="partnership">Partnership</option>
          </select>
          <input
            type="text"
            placeholder="Number of Dependents"
            value={taxData.dependents}
            onChange={(e) => setTaxData({...taxData, dependents: e.target.value})}
          />
          <input
            type="text"
            placeholder="Current Deductions"
            value={taxData.deductions}
            onChange={(e) => setTaxData({...taxData, deductions: e.target.value})}
          />
          <input
            type="text"
            placeholder="Investment Income"
            value={taxData.investments}
            onChange={(e) => setTaxData({...taxData, investments: e.target.value})}
          />
          <input
            type="text"
            placeholder="Real Estate Owned"
            value={taxData.realEstate}
            onChange={(e) => setTaxData({...taxData, realEstate: e.target.value})}
          />
          <select
            value={taxData.taxYear}
            onChange={(e) => setTaxData({...taxData, taxYear: e.target.value})}
          >
            <option value="2024">2024 Tax Year</option>
            <option value="2023">2023 Tax Year</option>
            <option value="2022">2022 Tax Year</option>
            <option value="2021">2021 Tax Year</option>
          </select>
        </div>
      </div>

      <div className="tax-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`tax-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="tax-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default TaxTools