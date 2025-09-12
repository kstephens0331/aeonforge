import React, { useState } from 'react'
import axios from 'axios'

function LegalTools({ serverInfo, user, authToken }) {
  const [activeCategory, setActiveCategory] = useState('contracts')
  const [documentData, setDocumentData] = useState({})
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedDocument, setGeneratedDocument] = useState('')

  const categories = {
    contracts: {
      title: 'Contract Generation',
      icon: '📄',
      tools: [
        { id: 'nda', name: 'Non-Disclosure Agreement', description: 'Comprehensive NDAs for business protection' },
        { id: 'employment', name: 'Employment Contract', description: 'Complete employment agreements' },
        { id: 'service', name: 'Service Agreement', description: 'Professional service contracts' },
        { id: 'lease', name: 'Lease Agreement', description: 'Residential and commercial leases' },
        { id: 'partnership', name: 'Partnership Agreement', description: 'Business partnership contracts' },
        { id: 'sales', name: 'Sales Contract', description: 'Goods and services sales agreements' },
        { id: 'consulting', name: 'Consulting Agreement', description: 'Independent contractor agreements' },
        { id: 'licensing', name: 'Licensing Agreement', description: 'IP and software licensing' }
      ]
    },
    business: {
      title: 'Business Formation',
      icon: '🏢',
      tools: [
        { id: 'llc', name: 'LLC Formation', description: 'Articles of organization and operating agreements' },
        { id: 'corporation', name: 'Corporation Setup', description: 'Corporate bylaws and articles of incorporation' },
        { id: 'bylaws', name: 'Corporate Bylaws', description: 'Complete corporate governance documents' },
        { id: 'shareholder', name: 'Shareholder Agreement', description: 'Equity and voting rights agreements' },
        { id: 'board', name: 'Board Resolutions', description: 'Corporate decision documentation' },
        { id: 'merger', name: 'Merger Documents', description: 'M&A legal documentation' }
      ]
    },
    compliance: {
      title: 'Compliance & Regulatory',
      icon: '⚖️',
      tools: [
        { id: 'privacy', name: 'Privacy Policy', description: 'GDPR/CCPA compliant privacy policies' },
        { id: 'terms', name: 'Terms of Service', description: 'Website and app terms of service' },
        { id: 'gdpr', name: 'GDPR Compliance', description: 'Data protection compliance documents' },
        { id: 'employment_law', name: 'Employment Law Compliance', description: 'HR policy and procedure documents' },
        { id: 'safety', name: 'Safety Compliance', description: 'OSHA and workplace safety documents' },
        { id: 'financial', name: 'Financial Compliance', description: 'SOX and regulatory compliance' }
      ]
    },
    litigation: {
      title: 'Litigation Support',
      icon: '⚔️',
      tools: [
        { id: 'complaint', name: 'Legal Complaint', description: 'Civil litigation complaint drafts' },
        { id: 'motion', name: 'Legal Motions', description: 'Court motion templates and drafts' },
        { id: 'discovery', name: 'Discovery Requests', description: 'Interrogatories and document requests' },
        { id: 'settlement', name: 'Settlement Agreement', description: 'Dispute resolution agreements' },
        { id: 'subpoena', name: 'Subpoena Documents', description: 'Court subpoena preparation' },
        { id: 'brief', name: 'Legal Brief', description: 'Court brief and memorandum drafts' }
      ]
    },
    estate: {
      title: 'Estate Planning',
      icon: '🏛️',
      tools: [
        { id: 'will', name: 'Last Will & Testament', description: 'Comprehensive will documents' },
        { id: 'trust', name: 'Trust Documents', description: 'Revocable and irrevocable trusts' },
        { id: 'power_attorney', name: 'Power of Attorney', description: 'Financial and healthcare POA' },
        { id: 'advance_directive', name: 'Advance Directive', description: 'Healthcare decision documents' },
        { id: 'guardianship', name: 'Guardianship Documents', description: 'Minor guardianship papers' },
        { id: 'probate', name: 'Probate Documents', description: 'Estate administration papers' }
      ]
    },
    intellectual: {
      title: 'Intellectual Property',
      icon: '💡',
      tools: [
        { id: 'patent', name: 'Patent Application', description: 'USPTO patent filing documents' },
        { id: 'trademark', name: 'Trademark Application', description: 'Brand protection filings' },
        { id: 'copyright', name: 'Copyright Registration', description: 'Creative work protection' },
        { id: 'trade_secret', name: 'Trade Secret Protection', description: 'Proprietary information agreements' },
        { id: 'invention', name: 'Invention Assignment', description: 'Employee invention agreements' },
        { id: 'infringement', name: 'Infringement Claims', description: 'IP violation notices' }
      ]
    }
  }

  const generateLegalDocument = async (toolId) => {
    setIsGenerating(true)
    
    const prompts = {
      nda: "Generate a comprehensive Non-Disclosure Agreement with mutual obligations, specific confidentiality terms, return of materials clauses, and remedies for breach. Include standard legal protections and enforceability provisions.",
      employment: "Create a complete employment contract including job duties, compensation, benefits, termination clauses, non-compete agreements, intellectual property assignment, and at-will employment provisions.",
      service: "Draft a professional service agreement with scope of work, deliverables, payment terms, intellectual property ownership, limitation of liability, and termination provisions.",
      lease: "Generate a comprehensive lease agreement with rent terms, security deposit, maintenance responsibilities, use restrictions, renewal options, and default remedies.",
      llc: "Create LLC Articles of Organization and Operating Agreement with member rights, profit/loss allocation, management structure, and dissolution procedures.",
      privacy: "Generate a GDPR and CCPA compliant privacy policy with data collection practices, use limitations, user rights, cookie policies, and international transfers.",
      will: "Draft a Last Will and Testament with executor appointment, asset distribution, guardian designation, and standard legal protections against challenges.",
      patent: "Create a USPTO patent application with detailed invention description, claims, drawings requirements, and prior art analysis.",
      // Add more prompts for other tools...
    }

    const prompt = `You are a legal expert. ${prompts[toolId] || 'Generate the requested legal document with comprehensive terms and professional language.'} 

Requirements:
1. Use formal legal language and structure
2. Include all necessary legal protections
3. Add appropriate disclaimers
4. Ensure enforceability and compliance
5. Format as a professional legal document
6. Include signature blocks and date fields
7. Add jurisdiction and governing law clauses

Create a complete, ready-to-use legal document that meets professional standards.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `legal_${toolId}_${Date.now()}`,
        model: 'gpt-3.5-turbo'
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      setGeneratedDocument(response.data.response)
      
      // Open document in new window for editing/saving
      const newWindow = window.open()
      newWindow.document.write(`
        <html>
          <head>
            <title>Legal Document - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: 'Times New Roman', serif; padding: 40px; line-height: 1.6; }
              h1 { text-align: center; text-transform: uppercase; }
              .signature-block { margin-top: 50px; }
              .date-line { border-bottom: 1px solid #000; width: 200px; display: inline-block; }
              @media print { body { padding: 20px; } }
            </style>
          </head>
          <body>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <button onclick="window.print()" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px;">Print Document</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating legal document:', error)
      setGeneratedDocument('Error generating document. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const renderToolCategory = () => {
    const category = categories[activeCategory]
    
    return (
      <div className="legal-category">
        <h3>{category.icon} {category.title}</h3>
        <div className="legal-tools-grid">
          {category.tools.map((tool) => (
            <div key={tool.id} className="legal-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-doc-btn"
                onClick={() => generateLegalDocument(tool.id)}
                disabled={isGenerating}
              >
                {isGenerating ? '⏳ Generating...' : '📝 Generate Document'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="legal-tools">
      <div className="legal-header">
        <h1>⚖️ Legal Document Generation</h1>
        <p>AI-powered legal document creation for all business and personal needs</p>
        <div className="legal-disclaimer">
          <strong>⚠️ Legal Disclaimer:</strong> These documents are AI-generated templates. 
          Always consult with a qualified attorney before using any legal documents.
        </div>
      </div>

      <div className="legal-navigation">
        {Object.entries(categories).map(([key, category]) => (
          <button
            key={key}
            className={`legal-nav-btn ${activeCategory === key ? 'active' : ''}`}
            onClick={() => setActiveCategory(key)}
          >
            <span className="nav-icon">{category.icon}</span>
            <span className="nav-title">{category.title}</span>
          </button>
        ))}
      </div>

      <div className="legal-content">
        {renderToolCategory()}
      </div>
    </div>
  )
}

export default LegalTools