import React, { useState } from 'react'
import axios from 'axios'

function AgricultureTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('planning')
  const [farmData, setFarmData] = useState({
    farmType: '',
    acreage: '',
    location: '',
    climateZone: '',
    soilType: '',
    waterSource: '',
    crops: '',
    livestock: '',
    experience: ''
  })
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState('')

  const sections = {
    planning: {
      title: 'Farm Planning',
      icon: '🌱',
      tools: [
        { id: 'crop_selection', name: 'Crop Selection Optimizer', description: 'Climate and soil-based crop recommendations' },
        { id: 'field_layout', name: 'Field Layout Design', description: 'Optimal field configuration and rotation planning' },
        { id: 'planting_calendar', name: 'Planting Calendar', description: 'Season-specific planting and harvesting schedules' },
        { id: 'rotation_planning', name: 'Crop Rotation Planning', description: 'Multi-year rotation strategies for soil health' },
        { id: 'companion_planting', name: 'Companion Planting', description: 'Beneficial plant combinations and spacing' },
        { id: 'succession_planting', name: 'Succession Planting', description: 'Continuous harvest planning and scheduling' }
      ]
    },
    soil: {
      title: 'Soil Management',
      icon: '🌍',
      tools: [
        { id: 'soil_testing', name: 'Soil Testing Analysis', description: 'pH, nutrients, and composition analysis' },
        { id: 'fertilizer_calculator', name: 'Fertilizer Calculator', description: 'NPK requirements and application rates' },
        { id: 'composting_guide', name: 'Composting Systems', description: 'Organic matter and compost management' },
        { id: 'erosion_control', name: 'Erosion Control', description: 'Soil conservation and protection strategies' },
        { id: 'cover_crops', name: 'Cover Crop Planning', description: 'Soil improvement through cover cropping' },
        { id: 'organic_certification', name: 'Organic Certification', description: 'USDA organic compliance and transition planning' }
      ]
    },
    water: {
      title: 'Water Management',
      icon: '💧',
      tools: [
        { id: 'irrigation_design', name: 'Irrigation System Design', description: 'Drip, sprinkler, and flood irrigation planning' },
        { id: 'water_conservation', name: 'Water Conservation', description: 'Efficient water use and conservation strategies' },
        { id: 'drainage_planning', name: 'Drainage Systems', description: 'Field drainage and water management' },
        { id: 'rainwater_harvesting', name: 'Rainwater Harvesting', description: 'Collection and storage system design' },
        { id: 'well_planning', name: 'Well Planning', description: 'Groundwater assessment and well placement' },
        { id: 'water_quality', name: 'Water Quality Testing', description: 'Agricultural water safety and treatment' }
      ]
    },
    livestock: {
      title: 'Livestock Management',
      icon: '🐄',
      tools: [
        { id: 'pasture_management', name: 'Pasture Management', description: 'Rotational grazing and grass management' },
        { id: 'feed_calculator', name: 'Feed Calculator', description: 'Nutritional requirements and feed planning' },
        { id: 'breeding_programs', name: 'Breeding Programs', description: 'Genetic improvement and breeding schedules' },
        { id: 'health_monitoring', name: 'Health Monitoring', description: 'Disease prevention and health management' },
        { id: 'facility_design', name: 'Facility Design', description: 'Barn, shelter, and infrastructure planning' },
        { id: 'record_keeping', name: 'Livestock Records', description: 'Health, breeding, and production tracking' }
      ]
    },
    economics: {
      title: 'Farm Economics',
      icon: '💰',
      tools: [
        { id: 'budget_planning', name: 'Farm Budget Planning', description: 'Income and expense forecasting' },
        { id: 'crop_insurance', name: 'Crop Insurance Analysis', description: 'Risk management and insurance options' },
        { id: 'market_analysis', name: 'Market Analysis', description: 'Commodity prices and market trends' },
        { id: 'grant_finder', name: 'Grant & Subsidy Finder', description: 'Government and private funding opportunities' },
        { id: 'tax_planning', name: 'Agricultural Tax Planning', description: 'Farm-specific tax strategies and deductions' },
        { id: 'enterprise_analysis', name: 'Enterprise Analysis', description: 'Profitability analysis by farm enterprise' }
      ]
    },
    technology: {
      title: 'Farm Technology',
      icon: '🚜',
      tools: [
        { id: 'precision_agriculture', name: 'Precision Agriculture', description: 'GPS, sensors, and data-driven farming' },
        { id: 'drone_applications', name: 'Drone Applications', description: 'Aerial monitoring and crop surveillance' },
        { id: 'equipment_selection', name: 'Equipment Selection', description: 'Machinery needs and cost analysis' },
        { id: 'automation_systems', name: 'Automation Systems', description: 'Farm automation and control systems' },
        { id: 'weather_monitoring', name: 'Weather Monitoring', description: 'Climate tracking and prediction systems' },
        { id: 'farm_management_software', name: 'Farm Management Software', description: 'Digital record keeping and analytics' }
      ]
    }
  }

  const generateAgricultureAnalysis = async (toolId) => {
    setIsAnalyzing(true)

    const prompts = {
      crop_selection: `Recommend optimal crops for the specified farm conditions including: Climate compatibility analysis, Soil suitability assessment, Water requirements evaluation, Market demand and profitability, Growing season optimization, Disease and pest resistance, Labor and equipment requirements, and Yield projections with ROI analysis.`,
      
      soil_testing: `Analyze soil conditions and provide management recommendations including: pH level assessment and adjustment, Nutrient analysis (NPK, micronutrients), Organic matter content evaluation, Soil structure and compaction assessment, Drainage and water retention analysis, Amendment recommendations (lime, sulfur, organic matter), Fertilizer application schedules, and Long-term soil health strategies.`,
      
      irrigation_design: `Design irrigation system including: Water source evaluation and capacity, Irrigation method selection (drip, sprinkler, flood), System layout and component sizing, Pressure requirements and pump selection, Filtration and water treatment needs, Automation and control systems, Water efficiency optimization, and Cost-benefit analysis with payback period.`,
      
      pasture_management: `Create pasture management plan including: Grass species selection and establishment, Rotational grazing schedule and paddock design, Stocking rate optimization, Fertilization and overseeding programs, Weed and pest control strategies, Water system placement, Fence and gate planning, and Pasture improvement timeline.`,
      
      budget_planning: `Develop comprehensive farm budget including: Revenue projections by enterprise, Variable costs (seeds, fertilizer, fuel, labor), Fixed costs (land, equipment, insurance), Cash flow analysis by month, Break-even analysis, Sensitivity analysis for price and yield variations, Capital investment planning, and Financial performance metrics.`,
      
      precision_agriculture: `Design precision agriculture system including: GPS guidance system selection, Variable rate application technology, Soil sampling and mapping strategies, Yield monitoring and data collection, Data management and analysis platforms, Equipment compatibility assessment, Implementation timeline and training, and ROI analysis with productivity gains.`,
      
      planting_calendar: `Create detailed planting calendar including: Frost dates and growing season analysis, Crop-specific planting windows, Succession planting schedules, Companion and intercropping timing, Field preparation schedules, Harvest timing optimization, Storage and processing considerations, and Weather contingency planning.`,
      
      fertilizer_calculator: `Calculate fertilizer requirements including: Soil test interpretation, Nutrient deficiency identification, NPK recommendations by crop, Application timing and methods, Organic vs synthetic options, Cost comparison analysis, Environmental impact assessment, and Application equipment requirements.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are an agricultural extension specialist and farming consultant. ${prompts[toolId] || 'Provide comprehensive agricultural analysis and farming recommendations.'} 

Farm Information:
- Farm Type: ${farmData.farmType || 'Not specified'}
- Acreage: ${farmData.acreage || 'Not specified'}
- Location: ${farmData.location || 'Not specified'}
- Climate Zone: ${farmData.climateZone || 'Not specified'}
- Soil Type: ${farmData.soilType || 'Not specified'}
- Water Source: ${farmData.waterSource || 'Not specified'}
- Current/Planned Crops: ${farmData.crops || 'Not specified'}
- Livestock: ${farmData.livestock || 'Not specified'}
- Farming Experience: ${farmData.experience || 'Not specified'}

Requirements:
1. Use current agricultural best practices and research
2. Include specific recommendations with quantities and timing
3. Provide cost estimates and economic analysis
4. Consider environmental sustainability and conservation
5. Format as professional agricultural consultation
6. Include implementation timelines and priorities
7. Add risk assessment and contingency planning
8. Provide both conventional and organic options where applicable

Create comprehensive agricultural guidance that maximizes productivity, profitability, and sustainability.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `agriculture_${toolId}_${Date.now()}`,
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
            <title>Agricultural Analysis - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 3px solid #27ae60; padding-bottom: 15px; }
              .farm-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #27ae60; }
              .recommendation-box { background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .timing-box { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #ffeaa7; }
              .cost-analysis { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .sustainability-note { background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #4caf50; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #27ae60; color: white; }
              .seasonal-guide { background: #f1f8e9; padding: 10px; border-radius: 4px; margin: 10px 0; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="farm-info">
              <strong>Farm Type:</strong> ${farmData.farmType || 'Not specified'}<br>
              <strong>Location:</strong> ${farmData.location || 'Not specified'}<br>
              <strong>Acreage:</strong> ${farmData.acreage || 'Not specified'}<br>
              <strong>Climate:</strong> ${farmData.climateZone || 'Not specified'}<br>
              <strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #27ae60; color: white; border: none; border-radius: 4px;">Print Plan</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating agriculture analysis:', error)
      setAnalysisResult('Error generating agricultural analysis. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="agriculture-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="agriculture-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="agriculture-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-agriculture-btn"
                onClick={() => generateAgricultureAnalysis(tool.id)}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? '⏳ Analyzing...' : '🌾 Generate Plan'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="agriculture-tools">
      <div className="agriculture-header">
        <h1>🌾 Agriculture & Farming Tools</h1>
        <p>Comprehensive farm planning, crop management, and agricultural optimization</p>
      </div>

      <div className="agriculture-form">
        <h3>Farm Information</h3>
        <div className="form-grid">
          <select
            value={farmData.farmType}
            onChange={(e) => setFarmData({...farmData, farmType: e.target.value})}
          >
            <option value="">Farm Type</option>
            <option value="crop-farm">Crop Farm</option>
            <option value="livestock-ranch">Livestock Ranch</option>
            <option value="mixed-farm">Mixed Crop & Livestock</option>
            <option value="dairy-farm">Dairy Farm</option>
            <option value="organic-farm">Organic Farm</option>
            <option value="greenhouse">Greenhouse Operation</option>
            <option value="orchard">Orchard/Fruit Farm</option>
            <option value="vegetable-farm">Vegetable Farm</option>
            <option value="grain-farm">Grain Farm</option>
            <option value="specialty-crop">Specialty Crop Farm</option>
          </select>
          <select
            value={farmData.acreage}
            onChange={(e) => setFarmData({...farmData, acreage: e.target.value})}
          >
            <option value="">Farm Size</option>
            <option value="under-5">Under 5 acres</option>
            <option value="5-25">5-25 acres</option>
            <option value="26-100">26-100 acres</option>
            <option value="101-500">101-500 acres</option>
            <option value="501-1000">501-1,000 acres</option>
            <option value="over-1000">Over 1,000 acres</option>
          </select>
          <input
            type="text"
            placeholder="Location (State/Region)"
            value={farmData.location}
            onChange={(e) => setFarmData({...farmData, location: e.target.value})}
          />
          <select
            value={farmData.climateZone}
            onChange={(e) => setFarmData({...farmData, climateZone: e.target.value})}
          >
            <option value="">Climate Zone</option>
            <option value="zone-3">Zone 3 (Very Cold)</option>
            <option value="zone-4">Zone 4 (Cold)</option>
            <option value="zone-5">Zone 5 (Cool)</option>
            <option value="zone-6">Zone 6 (Moderate)</option>
            <option value="zone-7">Zone 7 (Mild)</option>
            <option value="zone-8">Zone 8 (Warm)</option>
            <option value="zone-9">Zone 9 (Hot)</option>
            <option value="zone-10">Zone 10 (Very Hot)</option>
            <option value="tropical">Tropical</option>
          </select>
          <select
            value={farmData.soilType}
            onChange={(e) => setFarmData({...farmData, soilType: e.target.value})}
          >
            <option value="">Soil Type</option>
            <option value="clay">Clay</option>
            <option value="sandy">Sandy</option>
            <option value="loamy">Loamy</option>
            <option value="silty">Silty</option>
            <option value="rocky">Rocky</option>
            <option value="mixed">Mixed</option>
            <option value="unknown">Unknown - Need Testing</option>
          </select>
          <select
            value={farmData.waterSource}
            onChange={(e) => setFarmData({...farmData, waterSource: e.target.value})}
          >
            <option value="">Water Source</option>
            <option value="well">Well Water</option>
            <option value="municipal">Municipal Water</option>
            <option value="surface-water">Surface Water (River/Lake)</option>
            <option value="rainwater">Rainwater Collection</option>
            <option value="irrigation-canal">Irrigation Canal</option>
            <option value="multiple">Multiple Sources</option>
            <option value="none">No Reliable Source</option>
          </select>
          <input
            type="text"
            placeholder="Current/Planned Crops"
            value={farmData.crops}
            onChange={(e) => setFarmData({...farmData, crops: e.target.value})}
          />
          <input
            type="text"
            placeholder="Livestock (if any)"
            value={farmData.livestock}
            onChange={(e) => setFarmData({...farmData, livestock: e.target.value})}
          />
          <select
            value={farmData.experience}
            onChange={(e) => setFarmData({...farmData, experience: e.target.value})}
          >
            <option value="">Farming Experience</option>
            <option value="beginner">Beginner (0-2 years)</option>
            <option value="novice">Novice (3-5 years)</option>
            <option value="intermediate">Intermediate (6-10 years)</option>
            <option value="experienced">Experienced (11-20 years)</option>
            <option value="expert">Expert (20+ years)</option>
          </select>
        </div>
      </div>

      <div className="agriculture-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`agriculture-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="agriculture-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default AgricultureTools