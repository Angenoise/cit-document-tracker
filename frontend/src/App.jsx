import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Toaster, toast } from 'react-hot-toast'
import DocumentForm from './components/DocumentForm'
import DocumentList from './components/DocumentList'
import DocumentStats from './components/DocumentStats'
import LoginForm from './components/LoginForm'
import AdminPanel from './components/AdminPanel'
import UserManagement from './components/UserManagement'
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
  const [user, setUser] = useState(null)
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken') || '')
  const [authError, setAuthError] = useState(null)
  const [authLoading, setAuthLoading] = useState(false)
  const [selectedDocument, setSelectedDocument] = useState(null)
  const [qrLookupResult, setQrLookupResult] = useState(null)

  const authHeaders = () => {
    if (!authToken) {
      return {}
    }
    return {
      Authorization: `Token ${authToken}`,
    }
  }

  const handleClearAuth = () => {
    localStorage.removeItem('authToken')
    setAuthToken('')
    setUser(null)
    setDocuments([])
    setStats(null)
    setSelectedDocument(null)
    setQrLookupResult(null)
  }

  const fetchAuthStatus = async () => {
    if (!authToken) {
      return
    }

    try {
      setAuthError(null)
      const response = await axios.get(`${API_BASE_URL}/auth/status/`, {
        headers: {
          ...authHeaders(),
          'Content-Type': 'application/json',
        },
      })
      setUser(response.data)
    } catch (err) {
      console.error('Auth status failed:', err)
      handleClearAuth()
    }
  }

  useEffect(() => {
    fetchAuthStatus()
  }, [authToken])

  const fetchDocuments = async () => {
    if (!user) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.get(`${API_BASE_URL}/documents/`, {
        headers: {
          ...authHeaders(),
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
    if (!user) {
      return
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/documents/stats/`, {
        headers: authHeaders(),
      })
      setStats(response.data)
    } catch (err) {
      setError(`Failed to fetch stats: ${getApiErrorMessage(err, 'Unable to load stats')}`)
      console.error('Error fetching stats:', err)
    }
  }

  const resolveQrCode = async (encryptedId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/resolve_qr/`, {
        headers: authHeaders(),
        params: { encrypted_id: encryptedId },
      })

      setQrLookupResult(response.data)
      setSelectedDocument(response.data.document)
      toast.success('QR code resolved successfully')
      return response.data
    } catch (err) {
      const message = getApiErrorMessage(err, 'Unable to resolve QR code')
      toast.error(message)
      throw new Error(message)
    }
  }

  useEffect(() => {
    if (user) {
      fetchDocuments()
      fetchStats()
    }
  }, [user, searchQuery, filterOwner])

  const handleLogin = async ({ username, password }) => {
    setAuthError(null)

    if (!username?.trim() || !password) {
      const message = 'Username and password are required.'
      setAuthError(message)
      return { success: false, error: message }
    }

    setAuthLoading(true)

    try {
      const response = await axios.post(
        `${API_BASE_URL}/auth/login/`,
        { username: username.trim(), password },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      const token = response.data.token
      localStorage.setItem('authToken', token)
      setAuthToken(token)
      setUser({ username: response.data.username, is_staff: response.data.is_staff })
      toast.success('Logged in successfully')
      return { success: true }
    } catch (err) {
      const message = getApiErrorMessage(err, 'Login failed')
      setAuthError(message)
      return { success: false, error: message }
    } finally {
      setAuthLoading(false)
    }
  }

  const handleRegister = async ({ username, password }) => {
    setAuthError(null)

    if (!username?.trim() || !password) {
      const message = 'Username and password are required.'
      setAuthError(message)
      return { success: false, error: message }
    }

    setAuthLoading(true)

    try {
      const response = await axios.post(
        `${API_BASE_URL}/auth/register/`,
        { username: username.trim(), password },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      const token = response.data.token
      localStorage.setItem('authToken', token)
      setAuthToken(token)
      setUser({ username: response.data.username, is_staff: response.data.is_staff })
      toast.success('Account created successfully')
      return { success: true }
    } catch (err) {
      const message = getApiErrorMessage(err, 'Registration failed')
      setAuthError(message)
      return { success: false, error: message }
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await axios.post(
        `${API_BASE_URL}/auth/logout/`,
        {},
        {
          headers: {
            ...authHeaders(),
            'Content-Type': 'application/json',
          },
        }
      )
    } catch (err) {
      console.error('Logout failed:', err)
    } finally {
      handleClearAuth()
      toast('Logged out successfully')
    }
  }

  const handleCreateDocument = async (formData) => {
    setError(null)

    try {
      const isFormData = typeof FormData !== 'undefined' && formData instanceof FormData
      const response = await axios.post(`${API_BASE_URL}/documents/`, formData, {
        headers: {
          ...authHeaders(),
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

    try {
      await axios.delete(`${API_BASE_URL}/documents/${documentId}/`, {
        headers: authHeaders(),
      })
      setDocuments(documents.filter((doc) => doc.id !== documentId))
      fetchStats()
    } catch (err) {
      setError(`Failed to delete document: ${getApiErrorMessage(err, 'Unable to delete document')}`)
    }
  }

  const handleViewDocument = (document) => {
    setSelectedDocument(document)
  }

  const owners = [...new Set(documents.map((doc) => doc.owner))].filter(Boolean)
  const isAdmin = user?.is_staff

  if (!user) {
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
              <p>Login to access your documents and admin dashboard.</p>
            </div>
            <div className="logo-item">
              <img src={schoolLogo} alt="University Logo" style={{ height: '80px', width: 'auto' }} />
            </div>
          </div>
        </div>

        <div className="container">
          <LoginForm
            onLogin={handleLogin}
            onRegister={handleRegister}
            authError={authError}
            loading={authLoading}
          />
        </div>
      </div>
    )
  }

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
            <p>{isAdmin ? 'Admin dashboard and full document controls' : 'Your documents, encrypted and tracked securely'}</p>
          </div>
          <div className="logo-item">
            <img src={schoolLogo} alt="University Logo" style={{ height: '80px', width: 'auto' }} />
          </div>
        </div>
        <div className="user-info">
          <span>{`Signed in as ${user.username}${isAdmin ? ' (Admin)' : ''}`}</span>
          <button className="btn-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="container">
        {error && <div className="error-banner">{error}</div>}

        {isAdmin ? (
          <>
            <AdminPanel stats={stats} />
            <UserManagement authHeaders={authHeaders} />
          </>
        ) : (
          stats && <DocumentStats stats={stats} />
        )}

        <DocumentForm
          onCreateDocument={handleCreateDocument}
          isAdmin={isAdmin}
          currentUser={user.username}
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
            onDeleteDocument={handleDeleteDocument}
            onViewDocument={handleViewDocument}
          />
        )}

        {selectedDocument && (
          <DocumentDetailModal
            document={selectedDocument}
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
