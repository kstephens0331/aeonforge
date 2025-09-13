import React, { useState } from 'react'
import axios from 'axios'

function TransportationTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('logistics')
  const [transportData, setTransportData] = useState({
    operationType: '',
    fleetSize: '',
    serviceArea: '',
    cargoType: '',
    revenue: '',
    routes: '',
    vehicles: '',
    regulations: '',
    technology: ''
  })
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [optimizationResult, setOptimizationResult] = useState('')

  const sections = {
    logistics: {
      title: 'Logistics & Supply Chain',
      icon: '📦',
      tools: [
        { id: 'route_optimization', name: 'Route Optimization', description: 'AI-powered route planning and traffic optimization' },
        { id: 'warehouse_management', name: 'Warehouse Management', description: 'Inventory flow and storage optimization' },
        { id: 'supply_chain', name: 'Supply Chain Analysis', description: 'End-to-end supply chain optimization' },
        { id: 'demand_forecasting', name: 'Demand Forecasting', description: 'Predictive analytics for shipping demand' },
        { id: 'load_planning', name: 'Load Planning', description: 'Cargo optimization and weight distribution' },
        { id: 'delivery_scheduling', name: 'Delivery Scheduling', description: 'Time window optimization and customer satisfaction' }
      ]
    },
    fleet: {
      title: 'Fleet Management',
      icon: '🚚',
      tools: [
        { id: 'fleet_optimization', name: 'Fleet Optimization', description: 'Vehicle allocation and utilization analysis' },
        { id: 'maintenance_scheduling', name: 'Maintenance Scheduling', description: 'Preventive maintenance and downtime reduction' },
        { id: 'fuel_management', name: 'Fuel Management', description: 'Fuel efficiency and cost optimization' },
        { id: 'driver_management', name: 'Driver Management', description: 'Scheduling, performance, and compliance tracking' },
        { id: 'vehicle_tracking', name: 'Vehicle Tracking', description: 'GPS monitoring and real-time fleet visibility' },
        { id: 'telematics_analysis', name: 'Telematics Analysis', description: 'Vehicle performance and driver behavior insights' }
      ]
    },
    shipping: {
      title: 'Shipping & Freight',
      icon: '🚢',
      tools: [
        { id: 'freight_optimization', name: 'Freight Optimization', description: 'Mode selection and carrier comparison' },
        { id: 'container_optimization', name: 'Container Optimization', description: 'Container loading and space utilization' },
        { id: 'international_shipping', name: 'International Shipping', description: 'Global trade and customs compliance' },
        { id: 'last_mile_delivery', name: 'Last Mile Delivery', description: 'Final delivery optimization and customer experience' },
        { id: 'cross_docking', name: 'Cross Docking', description: 'Transshipment and distribution center optimization' },
        { id: 'carrier_selection', name: 'Carrier Selection', description: 'Vendor evaluation and contract optimization' }
      ]
    },
    compliance: {
      title: 'Compliance & Safety',
      icon: '🛡️',
      tools: [
        { id: 'dot_compliance', name: 'DOT Compliance', description: 'Department of Transportation regulatory compliance' },
        { id: 'hours_of_service', name: 'Hours of Service', description: 'Driver fatigue management and HOS compliance' },
        { id: 'safety_management', name: 'Safety Management', description: 'Accident prevention and safety protocols' },
        { id: 'hazmat_compliance', name: 'Hazmat Compliance', description: 'Dangerous goods transportation regulations' },
        { id: 'environmental_compliance', name: 'Environmental Compliance', description: 'Emissions tracking and environmental regulations' },
        { id: 'insurance_optimization', name: 'Insurance Optimization', description: 'Coverage analysis and risk management' }
      ]
    },
    technology: {
      title: 'Transportation Technology',
      icon: '📱',
      tools: [
        { id: 'tms_selection', name: 'TMS Selection', description: 'Transportation Management System evaluation' },
        { id: 'iot_integration', name: 'IoT Integration', description: 'Sensor networks and smart transportation' },
        { id: 'automation_planning', name: 'Automation Planning', description: 'Autonomous vehicles and robotics integration' },
        { id: 'api_integration', name: 'API Integration', description: 'System connectivity and data exchange' },
        { id: 'mobile_solutions', name: 'Mobile Solutions', description: 'Driver and customer mobile applications' },
        { id: 'blockchain_logistics', name: 'Blockchain Logistics', description: 'Supply chain transparency and traceability' }
      ]
    },
    analytics: {
      title: 'Analytics & Optimization',
      icon: '📊',
      tools: [
        { id: 'performance_analytics', name: 'Performance Analytics', description: 'KPI tracking and operational metrics' },
        { id: 'cost_analysis', name: 'Cost Analysis', description: 'Transportation cost optimization and reduction' },
        { id: 'customer_analytics', name: 'Customer Analytics', description: 'Service quality and customer satisfaction metrics' },
        { id: 'network_optimization', name: 'Network Optimization', description: 'Distribution network design and analysis' },
        { id: 'capacity_planning', name: 'Capacity Planning', description: 'Resource allocation and scalability planning' },
        { id: 'benchmarking', name: 'Industry Benchmarking', description: 'Competitive analysis and performance comparison' }
      ]
    }
  }

  const generateTransportationAnalysis = async (toolId) => {
    setIsOptimizing(true)

    const prompts = {
      route_optimization: `Optimize transportation routes including: Traffic pattern analysis, Distance and time calculations, Multi-stop route sequencing, Vehicle capacity constraints, Delivery time windows, Fuel cost minimization, Driver break requirements, Real-time traffic integration, and Emergency route alternatives with cost-benefit analysis.`,
      
      fleet_optimization: `Analyze fleet operations including: Vehicle utilization rates, Right-sizing fleet composition, Replacement timing analysis, Lease vs buy analysis, Geographic deployment optimization, Seasonal demand adjustments, Cost per mile calculations, ROI analysis by vehicle type, and Fleet expansion/reduction recommendations.`,
      
      supply_chain: `Optimize supply chain operations including: Supplier network analysis, Inventory optimization, Lead time reduction strategies, Risk mitigation planning, Cost structure analysis, Performance metrics tracking, Technology integration opportunities, and End-to-end visibility improvements.`,
      
      warehouse_management: `Design warehouse optimization including: Layout and workflow design, Inventory placement strategies, Pick path optimization, Automation opportunities, Labor productivity analysis, Storage capacity utilization, Equipment requirements, and Throughput maximization strategies.`,
      
      freight_optimization: `Optimize freight operations including: Mode selection analysis (truck, rail, air, ocean), Carrier rate comparison, Transit time optimization, Consolidation opportunities, Intermodal transportation options, Seasonal rate fluctuations, Volume discounts analysis, and Service level agreements.`,
      
      dot_compliance: `Ensure DOT compliance including: Regulatory requirements overview, Driver qualification standards, Vehicle inspection protocols, Record keeping requirements, Safety rating maintenance, Violation prevention strategies, Audit preparation, and Compliance monitoring systems.`,
      
      performance_analytics: `Generate performance analytics including: KPI dashboard design, Operational efficiency metrics, Customer service measurements, Financial performance indicators, Trend analysis, Benchmarking against industry standards, Predictive analytics, and Actionable improvement recommendations.`,
      
      tms_selection: `Evaluate Transportation Management Systems including: Feature comparison matrix, Integration capabilities assessment, Scalability analysis, Cost-benefit evaluation, Implementation timeline, Vendor evaluation, ROI projections, and Selection criteria weighting.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are a transportation and logistics expert with deep industry knowledge. ${prompts[toolId] || 'Provide comprehensive transportation analysis and optimization recommendations.'} 

Transportation Business Information:
- Operation Type: ${transportData.operationType || 'Not specified'}
- Fleet Size: ${transportData.fleetSize || 'Not specified'}
- Service Area: ${transportData.serviceArea || 'Not specified'}
- Cargo Type: ${transportData.cargoType || 'Not specified'}
- Annual Revenue: ${transportData.revenue || 'Not specified'}
- Primary Routes: ${transportData.routes || 'Not specified'}
- Vehicle Types: ${transportData.vehicles || 'Not specified'}
- Regulatory Environment: ${transportData.regulations || 'Not specified'}
- Technology Level: ${transportData.technology || 'Not specified'}

Requirements:
1. Use current transportation industry best practices and regulations
2. Include specific metrics, KPIs, and performance indicators
3. Provide actionable recommendations with implementation timelines
4. Consider regulatory compliance and safety requirements
5. Format as professional transportation consulting report
6. Include cost-benefit analysis and ROI projections
7. Add technology integration and automation opportunities
8. Provide both short-term and long-term strategic recommendations

Create comprehensive transportation optimization strategy that improves efficiency, reduces costs, and enhances service quality.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `transportation_${toolId}_${Date.now()}`,
        model: 'gpt-3.5-turbo'
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      setOptimizationResult(response.data.response)
      
      // Open analysis in new window
      const newWindow = window.open()
      newWindow.document.write(`
        <html>
          <head>
            <title>Transportation Analysis - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 15px; }
              .transport-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #3498db; }
              .optimization-box { background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .cost-savings { background: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #c3e6cb; }
              .compliance-warning { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #ffeaa7; }
              .efficiency-metrics { background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #007bff; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #3498db; color: white; }
              .route-info { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="transport-info">
              <strong>Operation:</strong> ${transportData.operationType || 'Not specified'}<br>
              <strong>Fleet Size:</strong> ${transportData.fleetSize || 'Not specified'}<br>
              <strong>Service Area:</strong> ${transportData.serviceArea || 'Not specified'}<br>
              <strong>Cargo Type:</strong> ${transportData.cargoType || 'Not specified'}<br>
              <strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #3498db; color: white; border: none; border-radius: 4px;">Print Analysis</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating transportation analysis:', error)
      setOptimizationResult('Error generating transportation analysis. Please try again.')
    } finally {
      setIsOptimizing(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="transportation-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="transportation-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="transportation-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-transportation-btn"
                onClick={() => generateTransportationAnalysis(tool.id)}
                disabled={isOptimizing}
              >
                {isOptimizing ? '⏳ Optimizing...' : '🚛 Generate Analysis'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="transportation-tools">
      <div className="transportation-header">
        <h1>🚛 Transportation & Logistics Tools</h1>
        <p>Comprehensive fleet management, route optimization, and supply chain solutions</p>
      </div>

      <div className="transportation-form">
        <h3>Transportation Business Information</h3>
        <div className="form-grid">
          <select
            value={transportData.operationType}
            onChange={(e) => setTransportData({...transportData, operationType: e.target.value})}
          >
            <option value="">Operation Type</option>
            <option value="trucking-company">Trucking Company</option>
            <option value="logistics-provider">3PL/4PL Provider</option>
            <option value="courier-service">Courier/Delivery Service</option>
            <option value="freight-forwarder">Freight Forwarder</option>
            <option value="warehouse-operator">Warehouse Operator</option>
            <option value="shipping-line">Shipping Line</option>
            <option value="air-cargo">Air Cargo</option>
            <option value="rail-transport">Rail Transport</option>
            <option value="intermodal">Intermodal Transport</option>
            <option value="last-mile">Last Mile Delivery</option>
          </select>
          <select
            value={transportData.fleetSize}
            onChange={(e) => setTransportData({...transportData, fleetSize: e.target.value})}
          >
            <option value="">Fleet Size</option>
            <option value="1-5">1-5 vehicles</option>
            <option value="6-25">6-25 vehicles</option>
            <option value="26-100">26-100 vehicles</option>
            <option value="101-500">101-500 vehicles</option>
            <option value="over-500">Over 500 vehicles</option>
            <option value="no-fleet">Asset-light/Brokerage</option>
          </select>
          <select
            value={transportData.serviceArea}
            onChange={(e) => setTransportData({...transportData, serviceArea: e.target.value})}
          >
            <option value="">Service Area</option>
            <option value="local">Local (City/Metro)</option>
            <option value="regional">Regional (State/Multi-state)</option>
            <option value="national">National</option>
            <option value="international">International</option>
            <option value="global">Global</option>
          </select>
          <select
            value={transportData.cargoType}
            onChange={(e) => setTransportData({...transportData, cargoType: e.target.value})}
          >
            <option value="">Primary Cargo Type</option>
            <option value="general-freight">General Freight</option>
            <option value="refrigerated">Refrigerated/Cold Chain</option>
            <option value="hazmat">Hazardous Materials</option>
            <option value="oversized">Oversized/Heavy Haul</option>
            <option value="automotive">Automotive</option>
            <option value="retail">Retail/E-commerce</option>
            <option value="food-beverage">Food & Beverage</option>
            <option value="pharmaceutical">Pharmaceutical</option>
            <option value="construction">Construction Materials</option>
            <option value="mixed">Mixed Cargo</option>
          </select>
          <select
            value={transportData.revenue}
            onChange={(e) => setTransportData({...transportData, revenue: e.target.value})}
          >
            <option value="">Annual Revenue</option>
            <option value="under-500k">Under $500K</option>
            <option value="500k-2m">$500K - $2M</option>
            <option value="2m-10m">$2M - $10M</option>
            <option value="10m-50m">$10M - $50M</option>
            <option value="50m-250m">$50M - $250M</option>
            <option value="over-250m">Over $250M</option>
          </select>
          <input
            type="text"
            placeholder="Primary Routes/Lanes"
            value={transportData.routes}
            onChange={(e) => setTransportData({...transportData, routes: e.target.value})}
          />
          <input
            type="text"
            placeholder="Vehicle Types (Truck, Van, etc.)"
            value={transportData.vehicles}
            onChange={(e) => setTransportData({...transportData, vehicles: e.target.value})}
          />
          <select
            value={transportData.regulations}
            onChange={(e) => setTransportData({...transportData, regulations: e.target.value})}
          >
            <option value="">Regulatory Environment</option>
            <option value="intrastate">Intrastate Only</option>
            <option value="interstate">Interstate Commerce</option>
            <option value="international">International Trade</option>
            <option value="specialized">Specialized (Hazmat, etc.)</option>
            <option value="multiple">Multiple Jurisdictions</option>
          </select>
          <select
            value={transportData.technology}
            onChange={(e) => setTransportData({...transportData, technology: e.target.value})}
          >
            <option value="">Technology Adoption Level</option>
            <option value="basic">Basic (Paper-based)</option>
            <option value="emerging">Emerging (Basic Software)</option>
            <option value="intermediate">Intermediate (TMS/GPS)</option>
            <option value="advanced">Advanced (IoT/Analytics)</option>
            <option value="cutting-edge">Cutting-edge (AI/Automation)</option>
          </select>
        </div>
      </div>

      <div className="transportation-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`transportation-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="transportation-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default TransportationTools