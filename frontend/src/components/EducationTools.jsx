import React, { useState } from 'react'
import axios from 'axios'

function EducationTools({ serverInfo, user, authToken }) {
  const [activeSection, setActiveSection] = useState('curriculum')
  const [educationData, setEducationData] = useState({
    subject: '',
    gradeLevel: '',
    studentCount: '',
    duration: '',
    objectives: '',
    standards: '',
    resources: '',
    assessmentType: '',
    learningStyle: ''
  })
  const [isGenerating, setIsGenerating] = useState(false)
  const [educationResult, setEducationResult] = useState('')

  const sections = {
    curriculum: {
      title: 'Curriculum Development',
      icon: '📚',
      tools: [
        { id: 'lesson_plans', name: 'Lesson Plan Generator', description: 'Complete lesson plans with objectives and activities' },
        { id: 'curriculum_mapping', name: 'Curriculum Mapping', description: 'Standards-aligned curriculum sequences' },
        { id: 'scope_sequence', name: 'Scope & Sequence', description: 'Year-long planning and pacing guides' },
        { id: 'unit_plans', name: 'Unit Plan Development', description: 'Multi-week thematic unit planning' },
        { id: 'learning_objectives', name: 'Learning Objectives', description: 'Bloom\'s taxonomy aligned objectives' },
        { id: 'differentiation', name: 'Differentiated Instruction', description: 'Multi-level learning accommodations' }
      ]
    },
    assessment: {
      title: 'Assessment & Evaluation',
      icon: '📝',
      tools: [
        { id: 'quiz_generator', name: 'Quiz & Test Generator', description: 'Multiple choice, short answer, and essay questions' },
        { id: 'rubric_creator', name: 'Rubric Creator', description: 'Performance-based assessment rubrics' },
        { id: 'formative_assessment', name: 'Formative Assessment', description: 'Real-time learning check strategies' },
        { id: 'portfolio_assessment', name: 'Portfolio Assessment', description: 'Student work collection and evaluation' },
        { id: 'grade_calculator', name: 'Grade Calculator', description: 'Weighted grades and progress tracking' },
        { id: 'feedback_generator', name: 'Feedback Generator', description: 'Constructive student feedback templates' }
      ]
    },
    resources: {
      title: 'Educational Resources',
      icon: '🎯',
      tools: [
        { id: 'worksheet_generator', name: 'Worksheet Generator', description: 'Practice sheets and activity pages' },
        { id: 'presentation_creator', name: 'Presentation Creator', description: 'Interactive slide presentations' },
        { id: 'activity_planner', name: 'Activity Planner', description: 'Hands-on learning experiences' },
        { id: 'game_creator', name: 'Educational Games', description: 'Learning games and interactive activities' },
        { id: 'video_scripts', name: 'Video Scripts', description: 'Educational video content planning' },
        { id: 'reading_lists', name: 'Reading Lists', description: 'Age-appropriate book recommendations' }
      ]
    },
    technology: {
      title: 'Educational Technology',
      icon: '💻',
      tools: [
        { id: 'lms_setup', name: 'LMS Course Setup', description: 'Learning management system configuration' },
        { id: 'online_course', name: 'Online Course Builder', description: 'Digital learning experience design' },
        { id: 'virtual_classroom', name: 'Virtual Classroom', description: 'Remote learning environment setup' },
        { id: 'interactive_content', name: 'Interactive Content', description: 'Multimedia learning materials' },
        { id: 'ai_tutoring', name: 'AI Tutoring System', description: 'Personalized learning assistance' },
        { id: 'learning_analytics', name: 'Learning Analytics', description: 'Student progress data analysis' }
      ]
    },
    special: {
      title: 'Special Education',
      icon: '🌟',
      tools: [
        { id: 'iep_planning', name: 'IEP Planning', description: 'Individualized Education Program development' },
        { id: 'accommodation_plans', name: 'Accommodation Plans', description: 'Learning disability support strategies' },
        { id: 'behavior_plans', name: 'Behavior Intervention', description: 'Positive behavior support systems' },
        { id: 'adaptive_materials', name: 'Adaptive Materials', description: 'Modified learning resources' },
        { id: 'progress_monitoring', name: 'Progress Monitoring', description: 'Special needs student tracking' },
        { id: 'transition_planning', name: 'Transition Planning', description: 'Post-secondary preparation support' }
      ]
    },
    professional: {
      title: 'Professional Development',
      icon: '🎓',
      tools: [
        { id: 'teacher_training', name: 'Teacher Training', description: 'Professional development programs' },
        { id: 'classroom_management', name: 'Classroom Management', description: 'Behavior and environment strategies' },
        { id: 'parent_communication', name: 'Parent Communication', description: 'Family engagement strategies' },
        { id: 'research_projects', name: 'Action Research', description: 'Classroom-based research design' },
        { id: 'conference_planning', name: 'Conference Planning', description: 'Educational event organization' },
        { id: 'grant_writing', name: 'Education Grant Writing', description: 'Funding proposal development' }
      ]
    }
  }

  const generateEducationContent = async (toolId) => {
    setIsGenerating(true)

    const prompts = {
      lesson_plans: `Create a comprehensive lesson plan for ${educationData.subject || 'the specified subject'} at ${educationData.gradeLevel || 'grade level'}. Include: Learning Objectives (aligned with standards), Materials List, Lesson Introduction/Hook, Step-by-Step Activities, Differentiation Strategies, Assessment Methods, Closure/Summary, and Extension Activities.`,
      
      curriculum_mapping: `Develop curriculum mapping for ${educationData.subject || 'the subject area'} including: Standards Alignment, Essential Questions, Key Concepts and Skills, Assessment Strategies, Timeline and Pacing, Cross-curricular Connections, and Resource Requirements.`,
      
      quiz_generator: `Generate a comprehensive assessment with: Multiple Choice Questions (with distractors), Short Answer Questions, Essay Prompts, Performance Tasks, Answer Key with Explanations, Scoring Rubric, and Differentiated Versions for various ability levels.`,
      
      rubric_creator: `Create detailed assessment rubrics with: Performance Criteria, Proficiency Levels (Exemplary, Proficient, Developing, Beginning), Specific Descriptors, Point Values, and Student-Friendly Language versions.`,
      
      worksheet_generator: `Design educational worksheets including: Clear Instructions, Varied Question Types, Progressive Difficulty Levels, Answer Keys, Extension Activities, and Accommodation Suggestions for diverse learners.`,
      
      iep_planning: `Develop IEP components including: Present Levels of Performance, Measurable Annual Goals, Short-term Objectives, Special Education Services, Related Services, Accommodations and Modifications, and Transition Services.`,
      
      online_course: `Create online course structure with: Course Overview and Objectives, Module Breakdown, Interactive Elements, Multimedia Content Plan, Assessment Strategy, Discussion Forums, and Technical Requirements.`,
      
      classroom_management: `Develop classroom management plan including: Physical Environment Setup, Behavioral Expectations, Routine and Procedures, Positive Reinforcement Systems, Consequence Hierarchy, and Parent Communication Strategies.`,
      
      // Add more prompts for other tools...
    }

    const prompt = `You are an experienced educator and curriculum specialist. ${prompts[toolId] || 'Create comprehensive educational materials and strategies.'} 

Educational Context:
- Subject/Topic: ${educationData.subject || 'Not specified'}
- Grade Level: ${educationData.gradeLevel || 'Not specified'}
- Number of Students: ${educationData.studentCount || 'Not specified'}
- Duration: ${educationData.duration || 'Not specified'}
- Learning Objectives: ${educationData.objectives || 'Not specified'}
- Standards: ${educationData.standards || 'Not specified'}
- Available Resources: ${educationData.resources || 'Not specified'}
- Assessment Type: ${educationData.assessmentType || 'Not specified'}
- Learning Styles: ${educationData.learningStyle || 'Not specified'}

Requirements:
1. Use evidence-based educational practices
2. Align with current educational standards (Common Core, NGSS, etc.)
3. Include differentiation for diverse learners
4. Provide clear, actionable implementation steps
5. Format for immediate classroom use
6. Include assessment and evaluation methods
7. Consider 21st-century learning skills
8. Incorporate technology integration where appropriate

Create professional-quality educational materials that enhance student learning and achievement.`

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, {
        message: prompt,
        conversation_id: `education_${toolId}_${Date.now()}`,
        model: 'gpt-3.5-turbo'
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      })

      setEducationResult(response.data.response)
      
      // Open content in new window
      const newWindow = window.open()
      newWindow.document.write(`
        <html>
          <head>
            <title>Educational Resource - ${toolId.replace('_', ' ').toUpperCase()}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
              h1, h2, h3 { color: #2c3e50; }
              h1 { text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 15px; }
              .lesson-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #3498db; }
              .objective-box { background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .activity-section { background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; }
              .assessment-box { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #ffeaa7; }
              .differentiation-box { background: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #c3e6cb; }
              table { border-collapse: collapse; width: 100%; margin: 20px 0; }
              th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
              th { background-color: #3498db; color: white; }
              .standards-note { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; font-style: italic; }
              @media print { body { padding: 20px; } .no-print { display: none; } }
            </style>
          </head>
          <body>
            <div class="lesson-info">
              <strong>Subject:</strong> ${educationData.subject || 'Not specified'}<br>
              <strong>Grade Level:</strong> ${educationData.gradeLevel || 'Not specified'}<br>
              <strong>Duration:</strong> ${educationData.duration || 'Not specified'}<br>
              <strong>Students:</strong> ${educationData.studentCount || 'Not specified'}<br>
              <strong>Created:</strong> ${new Date().toLocaleDateString()}
            </div>
            <div style="white-space: pre-wrap;">${response.data.response}</div>
            <button onclick="window.print()" class="no-print" style="position: fixed; top: 10px; right: 10px; padding: 10px; background: #3498db; color: white; border: none; border-radius: 4px;">Print Resource</button>
          </body>
        </html>
      `)

    } catch (error) {
      console.error('Error generating educational content:', error)
      setEducationResult('Error generating educational content. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const renderSection = () => {
    const section = sections[activeSection]
    
    return (
      <div className="education-section">
        <h3>{section.icon} {section.title}</h3>
        <div className="education-tools-grid">
          {section.tools.map((tool) => (
            <div key={tool.id} className="education-tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <button
                className="generate-education-btn"
                onClick={() => generateEducationContent(tool.id)}
                disabled={isGenerating}
              >
                {isGenerating ? '⏳ Generating...' : '📚 Generate Resource'}
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="education-tools">
      <div className="education-header">
        <h1>🎓 Education & Curriculum Development</h1>
        <p>Comprehensive educational planning, assessment, and resource creation tools</p>
      </div>

      <div className="education-form">
        <h3>Educational Context</h3>
        <div className="form-grid">
          <input
            type="text"
            placeholder="Subject/Topic"
            value={educationData.subject}
            onChange={(e) => setEducationData({...educationData, subject: e.target.value})}
          />
          <select
            value={educationData.gradeLevel}
            onChange={(e) => setEducationData({...educationData, gradeLevel: e.target.value})}
          >
            <option value="">Grade Level</option>
            <option value="pre-k">Pre-K</option>
            <option value="kindergarten">Kindergarten</option>
            <option value="1st-grade">1st Grade</option>
            <option value="2nd-grade">2nd Grade</option>
            <option value="3rd-grade">3rd Grade</option>
            <option value="4th-grade">4th Grade</option>
            <option value="5th-grade">5th Grade</option>
            <option value="6th-grade">6th Grade</option>
            <option value="7th-grade">7th Grade</option>
            <option value="8th-grade">8th Grade</option>
            <option value="9th-grade">9th Grade</option>
            <option value="10th-grade">10th Grade</option>
            <option value="11th-grade">11th Grade</option>
            <option value="12th-grade">12th Grade</option>
            <option value="college">College</option>
            <option value="adult-ed">Adult Education</option>
          </select>
          <input
            type="text"
            placeholder="Number of Students"
            value={educationData.studentCount}
            onChange={(e) => setEducationData({...educationData, studentCount: e.target.value})}
          />
          <select
            value={educationData.duration}
            onChange={(e) => setEducationData({...educationData, duration: e.target.value})}
          >
            <option value="">Duration</option>
            <option value="30-minutes">30 minutes</option>
            <option value="45-minutes">45 minutes</option>
            <option value="1-hour">1 hour</option>
            <option value="90-minutes">90 minutes</option>
            <option value="1-week">1 week</option>
            <option value="2-weeks">2 weeks</option>
            <option value="1-month">1 month</option>
            <option value="semester">Semester</option>
            <option value="year">Full year</option>
          </select>
          <textarea
            placeholder="Learning Objectives"
            value={educationData.objectives}
            onChange={(e) => setEducationData({...educationData, objectives: e.target.value})}
            style={{gridColumn: 'span 2', height: '60px', resize: 'vertical'}}
          />
          <input
            type="text"
            placeholder="Standards (Common Core, NGSS, etc.)"
            value={educationData.standards}
            onChange={(e) => setEducationData({...educationData, standards: e.target.value})}
          />
          <input
            type="text"
            placeholder="Available Resources"
            value={educationData.resources}
            onChange={(e) => setEducationData({...educationData, resources: e.target.value})}
          />
          <select
            value={educationData.assessmentType}
            onChange={(e) => setEducationData({...educationData, assessmentType: e.target.value})}
          >
            <option value="">Assessment Type</option>
            <option value="formative">Formative</option>
            <option value="summative">Summative</option>
            <option value="diagnostic">Diagnostic</option>
            <option value="performance">Performance-based</option>
            <option value="portfolio">Portfolio</option>
            <option value="self-assessment">Self-assessment</option>
          </select>
          <select
            value={educationData.learningStyle}
            onChange={(e) => setEducationData({...educationData, learningStyle: e.target.value})}
          >
            <option value="">Primary Learning Style</option>
            <option value="visual">Visual</option>
            <option value="auditory">Auditory</option>
            <option value="kinesthetic">Kinesthetic</option>
            <option value="reading-writing">Reading/Writing</option>
            <option value="mixed">Mixed/Multiple</option>
          </select>
        </div>
      </div>

      <div className="education-navigation">
        {Object.entries(sections).map(([key, section]) => (
          <button
            key={key}
            className={`education-nav-btn ${activeSection === key ? 'active' : ''}`}
            onClick={() => setActiveSection(key)}
          >
            <span className="nav-icon">{section.icon}</span>
            <span className="nav-title">{section.title}</span>
          </button>
        ))}
      </div>

      <div className="education-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default EducationTools