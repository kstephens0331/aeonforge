import React, { useState, useEffect } from 'react'
import axios from 'axios'
import FileUpload from './FileUpload'

function ProjectsTab({ serverInfo }) {
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(null)
  const [showNewProjectForm, setShowNewProjectForm] = useState(false)
  const [newProject, setNewProject] = useState({
    name: '',
    type: 'web-app',
    description: '',
    requirements: '',
    timeline: '1-2 weeks',
    files: []
  })

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = () => {
    // Load projects from localStorage for now
    const saved = localStorage.getItem('aeonforge-projects')
    if (saved) {
      setProjects(JSON.parse(saved))
    }
  }

  const saveProjects = (updatedProjects) => {
    setProjects(updatedProjects)
    localStorage.setItem('aeonforge-projects', JSON.stringify(updatedProjects))
  }

  const createProject = () => {
    const project = {
      id: Date.now().toString(),
      ...newProject,
      status: 'planning',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      files: [],
      tasks: []
    }

    const updatedProjects = [project, ...projects]
    saveProjects(updatedProjects)
    setShowNewProjectForm(false)
    setNewProject({
      name: '',
      type: 'web-app',
      description: '',
      requirements: '',
      timeline: '1-2 weeks',
      files: []
    })
    setSelectedProject(project)
  }

  const updateProject = (projectId, updates) => {
    const updatedProjects = projects.map(p => 
      p.id === projectId 
        ? { ...p, ...updates, updatedAt: new Date().toISOString() }
        : p
    )
    saveProjects(updatedProjects)
    if (selectedProject?.id === projectId) {
      setSelectedProject({ ...selectedProject, ...updates })
    }
  }

  const deleteProject = (projectId) => {
    const updatedProjects = projects.filter(p => p.id !== projectId)
    saveProjects(updatedProjects)
    if (selectedProject?.id === projectId) {
      setSelectedProject(null)
    }
  }

  const generateProject = async (project) => {
    try {
      updateProject(project.id, { status: 'generating' })
      
      // Prepare form data for file upload
      const formData = new FormData()
      let message = `Create a ${project.type}: ${project.name}. ${project.description}. Requirements: ${project.requirements}`
      
      if (project.files && project.files.length > 0) {
        const filesList = project.files.map(f => `📎 ${f.name} (${(f.size / 1024 / 1024).toFixed(2)} MB)`).join('\n')
        message += `\n\nProject Files:\n${filesList}`
        
        // Add files to form data
        project.files.forEach((fileObj, index) => {
          formData.append(`file_${index}`, fileObj.file)
        })
        formData.append('file_count', project.files.length.toString())
      } else {
        formData.append('file_count', '0')
      }
      
      formData.append('message', message)
      formData.append('conversation_id', `project_${project.id}`)
      formData.append('model', serverInfo.default_model || 'gpt-3.5-turbo')

      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/chat`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.needs_approval) {
        updateProject(project.id, { 
          status: 'awaiting_approval',
          generationResponse: response.data
        })
      } else {
        updateProject(project.id, { 
          status: 'completed',
          generationResponse: response.data
        })
      }
    } catch (error) {
      console.error('Error generating project:', error)
      updateProject(project.id, { status: 'error' })
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'planning': return '#3b82f6'
      case 'generating': return '#f59e0b'
      case 'awaiting_approval': return '#8b5cf6'
      case 'completed': return '#10b981'
      case 'error': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'planning': return '📋'
      case 'generating': return '⚡'
      case 'awaiting_approval': return '⏳'
      case 'completed': return '✅'
      case 'error': return '❌'
      default: return '📁'
    }
  }

  return (
    <div className="projects-tab">
      {/* Header */}
      <div className="projects-header">
        <div className="header-content">
          <h1>Project Management</h1>
          <p>AI-powered development project planning and execution</p>
        </div>
        <button 
          className="new-project-btn"
          onClick={() => setShowNewProjectForm(true)}
        >
          ➕ New Project
        </button>
      </div>

      <div className="projects-layout">
        {/* Project List */}
        <div className="projects-list">
          <h3>Projects ({projects.length})</h3>
          
          {projects.length === 0 ? (
            <div className="empty-state">
              <p>No projects yet</p>
              <button 
                className="create-first-project"
                onClick={() => setShowNewProjectForm(true)}
              >
                Create your first project
              </button>
            </div>
          ) : (
            <div className="project-items">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className={`project-item ${selectedProject?.id === project.id ? 'selected' : ''}`}
                  onClick={() => setSelectedProject(project)}
                >
                  <div className="project-header">
                    <div className="project-title">
                      <span className="project-icon">{getStatusIcon(project.status)}</span>
                      {project.name}
                    </div>
                    <div 
                      className="project-status"
                      style={{ color: getStatusColor(project.status) }}
                    >
                      {project.status.replace('_', ' ')}
                    </div>
                  </div>
                  <div className="project-meta">
                    <span className="project-type">{project.type.replace('-', ' ')}</span>
                    <span className="project-date">
                      {new Date(project.updatedAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Project Details */}
        <div className="project-details">
          {selectedProject ? (
            <div className="project-detail-content">
              <div className="detail-header">
                <div className="detail-title">
                  <h2>{selectedProject.name}</h2>
                  <div 
                    className="detail-status"
                    style={{ backgroundColor: getStatusColor(selectedProject.status) }}
                  >
                    {getStatusIcon(selectedProject.status)} {selectedProject.status.replace('_', ' ')}
                  </div>
                </div>
                
                <div className="detail-actions">
                  {selectedProject.status === 'planning' && (
                    <button 
                      className="generate-btn"
                      onClick={() => generateProject(selectedProject)}
                    >
                      🚀 Generate Project
                    </button>
                  )}
                  <button 
                    className="delete-btn"
                    onClick={() => deleteProject(selectedProject.id)}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>

              <div className="detail-sections">
                <div className="detail-section">
                  <h4>Description</h4>
                  <p>{selectedProject.description || 'No description provided'}</p>
                </div>

                <div className="detail-section">
                  <h4>Project Type</h4>
                  <p>{selectedProject.type.replace('-', ' ')}</p>
                </div>

                <div className="detail-section">
                  <h4>Requirements</h4>
                  <pre>{selectedProject.requirements || 'No specific requirements'}</pre>
                </div>

                <div className="detail-section">
                  <h4>Timeline</h4>
                  <p>{selectedProject.timeline}</p>
                </div>

                {selectedProject.files && selectedProject.files.length > 0 && (
                  <div className="detail-section">
                    <h4>Project Files ({selectedProject.files.length})</h4>
                    <div className="project-files-list">
                      {selectedProject.files.map((fileObj) => (
                        <div key={fileObj.id} className="project-file-item">
                          <span className="file-icon">
                            {fileObj.type.startsWith('image/') ? '🖼️' :
                             fileObj.type.includes('pdf') ? '📄' :
                             fileObj.type.includes('text') ? '📄' :
                             fileObj.type.includes('zip') ? '🗜️' : '📎'}
                          </span>
                          <div className="file-info">
                            <div className="file-name">{fileObj.name}</div>
                            <div className="file-meta">
                              {(fileObj.size / 1024 / 1024).toFixed(2)} MB • {fileObj.type}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedProject.generationResponse && (
                  <div className="detail-section">
                    <h4>AI Generation Result</h4>
                    <div 
                      className="generation-response"
                      dangerouslySetInnerHTML={{ 
                        __html: selectedProject.generationResponse.message
                          .replace(/\n/g, '<br />')
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') 
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="no-project-selected">
              <h3>Select a project to view details</h3>
              <p>Choose a project from the list to see its details and manage it</p>
            </div>
          )}
        </div>
      </div>

      {/* New Project Modal */}
      {showNewProjectForm && (
        <div className="modal-overlay" onClick={() => setShowNewProjectForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Project</h3>
              <button 
                className="close-modal"
                onClick={() => setShowNewProjectForm(false)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Project Name</label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                  placeholder="Enter project name"
                />
              </div>

              <div className="form-group">
                <label>Upload Project Files (Optional)</label>
                <FileUpload
                  onFilesSelected={(files) => setNewProject({...newProject, files: files})}
                  maxFiles={50}
                  context="projects"
                  disabled={false}
                />
              </div>

              <div className="form-group">
                <label>Project Type</label>
                <select
                  value={newProject.type}
                  onChange={(e) => setNewProject({...newProject, type: e.target.value})}
                >
                  <option value="web-app">Web Application</option>
                  <option value="mobile-app">Mobile Application</option>
                  <option value="desktop-app">Desktop Application</option>
                  <option value="api">REST API</option>
                  <option value="cli-tool">CLI Tool</option>
                  <option value="library">Library/Package</option>
                  <option value="script">Script/Automation</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                  placeholder="Describe what this project should do"
                  rows={3}
                />
              </div>

              <div className="form-group">
                <label>Requirements</label>
                <textarea
                  value={newProject.requirements}
                  onChange={(e) => setNewProject({...newProject, requirements: e.target.value})}
                  placeholder="List specific features, technologies, or constraints"
                  rows={4}
                />
              </div>

              <div className="form-group">
                <label>Timeline</label>
                <select
                  value={newProject.timeline}
                  onChange={(e) => setNewProject({...newProject, timeline: e.target.value})}
                >
                  <option value="1-2 days">1-2 days</option>
                  <option value="1 week">1 week</option>
                  <option value="1-2 weeks">1-2 weeks</option>
                  <option value="1 month">1 month</option>
                  <option value="2-3 months">2-3 months</option>
                  <option value="6+ months">6+ months</option>
                </select>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="cancel-btn"
                onClick={() => setShowNewProjectForm(false)}
              >
                Cancel
              </button>
              <button 
                className="create-btn"
                onClick={createProject}
                disabled={!newProject.name.trim()}
              >
                Create Project
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectsTab