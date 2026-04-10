import React, { useState } from 'react'
import './DocumentForm.css'

function QrLookupPanel({ onLookup }) {
  const [encryptedId, setEncryptedId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!encryptedId.trim()) {
      setError('Enter an encrypted ID from a QR code.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const rawInput = encryptedId.trim()
      let token = ''
      let fallbackEncryptedId = rawInput

      try {
        const parsedUrl = new URL(rawInput)
        token = parsedUrl.searchParams.get('qr_token') || ''
      } catch (_err) {
        // Not a URL. Continue with direct token/encrypted-id parsing.
      }

      if (!token && rawInput.includes(':') && rawInput.length > 32) {
        token = rawInput
      }

      await onLookup({ token, encryptedId: fallbackEncryptedId })
      setEncryptedId('')
    } catch (lookupError) {
      setError(lookupError.message || 'Unable to resolve QR code.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="form-card card">
      <h2>QR Lookup</h2>
      <p className="form-info">Paste the QR URL, signed token, or encrypted ID to open the matching document record.</p>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="encryptedId">Encrypted ID</label>
          <input
            id="encryptedId"
            type="text"
            value={encryptedId}
            onChange={(event) => setEncryptedId(event.target.value)}
            placeholder="Paste QR URL, token, or encrypted ID"
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
