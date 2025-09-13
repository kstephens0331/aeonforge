import React, { useState } from 'react'
import axios from 'axios'

function RetailTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('analytics')
  const [retailData, setRetailData] = useState({
    businessType: '',
    industry: '',
    revenue: '',
    customerBase: '',
    salesChannels: '',
    location: '',
    competition: '',
    seasonality: '',
    inventory: ''
  })
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState('')

  const sections = {
    analytics: {
      title: 'Retail Analytics',
      icon: '📊',
      tools: [
        { id: 'sales_analytics', name: 'Sales Analytics', description: 'Revenue analysis, trends, and performance metrics' },
        { id: 'customer_analytics', name: 'Customer Analytics', description: 'Customer behavior, segmentation, and lifetime value' },
        { id: 'inventory_analytics', name: 'Inventory Analytics', description: 'Stock levels, turnover rates, and demand forecasting' },
        { id: 'profit_margin', name: 'Profit Margin Analysis', description: 'Cost analysis and margin optimization' },
        { id: 'seasonal_analysis', name: 'Seasonal Analysis', description: 'Seasonal trends and demand patterns' },
        { id: 'competitor_analysis', name: 'Competitor Analysis', description: 'Market positioning and competitive intelligence' }
      ]
    },
    ecommerce: {
      title: 'E-commerce Optimization',
      icon: '🛒',
      tools: [
        { id: 'website_optimization', name: 'Website Optimization', description: 'Conversion rate optimization and UX analysis' },
        { id: 'product_listing', name: 'Product Listing Optimizer', description: 'SEO-optimized product descriptions and catalogs' },
        { id: 'checkout_optimization', name: 'Checkout Optimization', description: 'Cart abandonment reduction strategies' },
        { id: 'mobile_optimization', name: 'Mobile Optimization', description: 'Mobile commerce and app optimization' },
        { id: 'marketplace_optimization', name: 'Marketplace Optimization', description: 'Amazon, eBay, and platform-specific optimization' },
        { id: 'email_automation', name: 'Email Automation', description: 'Automated email marketing and customer retention' }
      ]
    },
    marketing: {
      title: 'Retail Marketing',
      icon: '📢',
      tools: [
        { id: 'loyalty_programs', name: 'Loyalty Programs', description: 'Customer retention and rewards program design' },
        { id: 'promotional_campaigns', name: 'Promotional Campaigns', description: 'Sales promotions and discount strategies' },
        { id: 'social_commerce', name: 'Social Commerce', description: 'Social media selling and influencer marketing' },
        { id: 'content_marketing', name: 'Content Marketing', description: 'Product content and brand storytelling' },
        { id: 'local_marketing', name: 'Local Marketing', description: 'Geographic and community-based marketing' },
        { id: 'cross_selling', name: 'Cross-selling & Upselling', description: 'Product recommendation and bundling strategies' }
      ]
    },
    inventory: {
      title: 'Inventory Management',
      icon: '📦',
      tools: [
        { id: 'demand_forecasting', name: 'Demand Forecasting', description: 'AI-powered sales prediction and planning' },
        { id: 'stock_optimization', name: 'Stock Optimization', description: 'Optimal inventory levels and reorder points' },
        { id: 'supplier_management', name: 'Supplier Management', description: 'Vendor relationships and procurement optimization' },
        { id: 'warehouse_optimization', name: 'Warehouse Optimization', description: 'Storage efficiency and fulfillment processes' },
        { id: 'abc_analysis', name: 'ABC Analysis', description: 'Product categorization and priority management' },
        { id: 'dead_stock', name: 'Dead Stock Analysis', description: 'Slow-moving inventory identification and clearance' }
      ]
    },
    operations: {
      title: 'Store Operations',
      icon: '🏪',
      tools: [
        { id: 'staff_scheduling', name: 'Staff Scheduling', description: 'Employee scheduling and labor optimization' },
        { id: 'pos_optimization', name: 'POS Optimization', description: 'Point-of-sale system configuration and efficiency' },
        { id: 'store_layout', name: 'Store Layout Design', description: 'Visual merchandising and space optimization' },
        { id: 'loss_prevention', name: 'Loss Prevention', description: 'Theft prevention and security protocols' },
        { id: 'customer_service', name: 'Customer Service', description: 'Service protocols and training programs' },
        { id: 'quality_control', name: 'Quality Control', description: 'Product quality and returns management' }
      ]
    },
    financial: {
      title: 'Financial Management',
      icon: '💰',
      tools: [
        { id: 'pricing_strategy', name: 'Pricing Strategy', description: 'Dynamic pricing and competitive analysis' },
        { id: 'cash_flow', name: 'Cash Flow Management', description: 'Working capital and payment optimization' },
        { id: 'financial_reporting', name: 'Financial Reporting', description: 'P&L analysis and performance dashboards' },
        { id: 'tax_optimization', name: 'Retail Tax Optimization', description: 'Sales tax compliance and optimization' },
        { id: 'cost_reduction', name: 'Cost Reduction', description: 'Expense analysis and operational efficiency' },
        { id: 'roi_analysis', name: 'ROI Analysis', description: 'Marketing and operational return on investment' }
      ]
    }
  }

  const generateRetailAnalysis = async (toolId) => {
    setIsAnalyzing(true)

    const prompts = {
      sales_analytics: `Analyze retail sales performance including: Revenue trends and growth patterns, Product performance rankings, Sales by time period (daily, weekly, monthly), Geographic sales distribution, Channel performance comparison, Customer acquisition costs, Average order value analysis, and Key performance indicators with benchmarks.`,
      
      customer_analytics: `Perform customer analysis including: Customer segmentation and personas, Lifetime value calculations, Purchase behavior patterns, Retention and churn analysis, Demographic and psychographic insights, Customer journey mapping, Loyalty program effectiveness, and Personalization opportunities.`,
      
      inventory_analytics: `Generate inventory insights including: Stock turnover rates by category, Demand forecasting with seasonal adjustments, Inventory carrying costs, Stock-out frequency and impact, Supplier performance metrics, Lead time analysis, Safety stock recommendations, and Inventory optimization strategies.`,
      
      website_optimization: `Optimize e-commerce performance with: Conversion rate analysis and improvement, User experience audit and recommendations, Page load speed optimization, Mobile responsiveness evaluation, SEO analysis and recommendations, A/B testing strategies, Shopping cart optimization, and Customer journey optimization.`,
      
      demand_forecasting: `Create demand forecasting model including: Historical sales trend analysis, Seasonal pattern identification, External factor impact (holidays, events), Market trend integration, Forecast accuracy metrics, Inventory planning recommendations, Reorder point calculations, and Risk assessment scenarios.`,
      
      pricing_strategy: `Develop pricing strategy including: Competitive price analysis, Price elasticity assessment, Dynamic pricing recommendations, Margin optimization strategies, Bundle pricing opportunities, Psychological pricing tactics, Promotional pricing impact, and Market positioning analysis.`,
      
      loyalty_programs: `Design loyalty program including: Program structure and tier design, Reward value optimization, Customer engagement strategies, Gamification elements, Technology platform recommendations, ROI projections and metrics, Communication strategies, and Program launch plan.`,
      
      store_layout: `Optimize store layout with: Customer flow analysis, Product placement strategies, Category adjacency planning, Visual merchandising guidelines, Checkout area optimization, Seasonal layout adjustments, Accessibility compliance, and Sales density optimization.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are a retail consultant and e-commerce optimization expert. ${prompts[toolId] || 'Provide comprehensive retail analysis and optimization recommendations.'} 

Business Information:
- Business Type: ${retailData.businessType || 'Not specified'}
- Industry: ${retailData.industry || 'Not specified'}
- Annual Revenue: ${retailData.revenue || 'Not specified'}
- Customer Base: ${retailData.customerBase || 'Not specified'}
- Sales Channels: ${retailData.salesChannels || 'Not specified'}
- Location: ${retailData.location || 'Not specified'}
- Competition Level: ${retailData.competition || 'Not specified'}
- Seasonality: ${retailData.seasonality || 'Not specified'}
- Inventory Size: ${retailData.inventory || 'Not specified'}

Requirements:
1. Use current retail industry best practices and trends
2. Include specific metrics and KPIs for measurement
3. Provide actionable recommendations with implementation steps
4. Include technology solutions and vendor recommendations
5. Format as professional retail strategy document
6. Add cost-benefit analysis and ROI projections
7. Include competitive advantages and market opportunities
8. Provide both short-term and long-term strategies

Create comprehensive retail optimization strategy that drives sales growth and operational efficiency.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `retail_${toolId}_${Date.now()}`,
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
            <title>Retail Analysis - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 3px solid #9b59b6; padding-bottom: 15px; }
              .business-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #9b59b6; }
              .metrics-box { background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .strategy-section { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #ffeaa7; }
              .implementation-box { background: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #c3e6cb; }
              .roi-highlight { background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #007bff; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #9b59b6; color: white; }
              .recommendation { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; font-weight: bold; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="business-info">
              <strong>Business:</strong> ${retailData.businessType || 'Not specified'}<br>
              <strong>Industry:</strong> ${retailData.industry || 'Not specified'}<br>
              <strong>Revenue:</strong> ${retailData.revenue || 'Not specified'}<br>
              <strong>Channels:</strong> ${retailData.salesChannels || 'Not specified'}<br>
              <strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #9b59b6; color: white; border: none; border-radius: 4px;">Print Analysis</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating retail analysis:', error)
      setAnalysisResult('Error generating retail analysis. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="retail-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="retail-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="retail-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-retail-btn"
                onClick={() => generateRetailAnalysis(tool.id)}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? '⏳ Analyzing...' : '🛒 Generate Analysis'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="retail-tools">
      <div className="retail-header">
        <h1>🛒 Retail & E-commerce Optimization</h1>
        <p>Comprehensive retail analytics, operations, and growth optimization tools</p>
      </div>

      <div className="retail-form">
        <h3>Business Information</h3>
        <div className="form-grid">
          <select
            value={retailData.businessType}
            onChange={(e) => setRetailData({...retailData, businessType: e.target.value})}
          >
            <option value="">Business Type</option>
            <option value="brick-mortar">Brick & Mortar Store</option>
            <option value="e-commerce">E-commerce Only</option>
            <option value="omnichannel">Omnichannel Retail</option>
            <option value="marketplace-seller">Marketplace Seller</option>
            <option value="dropshipping">Dropshipping</option>
            <option value="wholesale">Wholesale</option>
            <option value="franchise">Franchise</option>
          </select>
          <select
            value={retailData.industry}
            onChange={(e) => setRetailData({...retailData, industry: e.target.value})}
          >
            <option value="">Industry</option>
            <option value="fashion-apparel">Fashion & Apparel</option>
            <option value="electronics">Electronics</option>
            <option value="home-garden">Home & Garden</option>
            <option value="beauty-cosmetics">Beauty & Cosmetics</option>
            <option value="sports-outdoors">Sports & Outdoors</option>
            <option value="books-media">Books & Media</option>
            <option value="food-beverage">Food & Beverage</option>
            <option value="toys-games">Toys & Games</option>
            <option value="health-wellness">Health & Wellness</option>
            <option value="automotive">Automotive</option>
          </select>
          <select
            value={retailData.revenue}
            onChange={(e) => setRetailData({...retailData, revenue: e.target.value})}
          >
            <option value="">Annual Revenue</option>
            <option value="under-50k">Under $50K</option>
            <option value="50k-250k">$50K - $250K</option>
            <option value="250k-1m">$250K - $1M</option>
            <option value="1m-5m">$1M - $5M</option>
            <option value="5m-25m">$5M - $25M</option>
            <option value="over-25m">Over $25M</option>
          </select>
          <select
            value={retailData.customerBase}
            onChange={(e) => setRetailData({...retailData, customerBase: e.target.value})}
          >
            <option value="">Customer Base Size</option>
            <option value="under-100">Under 100</option>
            <option value="100-1k">100 - 1,000</option>
            <option value="1k-10k">1,000 - 10,000</option>
            <option value="10k-100k">10,000 - 100,000</option>
            <option value="over-100k">Over 100,000</option>
          </select>
          <input
            type="text"
            placeholder="Sales Channels (Online, Store, Marketplace, etc.)"
            value={retailData.salesChannels}
            onChange={(e) => setRetailData({...retailData, salesChannels: e.target.value})}
          />
          <input
            type="text"
            placeholder="Primary Location/Market"
            value={retailData.location}
            onChange={(e) => setRetailData({...retailData, location: e.target.value})}
          />
          <select
            value={retailData.competition}
            onChange={(e) => setRetailData({...retailData, competition: e.target.value})}
          >
            <option value="">Competition Level</option>
            <option value="low">Low Competition</option>
            <option value="moderate">Moderate Competition</option>
            <option value="high">High Competition</option>
            <option value="intense">Intense Competition</option>
          </select>
          <select
            value={retailData.seasonality}
            onChange={(e) => setRetailData({...retailData, seasonality: e.target.value})}
          >
            <option value="">Seasonality Impact</option>
            <option value="none">No Seasonality</option>
            <option value="low">Low Seasonal Variation</option>
            <option value="moderate">Moderate Seasonality</option>
            <option value="high">High Seasonality</option>
            <option value="holiday-driven">Holiday Driven</option>
          </select>
          <select
            value={retailData.inventory}
            onChange={(e) => setRetailData({...retailData, inventory: e.target.value})}
          >
            <option value="">Inventory Size</option>
            <option value="under-100">Under 100 SKUs</option>
            <option value="100-500">100 - 500 SKUs</option>
            <option value="500-2k">500 - 2,000 SKUs</option>
            <option value="2k-10k">2,000 - 10,000 SKUs</option>
            <option value="over-10k">Over 10,000 SKUs</option>
          </select>
        </div>
      </div>

      <div className="retail-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`retail-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="retail-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default RetailTools