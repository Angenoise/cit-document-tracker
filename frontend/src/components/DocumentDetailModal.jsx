import React from 'react'
import './DocumentForm.css'

function DocumentDetailModal({ document, onClose }) {
  if (!document) {
    return null
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(event) => event.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>{document.title}</h2>
            <p>{document.document_number || 'Pending number'} - {document.reference_code || 'No reference code yet'}</p>
          </div>
          <button className="btn-secondary" onClick={onClose}>Close</button>
        </div>

        <div className="detail-grid">
          <div><strong>Department:</strong> {document.department}</div>
          <div><strong>Type:</strong> {document.doc_type}</div>
          <div><strong>Status:</strong> {document.status}</div>
          <div><strong>Priority:</strong> {document.priority}</div>
          <div><strong>Owner:</strong> {document.owner}</div>
          <div><strong>Sender:</strong> {document.sender}</div>
          <div><strong>Receiver:</strong> {document.receiver}</div>
          <div><strong>Due date:</strong> {document.due_date || 'N/A'}</div>
          <div><strong>Encrypted ID:</strong> {document.encrypted_id}</div>
        </div>

        <div className="form-group" style={{ marginTop: '1rem' }}>
          <label>Description</label>
          <div className="readonly-owner">{document.description || 'N/A'}</div>
        </div>

        <div className="form-group">
          <label>Remarks</label>
          <div className="readonly-owner">{document.remarks || 'N/A'}</div>
        </div>

        <div className="form-group">
          <label>Attachment</label>
          <div className="readonly-owner">
            {document.attachment ? (
              <a href={document.attachment} target="_blank" rel="noreferrer">Open attachment</a>
            ) : 'No attachment uploaded'}
          </div>
        </div>

        <div className="form-group">
          <label>Document Activity</label>
          <div className="timeline">
            {(document.activities || []).length > 0 ? (
              document.activities.map((activity) => (
                <div key={activity.id} className="timeline-item">
                  <strong>{activity.action}</strong>
                  <div>{activity.message}</div>
                  <small>
                    {activity.changed_by || 'System'} - {new Date(activity.created_at).toLocaleString()}
                  </small>
                </div>
              ))
            ) : (
              <div className="readonly-owner">No activity yet</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DocumentDetailModal
