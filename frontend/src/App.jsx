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
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterOwner, setFilterOwner] = useState('')
  const [selectedDocument, setSelectedDocument] = useState(null)
  const [selectedDocumentKey, setSelectedDocumentKey] = useState('')
  const [qrLookupResult, setQrLookupResult] = useState(null)

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

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/stats/`)
      setStats(response.data)
    } catch (err) {
      setError(`Failed to fetch stats: ${getApiErrorMessage(err, 'Unable to load stats')}`)
      console.error('Error fetching stats:', err)
    }
  }

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

  useEffect(() => {
    fetchDocuments()
    fetchStats()
  }, [searchQuery, filterOwner])

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

  const owners = [...new Set(documents.map((doc) => doc.owner))].filter(Boolean)

  return (
    <div className="app">
      <Toaster position="top-right" />
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

      <div className="container">
        {error && <div className="error-banner">{error}</div>}

        {stats && <DocumentStats stats={stats} />}

        <DocumentForm
          onCreateDocument={handleCreateDocument}
          isAdmin={true}
          currentUser=""
        />

        <QrLookupPanel onLookup={resolveQrCode} />

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

        {selectedDocument && (
          <DocumentDetailModal
            document={selectedDocument}
            onSave={handleUpdateDocument}
            onClose={() => setSelectedDocument(null)}
          />
        )}

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
