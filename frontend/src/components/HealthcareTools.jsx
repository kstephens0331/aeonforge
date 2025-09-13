import React, { useState } from 'react'
import axios from 'axios'

function HealthcareTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('symptoms')
  const [healthData, setHealthData] = useState({
    age: '',
    gender: '',
    symptoms: '',
    medicalHistory: '',
    medications: '',
    allergies: '',
    lifestyle: '',
    vitals: '',
    duration: ''
  })
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState('')

  const sections = {
    symptoms: {
      title: 'Symptom Analysis',
      icon: '🩺',
      tools: [
        { id: 'symptom_checker', name: 'AI Symptom Checker', description: 'Comprehensive symptom analysis and differential diagnosis' },
        { id: 'triage_assessment', name: 'Medical Triage', description: 'Urgency assessment and care recommendations' },
        { id: 'pain_assessment', name: 'Pain Assessment', description: 'Detailed pain analysis and management options' },
        { id: 'mental_health', name: 'Mental Health Screening', description: 'Depression, anxiety, and mood disorder assessment' },
        { id: 'pediatric_symptoms', name: 'Pediatric Assessment', description: 'Child-specific symptom evaluation' },
        { id: 'womens_health', name: 'Women\'s Health', description: 'Reproductive and gynecological health analysis' }
      ]
    },
    diagnosis: {
      title: 'Diagnostic Support',
      icon: '🔬',
      tools: [
        { id: 'differential_diagnosis', name: 'Differential Diagnosis', description: 'Evidence-based diagnostic possibilities' },
        { id: 'lab_interpreter', name: 'Lab Results Interpreter', description: 'Blood work and diagnostic test analysis' },
        { id: 'imaging_analysis', name: 'Medical Imaging Guide', description: 'X-ray, CT, MRI interpretation guidance' },
        { id: 'vital_signs', name: 'Vital Signs Analysis', description: 'Blood pressure, heart rate, temperature assessment' },
        { id: 'medication_interaction', name: 'Drug Interaction Checker', description: 'Medication safety and interaction analysis' },
        { id: 'genetic_risk', name: 'Genetic Risk Assessment', description: 'Hereditary condition risk evaluation' }
      ]
    },
    treatment: {
      title: 'Treatment Planning',
      icon: '💊',
      tools: [
        { id: 'treatment_options', name: 'Treatment Options', description: 'Evidence-based treatment recommendations' },
        { id: 'medication_guide', name: 'Medication Guide', description: 'Drug information and dosing guidelines' },
        { id: 'therapy_plans', name: 'Therapy Plans', description: 'Physical therapy and rehabilitation programs' },
        { id: 'surgical_options', name: 'Surgical Consultation', description: 'Surgical procedure information and risks' },
        { id: 'alternative_medicine', name: 'Alternative Medicine', description: 'Complementary and integrative treatments' },
        { id: 'recovery_planning', name: 'Recovery Planning', description: 'Post-treatment care and monitoring' }
      ]
    },
    prevention: {
      title: 'Preventive Care',
      icon: '🛡️',
      tools: [
        { id: 'health_screening', name: 'Health Screenings', description: 'Age-appropriate preventive care schedule' },
        { id: 'vaccination_schedule', name: 'Vaccination Planning', description: 'Immunization recommendations and schedules' },
        { id: 'nutrition_analysis', name: 'Nutrition Analysis', description: 'Dietary assessment and meal planning' },
        { id: 'fitness_planning', name: 'Fitness Planning', description: 'Exercise prescriptions and activity recommendations' },
        { id: 'wellness_coaching', name: 'Wellness Coaching', description: 'Lifestyle modification and health optimization' },
        { id: 'risk_stratification', name: 'Risk Stratification', description: 'Disease risk assessment and prevention strategies' }
      ]
    },
    chronic: {
      title: 'Chronic Disease Management',
      icon: '📊',
      tools: [
        { id: 'diabetes_management', name: 'Diabetes Management', description: 'Blood sugar monitoring and insulin optimization' },
        { id: 'hypertension_control', name: 'Hypertension Control', description: 'Blood pressure management strategies' },
        { id: 'heart_disease', name: 'Cardiac Care', description: 'Heart disease monitoring and treatment' },
        { id: 'respiratory_care', name: 'Respiratory Care', description: 'Asthma, COPD, and lung disease management' },
        { id: 'arthritis_management', name: 'Arthritis Management', description: 'Joint pain and mobility optimization' },
        { id: 'cancer_support', name: 'Cancer Support', description: 'Oncology treatment planning and support' }
      ]
    },
    research: {
      title: 'Medical Research',
      icon: '🧬',
      tools: [
        { id: 'pubmed_search', name: 'PubMed Research', description: 'Medical literature search and analysis' },
        { id: 'clinical_trials', name: 'Clinical Trials Finder', description: 'Research study opportunities' },
        { id: 'evidence_synthesis', name: 'Evidence Synthesis', description: 'Systematic review and meta-analysis' },
        { id: 'medical_guidelines', name: 'Clinical Guidelines', description: 'Professional medical guidelines and protocols' },
        { id: 'drug_research', name: 'Drug Research', description: 'Pharmaceutical research and development analysis' },
        { id: 'biomarker_analysis', name: 'Biomarker Analysis', description: 'Predictive and diagnostic biomarker evaluation' }
      ]
    }
  }

  const generateHealthAnalysis = async (toolId) => {
    setIsAnalyzing(true)

    const prompts = {
      symptom_checker: `Perform comprehensive symptom analysis based on the provided information. Include: Differential diagnosis with probability rankings, Recommended diagnostic tests, Urgency assessment (emergency, urgent, routine), Red flag symptoms to watch for, Self-care recommendations, and When to seek immediate medical attention.`,
      
      triage_assessment: `Conduct medical triage assessment including: Severity scoring (1-5 scale), Immediate care needs, Appropriate care setting (ER, urgent care, primary care), Timeline for seeking care, Warning signs requiring escalation, and Follow-up recommendations.`,
      
      lab_interpreter: `Analyze laboratory results with: Reference range comparisons, Clinical significance of abnormal values, Possible causes of abnormalities, Additional testing recommendations, Trending analysis if applicable, and Clinical correlation with symptoms.`,
      
      treatment_options: `Provide evidence-based treatment recommendations including: First-line treatment options, Alternative therapies, Expected outcomes and timelines, Potential side effects and risks, Monitoring requirements, and Lifestyle modifications.`,
      
      medication_guide: `Create comprehensive medication analysis with: Mechanism of action, Proper dosing and administration, Drug interactions and contraindications, Side effect profile, Monitoring parameters, and Patient education points.`,
      
      health_screening: `Develop personalized screening recommendations including: Age-appropriate screenings, Risk-based additional tests, Screening intervals and schedules, Preparation instructions, Cost considerations, and Follow-up protocols.`,
      
      diabetes_management: `Create diabetes care plan with: Blood glucose monitoring protocols, Medication optimization, Dietary recommendations, Exercise prescriptions, Complication screening, and Emergency management plans.`,
      
      pubmed_search: `Conduct medical literature review including: Current research findings, Evidence quality assessment, Clinical applicability, Conflicting studies analysis, Research gaps identification, and Clinical recommendations.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are a board-certified physician and medical expert. ${prompts[toolId] || 'Provide comprehensive medical analysis and evidence-based recommendations.'} 

Patient Information:
- Age: ${healthData.age || 'Not specified'}
- Gender: ${healthData.gender || 'Not specified'}
- Primary Symptoms: ${healthData.symptoms || 'Not specified'}
- Medical History: ${healthData.medicalHistory || 'Not specified'}
- Current Medications: ${healthData.medications || 'Not specified'}
- Allergies: ${healthData.allergies || 'Not specified'}
- Lifestyle Factors: ${healthData.lifestyle || 'Not specified'}
- Vital Signs: ${healthData.vitals || 'Not specified'}
- Symptom Duration: ${healthData.duration || 'Not specified'}

IMPORTANT MEDICAL DISCLAIMERS:
1. This analysis is for educational and informational purposes only
2. Does not constitute medical advice, diagnosis, or treatment
3. Not a substitute for professional medical consultation
4. Emergency symptoms require immediate medical attention
5. Always consult qualified healthcare providers for medical decisions

Requirements:
1. Use evidence-based medical guidelines and current standards of care
2. Provide differential diagnoses with probability estimates
3. Include both common and serious conditions in consideration
4. Specify when immediate medical attention is required
5. Format as professional medical assessment
6. Include patient education and self-care guidance
7. Reference relevant medical literature when applicable
8. Emphasize the importance of professional medical evaluation

Generate comprehensive medical analysis that prioritizes patient safety and evidence-based care.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `healthcare_${toolId}_${Date.now()}`,
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
            <title>Medical Analysis - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 3px solid #e74c3c; padding-bottom: 15px; }
              .patient-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #e74c3c; }
              .diagnosis-box { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #ffeaa7; }
              .emergency-warning { background: #f8d7da; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #dc3545; color: #721c24; font-weight: bold; }
              .treatment-box { background: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #c3e6cb; }
              .prevention-box { background: #cce5ff; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #80bdff; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #e74c3c; color: white; }
              .probability { font-weight: bold; color: #007bff; }
              .medical-disclaimer { background: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #dc3545; font-size: 0.9em; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="patient-info">
              <strong>Patient Information:</strong><br>
              Age: ${healthData.age || 'Not specified'} | Gender: ${healthData.gender || 'Not specified'}<br>
              <strong>Symptoms:</strong> ${healthData.symptoms || 'Not specified'}<br>
              <strong>Duration:</strong> ${healthData.duration || 'Not specified'}<br>
              <strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <div class="medical-disclaimer">
              <strong>🚨 IMPORTANT MEDICAL DISCLAIMER:</strong><br>
              This analysis is for educational purposes only and does not constitute medical advice, diagnosis, or treatment. 
              It is not a substitute for professional medical consultation. If you are experiencing a medical emergency, 
              call 911 immediately. Always consult with qualified healthcare providers for medical decisions and treatment plans.
            </div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #e74c3c; color: white; border: none; border-radius: 4px;">Print Analysis</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating healthcare analysis:', error)
      setAnalysisResult('Error generating medical analysis. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="healthcare-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="healthcare-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="healthcare-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-health-btn"
                onClick={() => generateHealthAnalysis(tool.id)}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? '⏳ Analyzing...' : '🩺 Generate Analysis'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="healthcare-tools">
      <div className="healthcare-header">
        <h1>🏥 Healthcare & Medical Diagnosis</h1>
        <p>AI-powered medical analysis and healthcare decision support tools</p>
        <div className="medical-disclaimer">
          <strong>⚠️ Medical Disclaimer:</strong> These tools are for educational purposes only and do not replace professional medical advice. 
          Always consult healthcare providers for medical decisions. In emergencies, call 911 immediately.
        </div>
      </div>

      <div className="healthcare-form">
        <h3>Patient Information</h3>
        <div className="form-grid">
          <input
            type="text"
            placeholder="Age"
            value={healthData.age}
            onChange={(e) => setHealthData({...healthData, age: e.target.value})}
          />
          <select
            value={healthData.gender}
            onChange={(e) => setHealthData({...healthData, gender: e.target.value})}
          >
            <option value="">Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
            <option value="prefer-not-to-say">Prefer not to say</option>
          </select>
          <textarea
            placeholder="Primary Symptoms (describe in detail)"
            value={healthData.symptoms}
            onChange={(e) => setHealthData({...healthData, symptoms: e.target.value})}
            style={{gridColumn: 'span 2', height: '80px', resize: 'vertical'}}
          />
          <textarea
            placeholder="Medical History (conditions, surgeries, etc.)"
            value={healthData.medicalHistory}
            onChange={(e) => setHealthData({...healthData, medicalHistory: e.target.value})}
            style={{gridColumn: 'span 2', height: '60px', resize: 'vertical'}}
          />
          <input
            type="text"
            placeholder="Current Medications"
            value={healthData.medications}
            onChange={(e) => setHealthData({...healthData, medications: e.target.value})}
          />
          <input
            type="text"
            placeholder="Known Allergies"
            value={healthData.allergies}
            onChange={(e) => setHealthData({...healthData, allergies: e.target.value})}
          />
          <input
            type="text"
            placeholder="Lifestyle Factors (smoking, alcohol, exercise)"
            value={healthData.lifestyle}
            onChange={(e) => setHealthData({...healthData, lifestyle: e.target.value})}
          />
          <input
            type="text"
            placeholder="Vital Signs (BP, HR, temp if known)"
            value={healthData.vitals}
            onChange={(e) => setHealthData({...healthData, vitals: e.target.value})}
          />
          <select
            value={healthData.duration}
            onChange={(e) => setHealthData({...healthData, duration: e.target.value})}
          >
            <option value="">Symptom Duration</option>
            <option value="less-than-1-day">Less than 1 day</option>
            <option value="1-3-days">1-3 days</option>
            <option value="4-7-days">4-7 days</option>
            <option value="1-2-weeks">1-2 weeks</option>
            <option value="2-4-weeks">2-4 weeks</option>
            <option value="1-3-months">1-3 months</option>
            <option value="over-3-months">Over 3 months</option>
            <option value="chronic-ongoing">Chronic/Ongoing</option>
          </select>
        </div>
      </div>

      <div className="healthcare-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`healthcare-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="healthcare-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default HealthcareTools