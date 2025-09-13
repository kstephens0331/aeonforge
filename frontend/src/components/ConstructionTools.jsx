import React, { useState } from 'react'
import axios from 'axios'

function ConstructionTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('planning')
  const [constructionData, setConstructionData] = useState({
    projectType: '',
    location: '',
    squareFootage: '',
    budget: '',
    timeline: '',
    buildingType: '',
    soilType: '',
    climateZone: '',
    codes: ''
  })
  const [isCalculating, setIsCalculating] = useState(false)
  const [calculationResult, setCalculationResult] = useState('')

  const sections = {
    planning: {
      title: 'Project Planning',
      icon: '📐',
      tools: [
        { id: 'project_feasibility', name: 'Project Feasibility Study', description: 'Comprehensive project viability and risk assessment' },
        { id: 'site_analysis', name: 'Site Analysis', description: 'Topographical, geological, and environmental evaluation' },
        { id: 'design_development', name: 'Design Development', description: 'Architectural and engineering design planning' },
        { id: 'permit_planning', name: 'Permit Planning', description: 'Building permits and regulatory compliance' },
        { id: 'schedule_planning', name: 'Construction Scheduling', description: 'Project timeline and critical path analysis' },
        { id: 'risk_assessment', name: 'Risk Assessment', description: 'Construction risk identification and mitigation' }
      ]
    },
    estimation: {
      title: 'Cost Estimation',
      icon: '💰',
      tools: [
        { id: 'cost_estimator', name: 'Construction Cost Estimator', description: 'Detailed project cost breakdown and analysis' },
        { id: 'material_calculator', name: 'Material Calculator', description: 'Quantity takeoffs and material requirements' },
        { id: 'labor_calculator', name: 'Labor Cost Calculator', description: 'Workforce planning and labor cost analysis' },
        { id: 'equipment_rental', name: 'Equipment Rental Analysis', description: 'Heavy machinery and tool rental optimization' },
        { id: 'bid_preparation', name: 'Bid Preparation', description: 'Competitive bidding and proposal development' },
        { id: 'change_order', name: 'Change Order Management', description: 'Project modification cost analysis' }
      ]
    },
    structural: {
      title: 'Structural Engineering',
      icon: '🏗️',
      tools: [
        { id: 'load_calculations', name: 'Load Calculations', description: 'Dead, live, wind, and seismic load analysis' },
        { id: 'foundation_design', name: 'Foundation Design', description: 'Footing, slab, and deep foundation engineering' },
        { id: 'beam_design', name: 'Beam Design', description: 'Steel and concrete beam sizing and analysis' },
        { id: 'column_design', name: 'Column Design', description: 'Compression member design and analysis' },
        { id: 'seismic_analysis', name: 'Seismic Analysis', description: 'Earthquake resistance and code compliance' },
        { id: 'wind_analysis', name: 'Wind Load Analysis', description: 'Hurricane and wind resistance calculations' }
      ]
    },
    mechanical: {
      title: 'MEP Engineering',
      icon: '⚡',
      tools: [
        { id: 'hvac_design', name: 'HVAC Design', description: 'Heating, ventilation, and air conditioning systems' },
        { id: 'electrical_design', name: 'Electrical Design', description: 'Power distribution and lighting design' },
        { id: 'plumbing_design', name: 'Plumbing Design', description: 'Water supply and drainage system design' },
        { id: 'fire_protection', name: 'Fire Protection Systems', description: 'Sprinkler and fire safety system design' },
        { id: 'energy_analysis', name: 'Energy Analysis', description: 'Building energy efficiency and LEED compliance' },
        { id: 'load_calculations_mep', name: 'MEP Load Calculations', description: 'Electrical, thermal, and hydraulic load analysis' }
      ]
    },
    safety: {
      title: 'Safety & Compliance',
      icon: '🦺',
      tools: [
        { id: 'safety_plan', name: 'Safety Plan Development', description: 'OSHA-compliant safety planning and protocols' },
        { id: 'code_compliance', name: 'Code Compliance Check', description: 'Building code verification and analysis' },
        { id: 'inspection_checklist', name: 'Inspection Checklists', description: 'Quality control and inspection protocols' },
        { id: 'hazmat_assessment', name: 'Hazardous Materials', description: 'Asbestos, lead, and environmental hazard assessment' },
        { id: 'emergency_planning', name: 'Emergency Planning', description: 'Evacuation and emergency response procedures' },
        { id: 'insurance_analysis', name: 'Insurance Analysis', description: 'Construction insurance and liability assessment' }
      ]
    },
    management: {
      title: 'Project Management',
      icon: '👷',
      tools: [
        { id: 'project_tracking', name: 'Project Tracking', description: 'Progress monitoring and milestone management' },
        { id: 'resource_planning', name: 'Resource Planning', description: 'Workforce and material resource allocation' },
        { id: 'quality_control', name: 'Quality Control', description: 'QA/QC protocols and defect tracking' },
        { id: 'vendor_management', name: 'Vendor Management', description: 'Subcontractor and supplier coordination' },
        { id: 'communication_plan', name: 'Communication Plan', description: 'Stakeholder communication and reporting' },
        { id: 'closeout_procedures', name: 'Project Closeout', description: 'Final inspections and project handover' }
      ]
    }
  }

  const generateConstructionAnalysis = async (toolId) => {
    setIsCalculating(true)

    const prompts = {
      cost_estimator: `Generate comprehensive construction cost estimate including: Site preparation costs, Foundation and structural costs, Framing and envelope costs, MEP systems costs, Interior finishes costs, Contingency allowances, Labor rates by trade, Equipment and tool costs, Permit and inspection fees, and Total project cost breakdown with square foot pricing.`,
      
      load_calculations: `Perform structural load calculations including: Dead load analysis (structural self-weight), Live load requirements per occupancy, Snow load calculations for roof design, Wind load analysis per ASCE 7, Seismic load calculations and base shear, Load combinations per building code, Critical load paths identification, and Safety factor applications.`,
      
      material_calculator: `Calculate material quantities including: Concrete volume and reinforcement, Lumber quantities by dimension, Steel tonnage and connection requirements, Masonry unit counts and mortar, Roofing materials and underlayment, Insulation board feet calculations, Drywall and finishing materials, and Waste factors and delivery scheduling.`,
      
      hvac_design: `Design HVAC system including: Heat loss and gain calculations, Equipment sizing and selection, Ductwork design and layout, Zone control and thermostat placement, Ventilation requirements per code, Energy efficiency optimization, Equipment specifications and costs, and Installation and commissioning procedures.`,
      
      safety_plan: `Develop comprehensive safety plan including: Hazard identification and analysis, Personal protective equipment requirements, Fall protection and scaffolding safety, Excavation and trenching safety, Electrical safety protocols, Equipment operation safety, Emergency response procedures, and OSHA compliance documentation.`,
      
      project_feasibility: `Conduct project feasibility analysis including: Market analysis and demand assessment, Site suitability and constraints, Regulatory and zoning compliance, Environmental impact considerations, Financial pro forma and ROI analysis, Risk assessment and mitigation, Timeline and milestone analysis, and Go/no-go recommendations.`,
      
      foundation_design: `Design foundation system including: Soil bearing capacity analysis, Foundation type selection and sizing, Reinforcement design and detailing, Waterproofing and drainage design, Frost protection considerations, Settlement analysis and monitoring, Construction sequencing and methods, and Cost estimation and specifications.`,
      
      electrical_design: `Design electrical system including: Load calculations and demand factors, Panel schedules and circuit design, Lighting design and control systems, Power distribution and receptacle layout, Code compliance and safety requirements, Energy efficiency and smart systems, Equipment specifications and costs, and Installation and testing procedures.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are a licensed professional engineer and construction manager. ${prompts[toolId] || 'Provide comprehensive construction analysis and engineering recommendations.'} 

Project Information:
- Project Type: ${constructionData.projectType || 'Not specified'}
- Location: ${constructionData.location || 'Not specified'}
- Square Footage: ${constructionData.squareFootage || 'Not specified'}
- Budget: ${constructionData.budget || 'Not specified'}
- Timeline: ${constructionData.timeline || 'Not specified'}
- Building Type: ${constructionData.buildingType || 'Not specified'}
- Soil Type: ${constructionData.soilType || 'Not specified'}
- Climate Zone: ${constructionData.climateZone || 'Not specified'}
- Building Codes: ${constructionData.codes || 'Not specified'}

Requirements:
1. Use current building codes and engineering standards
2. Include detailed calculations and technical specifications
3. Provide safety factors and code compliance verification
4. Include material specifications and vendor recommendations
5. Format as professional engineering documentation
6. Add cost estimates and timeline projections
7. Include quality control and inspection requirements
8. Provide both design options and value engineering alternatives

IMPORTANT: This analysis is for preliminary planning only. All structural and MEP designs must be reviewed and sealed by licensed professionals in the project jurisdiction.

Create comprehensive construction analysis that ensures safety, code compliance, and project success.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `construction_${toolId}_${Date.now()}`,
        model: 'gpt-3.5-turbo'
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      setCalculationResult(response.data.response)
      
      // Open analysis in new window
      const newWindow = window.open()
      newWindow.document.write(`
        <html>
          <head>
            <title>Construction Analysis - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 3px solid #f39c12; padding-bottom: 15px; }
              .project-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #f39c12; }
              .calculation-box { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #ffeaa7; }
              .safety-warning { background: #f8d7da; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #dc3545; color: #721c24; font-weight: bold; }
              .specification-box { background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .cost-summary { background: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #c3e6cb; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #f39c12; color: white; }
              .code-reference { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; font-style: italic; }
              .engineering-disclaimer { background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #ffc107; font-size: 0.9em; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="project-info">
              <strong>Project:</strong> ${constructionData.projectType || 'Not specified'}<br>
              <strong>Location:</strong> ${constructionData.location || 'Not specified'}<br>
              <strong>Size:</strong> ${constructionData.squareFootage || 'Not specified'} sq ft<br>
              <strong>Budget:</strong> ${constructionData.budget || 'Not specified'}<br>
              <strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <div class="engineering-disclaimer">
              <strong>🚨 ENGINEERING DISCLAIMER:</strong><br>
              This analysis is for preliminary planning purposes only and does not constitute professional engineering design. 
              All structural, MEP, and architectural designs must be reviewed, modified as necessary, and sealed by licensed 
              professionals in the project jurisdiction before construction. Building codes and requirements vary by location.
            </div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #f39c12; color: white; border: none; border-radius: 4px;">Print Analysis</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating construction analysis:', error)
      setCalculationResult('Error generating construction analysis. Please try again.')
    } finally {
      setIsCalculating(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="construction-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="construction-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="construction-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-construction-btn"
                onClick={() => generateConstructionAnalysis(tool.id)}
                disabled={isCalculating}
              >
                {isCalculating ? '⏳ Calculating...' : '🏗️ Generate Analysis'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="construction-tools">
      <div className="construction-header">
        <h1>🏗️ Construction & Engineering Tools</h1>
        <p>Professional construction planning, engineering design, and project management</p>
        <div className="engineering-disclaimer">
          <strong>⚠️ Engineering Disclaimer:</strong> These tools provide preliminary analysis only. 
          All designs must be reviewed and sealed by licensed professionals before construction.
        </div>
      </div>

      <div className="construction-form">
        <h3>Project Information</h3>
        <div className="form-grid">
          <select
            value={constructionData.projectType}
            onChange={(e) => setConstructionData({...constructionData, projectType: e.target.value})}
          >
            <option value="">Project Type</option>
            <option value="residential-single">Single Family Residential</option>
            <option value="residential-multi">Multi-Family Residential</option>
            <option value="commercial-office">Commercial Office</option>
            <option value="commercial-retail">Commercial Retail</option>
            <option value="industrial">Industrial/Warehouse</option>
            <option value="institutional">Institutional</option>
            <option value="healthcare">Healthcare</option>
            <option value="educational">Educational</option>
            <option value="hospitality">Hospitality</option>
            <option value="mixed-use">Mixed Use</option>
          </select>
          <input
            type="text"
            placeholder="Project Location (City, State)"
            value={constructionData.location}
            onChange={(e) => setConstructionData({...constructionData, location: e.target.value})}
          />
          <input
            type="text"
            placeholder="Square Footage"
            value={constructionData.squareFootage}
            onChange={(e) => setConstructionData({...constructionData, squareFootage: e.target.value})}
          />
          <select
            value={constructionData.budget}
            onChange={(e) => setConstructionData({...constructionData, budget: e.target.value})}
          >
            <option value="">Budget Range</option>
            <option value="under-100k">Under $100K</option>
            <option value="100k-500k">$100K - $500K</option>
            <option value="500k-1m">$500K - $1M</option>
            <option value="1m-5m">$1M - $5M</option>
            <option value="5m-10m">$5M - $10M</option>
            <option value="over-10m">Over $10M</option>
          </select>
          <select
            value={constructionData.timeline}
            onChange={(e) => setConstructionData({...constructionData, timeline: e.target.value})}
          >
            <option value="">Project Timeline</option>
            <option value="3-months">3 months</option>
            <option value="6-months">6 months</option>
            <option value="1-year">1 year</option>
            <option value="18-months">18 months</option>
            <option value="2-years">2 years</option>
            <option value="over-2-years">Over 2 years</option>
          </select>
          <select
            value={constructionData.buildingType}
            onChange={(e) => setConstructionData({...constructionData, buildingType: e.target.value})}
          >
            <option value="">Building Type</option>
            <option value="wood-frame">Wood Frame</option>
            <option value="steel-frame">Steel Frame</option>
            <option value="concrete">Concrete</option>
            <option value="masonry">Masonry</option>
            <option value="prefab">Prefabricated</option>
            <option value="hybrid">Hybrid Construction</option>
          </select>
          <select
            value={constructionData.soilType}
            onChange={(e) => setConstructionData({...constructionData, soilType: e.target.value})}
          >
            <option value="">Soil Type</option>
            <option value="clay">Clay</option>
            <option value="sand">Sand</option>
            <option value="silt">Silt</option>
            <option value="rock">Rock</option>
            <option value="mixed">Mixed</option>
            <option value="unknown">Unknown - Requires Testing</option>
          </select>
          <select
            value={constructionData.climateZone}
            onChange={(e) => setConstructionData({...constructionData, climateZone: e.target.value})}
          >
            <option value="">Climate Zone</option>
            <option value="zone-1">Zone 1 (Very Hot)</option>
            <option value="zone-2">Zone 2 (Hot)</option>
            <option value="zone-3">Zone 3 (Warm)</option>
            <option value="zone-4">Zone 4 (Mixed)</option>
            <option value="zone-5">Zone 5 (Cool)</option>
            <option value="zone-6">Zone 6 (Cold)</option>
            <option value="zone-7">Zone 7 (Very Cold)</option>
            <option value="zone-8">Zone 8 (Subarctic)</option>
          </select>
          <input
            type="text"
            placeholder="Applicable Building Codes (IBC, IRC, etc.)"
            value={constructionData.codes}
            onChange={(e) => setConstructionData({...constructionData, codes: e.target.value})}
          />
        </div>
      </div>

      <div className="construction-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`construction-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="construction-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default ConstructionTools