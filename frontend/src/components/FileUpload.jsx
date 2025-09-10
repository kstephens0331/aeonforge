import React, { useState, useRef, useCallback } from 'react'

function FileUpload({ 
  onFilesSelected, 
  maxFiles = 50, 
  acceptedTypes = "*/*",
  context = "general",
  disabled = false 
}) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState([])
  const fileInputRef = useRef(null)

  const getContextConfig = () => {
    switch (context) {
      case 'chat':
        return {
          title: "Upload Files for Analysis",
          description: "Upload documents, images, code files, or data for AI analysis",
          acceptedTypes: "*/*",
          maxSize: "10MB per file",
          examples: "PDFs, images, documents, code files, spreadsheets, etc."
        }
      case 'projects':
        return {
          title: "Upload Project Files",
          description: "Upload requirements documents, designs, or reference materials",
          acceptedTypes: ".pdf,.doc,.docx,.txt,.md,.jpg,.png,.zip",
          maxSize: "25MB per file",
          examples: "Requirements docs, wireframes, specs, reference materials"
        }
      case 'medical':
        return {
          title: "Upload Medical Documents",
          description: "Upload research papers, clinical data, or medical images",
          acceptedTypes: ".pdf,.doc,.docx,.txt,.dcm,.jpg,.png,.csv,.xlsx",
          maxSize: "50MB per file",
          examples: "Research papers, clinical studies, medical images, data files"
        }
      default:
        return {
          title: "Upload Files",
          description: "Select files to upload",
          acceptedTypes: "*/*",
          maxSize: "10MB per file",
          examples: "Various file types supported"
        }
    }
  }

  const config = getContextConfig()

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const validateFile = (file) => {
    const maxSizeMap = {
      'chat': 10 * 1024 * 1024,     // 10MB
      'projects': 25 * 1024 * 1024,  // 25MB
      'medical': 50 * 1024 * 1024    // 50MB
    }
    
    const maxSize = maxSizeMap[context] || 10 * 1024 * 1024
    
    if (file.size > maxSize) {
      return `File "${file.name}" is too large. Maximum size is ${config.maxSize}`
    }
    
    return null
  }

  const processFiles = (files) => {
    const fileArray = Array.from(files)
    const errors = []
    const validFiles = []

    // Check file count
    if (selectedFiles.length + fileArray.length > maxFiles) {
      errors.push(`Cannot upload more than ${maxFiles} files at once. Currently selected: ${selectedFiles.length}`)
      return { validFiles: [], errors }
    }

    // Validate each file
    fileArray.forEach(file => {
      const error = validateFile(file)
      if (error) {
        errors.push(error)
      } else {
        validFiles.push({
          id: Date.now() + Math.random(),
          file: file,
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified,
          uploadStatus: 'ready'
        })
      }
    })

    return { validFiles, errors }
  }

  const handleFiles = (files) => {
    const { validFiles, errors } = processFiles(files)
    
    if (errors.length > 0) {
      alert(errors.join('\n'))
    }

    if (validFiles.length > 0) {
      const newFiles = [...selectedFiles, ...validFiles]
      setSelectedFiles(newFiles)
      onFilesSelected(newFiles)
    }
  }

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (disabled) return

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files)
    }
  }, [disabled, selectedFiles])

  const handleChange = (e) => {
    e.preventDefault()
    if (disabled) return
    
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files)
    }
  }

  const removeFile = (fileId) => {
    const newFiles = selectedFiles.filter(f => f.id !== fileId)
    setSelectedFiles(newFiles)
    onFilesSelected(newFiles)
  }

  const clearAll = () => {
    setSelectedFiles([])
    onFilesSelected([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const openFileDialog = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  const getFileIcon = (type) => {
    if (type.startsWith('image/')) return '🖼️'
    if (type.startsWith('video/')) return '🎥'
    if (type.startsWith('audio/')) return '🎵'
    if (type.includes('pdf')) return '📄'
    if (type.includes('word') || type.includes('document')) return '📝'
    if (type.includes('spreadsheet') || type.includes('excel')) return '📊'
    if (type.includes('presentation')) return '📋'
    if (type.includes('text')) return '📄'
    if (type.includes('zip') || type.includes('archive')) return '🗜️'
    return '📎'
  }

  return (
    <div className="file-upload-container">
      {/* Upload Area */}
      <div
        className={`file-upload-area ${dragActive ? 'drag-active' : ''} ${disabled ? 'disabled' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes}
          onChange={handleChange}
          style={{ display: 'none' }}
          disabled={disabled}
        />
        
        <div className="upload-content">
          <div className="upload-icon">📎</div>
          <div className="upload-text">
            <h4>{config.title}</h4>
            <p>{config.description}</p>
            <div className="upload-specs">
              <span>Max {maxFiles} files • {config.maxSize}</span>
              <span className="upload-examples">{config.examples}</span>
            </div>
          </div>
          <button 
            type="button" 
            className="upload-button"
            disabled={disabled}
          >
            {dragActive ? 'Drop files here' : 'Choose Files'}
          </button>
        </div>
      </div>

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <div className="files-header">
            <h4>Selected Files ({selectedFiles.length}/{maxFiles})</h4>
            <button 
              type="button" 
              className="clear-all-btn"
              onClick={clearAll}
              disabled={disabled}
            >
              Clear All
            </button>
          </div>
          
          <div className="files-list">
            {selectedFiles.map((fileObj) => (
              <div key={fileObj.id} className="file-item">
                <div className="file-info">
                  <span className="file-icon">{getFileIcon(fileObj.type)}</span>
                  <div className="file-details">
                    <div className="file-name">{fileObj.name}</div>
                    <div className="file-meta">
                      {formatFileSize(fileObj.size)} • {fileObj.type || 'Unknown type'}
                    </div>
                  </div>
                </div>
                
                <div className="file-actions">
                  <span className={`upload-status ${fileObj.uploadStatus}`}>
                    {fileObj.uploadStatus === 'ready' && '⏳'}
                    {fileObj.uploadStatus === 'uploading' && '📤'}
                    {fileObj.uploadStatus === 'complete' && '✅'}
                    {fileObj.uploadStatus === 'error' && '❌'}
                  </span>
                  <button
                    type="button"
                    className="remove-file-btn"
                    onClick={() => removeFile(fileObj.id)}
                    disabled={disabled}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Progress/Status */}
      {selectedFiles.some(f => f.uploadStatus === 'uploading') && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
          <span className="progress-text">Uploading files...</span>
        </div>
      )}
    </div>
  )
}

export default FileUpload