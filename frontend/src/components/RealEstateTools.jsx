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
    if (isAnalyzing) return
    setIsAnalyzing(true)
    setAnalysisResult('')

    const prompts = {
      // Property Analysis
      property_valuation: `Perform comprehensive property valuation analysis for ${propertyData.address || 'the subject property'} (${propertyData.propertyType || 'property type'}, ${propertyData.sqft || 'X'} sqft, ${propertyData.bedrooms || 'X'}/${propertyData.bathrooms || 'X'}, built ${propertyData.yearBuilt || 'X'}). Include: 1) COMPARATIVE MARKET ANALYSIS: 3-5 recent comparable sales within 0.5 miles, adjustment calculations for size, condition, location, date of sale 2) PRICE PER SQUARE FOOT: Subject property vs comparables, neighborhood averages, price/sqft trends 3) MARKET VALUE RANGE: Conservative estimate, most likely value, optimistic estimate with confidence levels 4) APPRECIATION ANALYSIS: Historical appreciation rates (1, 3, 5-year), market cycle position, future projections 5) CONDITION ADJUSTMENTS: Estimated repair/upgrade costs, impact on value, modernization needs 6) MARKET FACTORS: Supply/demand dynamics, days on market, price reductions, seasonal trends Include specific dollar amounts, percentage adjustments, and final valuation range with methodology explanation.`,
      
      investment_analysis: `Create detailed investment analysis for ${propertyData.address || 'the subject property'} at $${propertyData.price || 'X'} purchase price. Include: 1) PURCHASE ANALYSIS: Purchase price, down payment options (10%, 20%, 25%), closing costs estimate, total cash required 2) FINANCING SCENARIOS: Different loan amounts, interest rates, payment calculations, cash flow impact 3) CASH-ON-CASH RETURN: Annual cash flow divided by cash invested, monthly and annual calculations 4) TOTAL ROI CALCULATION: Appreciation + cash flow + tax benefits + principal paydown over holding period 5) INTERNAL RATE OF RETURN (IRR): Time-weighted return calculation, comparison to benchmarks 6) NET PRESENT VALUE (NPV): Discounted future cash flows, investment viability assessment 7) PAYBACK PERIOD: Time to recover initial investment, break-even analysis 8) 10-YEAR PROJECTIONS: Annual cash flow, appreciation, equity build-up, total return scenarios 9) SENSITIVITY ANALYSIS: Impact of rent changes, vacancy rates, expense increases, interest rate changes Include specific calculations, formulas used, and investment grade recommendations.`,
      
      rental_analysis: `Analyze rental income potential for ${propertyData.address || 'the subject property'} in ${propertyData.marketArea || 'the local market'}. Include: 1) MARKET RENT ANALYSIS: 5-8 comparable rentals, rent per square foot, rent adjustments for features/condition 2) RENTAL YIELD CALCULATIONS: Gross rental yield (annual rent/purchase price), net rental yield after expenses 3) GROSS RENT MULTIPLIER (GRM): Purchase price divided by gross annual rent, market comparison 4) VACANCY ANALYSIS: Local vacancy rates, seasonal patterns, vacancy allowance (typically 5-8%) 5) OPERATING EXPENSES: Property taxes, insurance, maintenance, management fees, utilities, reserves 6) NET OPERATING INCOME: Gross rent minus operating expenses, NOI calculation 7) CASH FLOW PROJECTIONS: Monthly net cash flow, annual cash flow, positive/negative cash flow scenarios 8) RENT ESCALATION: Market rent growth rates, lease escalation clauses, long-term projections 9) PROPERTY MANAGEMENT: Self-management vs professional management, cost-benefit analysis Include specific rental comps, operating expense percentages, and cash flow calculations.`,
      
      flip_analysis: `Create fix & flip analysis for ${propertyData.address || 'the subject property'} purchased at $${propertyData.price || 'X'}. Include: 1) ACQUISITION COSTS: Purchase price, closing costs, inspection fees, due diligence expenses 2) REHAB ESTIMATES: Kitchen renovation ($15-50k), bathroom upgrades ($8-25k), flooring ($3-8/sqft), paint/cosmetics ($3-6/sqft), HVAC/electrical/plumbing as needed, exterior improvements 3) AFTER REPAIR VALUE (ARV): Comparable sales of renovated properties, price per square foot after renovation, market value range 4) HOLDING COSTS: Carrying costs during renovation, utilities, insurance, interest on loans, property taxes 5) SELLING COSTS: Real estate commissions (6%), closing costs, staging, marketing expenses 6) TIMELINE ANALYSIS: Purchase to renovation start, renovation duration, marketing time, total holding period 7) PROFIT CALCULATIONS: ARV minus all costs and expenses, profit margin percentage, return on investment 8) RISK ASSESSMENT: Construction overruns, market value changes, extended holding time, financing risks 9) 70% RULE APPLICATION: Maximum purchase price (70% of ARV minus rehab costs), deal evaluation Include detailed cost breakdowns and profit projections with conservative/optimistic scenarios.`,
      
      cash_flow: `Generate comprehensive cash flow analysis for ${propertyData.address || 'the subject property'} with $${propertyData.rentAmount || 'X'}/month rent. Include: 1) GROSS RENTAL INCOME: Monthly rent, annual rent, other income (parking, laundry, storage) 2) VACANCY ALLOWANCE: Market vacancy rate (typically 5-8%), monthly vacancy deduction 3) EFFECTIVE GROSS INCOME: Gross rent minus vacancy allowance 4) OPERATING EXPENSES: Property taxes (1-3% of value), insurance ($500-2000/year), maintenance (5-10% of rent), management fees (6-12% of rent), utilities, landscaping, pest control, reserves for repairs 5) NET OPERATING INCOME (NOI): Effective gross income minus operating expenses 6) DEBT SERVICE: Principal and interest payments, monthly and annual amounts 7) CASH FLOW BEFORE TAX (CFBT): NOI minus debt service 8) TAX BENEFITS: Depreciation deduction (3.636% annually for residential), interest deduction, expense deductions, tax savings 9) CASH FLOW AFTER TAX (CFAT): CFBT plus tax savings 10) BREAK-EVEN ANALYSIS: Minimum rent required to break even, occupancy rate needed Include monthly and annual calculations with sensitivity analysis for key variables.`,
      
      market_analysis: `Perform comprehensive market analysis for ${propertyData.marketArea || 'the local market area'}. Include: 1) MARKET OVERVIEW: Population demographics, median household income, employment statistics, major employers 2) HOUSING MARKET TRENDS: Median home prices, price appreciation rates (1, 3, 5-year), inventory levels, days on market 3) RENTAL MARKET: Average rents by property type, rental vacancy rates, rent growth trends, rental yield analysis 4) SUPPLY & DEMAND: New construction permits, housing starts, population growth, household formation rates 5) ECONOMIC INDICATORS: Job growth, unemployment rates, GDP growth, business development, infrastructure projects 6) MARKET CYCLE ANALYSIS: Current market phase (recovery, expansion, peak, contraction), cycle timing 7) COMPARABLE MARKETS: Regional comparisons, national benchmarks, market ranking 8) FUTURE OUTLOOK: Market forecasts, development pipeline, economic projections, investment attractiveness 9) RISK FACTORS: Market volatility, economic risks, regulatory changes, natural disaster exposure Include specific data points, sources, and investment timing recommendations.`,
      
      
      // Financing & Mortgages
      mortgage_calculator: `Calculate comprehensive mortgage scenarios for $${propertyData.price || 'X'} property. Include: 1) LOAN AMOUNT CALCULATIONS: Purchase price minus down payment for 5%, 10%, 15%, 20%, 25% down scenarios 2) MONTHLY PAYMENTS: Principal & interest for different loan terms (15, 20, 25, 30-year), current interest rates 3) AMORTIZATION SCHEDULE: Monthly payment breakdown (principal vs interest), loan balance reduction over time, equity build-up 4) TOTAL INTEREST PAID: Lifetime interest costs for different loan terms, interest savings with shorter terms 5) PAYMENT COMPARISONS: Monthly payment differences between loan terms, total cost comparison 6) PMI CALCULATIONS: Private mortgage insurance costs, PMI removal timeline, impact on payments 7) PREPAYMENT SCENARIOS: Extra payment impact, payoff acceleration, interest savings from prepayments 8) REFINANCING ANALYSIS: Break-even calculations for refinancing, closing cost recovery, rate reduction benefits 9) LOAN-TO-VALUE RATIOS: Initial LTV, LTV reduction over time, refinancing opportunities Include payment schedules and total cost analysis for optimal financing strategy.`,
      
      refinance_analysis: `Analyze refinancing opportunity for existing mortgage on ${propertyData.address || 'the subject property'}. Include: 1) CURRENT LOAN STATUS: Current balance, interest rate, monthly payment, remaining term 2) NEW LOAN SCENARIOS: Current market rates, new loan amount, new monthly payment, new loan terms 3) MONTHLY SAVINGS: Payment reduction, annual savings, percentage improvement 4) CLOSING COSTS: Loan origination fees, appraisal, title insurance, attorney fees, recording fees, total costs 5) BREAK-EVEN ANALYSIS: Months to recover closing costs, break-even timeline calculation 6) CASH-OUT OPTIONS: Available equity, cash-out amount, new loan-to-value ratio, cash-out benefits 7) NET BENEFIT ANALYSIS: Total savings over remaining loan term minus closing costs, net present value 8) RATE-AND-TERM vs CASH-OUT: Comparison of refinancing options, optimal strategy selection 9) TIMING CONSIDERATIONS: Rate trends, market conditions, personal financial situation Include specific calculations and recommendations for refinancing decision.`,
      
      loan_comparison: `Compare mortgage loan options for ${propertyData.address || 'the subject property'}. Include: 1) CONVENTIONAL LOANS: 30-year fixed, 15-year fixed, adjustable rate mortgages (ARM), jumbo loans 2) GOVERNMENT LOANS: FHA loans (3.5% down), VA loans (0% down for veterans), USDA rural loans, state/local programs 3) INTEREST RATES: Current rates for each loan type, rate differences, APR comparisons 4) DOWN PAYMENT REQUIREMENTS: Minimum down payments, impact on loan terms, PMI requirements 5) LOAN LIMITS: Conforming loan limits, jumbo loan thresholds, program-specific limits 6) QUALIFICATION CRITERIA: Credit score requirements, debt-to-income ratios, employment verification, asset requirements 7) MONTHLY PAYMENTS: Payment calculations for each loan type, total monthly housing costs 8) TOTAL LOAN COSTS: Lifetime costs, interest paid, fees and closing costs comparison 9) PROS & CONS ANALYSIS: Benefits and drawbacks of each loan type, optimal selection criteria Include detailed comparison matrix and loan program recommendations.`,
      
      qualification: `Analyze mortgage qualification for ${propertyData.address || 'the subject property'} purchase. Include: 1) INCOME REQUIREMENTS: Gross monthly income needed, employment verification, income stability requirements 2) DEBT-TO-INCOME RATIOS: Front-end ratio (housing costs/income, max 28%), back-end ratio (total debt/income, max 36-43%) 3) CREDIT SCORE IMPACT: Minimum credit scores by loan type, interest rate pricing adjustments, credit improvement strategies 4) DOWN PAYMENT SOURCES: Acceptable sources, gift funds, down payment assistance programs, asset verification 5) EMPLOYMENT HISTORY: Work history requirements, job stability, self-employment documentation, income verification 6) ASSET REQUIREMENTS: Cash reserves, liquid assets, retirement accounts, verification documentation 7) PROPERTY REQUIREMENTS: Appraisal process, property condition, occupancy requirements, insurance needs 8) LOAN APPROVAL PROCESS: Pre-qualification vs pre-approval, documentation requirements, approval timeline 9) QUALIFICATION IMPROVEMENT: Strategies to improve approval odds, credit repair, debt paydown, income enhancement Include qualification checklist and improvement action plan.`,
      
      closing_costs: `Estimate closing costs for ${propertyData.address || 'the subject property'} at $${propertyData.price || 'X'} purchase price. Include: 1) LENDER FEES: Loan origination (0.5-1% of loan), underwriting fee ($300-700), processing fee ($300-500), credit report ($25-50) 2) THIRD-PARTY FEES: Appraisal ($400-600), home inspection ($300-500), survey ($400-800), pest inspection ($100-300) 3) TITLE & ESCROW: Title insurance (0.5-1% of price), title search ($200-400), escrow fees ($500-1500), attorney fees ($500-1500) 4) GOVERNMENT FEES: Recording fees ($50-200), transfer taxes (varies by state), property taxes (prorated), city/county fees 5) INSURANCE: Homeowner's insurance (first year premium), flood insurance if required, umbrella insurance 6) PREPAID ITEMS: Property taxes, homeowner's insurance, interest (from closing to first payment) 7) ESCROW RESERVES: Tax and insurance reserves (2-3 months), initial escrow deposit 8) REAL ESTATE COMMISSIONS: Buyer agent commission (if applicable), transaction coordinator fees 9) TOTAL CLOSING COSTS: Grand total, percentage of purchase price, cash required at closing Include detailed cost breakdown and cash-to-close calculation.`,
      
      pmi_analysis: `Analyze Private Mortgage Insurance (PMI) for ${propertyData.address || 'the subject property'} purchase. Include: 1) PMI REQUIREMENT: LTV ratios requiring PMI (typically >80%), loan types subject to PMI, exemptions 2) PMI COST CALCULATION: Annual PMI rate (0.3-1.5% of loan amount), monthly PMI payment, cost factors 3) PMI REMOVAL OPTIONS: Automatic removal at 78% LTV, borrower-requested removal at 80% LTV, reappraisal requirements 4) PMI ELIMINATION TIMELINE: Loan balance reduction schedule, PMI removal date projection, accelerated payoff scenarios 5) PMI vs LARGER DOWN PAYMENT: Cost comparison, opportunity cost analysis, optimal down payment amount 6) LENDER-PAID PMI: Higher interest rate vs borrower-paid PMI, cost comparison over loan term 7) PIGGYBACK LOANS: 80/10/10 or 80/15/5 loans to avoid PMI, second mortgage considerations 8) PMI TAX DEDUCTIBILITY: Current tax treatment, income limitations, potential tax benefits 9) PMI ALTERNATIVES: VA loans, USDA loans, state programs, credit union options Include PMI cost projections and elimination strategies.`,
      
      
      // Investment Strategies  
      brrrr_strategy: `Analyze BRRRR (Buy, Rehab, Rent, Refinance, Repeat) strategy for ${propertyData.address || 'the subject property'}. Include: 1) BUY PHASE: Purchase at $${propertyData.price || 'X'}, acquisition costs, initial investment required, financing options 2) REHAB PHASE: Renovation scope, estimated costs ($X per category), timeline, contractor management, permit requirements 3) AFTER REPAIR VALUE (ARV): Comparable sales post-renovation, estimated ARV, value-add calculation 4) RENT PHASE: Market rent analysis, rental income potential, property management, cash flow projections 5) REFINANCE PHASE: New appraised value, refinance loan amount (75-80% LTV), cash-out calculation, new loan terms 6) CASH LEFT IN DEAL: Total invested minus refinance proceeds, final cash position, infinite return potential 7) REPEAT ANALYSIS: Available cash for next deal, portfolio scaling, compound growth projections 8) RISK ASSESSMENT: Renovation overruns, market changes, refinancing challenges, exit strategies 9) RETURN CALCULATIONS: Cash-on-cash return, IRR, equity multiple, portfolio growth rate Include detailed BRRRR worksheet with cash flow at each phase.`,
      
      wholesale_analysis: `Create wholesale real estate analysis for ${propertyData.address || 'the subject property'}. Include: 1) PROPERTY ACQUISITION: Contract price, earnest money, inspection period, contingencies 2) AFTER REPAIR VALUE (ARV): Renovation costs estimate, comparable sales analysis, maximum ARV 3) 70% RULE APPLICATION: Maximum all-in price (70% of ARV minus repairs), profit margin calculation 4) ASSIGNMENT FEE: Wholesale fee (typically $5-20k), assignment contract terms, fee justification 5) END BUYER ANALYSIS: Investor buyer criteria, profit requirements, financing capabilities 6) MARKETING STRATEGY: Buyer list development, property marketing, deal presentation 7) TIMELINE MANAGEMENT: Contract timeline, buyer procurement, closing coordination 8) LEGAL CONSIDERATIONS: Assignment contracts, disclosure requirements, licensing issues 9) PROFIT PROJECTIONS: Assignment fee, deal velocity, monthly income potential, annual projections Include assignment contract template and buyer qualification criteria.`,
      
      reit_analysis: `Analyze Real Estate Investment Trust (REIT) investment opportunities. Include: 1) REIT TYPES: Equity REITs, mortgage REITs, hybrid REITs, sector specialization (residential, commercial, retail, healthcare, industrial) 2) FINANCIAL ANALYSIS: Funds From Operations (FFO), Adjusted FFO, Net Asset Value (NAV), price-to-FFO ratio 3) DIVIDEND ANALYSIS: Current dividend yield, dividend coverage ratio, payout sustainability, dividend growth history 4) PORTFOLIO COMPOSITION: Property types, geographic diversification, tenant quality, lease terms 5) MANAGEMENT QUALITY: Track record, strategy execution, capital allocation, corporate governance 6) MARKET POSITION: Competitive advantages, market share, growth opportunities, industry trends 7) VALUATION METRICS: Price-to-book ratio, premium/discount to NAV, peer comparison, historical valuations 8) RISK ASSESSMENT: Interest rate sensitivity, market cycle exposure, leverage ratios, liquidity risks 9) INVESTMENT RECOMMENDATION: Buy/hold/sell rating, price targets, portfolio allocation, income vs growth focus Include REIT comparison matrix and portfolio allocation recommendations.`,
      
      syndication: `Analyze real estate syndication opportunity for ${propertyData.address || 'a syndicated property'}. Include: 1) DEAL STRUCTURE: Sponsor equity, investor equity, debt financing, total capitalization, ownership percentages 2) RETURN PROJECTIONS: Preferred return (typically 6-8%), IRR projections, equity multiple, distribution waterfall 3) SPONSOR ANALYSIS: Track record, experience, previous deals, asset management capability, alignment of interests 4) PROPERTY ANALYSIS: Location, condition, market position, value-add opportunities, exit strategy 5) FINANCIAL PROJECTIONS: Pro forma cash flows, renovation budgets, operating assumptions, sale projections 6) FEE STRUCTURE: Acquisition fees, asset management fees, disposition fees, promoted interest 7) RISK FACTORS: Market risks, execution risks, sponsor risks, liquidity constraints 8) LEGAL STRUCTURE: LLC or LP structure, investor rights, voting provisions, reporting requirements 9) INVESTMENT TERMS: Minimum investment, capital call schedule, distribution frequency, hold period Include investment summary and due diligence checklist.`,
      
      tax_benefits: `Analyze real estate tax benefits for ${propertyData.address || 'investment property'} ownership. Include: 1) DEPRECIATION BENEFITS: Residential (27.5 years) vs commercial (39 years) depreciation, annual deduction amounts, recapture implications 2) EXPENSE DEDUCTIONS: Interest, taxes, insurance, maintenance, management, professional fees, travel expenses 3) COST SEGREGATION: Accelerated depreciation, 5-7-15 year property classifications, bonus depreciation opportunities 4) 1031 EXCHANGES: Like-kind exchange rules, timeline requirements (45/180 days), replacement property identification, deferred gains 5) OPPORTUNITY ZONES: Qualified Opportunity Zone investments, capital gains deferral, 10-year hold benefits 6) PASSIVE ACTIVITY RULES: $25k rental loss allowance, active participation requirements, income phase-outs, passive loss carryforwards 7) QBI DEDUCTION: 20% qualified business income deduction for rental activities, REIT dividends, limitations 8) STATE TAX CONSIDERATIONS: State income tax impact, property tax deductions, state-specific benefits 9) TAX PLANNING STRATEGIES: Timing of sales, installment sales, charitable remainder trusts, estate planning Include tax savings calculations and optimization strategies.`,
      
      portfolio_analysis: `Analyze real estate investment portfolio performance and optimization. Include: 1) PORTFOLIO COMPOSITION: Property types, geographic diversification, acquisition dates, current values, outstanding debt 2) PERFORMANCE METRICS: Total return, cash-on-cash returns, IRR by property, portfolio-level returns, benchmarking 3) CASH FLOW ANALYSIS: Total portfolio cash flow, property-level performance, cash flow trends, distribution coverage 4) LEVERAGE ANALYSIS: LTV ratios by property, weighted average cost of debt, debt maturity schedule, refinancing opportunities 5) DIVERSIFICATION ASSESSMENT: Property type concentration, geographic concentration, tenant diversification, market cycle exposure 6) RISK ANALYSIS: Interest rate risk, market risk, liquidity risk, concentration risk, mitigation strategies 7) OPTIMIZATION OPPORTUNITIES: Underperforming assets, value-add potential, disposition candidates, acquisition targets 8) PORTFOLIO REBALANCING: Asset allocation targets, buying/selling recommendations, market timing considerations 9) GROWTH STRATEGY: Expansion plans, financing strategy, target markets, investment criteria Include portfolio dashboard and strategic recommendations.`,
      
      
      // Commercial Real Estate
      cap_rate: `Perform capitalization rate analysis for ${propertyData.address || 'the commercial property'} generating $${propertyData.rentAmount ? (propertyData.rentAmount * 12) : 'X'} annual NOI. Include: 1) CAP RATE CALCULATION: Net Operating Income ÷ Property Value, current cap rate derivation 2) MARKET CAP RATES: Comparable sales cap rates, property type averages, submarket comparisons, cap rate trends 3) CAP RATE COMPONENTS: Risk-free rate, risk premium, growth expectations, market factors 4) VALUE IMPACT: Property value at different cap rates, value sensitivity analysis, cap rate compression/expansion effects 5) INVESTMENT GRADE: Cap rate interpretation, investment quality assessment, relative value analysis 6) CAP RATE TRENDS: Historical trends, market cycle impacts, future projections, timing considerations 7) TERMINAL CAP RATE: Exit cap rate assumptions, hold period analysis, sale value projections 8) RISK ADJUSTMENT: Cap rate premiums for location, tenant quality, lease terms, property condition 9) INVESTMENT DECISION: Buy/sell recommendations, optimal cap rate targets, market timing Include cap rate sensitivity analysis and investment recommendation.`,
      
      noi_analysis: `Analyze Net Operating Income (NOI) for ${propertyData.address || 'the commercial property'}. Include: 1) GROSS RENTAL INCOME: Base rent, percentage rent, expense reimbursements, parking income, other income sources 2) VACANCY & CREDIT LOSS: Market vacancy rates, tenant credit quality, lease rollover risk, collection issues 3) EFFECTIVE GROSS INCOME: Gross income minus vacancy and credit losses 4) OPERATING EXPENSES: Property taxes, insurance, utilities, maintenance, management, professional services, reserves 5) EXPENSE ANALYSIS: Fixed vs variable expenses, expense ratios, benchmarking, cost control opportunities 6) NET OPERATING INCOME: EGI minus operating expenses, NOI margin, NOI growth trends 7) NOI PROJECTIONS: Annual NOI growth, rent escalations, expense inflation, reversion analysis 8) EXPENSE RECOVERY: CAM charges, tax escalations, insurance pass-throughs, tenant reimbursements 9) NOI OPTIMIZATION: Revenue enhancement, expense reduction, operational efficiency Include detailed NOI statement and optimization recommendations.`,
      
      dcf_analysis: `Create Discounted Cash Flow (DCF) analysis for ${propertyData.address || 'the commercial property'} investment. Include: 1) CASH FLOW PROJECTIONS: 10-year annual cash flows, rent growth assumptions, expense inflation, capital expenditures 2) DISCOUNT RATE: Required rate of return, risk-free rate plus risk premium, WACC calculation, market comparison 3) TERMINAL VALUE: Exit cap rate assumption, terminal cash flow, reversion value calculation 4) PRESENT VALUE: NPV calculation, discounted cash flows, terminal value present worth 5) SENSITIVITY ANALYSIS: Discount rate sensitivity, growth rate variations, exit cap rate scenarios 6) IRR CALCULATION: Internal rate of return, comparison to required return, investment hurdle rates 7) INVESTMENT METRICS: NPV, IRR, payback period, profitability index, MOIC (multiple on invested capital) 8) SCENARIO ANALYSIS: Base case, best case, worst case scenarios, probability-weighted returns 9) INVESTMENT RECOMMENDATION: Buy/sell decision, price targets, value range Include detailed DCF model with assumptions and sensitivity tables.`,
      
      lease_analysis: `Analyze commercial lease terms for ${propertyData.address || 'the commercial property'}. Include: 1) LEASE STRUCTURE: Base rent, escalations, expense pass-throughs, percentage rent, lease type (gross, net, modified gross) 2) RENT ANALYSIS: Market rent comparison, rent per square foot, effective rent calculation, free rent value 3) LEASE TERMS: Initial term, renewal options, expansion rights, assignment/subletting, use restrictions 4) EXPENSE PROVISIONS: CAM charges, tax escalations, insurance costs, expense caps, audit rights 5) TENANT IMPROVEMENTS: TI allowances, construction responsibilities, design approval, ownership 6) RENT ESCALATIONS: Annual increases, CPI adjustments, fixed escalations, fair market value resets 7) LEASE VALUE: Present value of lease, credit quality impact, lease vs market rent analysis 8) LEASE RISK: Credit risk, lease rollover, renewal probability, replacement cost analysis 9) LANDLORD/TENANT ECONOMICS: Effective rent, capital costs, net effective rent, investment returns Include lease abstract and financial impact analysis.`,
      
      market_rent: `Analyze commercial market rent for ${propertyData.address || 'the commercial property'} in ${propertyData.marketArea || 'the market'}. Include: 1) COMPARABLE ANALYSIS: Recent lease comparables, rent per square foot, location adjustments, building quality factors 2) MARKET SURVEY: Submarket rent ranges, vacancy rates, absorption trends, construction pipeline 3) RENT DRIVERS: Location factors, building amenities, parking, accessibility, demographics 4> LEASE CONCESSIONS: Free rent periods, tenant improvement allowances, expense abatements, effective rent calculation 5) MARKET TRENDS: Rent growth rates, market fundamentals, supply/demand balance, economic drivers 6) RENTAL RATE MATRIX: Rent by building class, location, size, lease term impacts 7) NEGOTIATING POSITION: Market leverage, tenant alternatives, landlord motivations, timing factors 8) RENT PROJECTIONS: Future market rent estimates, lease rollover analysis, budgeting assumptions 9) RECOMMENDATION: Market rent range, negotiation strategy, lease renewal considerations Include market rent survey and lease recommendation.`,
      
      vacancy_analysis: `Analyze vacancy rates and impact for ${propertyData.marketArea || 'the market area'} commercial properties. Include: 1) VACANCY STATISTICS: Current vacancy rates by property type, submarket comparison, historical trends 2) VACANCY DRIVERS: Economic factors, supply additions, demand changes, market fundamentals 3) ABSORPTION ANALYSIS: Net absorption trends, leasing velocity, space demand patterns 4) CONSTRUCTION PIPELINE: New supply delivery, development timeline, competitive impact 5) VACANCY COST IMPACT: Lost rental income, carrying costs, marketing expenses, concession costs 6) TENANT RETENTION: Renewal rates, expansion activity, tenant satisfaction, retention strategies 7) LEASING STRATEGY: Rental rates vs vacancy trade-offs, concession strategies, tenant mix optimization 8) MARKET CYCLE: Vacancy cycle patterns, peak/trough identification, timing implications 9) VACANCY FORECAST: Future vacancy projections, market fundamentals, investment implications Include vacancy trend analysis and leasing recommendations.`,
      
      
      // Development & Construction
      development_analysis: `Create comprehensive development feasibility study for ${propertyData.address || 'the development site'} in ${propertyData.marketArea || 'the market'}. Include: 1) SITE ANALYSIS: Land area, zoning, topography, utilities, access, environmental factors, highest and best use 2) LAND ACQUISITION: Purchase price, carrying costs, due diligence expenses, closing timeline 3) DEVELOPMENT PROGRAM: Building size, unit mix, density, parking requirements, amenities, site plan 4) CONSTRUCTION COSTS: Hard costs ($X/sqft by building type), site work, utilities, permits, impact fees 5) SOFT COSTS: Architecture, engineering, legal, financing, construction management, marketing (typically 15-25% of hard costs) 6) FINANCING STRUCTURE: Land loan, construction loan, permanent financing, equity requirements, cost of capital 7) DEVELOPMENT TIMELINE: Entitlements, design, construction, lease-up/sales, total project duration 8) REVENUE PROJECTIONS: Sales prices/rents, absorption rates, pricing strategy, market analysis 9) PROFITABILITY ANALYSIS: Development costs, gross revenue, net profit, IRR, profit margin, risk assessment Include detailed development pro forma and risk mitigation strategies.`,
      
      construction_costs: `Estimate construction costs for ${propertyData.address || 'the construction project'} (${propertyData.propertyType || 'building type'}). Include: 1) HARD COSTS: Site preparation, foundation, framing, roofing, mechanical/electrical/plumbing, finishes, cost per square foot by building type 2) COST BREAKDOWN: Structural (20-25%), MEP (25-30%), finishes (20-25%), site work (10-15%), other 3) BUILDING SYSTEMS: HVAC costs, electrical systems, plumbing, fire safety, security, smart building features 4) FINISH LEVELS: Basic, standard, premium finish packages, cost differentials, value engineering opportunities 5) SITE WORK: Grading, utilities, paving, landscaping, drainage, environmental remediation if needed 6) PERMIT COSTS: Building permits, impact fees, utility connections, inspection fees, regulatory costs 7) CONTINGENCIES: Construction contingency (5-10%), design contingency (3-5%), escalation factors 8) CONSTRUCTION TIMELINE: Project phases, construction duration, weather delays, permit processing time 9) COST CONTROL: Value engineering, competitive bidding, change order management, cost monitoring Include detailed construction budget and cost control strategies.`,
      
      permit_analysis: `Analyze permits and approvals for ${propertyData.address || 'the development project'} in ${propertyData.marketArea || 'the jurisdiction'}. Include: 1) ZONING ANALYSIS: Current zoning, permitted uses, density limits, setback requirements, height restrictions 2) ENTITLEMENT PROCESS: Conditional use permits, variances, planned unit developments, public hearings, approval timeline 3) BUILDING PERMITS: Permit requirements, plan review process, inspection schedule, permit costs 4) IMPACT FEES: Development impact fees, school fees, park fees, transportation fees, utility connections 5) ENVIRONMENTAL REVIEW: CEQA/NEPA requirements, environmental impact studies, mitigation measures 6) UTILITY APPROVALS: Water, sewer, electric, gas, telecommunications, capacity availability, upgrade requirements 7) REGULATORY COMPLIANCE: ADA compliance, energy codes, fire safety, flood zone requirements 8) APPROVAL TIMELINE: Permitting schedule, critical path items, potential delays, expediting options 9) COST SUMMARY: Total permit and approval costs, timeline impacts, budget implications Include permit checklist and approval timeline with cost estimates.`,
      
      subdivision: `Analyze subdivision development for ${propertyData.address || 'the raw land'}. Include: 1) SUBDIVISION ANALYSIS: Lot yield, lot sizes, street layout, utility placement, density optimization 2) MARKET ANALYSIS: Lot sales comparables, absorption rates, target buyers, pricing strategy 3) DEVELOPMENT COSTS: Infrastructure (streets, utilities, drainage), grading, landscaping, permits, soft costs 4) INFRASTRUCTURE REQUIREMENTS: Street improvements, utility extensions, sewer/water capacity, traffic impacts 5) ENTITLEMENT PROCESS: Tentative map, final map, improvement agreements, bonding requirements 6) PHASING STRATEGY: Development phases, infrastructure timing, sales phasing, cash flow management 7) LOT SALES PROJECTIONS: Sales pace, pricing progression, pre-sales strategy, absorption analysis 8) PROFITABILITY ANALYSIS: Total development cost, gross revenue, net profit, IRR, margin analysis 9) RISK ASSESSMENT: Market risks, entitlement risks, construction risks, absorption risks Include subdivision financial pro forma and phasing plan.`,
      
      spec_building: `Analyze speculative building development for ${propertyData.address || 'the development site'}. Include: 1) MARKET DEMAND: Space demand, tenant requirements, competing projects, absorption timing 2) BUILDING PROGRAM: Building size, layout, tenant improvements, parking, common areas 3) CONSTRUCTION BUDGET: Shell building costs, site work, permits, tenant improvements, contingencies 4) FINANCING STRATEGY: Construction loan, interest carry, equity requirements, permanent financing 5) LEASING STRATEGY: Pre-leasing vs spec building, rental rates, lease terms, concessions, broker commissions 6) HOLDING COSTS: Interest, taxes, insurance, marketing, property management during lease-up 7) LEASE-UP PROJECTIONS: Leasing timeline, absorption rate, tenant mix, lease terms 8) STABILIZED VALUE: NOI projection, cap rate analysis, sale vs hold analysis 9) RETURN ANALYSIS: Development yield, IRR, profit margin, risk-adjusted returns Include spec building pro forma and leasing timeline.`,
      
      infill_development: `Analyze urban infill development opportunity for ${propertyData.address || 'the infill site'}. Include: 1) SITE CONSTRAINTS: Lot size, zoning density, parking requirements, neighbor impacts, environmental issues 2) NEIGHBORHOOD ANALYSIS: Demographics, gentrification trends, transit access, walkability, amenities 3) PRODUCT TYPE: Condos, townhomes, small-lot SFR, mixed-use, optimal product for location 4) DEVELOPMENT CHALLENGES: Soil conditions, utilities, access, construction logistics, community opposition 5> COST PREMIUMS: Urban construction costs, parking costs, regulatory compliance, design requirements 6) MARKET POSITIONING: Target buyers, pricing strategy, competition, absorption rates 7) REGULATORY HURDLES: Zoning compliance, design review, neighborhood meetings, approval process 8) INFRASTRUCTURE: Existing utilities, street improvements, impact on traffic, parking solutions 9) FINANCIAL ANALYSIS: Land cost, development cost, sales prices, profit margins, IRR Include infill development feasibility analysis and risk mitigation plan.`,
      
      
      // Legal & Documentation
      purchase_agreement: `Generate real estate purchase agreement for ${propertyData.address || 'the subject property'} at $${propertyData.price || 'X'} purchase price. Include: 1) PARTIES: Buyer and seller identification, legal names, contact information, agent representation 2) PROPERTY DESCRIPTION: Legal description, property address, included fixtures and personal property 3) PURCHASE TERMS: Purchase price, earnest money deposit, financing contingency, down payment amount 4) CONTINGENCIES: Inspection contingency (typically 10-14 days), appraisal contingency, financing contingency, title contingency 5) CLOSING TERMS: Closing date, possession date, prorations, closing cost allocation 6) DISCLOSURES: Seller disclosures, lead-based paint, natural hazards, homeowner association 7) DEFAULT REMEDIES: Buyer default, seller default, earnest money disposition, specific performance 8) SPECIAL TERMS: As-is sales, seller concessions, repair negotiations, warranty provisions 9) SIGNATURES: Buyer and seller signatures, date of acceptance, counteroffers Include complete purchase agreement template with state-specific provisions.`,
      
      lease_agreement: `Create comprehensive lease agreement for ${propertyData.address || 'the rental property'} at $${propertyData.rentAmount || 'X'}/month. Include: 1) LEASE PARTIES: Landlord and tenant information, property management contacts, authorized agents 2) PROPERTY DESCRIPTION: Rental unit address, unit number, square footage, included amenities 3) LEASE TERMS: Monthly rent, lease term, security deposit, late fees, rent increases 4) TENANT OBLIGATIONS: Rent payment, property care, occupancy limits, pet policies, smoking policies 5) LANDLORD OBLIGATIONS: Property maintenance, habitability, repairs, utility responsibilities 6) USE RESTRICTIONS: Permitted uses, business restrictions, modifications, subletting policies 7) MAINTENANCE & REPAIRS: Tenant responsibilities, landlord responsibilities, emergency procedures, vendor access 8) TERMINATION: Notice requirements, lease violations, eviction procedures, holdover provisions 9) LEGAL PROVISIONS: Governing law, dispute resolution, attorney fees, severability Include residential and commercial lease templates with local law compliance.`,
      
      deed_forms: `Generate property deed forms for ${propertyData.address || 'the subject property'} transfer. Include: 1) DEED TYPES: Warranty deed, quitclaim deed, special warranty deed, deed selection criteria 2) GRANTOR/GRANTEE: Current owner information, new owner information, legal capacity verification 3) PROPERTY DESCRIPTION: Legal description from title report, property address, parcel number 4) CONSIDERATION: Purchase price, gift designation, tax implications, documentary stamps 5) TITLE WARRANTIES: Full warranty, limited warranty, no warranty provisions, title insurance coordination 6) EXECUTION REQUIREMENTS: Notarization, witness requirements, acknowledgment forms, recording information 7) TAX IMPLICATIONS: Transfer taxes, documentary stamps, homestead exemptions, property tax reassessment 8) RECORDING PROCESS: County recording requirements, recording fees, certified copies 9. SPECIAL SITUATIONS: Joint ownership, trust transfers, estate transfers, business entity transfers Include deed templates and recording checklists for different transfer scenarios.`,
      
      disclosure_forms: `Create property disclosure package for ${propertyData.address || 'the subject property'} (${propertyData.yearBuilt || 'built X'}). Include: 1) SELLER DISCLOSURES: Property condition, known defects, repair history, insurance claims, environmental hazards 2) MATERIAL FACTS: Neighborhood issues, noise problems, boundary disputes, easements, restrictive covenants 3> SYSTEMS DISCLOSURES: HVAC, electrical, plumbing, roofing, foundation, appliances, recent repairs 4) ENVIRONMENTAL DISCLOSURES: Lead-based paint (pre-1978), asbestos, mold, radon, underground tanks, soil contamination 5) NATURAL HAZARDS: Flood zones, earthquake faults, fire hazards, landslide areas, coastal hazards 6) REGULATORY DISCLOSURES: Zoning violations, unpermitted work, code violations, pending assessments 7) FINANCIAL DISCLOSURES: Property taxes, assessments, HOA fees, utility costs, rental income 8) LEGAL DISCLOSURES: Pending litigation, insurance claims, condemnation, bankruptcy impacts 9. ACKNOWLEDGMENTS: Buyer receipt, inspection rights, "as-is" provisions, disclosure updates Include comprehensive disclosure forms with legal compliance requirements.`,
      
      hoa_analysis: `Analyze Homeowner Association (HOA) for ${propertyData.address || 'the property'} in ${propertyData.marketArea || 'the community'}. Include: 1) HOA STRUCTURE: Governance structure, board composition, management company, decision-making process 2) FINANCIAL ANALYSIS: Monthly dues, special assessments, reserve funds, budget review, financial health 3) CC&Rs REVIEW: Covenants, conditions, restrictions, architectural guidelines, use restrictions 4) AMENITIES & SERVICES: Common areas, facilities, maintenance services, utilities, landscaping 5) RULE ENFORCEMENT: Violation procedures, fines, dispute resolution, architectural approval process 6) RESERVE STUDY: Capital improvements, replacement schedules, funding adequacy, future assessments 7) LEGAL COMPLIANCE: State HOA laws, disclosure requirements, board duties, homeowner rights 8) RESALE IMPACT: HOA approval process, transfer fees, document fees, buyer qualification 9. INVESTMENT CONSIDERATIONS: Rental restrictions, investment property rules, Airbnb policies, resale implications Include HOA document summary and investment impact analysis.`,
      
      title_analysis: `Perform title analysis for ${propertyData.address || 'the subject property'}. Include: 1) TITLE SEARCH: Chain of title, deed history, ownership verification, legal description accuracy 2) TITLE EXCEPTIONS: Easements, liens, encumbrances, restrictive covenants, utility rights 3) LIEN SEARCH: Mortgages, tax liens, judgment liens, mechanic's liens, HOA liens 4) SURVEY REVIEW: Boundary lines, encroachments, setback violations, easement conflicts 5) TITLE INSURANCE: Owner's policy, lender's policy, coverage amounts, premium costs, exceptions 6) TITLE DEFECTS: Clouds on title, correction procedures, quiet title actions, title curing 7) CLOSING PROTECTION: Title company selection, escrow procedures, wire fraud protection 8. SPECIAL SITUATIONS: Estate sales, foreclosures, tax sales, bankruptcy, divorce transfers 9. RESOLUTION STRATEGIES: Title problem solutions, insurance claims, legal remedies Include title commitment review and closing preparation checklist."
    }

    const specificPrompt = prompts[toolId]
    if (!specificPrompt) {
      setAnalysisResult('Error: Real estate tool not supported. Please contact support.')
      setIsAnalyzing(false)
      return
    }

    const prompt = `You are a senior real estate investment analyst and licensed appraiser with expertise in residential and commercial properties. ${specificPrompt}

Property Context:
- Address: ${propertyData.address || 'Not specified'}
- Price/Value: $${propertyData.price || 'Not specified'}
- Property Type: ${propertyData.propertyType || 'Not specified'}
- Square Footage: ${propertyData.sqft || 'Not specified'} sqft
- Configuration: ${propertyData.bedrooms || 'X'}BR/${propertyData.bathrooms || 'X'}BA
- Year Built: ${propertyData.yearBuilt || 'Not specified'}
- Rent/Income: $${propertyData.rentAmount || 'X'}/month
- Market Area: ${propertyData.marketArea || 'Not specified'}

CRITICAL REQUIREMENTS:
1. Include specific financial calculations with formulas and actual numbers
2. Provide detailed comparable property analysis with recent sales/leases
3. Use current market data, cap rates, and industry benchmarks
4. Include comprehensive risk assessment with mitigation strategies
5. Provide both conservative and optimistic scenario analysis
6. Format with professional real estate terminology and structure
7. Include specific investment recommendations with action items
8. Add market timing considerations and cycle analysis
9. Use actual real estate formulas (NOI, Cap Rate, Cash-on-Cash, IRR, etc.)
10. Make analysis ready for professional real estate decision-making

IMPORTANT: Create an institutional-quality real estate analysis that meets professional appraisal and investment standards. Include specific calculations, market data, and actionable recommendations.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat/completions`, {
        model: serverInfo.default_model || 'gpt-3.5-turbo',
        messages: [{
          role: 'system',
          content: 'You are a top-tier real estate investment analyst from CBRE or JLL with expertise in property valuation, investment analysis, and market research. Create institutional-quality real estate analyses with specific calculations, market data, and professional recommendations.'
        }, {
          role: 'user',
          content: prompt
        }],
        max_tokens: 3500,
        temperature: 0.1
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
      
      // Generate professional real estate analysis window
      setTimeout(() => {
        const toolName = sections[activeSection].tools.find(t => t.id === toolId)?.name || 'Real Estate Analysis'
        const newWindow = window.open('', '_blank')
        if (newWindow) {
          newWindow.document.write(`
            <!DOCTYPE html>
            <html>
              <head>
                <title>${toolName} - ${propertyData.address || 'Real Estate Analysis'}</title>
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
                    border-bottom: 3px solid #27ae60;
                    padding-bottom: 25px;
                  }
                  .document-title {
                    font-size: 20pt;
                    font-weight: bold;
                    color: #27ae60;
                    margin-bottom: 10px;
                  }
                  .property-info {
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 10px;
                    margin: 25px 0;
                    border-left: 5px solid #27ae60;
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                  }
                  .property-info strong {
                    color: #2c3e50;
                  }
                  .financial-summary {
                    background: #e8f5e8;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border: 2px solid #27ae60;
                  }
                  .risk-warning {
                    background: #fff3cd;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    border-left: 4px solid #ffc107;
                  }
                  .controls {
                    position: fixed;
                    top: 15px;
                    right: 15px;
                    background: white;
                    padding: 15px;
                    border: 2px solid #27ae60;
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
                  .print-btn { background: #27ae60; color: white; }
                  .save-btn { background: #3498db; color: white; }
                  .edit-btn { background: #f39c12; color: white; }
                  .calc-btn { background: #9b59b6; color: white; }
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
                    background-color: #27ae60;
                    color: white;
                    font-weight: bold;
                  }
                  .highlight {
                    background: #d5f4e6;
                    font-weight: bold;
                  }
                  .financial-calc {
                    background-color: #f0f9ff;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 15px 0;
                    border-left: 4px solid #3498db;
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
                  <button class="save-btn" onclick="downloadAnalysis()">💾 Save</button>
                  <button class="edit-btn" onclick="editAnalysis()">✏️ Edit</button>
                  <button class="calc-btn" onclick="openCalculator()">🧮 Calculator</button>
                </div>
                <div class="document-header">
                  <div class="document-title">${toolName}</div>
                  <div style="color: #7f8c8d; font-size: 12pt;">Professional Real Estate Investment Analysis</div>
                </div>
                <div class="property-info">
                  <div><strong>Property:</strong> ${propertyData.address || 'Not specified'}</div>
                  <div><strong>Price/Value:</strong> $${propertyData.price ? Number(propertyData.price).toLocaleString() : 'Not specified'}</div>
                  <div><strong>Type:</strong> ${propertyData.propertyType || 'Not specified'}</div>
                  <div><strong>Size:</strong> ${propertyData.sqft ? Number(propertyData.sqft).toLocaleString() : 'Not specified'} sqft</div>
                  <div><strong>Configuration:</strong> ${propertyData.bedrooms || 'X'}BR/${propertyData.bathrooms || 'X'}BA</div>
                  <div><strong>Year Built:</strong> ${propertyData.yearBuilt || 'Not specified'}</div>
                  <div><strong>Rent/Income:</strong> $${propertyData.rentAmount ? Number(propertyData.rentAmount).toLocaleString() : 'Not specified'}/month</div>
                  <div><strong>Market Area:</strong> ${propertyData.marketArea || 'Not specified'}</div>
                  <div><strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}</div>
                  <div><strong>Analyst:</strong> AeonForge Real Estate Intelligence</div>
                </div>
                <div id="analysis-content" style="white-space: pre-wrap;">${analysisContent}</div>
                
                <script>
                  function downloadAnalysis() {
                    const content = document.documentElement.outerHTML;
                    const blob = new Blob([content], { type: 'text/html' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '${toolName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${propertyData.address ? propertyData.address.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '_' : ''}' + new Date().toISOString().split('T')[0] + '.html';
                    a.click();
                    URL.revokeObjectURL(url);
                  }
                  
                  function editAnalysis() {
                    const content = document.getElementById('analysis-content');
                    if (content.contentEditable === 'true') {
                      content.contentEditable = 'false';
                      content.style.border = 'none';
                      content.style.background = 'transparent';
                      document.querySelector('.edit-btn').innerHTML = '✏️ Edit';
                    } else {
                      content.contentEditable = 'true';
                      content.style.border = '2px dashed #27ae60';
                      content.style.background = '#f8f9fa';
                      content.style.padding = '15px';
                      content.focus();
                      document.querySelector('.edit-btn').innerHTML = '✅ Save';
                    }
                  }
                  
                  function openCalculator() {
                    const calcWindow = window.open('', 'calc', 'width=400,height=600');
                    calcWindow.document.write(\`
                      <html>
                        <head><title>Real Estate Calculator</title></head>
                        <body style="font-family: Arial; padding: 20px;">
                          <h3>Real Estate Calculator</h3>
                          <div>
                            <h4>Cap Rate Calculator</h4>
                            NOI: <input type="number" id="noi" placeholder="Annual NOI"> <br><br>
                            Value: <input type="number" id="value" placeholder="Property Value"> <br><br>
                            <button onclick="calcCapRate()">Calculate Cap Rate</button>
                            <p id="capResult"></p>
                            
                            <h4>Cash-on-Cash Return</h4>
                            Annual Cash Flow: <input type="number" id="cashflow" placeholder="Annual Cash Flow"> <br><br>
                            Cash Invested: <input type="number" id="invested" placeholder="Cash Invested"> <br><br>
                            <button onclick="calcCashOnCash()">Calculate Return</button>
                            <p id="cocResult"></p>
                          </div>
                          <script>
                            function calcCapRate() {
                              const noi = document.getElementById('noi').value;
                              const value = document.getElementById('value').value;
                              if (noi && value) {
                                const capRate = (noi / value * 100).toFixed(2);
                                document.getElementById('capResult').innerHTML = 'Cap Rate: ' + capRate + '%';
                              }
                            }
                            function calcCashOnCash() {
                              const cf = document.getElementById('cashflow').value;
                              const inv = document.getElementById('invested').value;
                              if (cf && inv) {
                                const coc = (cf / inv * 100).toFixed(2);
                                document.getElementById('cocResult').innerHTML = 'Cash-on-Cash Return: ' + coc + '%';
                              }
                            }
                          </script>
                        </body>
                      </html>
                    \`);
                  }
                </script>
              </body>
            </html>
          `)
          newWindow.document.close()
        }
      }, 100)

    } catch (error) {
      console.error('Error generating real estate analysis:', error)
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error occurred'
      setAnalysisResult(`❌ Error generating analysis: ${errorMessage}\n\nPlease check your property details and try again. If the problem persists, contact support with error code: ${Date.now()}`)
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