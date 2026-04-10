# CIT Document Tracker - Complete Frontend Source Code

## files.py

Complete source code for all frontend components with full implementation details.

---

## App.jsx - Main Application Container

```jsx
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Toaster, toast } from 'react-hot-toast'
import DocumentForm from './components/DocumentForm'
import DocumentList from './components/DocumentList'
import DocumentStats from './components/DocumentStats'
import DocumentDetailModal from './components/DocumentDetailModal'
import QrLookupPanel from './components/QrLookupPanel'
import schoolLogo from './assets/school-logo.png'
import collegeLogo from './assets/college-logo.png'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const getApiErrorMessage = (err, fallbackMessage) => {
  const data = err?.response?.data

  if (typeof data === 'string' && data.trim()) {
    return data
  }

  if (data?.detail) {
    return data.detail
  }

  if (data?.error) {
    return data.error
  }

  if (data && typeof data === 'object') {
    const firstValue = Object.values(data)[0]

    if (Array.isArray(firstValue) && firstValue.length > 0) {
      return String(firstValue[0])
    }

    if (typeof firstValue === 'string' && firstValue.trim()) {
      return firstValue
    }
  }

  return fallbackMessage || err.message || 'Request failed'
}

function App() {
  // State Management
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterOwner, setFilterOwner] = useState('')
  const [selectedDocument, setSelectedDocument] = useState(null)
  const [selectedDocumentKey, setSelectedDocumentKey] = useState('')
  const [qrLookupResult, setQrLookupResult] = useState(null)

  // API: Fetch all documents with search & filter
  const fetchDocuments = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.get(`${API_BASE_URL}/documents/`, {
        headers: {
          'Content-Type': 'application/json',
        },
        params: {
          ...(searchQuery ? { search: searchQuery } : {}),
          ...(filterOwner ? { owner: filterOwner } : {}),
        },
      })

      setDocuments(response.data.results || response.data)
    } catch (err) {
      setError(`Failed to fetch documents: ${getApiErrorMessage(err, 'Unable to load documents')}`)
      console.error('Error fetching documents:', err)
    } finally {
      setLoading(false)
    }
  }

  // API: Fetch dashboard statistics
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/stats/`)
      setStats(response.data)
    } catch (err) {
      setError(`Failed to fetch stats: ${getApiErrorMessage(err, 'Unable to load stats')}`)
      console.error('Error fetching stats:', err)
    }
  }

  // API: Resolve QR code (encrypted_id + access_key)
  const resolveQrCode = async (encryptedId, accessKey) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/resolve_qr/`, {
        headers: {
          'X-Document-Key': accessKey,
        },
        params: { encrypted_id: encryptedId },
      })

      setQrLookupResult(response.data)
      setSelectedDocument(response.data.document)
      setSelectedDocumentKey(accessKey)
      toast.success('QR code resolved successfully')
      return response.data
    } catch (err) {
      const message = getApiErrorMessage(err, 'Unable to resolve QR code')
      toast.error(message)
      throw new Error(message)
    }
  }

  // Lifecycle: Fetch documents & stats on search/filter change
  useEffect(() => {
    fetchDocuments()
    fetchStats()
  }, [searchQuery, filterOwner])

  // API: Create new document
  const handleCreateDocument = async (formData) => {
    setError(null)

    try {
      const isFormData = typeof FormData !== 'undefined' && formData instanceof FormData
      const response = await axios.post(`${API_BASE_URL}/documents/`, formData, {
        headers: {
          ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        },
      })

      setDocuments([response.data, ...documents])
      fetchStats()
      toast.success(`Document "${response.data.title}" created successfully!`)
      return { success: true, data: response.data }
    } catch (err) {
      const errorMsg = getApiErrorMessage(err, 'Failed to create document')
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  // API: Delete document
  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return
    }

    const accessKey = window.prompt('Enter document access key to delete:') || ''
    if (!accessKey.trim()) {
      toast.error('Document access key is required.')
      return
    }

    try {
      await axios.delete(`${API_BASE_URL}/documents/${documentId}/`, {
        headers: {
          'X-Document-Key': accessKey.trim(),
        },
      })
      setDocuments(documents.filter((doc) => doc.id !== documentId))
      fetchStats()
    } catch (err) {
      setError(`Failed to delete document: ${getApiErrorMessage(err, 'Unable to delete document')}`)
    }
  }

  // API: View document (requires access key)
  const handleViewDocument = async (document) => {
    const accessKey = window.prompt('Enter document access key to view:') || ''
    if (!accessKey.trim()) {
      toast.error('Document access key is required.')
      return
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/documents/${document.id}/`, {
        headers: {
          'X-Document-Key': accessKey.trim(),
        },
      })
      setSelectedDocument(response.data)
      setSelectedDocumentKey(accessKey.trim())
    } catch (err) {
      const message = getApiErrorMessage(err, 'Unable to open document')
      toast.error(message)
    }
  }

  // API: Update document
  const handleUpdateDocument = async (documentId, payload) => {
    if (!selectedDocumentKey) {
      const message = 'Open the document using a valid access key before editing.'
      toast.error(message)
      return { success: false, error: message }
    }

    try {
      const response = await axios.patch(`${API_BASE_URL}/documents/${documentId}/`, payload, {
        headers: {
          'X-Document-Key': selectedDocumentKey,
          'Content-Type': 'application/json',
        },
      })

      setSelectedDocument(response.data)
      setDocuments((prev) => prev.map((doc) => (doc.id === response.data.id ? { ...doc, ...response.data } : doc)))
      fetchStats()
      toast.success('Document updated successfully')
      return { success: true, data: response.data }
    } catch (err) {
      const message = getApiErrorMessage(err, 'Unable to update document')
      toast.error(message)
      return { success: false, error: message }
    }
  }

  // Extract unique owner list for filter dropdown
  const owners = [...new Set(documents.map((doc) => doc.owner))].filter(Boolean)

  // Render main app
  return (
    <div className="app">
      {/* Toast notifications */}
      <Toaster position="top-right" />

      {/* Header */}
      <div className="app-header">
        <div className="header-row">
          <div className="logo-item">
            <img src={collegeLogo} alt="CIT Logo" style={{ height: '80px', width: 'auto' }} />
          </div>
          <div className="header-content">
            <h1>CIT Document Tracker</h1>
            <p>Pure document tracking for CIT with QR lookup and encrypted IDs.</p>
          </div>
          <div className="logo-item">
            <img src={schoolLogo} alt="University Logo" style={{ height: '80px', width: 'auto' }} />
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="container">
        {/* Error banner */}
        {error && <div className="error-banner">{error}</div>}

        {/* Dashboard statistics */}
        {stats && <DocumentStats stats={stats} />}

        {/* Create document form */}
        <DocumentForm
          onCreateDocument={handleCreateDocument}
          isAdmin={true}
          currentUser=""
        />

        {/* QR lookup panel */}
        <QrLookupPanel onLookup={resolveQrCode} />

        {/* Search & filter */}
        <div className="search-filter-section">
          <div className="search-box">
            <input
              type="text"
              placeholder="🔍 Search by title or owner..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {owners.length > 0 && (
            <div className="filter-box">
              <select
                value={filterOwner}
                onChange={(e) => setFilterOwner(e.target.value)}
              >
                <option value="">All Owners</option>
                {owners.map((owner) => (
                  <option key={owner} value={owner}>
                    {owner}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Document list or loading state */}
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            Loading documents...
          </div>
        ) : (
          <DocumentList
            documents={documents}
            onViewDocument={handleViewDocument}
          />
        )}

        {/* Document detail modal */}
        {selectedDocument && (
          <DocumentDetailModal
            document={selectedDocument}
            onSave={handleUpdateDocument}
            onClose={() => setSelectedDocument(null)}
          />
        )}

        {/* QR lookup result metadata */}
        {qrLookupResult && (
          <div className="qr-lookup-result card">
            <h3>QR Lookup Result</h3>
            <p>Resolved document ID: {qrLookupResult.resolved_document_id}</p>
            <p>Document number: {qrLookupResult.resolved_document_number}</p>
            <p>Reference code: {qrLookupResult.resolved_reference_code}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
```

---

## DocumentForm.jsx - Create Document Component

```jsx
import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import './DocumentForm.css'

function DocumentForm({ onCreateDocument, isAdmin, currentUser }) {
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    department: 'General',
    doc_type: 'Memo',
    description: '',
    sender: '',
    receiver: '',
    status: 'Pending',
    priority: 'Medium',
    due_date: '',
    remarks: '',
    access_key: '',
    owner: '',
    attachment: null,
  })

  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  // Initialize owner for non-admin users
  useEffect(() => {
    if (!isAdmin) {
      setFormData((prev) => ({
        ...prev,
        owner: currentUser || '',
      }))
    }
  }, [isAdmin, currentUser])

  // Handle input changes
  const handleChange = (e) => {
    const { name, value, type } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'file' ? e.target.files[0] : value,
    }))

    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }))
    }
  }

  // Validate form before submit
  const validateForm = () => {
    const newErrors = {}
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    }
    if (!formData.sender.trim()) {
      newErrors.sender = 'Sender is required'
    }
    if (!formData.receiver.trim()) {
      newErrors.receiver = 'Receiver is required'
    }
    if (!formData.access_key.trim()) {
      newErrors.access_key = 'Access key is required'
    }
    if (isAdmin && !formData.owner.trim()) {
      newErrors.owner = 'Owner is required for admin-created documents'
    }
    return newErrors
  }

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()

    const newErrors = validateForm()
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      toast.error('Please fill in all required fields')
      return
    }

    setLoading(true)
    try {
      // Build FormData payload
      const payload = new FormData()
      payload.append('title', formData.title.trim())
      payload.append('department', formData.department)
      payload.append('doc_type', formData.doc_type)
      payload.append('description', formData.description.trim())
      payload.append('sender', formData.sender.trim())
      payload.append('receiver', formData.receiver.trim())
      payload.append('status', formData.status)
      payload.append('priority', formData.priority)
      payload.append('access_key', formData.access_key.trim())
      if (formData.due_date) {
        payload.append('due_date', formData.due_date)
      }
      payload.append('remarks', formData.remarks.trim())
      if (isAdmin) {
        payload.append('owner', formData.owner.trim())
      }
      if (formData.attachment) {
        payload.append('attachment', formData.attachment)
      }

      // Submit to API
      const result = await onCreateDocument(payload)

      if (result.success) {
        // Reset form
        setFormData({
          title: '',
          department: 'General',
          doc_type: 'Memo',
          description: '',
          sender: '',
          receiver: '',
          status: 'Pending',
          priority: 'Medium',
          due_date: '',
          remarks: '',
          access_key: '',
          owner: isAdmin ? '' : currentUser || '',
          attachment: null,
        })
        setErrors({})
      } else {
        setErrors({ submit: result.error })
        toast.error(result.error)
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to create document'
      setErrors({ submit: errorMsg })
      toast.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="form-container">
      <div className="form-card card">
        <h2>Create New Document</h2>
        <form onSubmit={handleSubmit}>
          {/* Title Field */}
          <div className="form-group">
            <label htmlFor="title">Document Title *</label>
            <input
              id="title"
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Enter document title"
              maxLength="255"
              disabled={loading}
            />
            {errors.title && <span className="error">{errors.title}</span>}
          </div>

          {/* Owner Field (Admin only) */}
          {isAdmin && (
            <div className="form-group">
              <label htmlFor="owner">Document Owner *</label>
              <input
                id="owner"
                type="text"
                name="owner"
                value={formData.owner}
                onChange={handleChange}
                placeholder="Enter document owner name"
                maxLength="255"
                disabled={loading}
              />
              {errors.owner && <span className="error">{errors.owner}</span>}
            </div>
          )}

          {/* Sender Field */}
          <div className="form-group">
            <label htmlFor="sender">Sender *</label>
            <input
              id="sender"
              type="text"
              name="sender"
              value={formData.sender}
              onChange={handleChange}
              placeholder="Enter sender name"
              maxLength="255"
              disabled={loading}
            />
            {errors.sender && <span className="error">{errors.sender}</span>}
          </div>

          {/* Receiver Field */}
          <div className="form-group">
            <label htmlFor="receiver">Receiver *</label>
            <input
              id="receiver"
              type="text"
              name="receiver"
              value={formData.receiver}
              onChange={handleChange}
              placeholder="Enter receiver name"
              maxLength="255"
              disabled={loading}
            />
            {errors.receiver && <span className="error">{errors.receiver}</span>}
          </div>

          {/* Department Dropdown */}
          <div className="form-group">
            <label htmlFor="department">Department</label>
            <select
              id="department"
              name="department"
              value={formData.department}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="General">General</option>
              <option value="Registrar">Registrar</option>
              <option value="Dean Office">Dean Office</option>
              <option value="Guidance Office">Guidance Office</option>
              <option value="Accounting">Accounting</option>
              <option value="Library">Library</option>
            </select>
          </div>

          {/* Document Type Dropdown */}
          <div className="form-group">
            <label htmlFor="doc_type">Document Type</label>
            <select
              id="doc_type"
              name="doc_type"
              value={formData.doc_type}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="Memo">Memo</option>
              <option value="Letter">Letter</option>
              <option value="Report">Report</option>
            </select>
          </div>

          {/* Status Dropdown */}
          <div className="form-group">
            <label htmlFor="status">Status</label>
            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="Pending">Pending</option>
              <option value="In Process">In Process</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          {/* Priority Dropdown */}
          <div className="form-group">
            <label htmlFor="priority">Priority</label>
            <select
              id="priority"
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Urgent">Urgent</option>
            </select>
          </div>

          {/* Due Date Field */}
          <div className="form-group">
            <label htmlFor="due_date">Due Date</label>
            <input
              id="due_date"
              type="date"
              name="due_date"
              value={formData.due_date}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          {/* Description Field */}
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Enter document description"
              rows="3"
              disabled={loading}
            />
          </div>

          {/* Remarks Field */}
          <div className="form-group">
            <label htmlFor="remarks">Remarks</label>
            <textarea
              id="remarks"
              name="remarks"
              value={formData.remarks}
              onChange={handleChange}
              placeholder="Enter any remarks"
              rows="3"
              disabled={loading}
            />
          </div>

          {/* Access Key Field (REQUIRED) */}
          <div className="form-group">
            <label htmlFor="access_key">Access Key *</label>
            <input
              id="access_key"
              type="password"
              name="access_key"
              value={formData.access_key}
              onChange={handleChange}
              placeholder="Enter document access key (password)"
              disabled={loading}
            />
            {errors.access_key && <span className="error">{errors.access_key}</span>}
            <p className="form-info">This key will be required to view/edit the document.</p>
          </div>

          {/* Attachment Field */}
          <div className="form-group">
            <label htmlFor="attachment">Attachment</label>
            <input
              id="attachment"
              type="file"
              name="attachment"
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          {/* Submit Error */}
          {errors.submit && <div className="form-error-message">{errors.submit}</div>}

          {/* Submit Button */}
          <button type="submit" className="btn-primary btn-submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Document'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default DocumentForm
```

---

## DocumentList.jsx - Display Documents in Grid

```jsx
import React, { useState } from 'react'
import QRCode from 'qrcode.react'
import './DocumentList.css'

function DocumentList({ documents, onViewDocument }) {
  const [expandedId, setExpandedId] = useState(null)

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id)
  }

  // Download QR code as image
  const downloadQR = (encrypted_id, title) => {
    const qrElement = document.getElementById(`qr-${encrypted_id}`)
    if (qrElement) {
      const canvas = qrElement.querySelector('canvas')
      const link = document.createElement('a')
      link.href = canvas.toDataURL('image/png')
      link.download = `${title.replace(/\s+/g, '_')}_QR.png`
      link.click()
    }
  }

  // Copy to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  // Empty state
  if (documents.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📭</div>
        <h3>No documents yet</h3>
        <p>Create your first document to get started!</p>
      </div>
    )
  }

  // Render document grid
  return (
    <div className="document-list">
      <h2>📋 Documents ({documents.length})</h2>

      <div className="documents-grid">
        {documents.map((doc) => (
          <div key={doc.id} className="document-card card">
            {/* Card Header */}
            <div className="card-header">
              <div className="card-title-section">
                <h3>{doc.title}</h3>
                <p className="owner">👤 {doc.owner}</p>
                <p className="owner">No: {doc.document_number || 'Pending number'}</p>
                <p className="owner">Type: {doc.doc_type}</p>
              </div>
              <button
                className="expand-btn"
                onClick={() => toggleExpand(doc.id)}
              >
                {expandedId === doc.id ? '▼' : '▶'}
              </button>
            </div>

            {/* Card Meta (Summary) */}
            <div className="card-meta">
              <span className="meta-item">
                🆔 <strong>Enc ID:</strong>
                <code className="doc-id">{(doc.idea_encrypted_internal_id || '').substring(0, 12)}...</code>
              </span>
              <span className="meta-item">📅 {new Date(doc.created_at).toLocaleDateString()}</span>
              <span className="meta-item">Dept: {doc.department}</span>
              <span className="meta-item">Status: {doc.status}</span>
              <span className="meta-item">Priority: {doc.priority}</span>
            </div>

            {/* Card Expanded Content */}
            {expandedId === doc.id && (
              <div className="card-expanded">
                {/* Encrypted ID with copy button */}
                <div className="encryption-info">
                  <h4>Encrypted ID (Copy/Paste)</h4>
                  <div className="encrypted-id-display">
                    <code>{doc.encrypted_id}</code>
                    <button
                      className="copy-btn btn-small"
                      onClick={() => copyToClipboard(doc.encrypted_id)}
                      title="Copy encrypted ID"
                    >
                      📋
                    </button>
                  </div>
                  <p className="encryption-note">Use this value in QR Lookup if scanning is difficult.</p>
                </div>

                {/* QR Code section */}
                <div className="qr-section">
                  <h4>🔗 QR Code</h4>
                  <div id={`qr-${doc.encrypted_id}`} className="qr-container">
                    <QRCode
                      value={doc.encrypted_id}
                      size={200}
                      level="H"
                      includeMargin={true}
                    />
                  </div>
                  <button
                    className="btn-secondary btn-small"
                    onClick={() => downloadQR(doc.encrypted_id, doc.title)}
                  >
                    ⬇️ Download QR
                  </button>
                </div>
              </div>
            )}

            {/* Card Actions (empty for now) */}
            <div className="card-actions">
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default DocumentList
```

---

## QrLookupPanel.jsx - QR Resolution

```jsx
import React, { useState } from 'react'
import './DocumentForm.css'

function QrLookupPanel({ onLookup }) {
  const [encryptedId, setEncryptedId] = useState('')
  const [accessKey, setAccessKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!encryptedId.trim()) {
      setError('Enter an encrypted ID from a QR code.')
      return
    }

    if (!accessKey.trim()) {
      setError('Enter the document access key.')
      return
    }

    setLoading(true)
    setError('')

    try {
      await onLookup(encryptedId.trim(), accessKey.trim())
      setEncryptedId('')
      setAccessKey('')
    } catch (lookupError) {
      setError(lookupError.message || 'Unable to resolve QR code.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="form-card card">
      <h2>QR Lookup</h2>
      <p className="form-info">Paste the encrypted ID and enter the document access key.</p>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="encryptedId">Encrypted ID</label>
          <input
            id="encryptedId"
            type="text"
            value={encryptedId}
            onChange={(event) => setEncryptedId(event.target.value)}
            placeholder="Enter encrypted ID from QR code"
            disabled={loading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="accessKey">Access Key</label>
          <input
            id="accessKey"
            type="password"
            value={accessKey}
            onChange={(event) => setAccessKey(event.target.value)}
            placeholder="Enter document key"
            disabled={loading}
          />
        </div>
        {error && <div className="form-error-message">{error}</div>}
        <button type="submit" className="btn-primary btn-submit" disabled={loading}>
          {loading ? 'Looking up...' : 'Resolve QR Code'}
        </button>
      </form>
    </div>
  )
}

export default QrLookupPanel
```

---

## DocumentDetailModal.jsx - View/Edit Modal

```jsx
import React, { useState } from 'react'
import './DocumentForm.css'

function DocumentDetailModal({ document, onClose, onSave }) {
  if (!document) {
    return null
  }

  const [editMode, setEditMode] = useState(false)
  const [formState, setFormState] = useState({
    status: document.status || 'Pending',
    priority: document.priority || 'Medium',
    due_date: document.due_date || '',
    remarks: document.remarks || '',
  })

  const handleChange = (event) => {
    const { name, value } = event.target
    setFormState((prev) => ({ ...prev, [name]: value }))
  }

  const handleSave = async () => {
    if (!onSave) {
      return
    }

    const result = await onSave(document.id, formState)
    if (result.success) {
      setEditMode(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(event) => event.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div>
            <h2>{document.title}</h2>
            <p>{document.document_number || 'Pending number'} - {document.reference_code || 'No reference code yet'}</p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {!editMode ? (
              <button className="btn-secondary" onClick={() => setEditMode(true)}>Edit</button>
            ) : (
              <button className="btn-secondary" onClick={handleSave}>Save</button>
            )}
            <button className="btn-secondary" onClick={onClose}>Close</button>
          </div>
        </div>

        {/* Modal Content */}
        <div className="detail-grid">
          <div><strong>Department:</strong> {document.department}</div>
          <div><strong>Type:</strong> {document.doc_type}</div>

          {/* Status (editable) */}
          <div>
            <strong>Status:</strong>{' '}
            {editMode ? (
              <select name="status" value={formState.status} onChange={handleChange}>
                <option value="Pending">Pending</option>
                <option value="In Process">In Process</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
                <option value="Completed">Completed</option>
              </select>
            ) : (
              document.status
            )}
          </div>

          {/* Priority (editable) */}
          <div>
            <strong>Priority:</strong>{' '}
            {editMode ? (
              <select name="priority" value={formState.priority} onChange={handleChange}>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Urgent">Urgent</option>
              </select>
            ) : (
              document.priority
            )}
          </div>

          <div><strong>Owner:</strong> {document.owner}</div>
          <div><strong>Sender:</strong> {document.sender}</div>
          <div><strong>Receiver:</strong> {document.receiver}</div>

          {/* Due Date (editable) */}
          <div>
            <strong>Due date:</strong>{' '}
            {editMode ? (
              <input type="date" name="due_date" value={formState.due_date || ''} onChange={handleChange} />
            ) : (
              document.due_date || 'N/A'
            )}
          </div>

          <div><strong>Encrypted ID:</strong> {document.encrypted_id}</div>
        </div>

        {/* Description (read-only) */}
        <div className="form-group" style={{ marginTop: '1rem' }}>
          <label>Description</label>
          <div className="readonly-owner">{document.description || 'N/A'}</div>
        </div>

        {/* Remarks (editable) */}
        <div className="form-group">
          <label>Remarks</label>
          {editMode ? (
            <textarea
              name="remarks"
              value={formState.remarks}
              onChange={handleChange}
              rows="4"
            />
          ) : (
            <div className="readonly-owner">{document.remarks || 'N/A'}</div>
          )}
        </div>

        {/* Timestamps */}
        <div className="timeline">
          <div className="timeline-item">
            <strong>Created:</strong> {new Date(document.created_at).toLocaleString()}
          </div>
          <div className="timeline-item">
            <strong>Updated:</strong> {new Date(document.updated_at).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DocumentDetailModal
```

---

## DocumentStats.jsx - Dashboard Statistics

```jsx
import React from 'react'
import './DocumentStats.css'

function DocumentStats({ stats }) {
  if (!stats) return null

  return (
    <div className="stats-container">
      {/* Total Documents Card */}
      <div className="stat-card">
        <div className="stat-icon">📊</div>
        <div className="stat-content">
          <h3>{stats.total_documents}</h3>
          <p>Total Documents</p>
        </div>
      </div>

      {/* Unique Owners Card */}
      <div className="stat-card">
        <div className="stat-icon">👥</div>
        <div className="stat-content">
          <h3>{stats.unique_owners}</h3>
          <p>Unique Owners</p>
        </div>
      </div>

      {/* This Month Card */}
      <div className="stat-card">
        <div className="stat-icon">📅</div>
        <div className="stat-content">
          <h3>{stats.documents_this_month}</h3>
          <p>This Month</p>
        </div>
      </div>

      {/* Status Distribution Cards */}
      {stats.status_counts && (
        <>
          <div className="stat-card">
            <div className="stat-icon">🕒</div>
            <div className="stat-content">
              <h3>{stats.status_counts.pending}</h3>
              <p>Pending</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⚙️</div>
            <div className="stat-content">
              <h3>{stats.status_counts.in_process}</h3>
              <p>In Process</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <h3>{stats.status_counts.completed}</h3>
              <p>Completed</p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default DocumentStats
```

---

This file contains the complete source code for all React frontend components with comprehensive comments and documentation for each function and component.
