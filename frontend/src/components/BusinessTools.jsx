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
    if (isAnalyzing) return
    setIsAnalyzing(true)
    setAnalysisResult('')

    const prompts = {
      // Business Planning
      business_plan: `Generate a comprehensive business plan for ${businessData.companyName || 'a new business'} in the ${businessData.industry || 'specified'} industry (${businessData.revenue} revenue stage, ${businessData.funding} funding). Include: 1) Executive Summary with key metrics 2) Company Description with mission/vision 3) Market Analysis with TAM/SAM/SOM calculations 4) Organization structure with team roles 5) Product/Service detailed description 6) Marketing & Sales strategy with CAC/LTV 7) Financial projections (5-year P&L, cash flow, balance sheet) 8) Funding requirements with use of funds 9) Risk analysis with mitigation strategies 10) Implementation milestones. Use actual industry benchmarks and realistic assumptions.`,
      
      executive_summary: `Create a compelling 2-page executive summary for ${businessData.companyName || 'a startup'} targeting ${businessData.targetMarket || 'specified market'}. Include: Problem statement with market pain points, Solution with unique value proposition, Market opportunity with size calculations (TAM $X billion, SAM $Y million, SOM $Z million), Business model with revenue streams, Competitive advantage and differentiation, Traction metrics and milestones, Team credentials and experience, Financial highlights (revenue projections, gross margins, break-even timeline), Funding ask with specific use of funds, Exit strategy potential. Make it investor-ready with compelling data-driven narratives.`,
      
      market_analysis: `Perform comprehensive market analysis for ${businessData.industry || 'the specified industry'} targeting ${businessData.targetMarket || 'specified segment'}. Include: 1) Market size calculation: TAM (Total Addressable Market), SAM (Serviceable Addressable Market), SOM (Serviceable Obtainable Market) with specific dollar amounts 2) Growth trends with 5-year CAGR projections 3) Customer segmentation with demographics, psychographics, and buying behavior 4) Competitive landscape with top 10 competitors, market share analysis, and positioning map 5) Market drivers and trends (technology, regulation, consumer behavior) 6) Barriers to entry and competitive moats 7) Key success factors and critical assumptions 8) Market entry strategy and go-to-market approach. Provide specific data points and industry benchmarks.`,
      
      financial_projections: `Create detailed 5-year financial projections with realistic assumptions. Include: 1) Income Statement: Revenue projections by product/service line, COGS with gross margin calculations, Operating expenses (fixed/variable), EBITDA and net income 2) Cash Flow Statement: Operating cash flow, investing activities, financing activities, free cash flow 3) Balance Sheet: Assets, liabilities, equity with working capital analysis 4) Break-even analysis: Fixed costs, variable costs, contribution margin, break-even units and revenue 5) Key Financial Ratios: Gross margin, operating margin, current ratio, debt-to-equity, ROI, ROE 6) Sensitivity analysis: Best case (+20%), base case, worst case (-20%) scenarios 7) Assumptions: Growth rates, pricing, market penetration, cost inflation 8) Funding requirements with cash runway analysis. Use industry-standard growth rates and benchmarks.`,
      
      swot_analysis: `Conduct comprehensive SWOT analysis for ${businessData.companyName || 'the business'} in ${businessData.industry || 'specified industry'}. STRENGTHS (Internal Positive): Core competencies, unique resources, competitive advantages, team expertise, intellectual property, operational efficiencies, brand recognition, customer loyalty. WEAKNESSES (Internal Negative): Resource constraints, skill gaps, operational inefficiencies, limited market presence, financial limitations, technology gaps, organizational challenges. OPPORTUNITIES (External Positive): Market growth trends, emerging technologies, regulatory changes, partnership opportunities, new customer segments, international expansion, industry consolidation. THREATS (External Negative): Competitive pressure, market saturation, regulatory risks, economic downturns, technology disruption, supplier dependencies, customer concentration. Provide strategic recommendations with action items and prioritization matrix.`,
      
      risk_assessment: `Perform comprehensive business risk assessment for ${businessData.companyName || 'the business'}. Include: 1) Market Risks: Demand fluctuations, competitive threats, customer concentration, pricing pressure 2) Operational Risks: Supply chain disruptions, key person dependency, quality issues, scalability challenges 3) Financial Risks: Cash flow gaps, credit risks, currency exposure, funding availability 4) Technology Risks: System failures, cybersecurity threats, obsolescence, integration challenges 5) Regulatory Risks: Compliance requirements, license dependencies, policy changes, legal disputes 6) Strategic Risks: Partnership failures, acquisition integration, market entry mistakes For each risk: Likelihood (1-5), Impact (1-5), Risk Score, Mitigation strategies, Monitoring indicators, Contingency plans. Include risk matrix and action plan.`,
      
      // Funding & Investment
      pitch_deck: `Create a compelling 12-slide investor pitch deck for ${businessData.companyName || 'a startup'} seeking ${businessData.funding || 'specified'} funding. SLIDE 1: Problem - Specific pain points with market data SLIDE 2: Solution - Product demo/screenshots with key features SLIDE 3: Market Opportunity - TAM/SAM/SOM with growth projections SLIDE 4: Business Model - Revenue streams, pricing, unit economics SLIDE 5: Traction - User growth, revenue, partnerships, testimonials SLIDE 6: Competition - Competitive matrix with differentiation SLIDE 7: Product - Roadmap, features, development timeline SLIDE 8: Marketing Strategy - Customer acquisition, channels, CAC/LTV SLIDE 9: Team - Founders, advisors, key hires with relevant experience SLIDE 10: Financial Projections - 5-year revenue, expenses, profitability SLIDE 11: Funding Ask - Amount, use of funds, milestones SLIDE 12: Investment Terms - Valuation, equity, investor benefits. Include compelling narratives and data visualization suggestions.`,
      
      valuation: `Perform comprehensive business valuation for ${businessData.companyName || 'the business'} (${businessData.revenue} revenue, ${businessData.industry} industry). Use multiple valuation methods: 1) Discounted Cash Flow (DCF): Project 10-year free cash flows, calculate terminal value, determine WACC (weighted average cost of capital), present value calculations 2) Comparable Company Analysis: Identify 10 public company comparables, calculate multiples (EV/Revenue, EV/EBITDA, P/E), apply to subject company 3) Precedent Transaction Analysis: Recent M&A transactions, transaction multiples, control premium adjustments 4) Asset-Based Valuation: Book value, liquidation value, replacement cost 5) Revenue Multiple Method: Industry-specific multiples, growth adjustments 6) Earnings Multiple Method: P/E ratios, PEG ratios, sector analysis Include sensitivity analysis, valuation range (low/mid/high), and recommendations for value enhancement.`,
      
      term_sheet: `Generate professional investment term sheet for ${businessData.companyName || 'the company'} seeking ${businessData.funding || 'specified'} investment. Include: 1) INVESTMENT TERMS: Investment amount, valuation (pre/post-money), price per share, investor ownership percentage 2) SECURITIES: Preferred stock class, liquidation preference (1x non-participating preferred), dividend rate, conversion rights 3) GOVERNANCE: Board composition, voting rights, protective provisions, information rights, registration rights 4) ANTI-DILUTION: Weighted average broad-based, participation rights, drag-along/tag-along rights 5) EMPLOYEE OPTIONS: Option pool size (15-20%), vesting schedules (4-year with 1-year cliff) 6) RESTRICTIONS: Transfer restrictions, right of first refusal, co-sale rights 7) CLOSING CONDITIONS: Due diligence completion, legal documentation, regulatory approvals 8) EXPENSES: Legal fees allocation, closing costs Use standard VC terms with founder-friendly provisions where appropriate.`,
      
      cap_table: `Create detailed capitalization table for ${businessData.companyName || 'the company'} showing ownership structure. Include: PRE-MONEY CAP TABLE: Founders equity (typically 60-80%), Employee option pool (15-20%), Advisor shares (1-5%), Previous investors if any POST-MONEY CAP TABLE (after new investment): New investor ownership percentage, Founder dilution calculations, Employee option pool adjustments, Fully diluted share count MULTIPLE FUNDING ROUNDS: Seed round projections, Series A impact, Series B scenario modeling DILUTION ANALYSIS: Founder ownership through multiple rounds, Employee option pool management, Anti-dilution protection impact VALUATION SCENARIOS: Current valuation, Exit valuation projections (IPO/acquisition), Liquidation waterfall analysis Include formulas for ownership calculations and scenario modeling with different investment amounts and valuations.`,
      
      due_diligence: `Create comprehensive due diligence package for ${businessData.companyName || 'the company'} (${businessData.industry} industry). CORPORATE: Articles of incorporation, bylaws, board resolutions, capitalization table, option grants, IP assignments FINANCIAL: 3-year audited financials, management accounts, budgets/forecasts, cash flow statements, accounts receivable/payable aging LEGAL: Material contracts, employment agreements, IP portfolio, litigation history, regulatory compliance, insurance policies COMMERCIAL: Customer contracts, supplier agreements, pricing policies, sales pipeline, market research, competitive analysis TECHNOLOGY: IP portfolio, development roadmap, technical architecture, security policies, data privacy compliance HUMAN RESOURCES: Organization chart, employee contracts, compensation plans, HR policies, key person insurance TAX: Tax returns, transfer pricing, international structure, tax planning strategies INSURANCE: Coverage analysis, claims history, risk assessments Include data room organization with document checklist and confidentiality procedures.`,
      
      grant_proposal: `Draft government/private grant proposal for ${businessData.companyName || 'the organization'} in ${businessData.industry || 'specified sector'}. Include: 1) EXECUTIVE SUMMARY: Project overview, objectives, expected outcomes, funding request 2) STATEMENT OF NEED: Problem definition, market gap analysis, beneficiary identification, supporting data/statistics 3) PROJECT DESCRIPTION: Detailed methodology, timeline, deliverables, success metrics 4) GOALS & OBJECTIVES: SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound) 5) BUDGET & BUDGET NARRATIVE: Personnel costs, equipment, supplies, travel, indirect costs, cost-share requirements 6) EVALUATION PLAN: Outcome measurements, data collection methods, reporting schedule 7) ORGANIZATIONAL CAPACITY: Team qualifications, past performance, organizational structure, financial stability 8) SUSTAINABILITY: Long-term viability, revenue diversification, impact continuation 9) APPENDICES: Letters of support, organizational documents, team resumes, financial statements Tailor to specific grant requirements (SBIR, NSF, NIH, private foundations).`,
      
      // Operations & Management
      org_chart: `Design organizational structure for ${businessData.companyName || 'the company'} (${businessData.revenue} revenue stage). Include: 1) EXECUTIVE LEVEL: CEO, COO, CTO, CFO, VP Sales, VP Marketing with reporting relationships 2) DEPARTMENT STRUCTURE: Engineering (development teams, QA, DevOps), Sales (inside sales, field sales, sales ops), Marketing (product marketing, demand gen, content), Operations (supply chain, facilities, IT), Finance (accounting, FP&A, legal), HR (recruiting, people ops, compensation) 3) GROWTH PLANNING: Current headcount, hiring plan by quarter, budget per role, team scaling strategy 4) ROLES & RESPONSIBILITIES: Key accountabilities, decision-making authority, cross-functional collaboration 5) REPORTING STRUCTURE: Direct reports, matrix reporting, committee structures 6) COMPENSATION BANDS: Salary ranges by level, equity participation, bonus structures 7) SUCCESSION PLANNING: Key person risks, development paths, knowledge transfer Include org chart visualization and job leveling framework.`,
      
      job_descriptions: `Create comprehensive job descriptions for key positions at ${businessData.companyName || 'the company'}. For each role include: 1) JOB SUMMARY: Purpose, key objectives, success metrics 2) ESSENTIAL FUNCTIONS: Primary responsibilities (60-70% of time), secondary duties (30-40% of time) 3) QUALIFICATIONS: Required education, experience, certifications, technical skills, soft skills 4) COMPETENCIES: Leadership abilities, problem-solving, communication, teamwork, adaptability 5) PERFORMANCE STANDARDS: KPIs, evaluation criteria, goal-setting expectations 6) REPORTING RELATIONSHIPS: Direct supervisor, direct reports, key stakeholders 7) WORKING CONDITIONS: Remote/hybrid/onsite, travel requirements, physical demands 8) COMPENSATION: Salary range, variable pay, equity, benefits Include positions: Software Engineer, Sales Manager, Marketing Director, Operations Manager, Financial Analyst, Customer Success Manager, HR Business Partner. Use industry-standard language and legal compliance requirements.`,
      
      employee_handbook: `Create comprehensive employee handbook for ${businessData.companyName || 'the company'}. Include: 1) WELCOME & COMPANY CULTURE: Mission, vision, values, code of conduct, diversity & inclusion 2) EMPLOYMENT POLICIES: At-will employment, equal opportunity, anti-harassment, workplace safety 3) COMPENSATION & BENEFITS: Salary structure, bonus programs, equity plans, health insurance, retirement plans, PTO policy 4) WORK ARRANGEMENTS: Remote work policy, flexible schedules, office protocols, travel policies 5) TIME OFF: Vacation, sick leave, holidays, parental leave, bereavement, jury duty 6) PERFORMANCE MANAGEMENT: Review cycles, goal setting, career development, promotion criteria 7) WORKPLACE CONDUCT: Professional behavior, confidentiality, social media, conflict resolution 8) TECHNOLOGY & SECURITY: IT policies, data protection, BYOD guidelines, intellectual property 9) COMPLIANCE: Legal requirements, reporting procedures, grievance process Include acknowledgment forms and regular update procedures. Ensure compliance with federal, state, and local employment laws.`,
      
      vendor_analysis: `Conduct comprehensive vendor evaluation for ${businessData.companyName || 'the company'} in ${businessData.industry || 'specified industry'}. Include: 1) VENDOR CATEGORIES: Technology providers, professional services, manufacturing partners, logistics providers, office services 2) EVALUATION CRITERIA: Cost analysis (total cost of ownership), quality standards, reliability metrics, scalability capability, customer service, financial stability, geographic coverage 3) VENDOR ASSESSMENT MATRIX: Scoring system (1-10), weighted criteria, comparative analysis 4) DUE DILIGENCE: Financial health check, reference verification, compliance certification, insurance coverage, security standards 5) CONTRACT TERMS: Pricing models, SLAs, termination clauses, liability limits, intellectual property rights 6) RISK ASSESSMENT: Single source dependencies, geographic concentration, financial stability, regulatory compliance 7) VENDOR MANAGEMENT: Onboarding process, performance monitoring, relationship management, escalation procedures 8) COST OPTIMIZATION: Volume discounts, payment terms negotiation, competitive bidding Include vendor scorecard template and ongoing evaluation schedule.`,
      
      process_optimization: `Design process optimization strategy for ${businessData.companyName || 'the company'} operations. Include: 1) CURRENT STATE ANALYSIS: Process mapping, bottleneck identification, waste analysis, cycle time measurement 2) OPTIMIZATION OPPORTUNITIES: Automation candidates, elimination targets, consolidation possibilities, resource reallocation 3) TECHNOLOGY SOLUTIONS: Workflow automation tools, ERP integration, CRM optimization, reporting dashboards 4) LEAN METHODOLOGIES: Value stream mapping, 5S implementation, continuous improvement culture, kaizen events 5) PERFORMANCE METRICS: Efficiency gains, cost reduction targets, quality improvements, customer satisfaction 6) IMPLEMENTATION ROADMAP: Priority matrix, timeline, resource requirements, change management 7) COST-BENEFIT ANALYSIS: Investment requirements, expected savings, ROI calculations, payback period 8) RISK MANAGEMENT: Implementation risks, mitigation strategies, rollback procedures Include process flow diagrams and measurement framework.`,
      
      quality_systems: `Develop quality management system for ${businessData.companyName || 'the company'} in ${businessData.industry || 'specified industry'}. Include: 1) QUALITY POLICY: Mission statement, quality objectives, management commitment, customer focus 2) PROCESS DOCUMENTATION: Standard operating procedures, work instructions, quality manuals, process flow charts 3) QUALITY CONTROL: Inspection procedures, testing protocols, acceptance criteria, non-conformance handling 4) QUALITY ASSURANCE: Audit programs, management reviews, corrective action procedures, preventive measures 5) CONTINUOUS IMPROVEMENT: Performance monitoring, customer feedback systems, employee suggestion programs, benchmarking 6) TRAINING PROGRAMS: Quality awareness, technical skills, audit techniques, problem-solving methods 7) COMPLIANCE REQUIREMENTS: Industry standards (ISO 9001, Six Sigma), regulatory requirements, customer specifications 8) METRICS & KPIs: Defect rates, customer complaints, audit scores, process capability indices Include implementation timeline and certification roadmap.`,
      
      // Marketing & Sales
      marketing_plan: `Develop comprehensive marketing plan for ${businessData.companyName || 'the company'} targeting ${businessData.targetMarket || 'specified market'}. Include: 1) SITUATION ANALYSIS: SWOT analysis, competitive landscape, market trends, customer insights 2) TARGET MARKET: Buyer personas, market segmentation, addressable market size, customer journey mapping 3) POSITIONING STRATEGY: Value proposition, competitive differentiation, brand messaging, unique selling points 4) MARKETING OBJECTIVES: SMART goals, revenue targets, lead generation, brand awareness, market share 5) MARKETING MIX (4Ps): Product positioning, pricing strategy, distribution channels, promotional tactics 6) DIGITAL MARKETING: SEO/SEM, content marketing, social media, email campaigns, marketing automation 7) TRADITIONAL MARKETING: Events, PR, advertising, direct mail, partnerships 8) BUDGET ALLOCATION: Channel mix, cost per acquisition, ROI expectations, seasonal adjustments 9) IMPLEMENTATION TIMELINE: Campaign schedules, content calendar, resource allocation 10) MEASUREMENT & KPIs: Traffic, leads, conversions, CAC, LTV, brand metrics Include detailed campaign playbooks and attribution modeling.`,
      
      competitor_analysis: `Perform comprehensive competitive analysis for ${businessData.companyName || 'the company'} in ${businessData.industry || 'specified market'}. Include: 1) COMPETITIVE LANDSCAPE: Direct competitors (same target market/solution), indirect competitors (alternative solutions), emerging threats 2) COMPETITOR PROFILES: Company overview, revenue/size, market position, strengths/weaknesses, recent developments 3) PRODUCT COMPARISON: Feature analysis, pricing models, customer reviews, product roadmaps, technology stack 4) MARKETING ANALYSIS: Brand positioning, messaging strategy, marketing channels, content strategy, customer acquisition 5) SALES STRATEGY: Sales process, channel partnerships, pricing strategy, customer segments, geographic focus 6) FINANCIAL ANALYSIS: Revenue models, profitability, funding history, growth rates, market valuation 7) COMPETITIVE POSITIONING MAP: Price vs. features, market share vs. growth rate, customer satisfaction vs. innovation 8) OPPORTUNITIES & THREATS: Market gaps, competitive vulnerabilities, potential disruptions, partnership opportunities 9) STRATEGIC RECOMMENDATIONS: Differentiation strategies, competitive responses, market positioning Include competitive intelligence gathering methods and monitoring systems.`,
      
      pricing_strategy: `Develop comprehensive pricing strategy for ${businessData.companyName || 'the company'} (${businessData.revenue} stage). Include: 1) PRICING OBJECTIVES: Revenue maximization, market penetration, profit optimization, competitive positioning 2) COST ANALYSIS: Variable costs, fixed costs, contribution margin, break-even analysis, cost structure optimization 3) VALUE-BASED PRICING: Customer value quantification, willingness to pay analysis, price sensitivity research, value drivers 4) COMPETITIVE PRICING: Competitor price analysis, price positioning map, competitive response scenarios 5) PRICING MODELS: Subscription, usage-based, freemium, tiered pricing, bundle pricing, dynamic pricing 6) PRICE OPTIMIZATION: A/B testing framework, price elasticity analysis, demand forecasting, seasonal adjustments 7) CUSTOMER SEGMENTATION: Price discrimination opportunities, segment-specific pricing, geographic pricing variations 8) PSYCHOLOGICAL PRICING: Anchoring effects, price bundling, decoy pricing, charm pricing, reference pricing 9) IMPLEMENTATION PLAN: Rollout timeline, communication strategy, sales training, customer migration 10) MONITORING & ADJUSTMENT: KPI tracking, feedback collection, competitive response, pricing experiments Include pricing calculators and scenario modeling tools.`,
      
      sales_funnel: `Design comprehensive sales funnel for ${businessData.companyName || 'the company'} targeting ${businessData.targetMarket || 'specified customers'}. Include: 1) AWARENESS STAGE: Lead generation channels, content marketing, SEO, social media, advertising, PR, events 2) INTEREST STAGE: Lead magnets, email campaigns, retargeting, nurture sequences, educational content 3) CONSIDERATION STAGE: Product demos, case studies, comparison guides, trial offers, consultative selling 4) INTENT STAGE: Proposal generation, pricing discussions, objection handling, competitive differentiation 5) EVALUATION STAGE: References, proof of concepts, pilot programs, contract negotiations, decision criteria 6) PURCHASE STAGE: Closing techniques, contract execution, onboarding process, implementation planning 7) RETENTION STAGE: Customer success, upselling, cross-selling, renewal management, advocacy programs 8) CONVERSION OPTIMIZATION: A/B testing, landing page optimization, email sequences, sales scripts 9) SALES METRICS: Conversion rates by stage, sales velocity, average deal size, win rates, customer lifetime value 10) SALES TOOLS: CRM configuration, automation workflows, reporting dashboards, sales enablement Include funnel visualization and performance benchmarks.`,
      
      brand_strategy: `Create comprehensive brand strategy for ${businessData.companyName || 'the company'} in ${businessData.industry || 'specified market'}. Include: 1) BRAND PURPOSE: Mission statement, brand vision, core values, brand promise, emotional connection 2) BRAND POSITIONING: Market position, competitive differentiation, unique value proposition, brand pillars 3) TARGET AUDIENCE: Primary personas, demographic profile, psychographic insights, brand relationship, touchpoint mapping 4) BRAND PERSONALITY: Brand archetype, personality traits, tone of voice, communication style, brand behavior 5) BRAND IDENTITY: Logo design brief, color palette, typography, imagery style, design system guidelines 6) BRAND MESSAGING: Core messages, value propositions, elevator pitch, taglines, proof points 7) BRAND EXPERIENCE: Customer journey, touchpoint design, service standards, brand moments 8) BRAND ARCHITECTURE: Product/service hierarchy, sub-brands, co-branding guidelines, brand extensions 9) BRAND GUIDELINES: Usage standards, dos and don'ts, application examples, quality control 10) BRAND ACTIVATION: Launch strategy, internal alignment, external communication, measurement plan Include brand audit and competitive positioning analysis.`,
      
      digital_marketing: `Develop comprehensive digital marketing strategy for ${businessData.companyName || 'the company'}. Include: 1) DIGITAL AUDIT: Website analysis, SEO assessment, social media presence, content inventory, competitor benchmarking 2) SEO STRATEGY: Keyword research, on-page optimization, technical SEO, link building, local SEO, content strategy 3) SEM/PPC: Google Ads strategy, keyword bidding, ad copy testing, landing page optimization, budget allocation, conversion tracking 4) SOCIAL MEDIA: Platform selection, content strategy, community management, influencer partnerships, social commerce 5) CONTENT MARKETING: Editorial calendar, blog strategy, video content, infographics, webinars, lead magnets 6) EMAIL MARKETING: List building, segmentation, automation sequences, personalization, A/B testing 7) MARKETING AUTOMATION: Lead scoring, nurture campaigns, behavioral triggers, CRM integration 8) ANALYTICS & MEASUREMENT: Google Analytics setup, conversion tracking, attribution modeling, ROI analysis 9) BUDGET ALLOCATION: Channel mix optimization, cost per acquisition targets, performance-based budgeting 10) IMPLEMENTATION ROADMAP: Timeline, resource requirements, technology stack, team structure Include digital marketing toolkit and performance dashboards.`,
      
      // Financial Management
      cash_flow: `Create comprehensive cash flow analysis for ${businessData.companyName || 'the company'} (${businessData.revenue} revenue stage). Include: 1) OPERATING CASH FLOW: Revenue collection timing, accounts receivable aging, payment terms optimization, expense timing, accounts payable management 2) INVESTING CASH FLOW: Capital expenditure planning, asset purchases, R&D investments, acquisition activities 3) FINANCING CASH FLOW: Debt service, equity raises, dividend payments, loan proceeds 4) CASH FLOW PROJECTIONS: Monthly projections (12 months), quarterly projections (3 years), scenario planning (best/base/worst case) 5) WORKING CAPITAL ANALYSIS: Current assets, current liabilities, working capital requirements, seasonal variations 6) CASH CONVERSION CYCLE: Days sales outstanding (DSO), days inventory outstanding (DIO), days payable outstanding (DPO) 7) CASH MANAGEMENT: Minimum cash requirements, cash pooling, sweep accounts, investment policies 8) FINANCING NEEDS: Credit line requirements, term loan needs, equity funding gaps 9) CASH FLOW OPTIMIZATION: Collection improvements, payment term negotiations, inventory management Include monthly cash flow dashboard and covenant compliance tracking.`,
      
      budget_planning: `Develop comprehensive annual budget for ${businessData.companyName || 'the company'}. Include: 1) REVENUE BUDGET: Sales forecasts by product/service, customer segments, geographic regions, pricing assumptions, seasonal adjustments 2) COST OF GOODS SOLD: Direct materials, direct labor, manufacturing overhead, gross margin analysis 3) OPERATING EXPENSES: Personnel costs (salaries, benefits, bonuses), marketing spend, technology costs, facilities, professional services 4) CAPITAL BUDGET: Equipment purchases, technology investments, facility improvements, R&D projects 5) DEPARTMENT BUDGETS: Sales, marketing, operations, R&D, admin, detailed line item budgets with justifications 6) VARIANCE ANALYSIS: Monthly budget vs actual reporting, variance explanations, corrective actions 7) BUDGET CONTROLS: Approval processes, spending limits, purchase order systems, budget transfer procedures 8) ROLLING FORECASTS: Quarterly reforecasting, scenario planning, business drivers analysis 9) KPI DASHBOARD: Financial metrics, operational metrics, leading indicators, budget performance Include budget templates and variance reporting tools.`,
      
      cost_analysis: `Perform comprehensive cost analysis for ${businessData.companyName || 'the company'} operations. Include: 1) COST STRUCTURE: Fixed costs, variable costs, semi-variable costs, cost behavior analysis 2) ACTIVITY-BASED COSTING: Cost drivers identification, activity pools, overhead allocation, product/service profitability 3) COST CATEGORIES: Direct costs, indirect costs, overhead allocation, cost center analysis 4) COST REDUCTION OPPORTUNITIES: Process optimization, vendor negotiations, automation benefits, outsourcing analysis 5) BREAK-EVEN ANALYSIS: Fixed cost coverage, contribution margin, break-even units/revenue, margin of safety 6) PROFITABILITY ANALYSIS: Product/service margins, customer profitability, channel profitability, geographic analysis 7) COST BENCHMARKING: Industry comparisons, best practices, efficiency metrics, competitive positioning 8) COST CONTROL SYSTEMS: Budget monitoring, variance analysis, approval workflows, cost accountability 9) PRICING IMPLICATIONS: Cost-plus pricing, value-based pricing, competitive pricing, margin optimization Include cost reduction roadmap and monitoring dashboard.`,
      
      break_even: `Calculate comprehensive break-even analysis for ${businessData.companyName || 'the company'}. Include: 1) BREAK-EVEN CALCULATIONS: Fixed costs identification, variable cost per unit, contribution margin calculation, break-even point in units and revenue 2) PRODUCT/SERVICE ANALYSIS: Individual break-even by offering, weighted average contribution margin, product mix impact 3) SCENARIO ANALYSIS: Volume changes impact, price sensitivity, cost structure modifications, break-even shifts 4) GRAPHICAL ANALYSIS: Break-even charts, cost-volume-profit graphs, margin of safety visualization 5) OPERATIONAL LEVERAGE: Fixed cost impact, operating leverage ratio, profit sensitivity to volume changes 6) MULTI-PRODUCT ANALYSIS: Sales mix effects, cross-subsidization, resource allocation optimization 7) TIME-BASED ANALYSIS: Monthly break-even progression, seasonal variations, growth impact on break-even 8) STRATEGIC IMPLICATIONS: Pricing decisions, cost structure optimization, capacity planning, investment decisions Include break-even calculators and sensitivity analysis tools.`,
      
      roi_calculator: `Create comprehensive ROI analysis framework for ${businessData.companyName || 'the company'} investment decisions. Include: 1) ROI METRICS: Return on Investment, Return on Assets, Return on Equity, Internal Rate of Return, Net Present Value 2) INVESTMENT CATEGORIES: Technology investments, marketing campaigns, capital projects, human resources, R&D initiatives 3) COST-BENEFIT ANALYSIS: Initial investment, ongoing costs, quantifiable benefits, intangible benefits, risk adjustments 4) PAYBACK PERIOD: Simple payback, discounted payback, cumulative cash flows, investment recovery timeline 5) RISK ASSESSMENT: Probability analysis, scenario modeling, sensitivity analysis, Monte Carlo simulation 6) PORTFOLIO ANALYSIS: Multiple projects comparison, resource allocation optimization, priority ranking 7) POST-INVESTMENT TRACKING: Actual vs projected returns, variance analysis, lessons learned, process improvements 8) DECISION FRAMEWORK: Investment criteria, approval thresholds, governance process, performance metrics Include ROI calculators for different investment types and decision-making templates.`,
      
      tax_planning: `Develop comprehensive business tax strategy for ${businessData.companyName || 'the company'} (${businessData.industry} industry). Include: 1) TAX STRUCTURE OPTIMIZATION: Entity selection (LLC, S-Corp, C-Corp), state tax considerations, international structures 2) INCOME TAX PLANNING: Revenue timing, expense acceleration, depreciation strategies, R&D credits, bonus depreciation 3) DEDUCTION MAXIMIZATION: Business expenses, equipment purchases, travel costs, professional services, home office deductions 4) TAX CREDITS: R&D credits, hiring incentives, renewable energy credits, state-specific credits, international credits 5) QUARTERLY PLANNING: Estimated tax payments, safe harbor provisions, cash flow impact, penalty avoidance 6) YEAR-END STRATEGIES: Income deferral, expense acceleration, equipment purchases, retirement contributions 7) COMPLIANCE REQUIREMENTS: Filing deadlines, record keeping, audit preparation, documentation standards 8) MULTI-STATE CONSIDERATIONS: Nexus requirements, apportionment formulas, state-specific incentives 9) INTERNATIONAL TAX: Transfer pricing, GILTI provisions, BEAT tax, treaty benefits Include tax calendar and compliance checklist.`,
      
      // Legal & Compliance
      business_structure: `Analyze optimal business structure for ${businessData.companyName || 'the company'} (${businessData.revenue} revenue, ${businessData.funding} funding stage). Include: 1) ENTITY COMPARISON: Sole Proprietorship, Partnership, LLC, S-Corporation, C-Corporation comparison matrix 2) TAX IMPLICATIONS: Pass-through vs corporate taxation, double taxation, self-employment taxes, state tax considerations 3) LIABILITY PROTECTION: Personal asset protection, professional liability, corporate veil, indemnification 4) OPERATIONAL FLEXIBILITY: Management structure, profit distribution, ownership restrictions, transferability 5) FUNDING CONSIDERATIONS: Investor preferences, equity structures, convertible instruments, IPO readiness 6) COMPLIANCE REQUIREMENTS: Filing obligations, corporate formalities, record keeping, annual requirements 7) CONVERSION STRATEGIES: Entity conversion timeline, tax implications, documentation requirements 8) MULTI-STATE OPERATIONS: State registration requirements, nexus considerations, compliance obligations 9) INTERNATIONAL EXPANSION: Foreign subsidiaries, tax treaties, transfer pricing, regulatory compliance 10) RESTRUCTURING SCENARIOS: Growth stage transitions, acquisition preparations, tax optimization Include decision matrix and implementation timeline.`,
      
      contract_templates: `Create comprehensive contract template library for ${businessData.companyName || 'the company'} in ${businessData.industry || 'specified industry'}. Include: 1) CUSTOMER AGREEMENTS: Service agreements, software licenses, SaaS terms, maintenance contracts, professional services 2) VENDOR CONTRACTS: Purchase orders, supply agreements, consulting contracts, non-disclosure agreements, master service agreements 3) EMPLOYMENT DOCUMENTS: Offer letters, employment contracts, non-compete agreements, severance agreements, contractor agreements 4) PARTNERSHIP AGREEMENTS: Strategic partnerships, joint ventures, distribution agreements, reseller agreements, referral agreements 5) INTELLECTUAL PROPERTY: Licensing agreements, assignment agreements, work-for-hire contracts, confidentiality agreements 6) REAL ESTATE: Office leases, sublease agreements, property management contracts, purchase agreements 7) FINANCING DOCUMENTS: Loan agreements, security agreements, guarantees, investment agreements, promissory notes 8) STANDARD TERMS: Payment terms, liability limitations, indemnification clauses, dispute resolution, governing law 9) COMPLIANCE CLAUSES: Data privacy, industry regulations, international requirements, audit rights Include contract management system and approval workflows.`,
      
      compliance_checklist: `Create comprehensive regulatory compliance program for ${businessData.companyName || 'the company'} in ${businessData.industry || 'specified industry'}. Include: 1) INDUSTRY-SPECIFIC REGULATIONS: FDA, FTC, SEC, OSHA, EPA, industry-specific requirements, professional licensing 2) DATA PRIVACY: GDPR compliance, CCPA requirements, HIPAA obligations, data breach procedures, consent management 3) EMPLOYMENT LAW: Equal opportunity, wage and hour, safety regulations, family leave, worker classification 4) FINANCIAL REGULATIONS: SOX compliance, anti-money laundering, consumer protection, securities regulations 5) INTERNATIONAL COMPLIANCE: Export controls, foreign registration, tax obligations, regulatory approvals 6) COMPLIANCE MONITORING: Audit schedules, policy updates, training programs, violation reporting 7) DOCUMENTATION REQUIREMENTS: Policy manuals, training records, audit trails, regulatory filings 8) RISK ASSESSMENT: Compliance risks, penalty exposure, mitigation strategies, insurance coverage 9) INCIDENT RESPONSE: Violation procedures, regulatory reporting, corrective actions, prevention measures Include compliance calendar and monitoring dashboard.`,
      
      ip_protection: `Develop comprehensive intellectual property strategy for ${businessData.companyName || 'the company'} in ${businessData.industry || 'specified technology sector'}. Include: 1) IP AUDIT: Patent portfolio analysis, trademark inventory, copyright assets, trade secret identification, competitive landscape 2) PATENT STRATEGY: Invention disclosure process, patentability analysis, filing strategy, prosecution timeline, portfolio management 3) TRADEMARK PROTECTION: Brand name protection, logo registration, domain name strategy, international filing, enforcement procedures 4) COPYRIGHT MANAGEMENT: Original works identification, registration process, work-for-hire agreements, licensing opportunities 5) TRADE SECRETS: Confidential information identification, protection protocols, employee training, non-disclosure agreements 6) IP LICENSING: Licensing opportunities, valuation methods, license agreements, royalty structures, technology transfer 7) ENFORCEMENT STRATEGY: Infringement monitoring, cease and desist procedures, litigation strategy, settlement negotiations 8) INTERNATIONAL PROTECTION: PCT filing strategy, Madrid Protocol, Paris Convention, country-specific requirements 9) IP MONETIZATION: Licensing revenue, patent sales, joint ventures, cross-licensing agreements Include IP portfolio dashboard and competitive intelligence system.`,
      
      licensing: `Analyze licensing requirements for ${businessData.companyName || 'the company'} in ${businessData.industry || 'specified industry'}. Include: 1) BUSINESS LICENSES: General business license, sales tax permit, employer identification number, state registrations 2) PROFESSIONAL LICENSES: Industry-specific licenses, professional certifications, regulatory approvals, continuing education requirements 3) PERMITS: Building permits, zoning approvals, environmental permits, import/export licenses, special use permits 4) REGULATORY APPROVALS: FDA approvals, FCC licenses, financial services licenses, healthcare certifications 5) COMPLIANCE MONITORING: Renewal schedules, application processes, fee structures, compliance requirements 6) MULTI-JURISDICTION: State-by-state requirements, federal licenses, international permits, reciprocity agreements 7) APPLICATION PROCESS: Documentation requirements, timeline expectations, approval criteria, appeal procedures 8) ONGOING OBLIGATIONS: Reporting requirements, inspection protocols, compliance audits, violation consequences 9) COST ANALYSIS: License fees, compliance costs, opportunity costs, penalty exposure Include licensing calendar and compliance tracking system.`,
      
      insurance_needs: `Perform comprehensive business insurance analysis for ${businessData.companyName || 'the company'} (${businessData.revenue} revenue, ${businessData.industry} industry). Include: 1) COVERAGE ASSESSMENT: General liability, professional liability, product liability, cyber liability, employment practices liability 2) PROPERTY INSURANCE: Building coverage, equipment protection, business personal property, business interruption, extra expense 3) COMMERCIAL AUTO: Fleet coverage, hired/non-owned auto, commercial use of personal vehicles 4) WORKERS' COMPENSATION: Coverage requirements, classification codes, experience modification, safety programs 5) KEY PERSON INSURANCE: Life insurance, disability coverage, buy-sell agreements, succession planning 6) DIRECTORS & OFFICERS: D&O liability, management liability, fiduciary liability, crime coverage 7) CYBER INSURANCE: Data breach coverage, cyber extortion, business interruption, regulatory fines 8) RISK ASSESSMENT: Industry risks, operational risks, financial risks, regulatory risks 9) COST-BENEFIT ANALYSIS: Premium costs, deductible selection, coverage limits, risk retention 10) CLAIMS MANAGEMENT: Claims procedures, vendor relationships, loss prevention, insurance carrier relationships Include insurance coverage matrix and risk management program."
    }

    const specificPrompt = prompts[toolId]
    if (!specificPrompt) {
      setAnalysisResult('Error: Business tool not supported. Please contact support.')
      setIsAnalyzing(false)
      return
    }

    const prompt = `You are a senior business consultant with 20+ years of experience across industries. ${specificPrompt}

Company Context:
- Name: ${businessData.companyName || 'Not specified'}
- Industry: ${businessData.industry || 'Not specified'}
- Target Market: ${businessData.targetMarket || 'Not specified'}
- Revenue Stage: ${businessData.revenue || 'Not specified'}
- Funding Status: ${businessData.funding || 'Not specified'}

CRITICAL REQUIREMENTS:
1. Provide specific, actionable recommendations with implementation steps
2. Include real-world industry benchmarks and best practices
3. Use actual financial calculations and metrics with formulas
4. Format professionally with numbered sections and bullet points
5. Add realistic timelines and resource requirements
6. Include risk assessment with specific mitigation strategies
7. Provide competitive analysis with market positioning
8. Include ROI calculations and financial projections where applicable
9. Use data-driven insights and avoid generic advice
10. Make the document ready for immediate business implementation

IMPORTANT: Create a comprehensive, investor-grade document that meets professional consulting standards. Include specific numbers, calculations, and actionable next steps.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat/completions`, {
        model: serverInfo.default_model || 'gpt-3.5-turbo',
        messages: [{
          role: 'system',
          content: 'You are a top-tier business consultant from McKinsey & Company with expertise in strategy, finance, operations, and market analysis. Create professional, data-driven business documents with specific calculations and actionable recommendations.'
        }, {
          role: 'user',
          content: prompt
        }],
        max_tokens: 3500,
        temperature: 0.2
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.data?.choices?.[0]?.message?.content) {
        throw new Error('Invalid API response format')
      }

      const analysisContent = response.data.choices[0].message.content
      setAnalysisResult(analysisContent)
      
      // Generate professional business document window
      setTimeout(() => {
        const toolName = sections[activeSection].tools.find(t => t.id === toolId)?.name || 'Business Analysis'
        const newWindow = window.open('', '_blank')
        if (newWindow) {
          newWindow.document.write(`
            <!DOCTYPE html>
            <html>
              <head>
                <title>${toolName} - ${businessData.companyName || 'Business Analysis'}</title>
                <meta charset="UTF-8">
                <style>
                  body { 
                    font-family: 'Calibri', 'Arial', sans-serif; 
                    font-size: 11pt;
                    line-height: 1.5; 
                    margin: 0.75in; 
                    color: #000;
                  }
                  .document-header {
                    text-align: center;
                    margin-bottom: 40px;
                    border-bottom: 3px solid #e67e22;
                    padding-bottom: 25px;
                  }
                  .document-title {
                    font-size: 20pt;
                    font-weight: bold;
                    color: #e67e22;
                    margin-bottom: 10px;
                  }
                  .company-info {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 25px 0;
                    border-left: 4px solid #e67e22;
                  }
                  .company-info strong {
                    color: #2c3e50;
                  }
                  .section-header {
                    font-size: 14pt;
                    font-weight: bold;
                    color: #2c3e50;
                    border-bottom: 1px solid #bdc3c7;
                    padding-bottom: 5px;
                    margin-top: 30px;
                    margin-bottom: 15px;
                  }
                  .controls {
                    position: fixed;
                    top: 15px;
                    right: 15px;
                    background: white;
                    padding: 15px;
                    border: 2px solid #e67e22;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                  }
                  .controls button {
                    margin: 5px;
                    padding: 10px 16px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 11px;
                    font-weight: bold;
                  }
                  .print-btn { background: #3498db; color: white; }
                  .save-btn { background: #27ae60; color: white; }
                  .edit-btn { background: #f39c12; color: white; }
                  .export-btn { background: #9b59b6; color: white; }
                  table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                    font-size: 10pt;
                  }
                  th, td {
                    border: 1px solid #bdc3c7;
                    padding: 8px 12px;
                    text-align: left;
                  }
                  th {
                    background-color: #ecf0f1;
                    font-weight: bold;
                    color: #2c3e50;
                  }
                  .highlight {
                    background-color: #fff3cd;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 15px 0;
                    border-left: 4px solid #ffc107;
                  }
                  @media print { 
                    .controls { display: none; }
                    body { margin: 0.5in; font-size: 10pt; }
                    .document-header { margin-bottom: 30px; }
                  }
                </style>
              </head>
              <body>
                <div class="controls">
                  <button class="print-btn" onclick="window.print()">🖨️ Print</button>
                  <button class="save-btn" onclick="downloadDocument()">💾 Save PDF</button>
                  <button class="edit-btn" onclick="editDocument()">✏️ Edit</button>
                  <button class="export-btn" onclick="exportToExcel()">📊 Excel</button>
                </div>
                <div class="document-header">
                  <div class="document-title">${toolName}</div>
                  <div style="color: #7f8c8d; font-size: 12pt;">Professional Business Analysis Report</div>
                </div>
                <div class="company-info">
                  <strong>Company:</strong> ${businessData.companyName || 'Not specified'} &nbsp;&nbsp;
                  <strong>Industry:</strong> ${businessData.industry || 'Not specified'}<br>
                  <strong>Target Market:</strong> ${businessData.targetMarket || 'Not specified'} &nbsp;&nbsp;
                  <strong>Revenue Stage:</strong> ${businessData.revenue || 'Not specified'}<br>
                  <strong>Funding Status:</strong> ${businessData.funding || 'Not specified'} &nbsp;&nbsp;
                  <strong>Report Date:</strong> ${new Date().toLocaleDateString()}<br>
                  <strong>Generated By:</strong> AeonForge Business Intelligence Platform
                </div>
                <div id="document-content" style="white-space: pre-wrap;">${analysisContent}</div>
                
                <script>
                  function downloadDocument() {
                    const content = document.documentElement.outerHTML;
                    const blob = new Blob([content], { type: 'text/html' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '${toolName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${businessData.companyName ? businessData.companyName.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '_' : ''}' + new Date().toISOString().split('T')[0] + '.html';
                    a.click();
                    URL.revokeObjectURL(url);
                  }
                  
                  function editDocument() {
                    const content = document.getElementById('document-content');
                    if (content.contentEditable === 'true') {
                      content.contentEditable = 'false';
                      content.style.border = 'none';
                      content.style.background = 'transparent';
                      document.querySelector('.edit-btn').innerHTML = '✏️ Edit';
                    } else {
                      content.contentEditable = 'true';
                      content.style.border = '2px dashed #3498db';
                      content.style.background = '#f8f9fa';
                      content.style.padding = '15px';
                      content.focus();
                      document.querySelector('.edit-btn').innerHTML = '✅ Save';
                    }
                  }
                  
                  function exportToExcel() {
                    const content = document.getElementById('document-content').innerText;
                    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '${toolName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_data_' + new Date().toISOString().split('T')[0] + '.csv';
                    a.click();
                    URL.revokeObjectURL(url);
                  }
                </script>
              </body>
            </html>
          `)
          newWindow.document.close()
        }
      }, 100)

    } catch (error) {
      console.error('Error generating business document:', error)
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error occurred'
      setAnalysisResult(`❌ Error generating analysis: ${errorMessage}\n\nPlease check your inputs and try again. If the problem persists, contact support with error code: ${Date.now()}`)
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