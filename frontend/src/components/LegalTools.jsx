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
    if (isGenerating) return
    setIsGenerating(true)
    setGeneratedDocument('')
    
    const prompts = {
      // Contract Generation
      nda: "Generate a comprehensive Non-Disclosure Agreement with mutual obligations, specific confidentiality terms, return of materials clauses, remedies for breach, and 5-year term. Include definition of confidential information, permitted disclosures, and liquidated damages clause.",
      employment: "Create a complete employment contract including job title, duties, compensation structure, benefits package, vacation policy, termination clauses (with/without cause), non-compete agreement (12-month term), intellectual property assignment, and at-will employment provisions with severability clause.",
      service: "Draft a professional service agreement with detailed scope of work, specific deliverables and timelines, payment terms (net 30), intellectual property ownership, limitation of liability ($10,000 cap), indemnification clauses, and termination provisions (30-day notice).",
      lease: "Generate a comprehensive lease agreement with monthly rent amount, security deposit (1.5x rent), maintenance responsibilities (tenant vs landlord), use restrictions, pet policy, renewal options, late fees, and default remedies including eviction procedures.",
      partnership: "Create a business partnership agreement with capital contributions, profit/loss sharing percentages, management duties, decision-making authority, withdrawal procedures, buy-sell provisions, and dissolution terms.",
      sales: "Draft a sales contract for goods with product specifications, quantity, unit price, delivery terms (FOB), inspection period, warranty provisions, payment terms, and remedies for breach including specific performance.",
      consulting: "Generate an independent contractor agreement with project scope, deliverable deadlines, hourly/project rates, expense reimbursement, intellectual property ownership, confidentiality provisions, and 1099 tax acknowledgment.",
      licensing: "Create a licensing agreement with licensed property description, territory restrictions, royalty rates, minimum guarantees, quality control standards, termination rights, and trademark usage guidelines.",
      
      // Business Formation
      llc: "Create LLC Articles of Organization and comprehensive Operating Agreement with member names, capital contributions, membership percentages, profit/loss allocation, management structure (member-managed vs manager-managed), voting rights, transfer restrictions, and dissolution procedures.",
      corporation: "Generate Articles of Incorporation with corporate name, registered agent, authorized shares (common/preferred), par value, incorporator information, and comprehensive Corporate Bylaws with board structure, officer duties, shareholder meetings, and amendment procedures.",
      bylaws: "Draft complete Corporate Bylaws with board of directors composition, meeting requirements, quorum rules, officer positions and duties, shareholder voting procedures, dividend policies, and record-keeping requirements.",
      shareholder: "Create a shareholder agreement with share ownership percentages, voting agreements, transfer restrictions, right of first refusal, drag-along/tag-along rights, board representation, and buy-sell provisions with valuation methods.",
      board: "Generate board resolution templates for corporate actions including officer appointments, banking resolutions, contract approvals, dividend declarations, and major business decisions with proper authorization language.",
      merger: "Draft merger agreement with acquisition structure, purchase price allocation, representations and warranties, closing conditions, indemnification provisions, and post-closing covenants.",
      
      // Compliance & Regulatory
      privacy: "Generate a comprehensive privacy policy compliant with GDPR, CCPA, and other privacy laws including data collection practices, use limitations, third-party sharing, user rights (access, deletion, portability), cookie policies, international transfers with adequate safeguards, and contact information for privacy officer.",
      terms: "Create website/app Terms of Service with user obligations, prohibited uses, intellectual property rights, disclaimer of warranties, limitation of liability, indemnification, governing law, dispute resolution (arbitration clause), and account termination procedures.",
      gdpr: "Draft GDPR compliance documentation including data processing agreements, privacy impact assessments, breach notification procedures, data subject rights protocols, and consent management framework.",
      employment_law: "Create employment law compliance package with anti-discrimination policies, harassment prevention procedures, wage and hour compliance, family leave policies, safety protocols, and employee handbook with acknowledgment forms.",
      safety: "Generate OSHA compliance documentation including safety policies, hazard communication program, emergency procedures, training requirements, incident reporting, and safety committee charter.",
      financial: "Draft financial compliance documentation including SOX internal controls, audit procedures, financial reporting policies, insider trading policies, and regulatory filing requirements.",
      
      // Litigation Support
      complaint: "Create a civil litigation complaint with proper case caption, jurisdictional allegations, factual background, causes of action with legal elements, damages calculation, and prayer for relief including attorney fees.",
      motion: "Generate motion templates including motion to dismiss (12(b)(6)), summary judgment motion, discovery motions, and protective orders with supporting legal arguments and case law citations.",
      discovery: "Draft comprehensive discovery requests including interrogatories (25 questions), requests for production (document categories), requests for admission, and deposition outlines with follow-up questions.",
      settlement: "Create settlement agreement with release of all claims, payment terms, confidentiality provisions, non-admission clause, and enforcement mechanisms including liquidated damages.",
      subpoena: "Generate subpoena documents for witnesses and documents including proper service requirements, compliance deadlines, privilege objections, and motion to quash procedures.",
      brief: "Draft legal brief template with statement of issues, factual background, legal argument with case law citations, and conclusion with specific relief requested.",
      
      // Estate Planning
      will: "Generate a Last Will and Testament with testator identification, revocation of prior wills, executor appointment with powers, specific bequests, residuary clause, guardian designation for minors, no-contest clause, and proper attestation clause with witness requirements.",
      trust: "Create revocable living trust with settlor/trustee/beneficiary designations, trust property schedule, distribution provisions, successor trustee appointment, amendment procedures, and pour-over will coordination.",
      power_attorney: "Draft durable power of attorney for financial matters with agent appointment, specific powers granted, limitations, successor agents, and healthcare power of attorney with medical decision authority.",
      advance_directive: "Generate advance healthcare directive with living will provisions, DNR instructions, organ donation wishes, healthcare agent appointment, and HIPAA authorization for medical information sharing.",
      guardianship: "Create guardianship documents for minor children including guardian nomination, alternate guardians, financial management instructions, and court petition requirements.",
      probate: "Draft probate documentation including petition for probate, inventory of assets, creditor notices, final accounting, and distribution orders.",
      
      // Intellectual Property
      patent: "Create USPTO patent application with detailed invention description, technical specifications, claims (independent and dependent), drawings requirements, prior art analysis, and inventor declarations.",
      trademark: "Generate trademark application with mark description, goods/services classification, specimen requirements, use in commerce dates, and Madrid Protocol considerations for international filing.",
      copyright: "Draft copyright registration with work description, authorship information, publication details, deposit requirements, and work-for-hire determinations.",
      trade_secret: "Create trade secret protection agreement with confidential information definition, access restrictions, employee obligations, return of materials, and remedies for misappropriation.",
      invention: "Generate employee invention assignment with scope of covered inventions, assignment of rights, disclosure requirements, and compensation for inventions outside normal duties.",
      infringement: "Draft IP infringement cease and desist letter with specific infringement allegations, evidence of ownership, demand for cessation, damages calculation, and settlement proposal."
    }

    const specificPrompt = prompts[toolId]
    if (!specificPrompt) {
      setGeneratedDocument('Error: Document type not supported. Please contact support.')
      setIsGenerating(false)
      return
    }

    const prompt = `You are an experienced attorney specializing in document drafting. ${specificPrompt}

CRITICAL REQUIREMENTS:
1. Use proper legal terminology and formal structure
2. Include ALL standard legal protections and clauses
3. Add appropriate disclaimers and legal notices
4. Ensure enforceability under US law
5. Format as a professional legal document with proper headers
6. Include comprehensive signature blocks with date fields
7. Add governing law clause (state jurisdiction)
8. Include severability clause
9. Add force majeure provisions where applicable
10. Ensure document is ready for immediate legal use

IMPORTANT: Create a complete, legally sound document that meets professional attorney standards. Use proper legal formatting with numbered sections, defined terms, and standard legal language patterns.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat/completions`, {
        model: serverInfo.default_model || 'gpt-3.5-turbo',
        messages: [{
          role: 'system',
          content: 'You are an expert legal document drafting attorney with 20+ years of experience. Create professional, legally sound documents that meet all regulatory requirements.'
        }, {
          role: 'user',
          content: prompt
        }],
        max_tokens: 3000,
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

      const documentContent = response.data.choices[0].message.content
      setGeneratedDocument(documentContent)
      
      // Generate professional document window
      setTimeout(() => {
        const toolName = categories[activeCategory].tools.find(t => t.id === toolId)?.name || 'Legal Document'
        const newWindow = window.open('', '_blank')
        if (newWindow) {
          newWindow.document.write(`
            <!DOCTYPE html>
            <html>
              <head>
                <title>${toolName} - Generated by AeonForge Legal</title>
                <meta charset="UTF-8">
                <style>
                  body { 
                    font-family: 'Times New Roman', serif; 
                    font-size: 12pt;
                    line-height: 1.6; 
                    margin: 1in; 
                    color: #000;
                  }
                  .document-header {
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #000;
                    padding-bottom: 20px;
                  }
                  .document-title {
                    font-size: 16pt;
                    font-weight: bold;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                  }
                  .section-header {
                    font-weight: bold;
                    text-decoration: underline;
                    margin-top: 20px;
                    margin-bottom: 10px;
                  }
                  .signature-block {
                    margin-top: 50px;
                    page-break-inside: avoid;
                  }
                  .signature-line {
                    border-bottom: 1px solid #000;
                    width: 300px;
                    display: inline-block;
                    margin-right: 50px;
                  }
                  .date-line {
                    border-bottom: 1px solid #000;
                    width: 150px;
                    display: inline-block;
                  }
                  .controls {
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    background: white;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                  }
                  .controls button {
                    margin: 5px;
                    padding: 8px 15px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 12px;
                  }
                  .print-btn { background: #007bff; color: white; }
                  .save-btn { background: #28a745; color: white; }
                  .edit-btn { background: #ffc107; color: black; }
                  @media print { 
                    .controls { display: none; }
                    body { margin: 0.5in; font-size: 11pt; }
                  }
                </style>
              </head>
              <body>
                <div class="controls">
                  <button class="print-btn" onclick="window.print()">🖨️ Print</button>
                  <button class="save-btn" onclick="downloadDocument()">💾 Save</button>
                  <button class="edit-btn" onclick="editDocument()">✏️ Edit</button>
                </div>
                <div class="document-header">
                  <div class="document-title">${toolName}</div>
                  <div>Generated by AeonForge Legal Tools</div>
                  <div>Date: ${new Date().toLocaleDateString()}</div>
                </div>
                <div id="document-content" style="white-space: pre-wrap;">${documentContent}</div>
                
                <script>
                  function downloadDocument() {
                    const content = document.getElementById('document-content').innerText;
                    const blob = new Blob([content], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '${toolName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_' + new Date().toISOString().split('T')[0] + '.txt';
                    a.click();
                    URL.revokeObjectURL(url);
                  }
                  
                  function editDocument() {
                    const content = document.getElementById('document-content');
                    if (content.contentEditable === 'true') {
                      content.contentEditable = 'false';
                      content.style.border = 'none';
                      document.querySelector('.edit-btn').innerHTML = '✏️ Edit';
                    } else {
                      content.contentEditable = 'true';
                      content.style.border = '2px dashed #007bff';
                      content.focus();
                      document.querySelector('.edit-btn').innerHTML = '✅ Done';
                    }
                  }
                </script>
              </body>
            </html>
          `)
          newWindow.document.close()
        }
      }, 100)

    } catch (error) {
      console.error('Error generating legal document:', error)
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error occurred'
      setGeneratedDocument(`❌ Error generating document: ${errorMessage}\n\nPlease check your connection and try again. If the problem persists, contact support with error code: ${Date.now()}`)
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