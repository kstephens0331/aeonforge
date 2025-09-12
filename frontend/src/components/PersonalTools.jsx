import React, { useState, useEffect } from 'react'
import axios from 'axios'

function PersonalTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('budget')
  const [budgetData, setBudgetData] = useState({
    income: { monthly: '', sources: [] },
    expenses: { fixed: [], variable: [] },
    savings: { goals: [], emergency: '' },
    debts: []
  })
  const [creditData, setCreditData] = useState({
    bureaus: ['Experian', 'Equifax', 'TransUnion'],
    disputes: [],
    score: '',
    negativeItems: []
  })
  const [financeData, setFinanceData] = useState({
    accounts: [],
    investments: [],
    goals: []
  })

  const sections = {
    budget: {
      title: 'Budget Management',
      icon: '💰',
      description: 'Track income, expenses, and savings goals'
    },
    credit: {
      title: 'Credit Repair',
      icon: '📊',
      description: 'Dispute negative items and improve credit score'
    },
    finance: {
      title: 'Financial Tracking',
      icon: '💹',
      description: 'Monitor investments and financial goals'
    },
    planning: {
      title: 'Life Planning',
      icon: '🎯',
      description: 'Set and track personal development goals'
    },
    health: {
      title: 'Health & Wellness',
      icon: '🏃',
      description: 'Track fitness, nutrition, and mental health'
    },
    career: {
      title: 'Career Development',
      icon: '🚀',
      description: 'Skills tracking and career advancement'
    }
  }

  useEffect(() => {
    loadUserData()
  }, [])

  const loadUserData = () => {
    const savedBudget = localStorage.getItem(`aeonforge-budget-${user?.id}`)
    const savedCredit = localStorage.getItem(`aeonforge-credit-${user?.id}`)
    const savedFinance = localStorage.getItem(`aeonforge-finance-${user?.id}`)
    
    if (savedBudget) setBudgetData(JSON.parse(savedBudget))
    if (savedCredit) setCreditData(JSON.parse(savedCredit))
    if (savedFinance) setFinanceData(JSON.parse(savedFinance))
  }

  const saveBudgetData = (data) => {
    setBudgetData(data)
    localStorage.setItem(`aeonforge-budget-${user?.id}`, JSON.stringify(data))
  }

  const saveCreditData = (data) => {
    setCreditData(data)
    localStorage.setItem(`aeonforge-credit-${user?.id}`, JSON.stringify(data))
  }

  const saveFinanceData = (data) => {
    setFinanceData(data)
    localStorage.setItem(`aeonforge-finance-${user?.id}`, JSON.stringify(data))
  }

  const generateCreditDisputeLetter = async (item) => {
    const prompt = `Generate an aggressive but professional credit dispute letter for the following negative item:

Type: ${item.type}
Creditor: ${item.creditor}
Amount: $${item.amount}
Date: ${item.date}
Status: ${item.status}

Requirements:
1. Use strong legal language demanding verification
2. Reference Fair Credit Reporting Act (FCRA) violations
3. Request immediate deletion if verification cannot be provided
4. Include statutory penalties for non-compliance
5. Set 30-day deadline for response
6. Professional but assertive tone

Format as a formal business letter ready to send to credit bureaus.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `credit_dispute_${Date.now()}`,
        model: 'gpt-3.5-turbo'
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      return response.data.response
    } catch (error) {
      console.error('Error generating dispute letter:', error)
      return 'Error generating dispute letter. Please try again.'
    }
  }

  const addExpense = (type) => {
    const expense = {
      id: Date.now(),
      name: '',
      amount: '',
      category: '',
      date: new Date().toISOString().split('T')[0]
    }

    const updated = { ...budgetData }
    if (type === 'fixed') {
      updated.expenses.fixed.push(expense)
    } else {
      updated.expenses.variable.push(expense)
    }
    saveBudgetData(updated)
  }

  const addDebt = () => {
    const debt = {
      id: Date.now(),
      creditor: '',
      balance: '',
      minPayment: '',
      interestRate: '',
      dueDate: ''
    }

    const updated = { ...budgetData }
    updated.debts.push(debt)
    saveBudgetData(updated)
  }

  const addNegativeItem = () => {
    const item = {
      id: Date.now(),
      type: 'collection',
      creditor: '',
      amount: '',
      date: '',
      status: 'disputed'
    }

    const updated = { ...creditData }
    updated.negativeItems.push(item)
    saveCreditData(updated)
  }

  const calculateBudgetSummary = () => {
    const totalIncome = parseFloat(budgetData.income.monthly || 0)
    const totalFixed = budgetData.expenses.fixed.reduce((sum, expense) => 
      sum + parseFloat(expense.amount || 0), 0)
    const totalVariable = budgetData.expenses.variable.reduce((sum, expense) => 
      sum + parseFloat(expense.amount || 0), 0)
    const totalExpenses = totalFixed + totalVariable
    const remaining = totalIncome - totalExpenses

    return { totalIncome, totalExpenses, totalFixed, totalVariable, remaining }
  }

  const renderBudgetSection = () => {
    const summary = calculateBudgetSummary()

    return (
      <div className="personal-section">
        <h3>💰 Budget Overview</h3>
        
        <div className="budget-summary">
          <div className="summary-card income">
            <h4>Monthly Income</h4>
            <div className="amount">${summary.totalIncome.toFixed(2)}</div>
          </div>
          <div className="summary-card expenses">
            <h4>Total Expenses</h4>
            <div className="amount">${summary.totalExpenses.toFixed(2)}</div>
          </div>
          <div className={`summary-card remaining ${summary.remaining >= 0 ? 'positive' : 'negative'}`}>
            <h4>Remaining</h4>
            <div className="amount">${summary.remaining.toFixed(2)}</div>
          </div>
        </div>

        <div className="budget-sections">
          <div className="budget-category">
            <h4>Monthly Income</h4>
            <input
              type="number"
              placeholder="Monthly income"
              value={budgetData.income.monthly}
              onChange={(e) => saveBudgetData({
                ...budgetData,
                income: { ...budgetData.income, monthly: e.target.value }
              })}
            />
          </div>

          <div className="budget-category">
            <div className="category-header">
              <h4>Fixed Expenses</h4>
              <button onClick={() => addExpense('fixed')}>+ Add Fixed Expense</button>
            </div>
            {budgetData.expenses.fixed.map((expense) => (
              <div key={expense.id} className="expense-item">
                <input
                  type="text"
                  placeholder="Expense name"
                  value={expense.name}
                  onChange={(e) => {
                    const updated = { ...budgetData }
                    const item = updated.expenses.fixed.find(ex => ex.id === expense.id)
                    if (item) item.name = e.target.value
                    saveBudgetData(updated)
                  }}
                />
                <input
                  type="number"
                  placeholder="Amount"
                  value={expense.amount}
                  onChange={(e) => {
                    const updated = { ...budgetData }
                    const item = updated.expenses.fixed.find(ex => ex.id === expense.id)
                    if (item) item.amount = e.target.value
                    saveBudgetData(updated)
                  }}
                />
              </div>
            ))}
          </div>

          <div className="budget-category">
            <div className="category-header">
              <h4>Variable Expenses</h4>
              <button onClick={() => addExpense('variable')}>+ Add Variable Expense</button>
            </div>
            {budgetData.expenses.variable.map((expense) => (
              <div key={expense.id} className="expense-item">
                <input
                  type="text"
                  placeholder="Expense name"
                  value={expense.name}
                  onChange={(e) => {
                    const updated = { ...budgetData }
                    const item = updated.expenses.variable.find(ex => ex.id === expense.id)
                    if (item) item.name = e.target.value
                    saveBudgetData(updated)
                  }}
                />
                <input
                  type="number"
                  placeholder="Amount"
                  value={expense.amount}
                  onChange={(e) => {
                    const updated = { ...budgetData }
                    const item = updated.expenses.variable.find(ex => ex.id === expense.id)
                    if (item) item.amount = e.target.value
                    saveBudgetData(updated)
                  }}
                />
              </div>
            ))}
          </div>

          <div className="budget-category">
            <div className="category-header">
              <h4>Debts</h4>
              <button onClick={addDebt}>+ Add Debt</button>
            </div>
            {budgetData.debts.map((debt) => (
              <div key={debt.id} className="debt-item">
                <input
                  type="text"
                  placeholder="Creditor"
                  value={debt.creditor}
                  onChange={(e) => {
                    const updated = { ...budgetData }
                    const item = updated.debts.find(d => d.id === debt.id)
                    if (item) item.creditor = e.target.value
                    saveBudgetData(updated)
                  }}
                />
                <input
                  type="number"
                  placeholder="Balance"
                  value={debt.balance}
                  onChange={(e) => {
                    const updated = { ...budgetData }
                    const item = updated.debts.find(d => d.id === debt.id)
                    if (item) item.balance = e.target.value
                    saveBudgetData(updated)
                  }}
                />
                <input
                  type="number"
                  placeholder="Min Payment"
                  value={debt.minPayment}
                  onChange={(e) => {
                    const updated = { ...budgetData }
                    const item = updated.debts.find(d => d.id === debt.id)
                    if (item) item.minPayment = e.target.value
                    saveBudgetData(updated)
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const renderCreditSection = () => {
    return (
      <div className="personal-section">
        <h3>📊 Credit Repair Tools</h3>
        
        <div className="credit-overview">
          <div className="credit-score">
            <h4>Current Credit Score</h4>
            <input
              type="number"
              placeholder="Credit score"
              value={creditData.score}
              onChange={(e) => saveCreditData({
                ...creditData,
                score: e.target.value
              })}
            />
          </div>
        </div>

        <div className="credit-sections">
          <div className="credit-category">
            <div className="category-header">
              <h4>Negative Items to Dispute</h4>
              <button onClick={addNegativeItem}>+ Add Negative Item</button>
            </div>
            {creditData.negativeItems.map((item) => (
              <div key={item.id} className="negative-item">
                <div className="item-details">
                  <select
                    value={item.type}
                    onChange={(e) => {
                      const updated = { ...creditData }
                      const negItem = updated.negativeItems.find(ni => ni.id === item.id)
                      if (negItem) negItem.type = e.target.value
                      saveCreditData(updated)
                    }}
                  >
                    <option value="collection">Collection Account</option>
                    <option value="late-payment">Late Payment</option>
                    <option value="charge-off">Charge Off</option>
                    <option value="bankruptcy">Bankruptcy</option>
                    <option value="foreclosure">Foreclosure</option>
                    <option value="repossession">Repossession</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Creditor name"
                    value={item.creditor}
                    onChange={(e) => {
                      const updated = { ...creditData }
                      const negItem = updated.negativeItems.find(ni => ni.id === item.id)
                      if (negItem) negItem.creditor = e.target.value
                      saveCreditData(updated)
                    }}
                  />
                  <input
                    type="number"
                    placeholder="Amount"
                    value={item.amount}
                    onChange={(e) => {
                      const updated = { ...creditData }
                      const negItem = updated.negativeItems.find(ni => ni.id === item.id)
                      if (negItem) negItem.amount = e.target.value
                      saveCreditData(updated)
                    }}
                  />
                  <input
                    type="date"
                    value={item.date}
                    onChange={(e) => {
                      const updated = { ...creditData }
                      const negItem = updated.negativeItems.find(ni => ni.id === item.id)
                      if (negItem) negItem.date = e.target.value
                      saveCreditData(updated)
                    }}
                  />
                </div>
                <button 
                  className="generate-letter-btn"
                  onClick={async () => {
                    const letter = await generateCreditDisputeLetter(item)
                    // Open letter in new window for printing/saving
                    const newWindow = window.open()
                    newWindow.document.write(`
                      <html>
                        <head><title>Credit Dispute Letter</title></head>
                        <body style="font-family: Arial, sans-serif; padding: 20px;">
                          <pre style="white-space: pre-wrap;">${letter}</pre>
                        </body>
                      </html>
                    `)
                  }}
                >
                  🔥 Generate Aggressive Dispute Letter
                </button>
              </div>
            ))}
          </div>

          <div className="credit-tips">
            <h4>Credit Improvement Tips</h4>
            <ul>
              <li>Dispute all negative items with aggressive legal language</li>
              <li>Demand proof of validation for all debts</li>
              <li>Request immediate deletion if verification cannot be provided</li>
              <li>Keep credit utilization below 10% on all cards</li>
              <li>Never close old credit accounts (they help credit age)</li>
              <li>Set up automatic payments to avoid late fees</li>
              <li>Monitor all three credit bureaus monthly</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }

  const renderFinanceSection = () => {
    return (
      <div className="personal-section">
        <h3>💹 Financial Tracking</h3>
        
        <div className="finance-overview">
          <p>Track investments, savings goals, and financial milestones</p>
        </div>

        <div className="coming-soon">
          <h4>🚧 Advanced Financial Tools Coming Soon</h4>
          <ul>
            <li>Investment portfolio tracking</li>
            <li>Net worth calculator</li>
            <li>Retirement planning</li>
            <li>Tax optimization strategies</li>
            <li>Emergency fund calculator</li>
          </ul>
        </div>
      </div>
    )
  }

  const renderPlanningSection = () => {
    return (
      <div className="personal-section">
        <h3>🎯 Life Planning</h3>
        
        <div className="coming-soon">
          <h4>🚧 Life Planning Tools Coming Soon</h4>
          <ul>
            <li>Goal setting and tracking</li>
            <li>Habit formation tools</li>
            <li>Personal development plans</li>
            <li>Education and certification tracking</li>
            <li>Life milestone planning</li>
          </ul>
        </div>
      </div>
    )
  }

  const renderHealthSection = () => {
    return (
      <div className="personal-section">
        <h3>🏃 Health & Wellness</h3>
        
        <div className="coming-soon">
          <h4>🚧 Health Tools Coming Soon</h4>
          <ul>
            <li>Fitness tracking and workout plans</li>
            <li>Nutrition and meal planning</li>
            <li>Mental health check-ins</li>
            <li>Sleep quality monitoring</li>
            <li>Medication reminders</li>
          </ul>
        </div>
      </div>
    )
  }

  const renderCareerSection = () => {
    return (
      <div className="personal-section">
        <h3>🚀 Career Development</h3>
        
        <div className="coming-soon">
          <h4>🚧 Career Tools Coming Soon</h4>
          <ul>
            <li>Skills assessment and tracking</li>
            <li>Resume and cover letter optimization</li>
            <li>Interview preparation</li>
            <li>Networking tracker</li>
            <li>Salary negotiation tools</li>
          </ul>
        </div>
      </div>
    )
  }

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'budget': return renderBudgetSection()
      case 'credit': return renderCreditSection()
      case 'finance': return renderFinanceSection()
      case 'planning': return renderPlanningSection()
      case 'health': return renderHealthSection()
      case 'career': return renderCareerSection()
      default: return renderBudgetSection()
    }
  }

  return (
    <div className="personal-tools">
      <div className="personal-header">
        <h1>🌟 Personal Life Improvement Tools</h1>
        <p>Comprehensive tools to manage finances, improve credit, and enhance your life</p>
      </div>

      <div className="personal-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`nav-button ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <div className="nav-content">
              <div className="nav-title">{section.title}</div>
              <div className="nav-description">{section.description}</div>
            </div>
          </button>
        ))}
      </div>

      <div className="personal-content">
        {renderActiveSection()}
      </div>
    </div>
  )
}

export default PersonalTools