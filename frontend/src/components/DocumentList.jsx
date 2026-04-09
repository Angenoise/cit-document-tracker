import React, { useState } from 'react'
import QRCode from 'qrcode.react'
import './DocumentList.css'

function DocumentList({ documents, onDeleteDocument, onViewDocument }) {
  const [expandedId, setExpandedId] = useState(null)

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id)
  }

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

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  if (documents.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📭</div>
        <h3>No documents yet</h3>
        <p>Create your first document to get started!</p>
      </div>
    )
  }

  return (
    <div className="document-list">
      <h2>📋 Documents ({documents.length})</h2>
      
      <div className="documents-grid">
        {documents.map((doc) => (
          <div key={doc.id} className="document-card card">
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

            <div className="card-meta">
              <span className="meta-item">
                🆔 <strong>ID:</strong>
                <code className="doc-id">{doc.id.substring(0, 8)}...</code>
              </span>
              <span className="meta-item">📅 {new Date(doc.created_at).toLocaleDateString()}</span>
              <span className="meta-item">Dept: {doc.department}</span>
              <span className="meta-item">Status: {doc.status}</span>
              <span className="meta-item">Priority: {doc.priority}</span>
            </div>

            {expandedId === doc.id && (
              <div className="card-expanded">
                <div className="encryption-info">
                  <h4>Encrypted ID</h4>
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
                  <p className="encryption-note">
                    This ID is encrypted using IDEA algorithm
                  </p>
                </div>

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

                <div className="card-details">
                  <div className="detail-row">
                    <span className="label">Description:</span>
                    <span className="value">{doc.description || 'N/A'}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Reference code:</span>
                    <span className="value">{doc.reference_code || 'N/A'}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Department:</span>
                    <span className="value">{doc.department}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Sender:</span>
                    <span className="value">{doc.sender}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Receiver:</span>
                    <span className="value">{doc.receiver}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Full ID:</span>
                    <span className="value">{doc.id}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Due date:</span>
                    <span className="value">{doc.due_date || 'N/A'}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Remarks:</span>
                    <span className="value">{doc.remarks || 'N/A'}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Attachment:</span>
                    <span className="value">
                      {doc.attachment ? (
                        <a href={doc.attachment} target="_blank" rel="noreferrer">Open file</a>
                      ) : 'N/A'}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Created:</span>
                    <span className="value">
                      {new Date(doc.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Updated:</span>
                    <span className="value">
                      {new Date(doc.updated_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="card-actions">
              <button
                className="btn-secondary btn-small"
                onClick={() => onViewDocument && onViewDocument(doc)}
              >
                View Details
              </button>
              <button
                className="btn-danger btn-small"
                onClick={() => onDeleteDocument(doc.id)}
              >
                🗑️ Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default DocumentList
