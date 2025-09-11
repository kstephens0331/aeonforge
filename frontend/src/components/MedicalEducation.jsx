import React, { useState, useEffect } from 'react'
import axios from 'axios'
import FileUpload from './FileUpload'
import '../styles/fileupload.css'
import '../styles/medical-education.css'

function MedicalEducation({ serverInfo }) {
  const [activeTab, setActiveTab] = useState('upload')
  const [uploadedContent, setUploadedContent] = useState([])
  const [studySessions, setStudySessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [questions, setQuestions] = useState([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [userAnswer, setUserAnswer] = useState('')
  const [showAnswer, setShowAnswer] = useState(false)
  const [sessionName, setSessionName] = useState('')
  const [isGeneratingQuestions, setIsGeneratingQuestions] = useState(false)
  const [studyProgress, setStudyProgress] = useState({})

  useEffect(() => {
    loadStoredData()
  }, [])

  const loadStoredData = () => {
    const content = localStorage.getItem('medical-education-content')
    const sessions = localStorage.getItem('medical-education-sessions')
    const progress = localStorage.getItem('medical-education-progress')
    
    if (content) setUploadedContent(JSON.parse(content))
    if (sessions) setStudySessions(JSON.parse(sessions))
    if (progress) setStudyProgress(JSON.parse(progress))
  }

  const saveToStorage = () => {
    localStorage.setItem('medical-education-content', JSON.stringify(uploadedContent))
    localStorage.setItem('medical-education-sessions', JSON.stringify(studySessions))
    localStorage.setItem('medical-education-progress', JSON.stringify(studyProgress))
  }

  const handleContentUpload = (files) => {
    if (files.length > 0 && sessionName.trim()) {
      const newContent = {
        id: Date.now(),
        name: sessionName.trim(),
        files: files,
        uploadDate: new Date().toISOString(),
        studyCount: 0,
        lastStudied: null,
        topics: []
      }
      
      const updated = [...uploadedContent, newContent]
      setUploadedContent(updated)
      setSessionName('')
      saveToStorage()
      
      // Auto-switch to study tab
      setActiveTab('study')
    }
  }

  const generateQuestionsFromContent = async (content) => {
    setIsGeneratingQuestions(true)
    
    try {
      // Extract file content for analysis
      const fileContents = content.files.map(f => ({
        name: f.name,
        type: f.type,
        content: f.file ? 'File content would be processed here' : 'No content available'
      }))

      const prompt = `Based EXCLUSIVELY on the uploaded medical education materials titled "${content.name}", generate 10 comprehensive study questions. 

IMPORTANT RULES:
- Use ONLY information from the uploaded materials
- Do not add external medical knowledge
- Questions should test understanding, application, and critical thinking
- Include a mix of question types: multiple choice, short answer, and case-based
- For each question, provide the correct answer and explanation based solely on the uploaded content
- Reference specific sections or pages when possible

Uploaded Materials:
${fileContents.map(f => `File: ${f.name} (${f.type})`).join('\\n')}

Generate questions that help reinforce the key concepts from this specific content.`

      // Prepare form data for file upload
      const formData = new FormData()
      formData.append('content_name', content.name)
      formData.append('content_id', content.id.toString())
      formData.append('model', serverInfo.default_model || 'gpt-3.5-turbo')
      
      // Add files to form data
      content.files.forEach((fileObj, index) => {
        formData.append(`file_${index}`, fileObj.file)
      })
      formData.append('file_count', content.files.length.toString())

      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      // Use questions from backend response
      const parsedQuestions = response.data.questions || []
      
      setQuestions(parsedQuestions)
      setCurrentQuestionIndex(0)
      setShowAnswer(false)
      setUserAnswer('')
      
      // Create new study session
      const session = {
        id: Date.now(),
        contentId: content.id,
        contentName: content.name,
        questions: parsedQuestions,
        startTime: new Date().toISOString(),
        completed: false,
        score: 0,
        answers: []
      }
      
      setCurrentSession(session)
      setActiveTab('quiz')
      
    } catch (error) {
      console.error('Error generating questions:', error)
      alert('Error generating questions. Please try again.')
    } finally {
      setIsGeneratingQuestions(false)
    }
  }

  const parseQuestionsFromAI = (aiResponse, content) => {
    // Simple parsing - in production, this would be more sophisticated
    const questions = []
    const lines = aiResponse.split('\\n')
    let currentQuestion = null
    
    for (let line of lines) {
      if (line.match(/^\d+\./)) {
        if (currentQuestion) {
          questions.push(currentQuestion)
        }
        currentQuestion = {
          id: questions.length + 1,
          question: line.replace(/^\d+\./, '').trim(),
          type: 'short_answer',
          answer: '',
          explanation: '',
          userAnswer: '',
          correct: null
        }
      } else if (line.toLowerCase().includes('answer:') && currentQuestion) {
        currentQuestion.answer = line.replace(/answer:/i, '').trim()
      } else if (line.toLowerCase().includes('explanation:') && currentQuestion) {
        currentQuestion.explanation = line.replace(/explanation:/i, '').trim()
      }
    }
    
    if (currentQuestion) {
      questions.push(currentQuestion)
    }
    
    // Fallback questions if parsing fails
    if (questions.length === 0) {
      return [
        {
          id: 1,
          question: `What are the main topics covered in "${content.name}"?`,
          type: 'short_answer',
          answer: 'Based on the uploaded content, please review the key concepts.',
          explanation: 'This question tests your understanding of the overall material.',
          userAnswer: '',
          correct: null
        }
      ]
    }
    
    return questions.slice(0, 10) // Limit to 10 questions
  }

  const submitAnswer = () => {
    if (!currentSession || !questions[currentQuestionIndex]) return
    
    const currentQ = questions[currentQuestionIndex]
    const isCorrect = userAnswer.toLowerCase().trim().includes(currentQ.answer.toLowerCase().trim())
    
    // Update question with user's answer
    questions[currentQuestionIndex].userAnswer = userAnswer
    questions[currentQuestionIndex].correct = isCorrect
    
    // Update session answers
    currentSession.answers[currentQuestionIndex] = {
      question: currentQ.question,
      userAnswer: userAnswer,
      correctAnswer: currentQ.answer,
      correct: isCorrect
    }
    
    setShowAnswer(true)
    
    // Update score
    if (isCorrect) {
      currentSession.score += 1
    }
  }

  const nextQuestion = () => {
    setShowAnswer(false)
    setUserAnswer('')
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    } else {
      // Complete session
      completeSession()
    }
  }

  const completeSession = () => {
    if (!currentSession) return
    
    currentSession.completed = true
    currentSession.endTime = new Date().toISOString()
    currentSession.finalScore = `${currentSession.score}/${questions.length}`
    
    // Update study sessions
    const updatedSessions = [...studySessions, currentSession]
    setStudySessions(updatedSessions)
    
    // Update content study count
    const updatedContent = uploadedContent.map(content => 
      content.id === currentSession.contentId
        ? { ...content, studyCount: content.studyCount + 1, lastStudied: new Date().toISOString() }
        : content
    )
    setUploadedContent(updatedContent)
    
    // Update progress tracking
    const progress = studyProgress[currentSession.contentId] || { sessions: [], totalScore: 0, averageScore: 0 }
    progress.sessions.push({
      date: currentSession.startTime,
      score: currentSession.score,
      total: questions.length
    })
    progress.totalScore += currentSession.score
    progress.averageScore = progress.totalScore / progress.sessions.length
    
    setStudyProgress({
      ...studyProgress,
      [currentSession.contentId]: progress
    })
    
    saveToStorage()
    setActiveTab('results')
  }

  const deleteContent = (contentId) => {
    const updated = uploadedContent.filter(c => c.id !== contentId)
    setUploadedContent(updated)
    
    // Also remove related sessions and progress
    const filteredSessions = studySessions.filter(s => s.contentId !== contentId)
    setStudySessions(filteredSessions)
    
    const updatedProgress = { ...studyProgress }
    delete updatedProgress[contentId]
    setStudyProgress(updatedProgress)
    
    saveToStorage()
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="medical-education">
      {/* Header */}
      <div className="medical-header">
        <div className="header-content">
          <h1>📚 Medical Education Study Assistant</h1>
          <p>Upload your study materials and get personalized questions to reinforce learning</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="education-tabs">
        <button 
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📁 Upload Content
        </button>
        <button 
          className={`tab-button ${activeTab === 'study' ? 'active' : ''}`}
          onClick={() => setActiveTab('study')}
        >
          📖 Study Materials
        </button>
        <button 
          className={`tab-button ${activeTab === 'quiz' ? 'active' : ''}`}
          onClick={() => setActiveTab('quiz')}
          disabled={questions.length === 0}
        >
          ❓ Active Quiz
        </button>
        <button 
          className={`tab-button ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          📊 Results & Progress
        </button>
      </div>

      {/* Tab Content */}
      <div className="education-content">
        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="upload-tab">
            <div className="upload-section">
              <h3>Upload Study Materials</h3>
              <p>Upload your medical textbooks, notes, papers, or any study materials. AeonForge will generate questions based exclusively on your content.</p>
              
              <div className="session-name-input">
                <label>Study Session Name:</label>
                <input
                  type="text"
                  value={sessionName}
                  onChange={(e) => setSessionName(e.target.value)}
                  placeholder="e.g., 'Cardiology Chapter 5', 'Pharmacology Exam Prep'"
                />
              </div>
              
              <FileUpload
                onFilesSelected={handleContentUpload}
                maxFiles={10}
                context="medical"
                disabled={!sessionName.trim()}
              />
              
              {!sessionName.trim() && (
                <p className="warning-text">Please enter a session name before uploading files.</p>
              )}
            </div>
          </div>
        )}

        {/* Study Materials Tab */}
        {activeTab === 'study' && (
          <div className="study-tab">
            <h3>Your Study Materials</h3>
            
            {uploadedContent.length === 0 ? (
              <div className="empty-state">
                <p>No study materials uploaded yet.</p>
                <button onClick={() => setActiveTab('upload')}>Upload Your First Materials</button>
              </div>
            ) : (
              <div className="content-library">
                {uploadedContent.map((content) => (
                  <div key={content.id} className="content-card">
                    <div className="content-header">
                      <h4>{content.name}</h4>
                      <div className="content-actions">
                        <button
                          className="study-btn"
                          onClick={() => generateQuestionsFromContent(content)}
                          disabled={isGeneratingQuestions}
                        >
                          {isGeneratingQuestions ? '⏳ Generating...' : '🧠 Start Study Session'}
                        </button>
                        <button
                          className="delete-btn"
                          onClick={() => deleteContent(content.id)}
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                    
                    <div className="content-details">
                      <div className="content-stats">
                        <span>📁 {content.files.length} files</span>
                        <span>📅 {new Date(content.uploadDate).toLocaleDateString()}</span>
                        <span>🎓 {content.studyCount} study sessions</span>
                      </div>
                      
                      <div className="content-files">
                        {content.files.map((file, index) => (
                          <div key={index} className="file-item-small">
                            <span className="file-name">{file.name}</span>
                            <span className="file-size">({formatFileSize(file.size)})</span>
                          </div>
                        ))}
                      </div>
                      
                      {studyProgress[content.id] && (
                        <div className="progress-summary">
                          <span>Average Score: {studyProgress[content.id].averageScore.toFixed(1)}/10</span>
                          <span>Total Sessions: {studyProgress[content.id].sessions.length}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Quiz Tab */}
        {activeTab === 'quiz' && (
          <div className="quiz-tab">
            {questions.length === 0 ? (
              <div className="no-quiz">
                <p>No active quiz. Start a study session from your materials.</p>
                <button onClick={() => setActiveTab('study')}>Go to Study Materials</button>
              </div>
            ) : (
              <div className="quiz-interface">
                <div className="quiz-header">
                  <h3>{currentSession?.contentName}</h3>
                  <div className="quiz-progress">
                    Question {currentQuestionIndex + 1} of {questions.length}
                  </div>
                  <div className="quiz-score">
                    Score: {currentSession?.score || 0}/{questions.length}
                  </div>
                </div>
                
                <div className="question-card">
                  <div className="question-text">
                    <h4>Question {currentQuestionIndex + 1}:</h4>
                    <p>{questions[currentQuestionIndex]?.question}</p>
                  </div>
                  
                  <div className="answer-section">
                    <textarea
                      value={userAnswer}
                      onChange={(e) => setUserAnswer(e.target.value)}
                      placeholder="Enter your answer here..."
                      disabled={showAnswer}
                      rows={4}
                    />
                    
                    <div className="quiz-buttons">
                      {!showAnswer ? (
                        <button
                          onClick={submitAnswer}
                          disabled={!userAnswer.trim()}
                        >
                          Submit Answer
                        </button>
                      ) : (
                        <button onClick={nextQuestion}>
                          {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'Complete Quiz'}
                        </button>
                      )}
                    </div>
                  </div>
                  
                  {showAnswer && (
                    <div className={`answer-feedback ${questions[currentQuestionIndex]?.correct ? 'correct' : 'incorrect'}`}>
                      <h5>{questions[currentQuestionIndex]?.correct ? '✅ Correct!' : '❌ Needs Review'}</h5>
                      <p><strong>Expected Answer:</strong> {questions[currentQuestionIndex]?.answer}</p>
                      <p><strong>Explanation:</strong> {questions[currentQuestionIndex]?.explanation}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="results-tab">
            <h3>Study Results & Progress</h3>
            
            {studySessions.length === 0 ? (
              <div className="no-results">
                <p>No completed study sessions yet.</p>
                <button onClick={() => setActiveTab('study')}>Start Your First Study Session</button>
              </div>
            ) : (
              <div className="results-content">
                {/* Recent Session Results */}
                {currentSession && currentSession.completed && (
                  <div className="recent-session">
                    <h4>🎉 Session Complete!</h4>
                    <div className="session-summary">
                      <div className="score-display">
                        <span className="score">{currentSession.finalScore}</span>
                        <span className="percentage">
                          ({Math.round((currentSession.score / questions.length) * 100)}%)
                        </span>
                      </div>
                      <p>Study Material: {currentSession.contentName}</p>
                      <p>Time: {new Date(currentSession.startTime).toLocaleString()}</p>
                    </div>
                  </div>
                )}
                
                {/* Progress Overview */}
                <div className="progress-overview">
                  <h4>Overall Progress</h4>
                  {Object.entries(studyProgress).map(([contentId, progress]) => {
                    const content = uploadedContent.find(c => c.id === parseInt(contentId))
                    if (!content) return null
                    
                    return (
                      <div key={contentId} className="progress-item">
                        <h5>{content.name}</h5>
                        <div className="progress-stats">
                          <span>Sessions: {progress.sessions.length}</span>
                          <span>Avg Score: {progress.averageScore.toFixed(1)}/10</span>
                          <span>Best: {Math.max(...progress.sessions.map(s => s.score))}/10</span>
                        </div>
                        <div className="session-history">
                          {progress.sessions.slice(-5).map((session, index) => (
                            <div key={index} className="session-dot">
                              <span className={`dot ${session.score >= session.total * 0.7 ? 'good' : 'needs-work'}`}>
                                {session.score}/{session.total}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default MedicalEducation