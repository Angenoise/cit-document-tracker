# CIT Document Tracker - Complete Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Backend Source Code](#backend-source-code)
5. [Frontend Source Code](#frontend-source-code)
6. [API Endpoints](#api-endpoints)
7. [Security Features (CIA Triad)](#security-features-cia-triad)
8. [Usage Guide](#usage-guide)

---

## System Overview

**CIT Document Tracker** is a full-stack web application that demonstrates secure document management using the CIA Triad (Confidentiality, Integrity, Availability).

### Key Features
- **IDEA Encryption**: 128-bit block cipher encrypting document IDs
- **Per-Document Access Keys**: Hash-based authorization system
- **QR Code Integration**: Generate and scan encrypted document IDs
- **Audit Trail**: Complete activity logging of all document operations
- **Real-time Search & Filter**: Search by title/owner, filter by owner
- **Responsive UI**: Works on desktop and mobile devices
- **Dashboard Analytics**: Statistics on total documents, unique owners, and status distribution
- **Document Workflow**: Track status (Pending → In Process → Approved/Rejected → Completed)

### Tech Stack
```
Backend:  Django 5.0.1 + Django REST Framework
Frontend: React 18 + Vite + Axios
Database: SQLite (production-ready for PostgreSQL)
Encryption: IDEA cipher algorithm (128-bit blocks, 8 rounds)
Styling: CSS3 with responsive design
```

---

## Architecture

### System Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                  │
│  ┌─────────────┬────────────────┬──────────────────────┐   │
│  │ DocumentForm│ DocumentList   │ QrLookupPanel        │   │
│  │ (Create)    │ (View/Copy/QR) │ (Scan + Manual Enter)│   │
│  └─────────────┴────────────────┴──────────────────────┘   │
│                           │                                  │
│                    Axios HTTP Calls                         │
│                  X-Document-Key Header                      │
│                           │                                  │
└─────────────────────────────────────────────────────────────┘
                             │
               ┌─────────────────────────────┐
               │   DJANGO REST API (Port 8000)│
               │                              │
               │  DocumentViewSet             │
               │  - create()                  │
               │  - retrieve()                │
               │  - update()                  │
               │  - destroy()                 │
               │  - resolve_qr()              │
               │  - stats()                   │
               │                              │
               └─────────────────────────────┘
                             │
               ┌─────────────────────────────┐
               │      Database (SQLite)       │
               │                              │
               │  Document Table              │
               │  - encrypted_id (IDEA)       │
               │  - access_key_hash (bcrypt) │
               │  - status, priority, etc     │
               │                              │
               │  DocumentActivity Table      │
               │  - Audit logs                │
               └─────────────────────────────┘

ENCRYPTION LAYER:
               ┌─────────────────────────────┐
               │   IDEA Cipher Module         │
               │                              │
               │  encrypt_document_id()       │
               │  - Takes UUID + Key          │
               │  - Returns hex string        │
               │  - 128-bit block size        │
               │  - 8 + 1 rounds              │
               └─────────────────────────────┘
```

---

## Core Components

### Backend Architecture

#### 1. **models.py** - Data Models

**Document Model**
```python
class Document(models.Model):
    # Primary Key & Identifiers
    id = UUIDField(primary_key, unique)
    document_number = CharField(unique, auto-generated)
    reference_code = CharField(unique, auto-generated)
    encrypted_id = CharField(unique) # IDEA-encrypted UUID
    
    # Document Properties
    title = CharField(required)
    doc_type = CharField(choices: Memo, Letter, Report)
    department = CharField(choices: General, Registrar, Dean, Guidance, Accounting, Library)
    description = TextField(optional)
    
    # Workflow
    status = CharField(choices: Pending, In Process, Approved, Rejected, Completed)
    priority = CharField(choices: Low, Medium, High, Urgent)
    due_date = DateField(optional)
    remarks = TextField(optional)
    
    # Transport & Content
    sender = CharField(required)
    receiver = CharField(required)
    attachment = FileField(optional)
    owner = CharField(required) # Document owner name
    
    # Security
    access_key_hash = CharField() # bcrypt hash of password
    
    # Timestamps
    created_at = DateTimeField(auto_now_add)
    updated_at = DateTimeField(auto_now)

Key Methods:
    set_access_key(key: str)
        → Hashes key using Django make_password()
        → Stores in access_key_hash field
        
    check_access_key(key: str) -> bool
        → Verifies key matches access_key_hash
        → Returns True/False (password-verified)
        → Backward compatible with fallback
        
    save()
        → Auto-generates document_number: CIT-{year}-{uuid_prefix}
        → Encrypts UUID using IDEA cipher
        → Generates reference_code: REF-{first_8_chars_encrypted_id}
```

**DocumentActivity Model** - Audit Trail
```python
class DocumentActivity(models.Model):
    document = ForeignKey(Document)
    document_title = CharField()
    action = CharField(choices: Created, Updated, Deleted, Looked Up)
    message = TextField()
    previous_status = CharField()
    new_status = CharField()
    changed_by = CharField()
    created_at = DateTimeField(auto_now_add)
    
Purpose: Complete audit trail of all operations for security compliance
```

---

#### 2. **serializers.py** - Input/Output Handlers

**PublicDocumentSerializer** (used for list view)
```python
fields = [
    'id', 'document_number', 'reference_code', 'department',
    'title', 'doc_type', 'status', 'priority', 'owner',
    'created_at', 'updated_at'
]
- Excludes: description, remarks, attachment, sender, receiver
- Purpose: Lightweight list response without sensitive data
```

**DocumentSerializer** (used for CRUD operations)
```python
fields = [
    'id', 'document_number', 'reference_code', 'department',
    'title', 'doc_type', 'description', 'sender', 'receiver',
    'owner', 'status', 'priority', 'due_date', 'remarks',
    'attachment', 'access_key', 'encrypted_id',
    'idea_encrypted_internal_id', 'created_at', 'updated_at'
]

Special Fields:
    access_key (write_only)
        → Required on create()
        → User provides plaintext password
        → Automatically hashed before save
        
    idea_encrypted_internal_id (computed)
        → Returns IDEA-encrypted UUID
        → Used for display in UI (demo of encryption)
        → Different from encrypted_id (which is document lookup key)

Validators:
    - validate_title() → Prevent empty
    - validate_owner() → Prevent empty
    - validate_sender() → Prevent empty
    - validate_receiver() → Prevent empty
```

---

#### 3. **views.py** - API Endpoints

**DocumentViewSet** - REST CRUD Operations
```python
Endpoints:
    GET    /api/documents/
           → Lists all documents (summary view)
           → Search by: title, doc_type, description, sender, receiver, owner, status, priority, remarks
           → Filter by: owner (case-insensitive)
           → Order by: created_at (default), title, owner, due_date, status, priority
           
    POST   /api/documents/
           → Create new document
           → Required: title, owner, sender, receiver, access_key, department, doc_type
           → Returns: Full document object with encrypted_id
           → Logs: DocumentActivity.ACTION_CREATED
           
    GET    /api/documents/{id}/
           → Retrieve single document
           → Requires: X-Document-Key header OR access_key query param
           → Validates key using document.check_access_key()
           → Returns: Full document details if authorized
           
    PATCH  /api/documents/{id}/
           → Update document
           → Requires: X-Document-Key header (for authorization)
           → Updatable fields: status, priority, due_date, remarks, description, etc.
           → Logs: DocumentActivity.ACTION_UPDATED
           
    DELETE /api/documents/{id}/
           → Delete document
           → Requires: X-Document-Key header (for authorization)
           → Logs: DocumentActivity.ACTION_DELETED

Custom Actions:
    GET    /api/documents/stats/
           → Returns dashboard statistics:
             {
               "total_documents": 15,
               "unique_owners": 8,
               "documents_this_month": 5,
               "status_counts": {
                 "pending": 3,
                 "in_process": 2,
                 "approved": 5,
                 "rejected": 1,
                 "completed": 4
               }
             }
           
    GET    /api/documents/resolve_qr/
           → Scans QR code (contains encrypted_id)
           → Requires: encrypted_id (query param), X-Document-Key header
           → Validates access key
           → Returns: Document object + metadata
           → Logs: DocumentActivity.ACTION_LOOKED_UP
           
    GET    /api/documents/by_owner/
           → Filters documents by owner
           → Requires: owner (query param)
           → Returns: { owner, count, documents[] }

Key Methods:
    _get_access_key(request)
        → Extracts key from:
          1. X-Document-Key header (priority)
          2. access_key query parameter
          3. request.data['access_key']
        → Returns trimmed string
        
    _validate_document_access(request, document)
        → Gets access_key from request
        → Calls document.check_access_key()
        → Returns 400 if missing key
        → Returns 403 if invalid key
        → Returns None if valid
```

**DocumentActivityViewSet** - Audit Logs (Read-Only)
```python
Endpoints:
    GET    /api/activities/
           → Lists all activities
           → Filter by: document_id (query param)
           → Returns: List of audit records
           
Includes: action, message, status change, timestamp, changed_by
```

---

#### 4. **IDEA Encryption Module** (encryption/idea.py)

```python
class IDEA:
    """IDEA Block Cipher Implementation"""
    
    Properties:
        block_size = 64 bits (8 bytes)
        key_size = 128 bits (16 bytes)
        rounds = 8 data rounds + 1 output transformation
        
    Methods:
        encrypt(plaintext: bytes) -> bytes
            → Takes 8-byte plaintext block
            → Returns 8-byte ciphertext block
            → 128-bit key provides strong encryption
            
        decrypt(ciphertext: bytes) -> bytes
            → Reverse operation of encrypt()
            → Requires same key

Function: encrypt_document_id(doc_id, key)
    Input:
        doc_id: First 8 characters of UUID (string)
        key: 128-bit encryption key (bytes)
    
    Process:
        1. Pad doc_id to 8 bytes (ASCII encoding)
        2. Create IDEA cipher with key
        3. Encrypt padded bytes
        4. Convert to hex string
        5. Return uppercase hex
        
    Output: 16-character hex string (32 hex digits = 16 bytes)
    
    Example:
        Input:  "12345678" + key
        Output: "A1B2C3D4E5F67890..."
```

---

### Frontend Architecture

#### 1. **App.jsx** - Main Application Container

```jsx
State Management:
    documents[]              → List of all documents
    loading: boolean         → Loading indicator
    error: string           → Error messages
    stats: object           → Dashboard statistics
    searchQuery: string     → Search input value
    filterOwner: string     → Selected owner filter
    selectedDocument: object → Currently viewed document
    selectedDocumentKey: string → Access key for current document
    qrLookupResult: object  → QR scan result metadata

API Calls:
    fetchDocuments()
        → GET /api/documents/
        → Filters by: searchQuery, filterOwner
        → Updates documents state
        
    fetchStats()
        → GET /api/documents/stats/
        → Updates stats state
        
    resolveQrCode(encryptedId, accessKey)
        → GET /api/documents/resolve_qr/
        → Header: X-Document-Key: accessKey
        → Params: encrypted_id
        → Sets selectedDocument + selectedDocumentKey
        
    handleCreateDocument(formData)
        → POST /api/documents/
        → Payload: title, owner, sender, receiver, access_key, etc.
        → Prepends new document to list
        
    handleViewDocument(document)
        → Prompts for access key
        → GET /api/documents/{id}/
        → Sets selectedDocument if authorized
        
    handleUpdateDocument(documentId, payload)
        → PATCH /api/documents/{documentId}/
        → Requires selectedDocumentKey in header
        → Updates document in list

Component Hierarchy:
    <App>
        ├── <Header> (Logo + Title)
        ├── <DocumentStats> (Dashboard Cards)
        ├── <DocumentForm> (Create Document)
        ├── <QrLookupPanel> (Scan/Type Encrypted ID + Key)
        ├── <SearchFilter> (Search + Owner Filter)
        ├── <DocumentList> (Grid of Document Cards)
        │   └── Document Expand Section:
        │       ├── Encrypted ID Display (Copy Button)
        │       └── QR Code (Download Button)
        ├── <DocumentDetailModal> (View/Edit Document)
        └── <Toast Notifications> (Success/Error Messages)
```

---

#### 2. **DocumentForm.jsx** - Create Document Component

```jsx
Input Fields:
    ✓ Title (required)
    ✓ Owner (required)
    ✓ Sender (required)
    ✓ Receiver (required)
    ✓ Access Key (required) → Password field
    - Department (dropdown)
    - Document Type (dropdown)
    - Description (textarea)
    - Status (dropdown)
    - Priority (dropdown)
    - Due Date (date picker)
    - Remarks (textarea)
    - Attachment (file upload)

Workflow:
    1. User fills form
    2. Client-side validation
    3. Submit → handleCreateDocument()
    4. Backend encrypts ID + hashes key
    5. Success → Document added to list + stats updated
    6. Error → Display error message
    
Styling:
    - Navy blue (#031B40) CIT branding
    - Clean card layout
    - Responsive inputs
    - Error message display
```

---

#### 3. **DocumentList.jsx** - Display Documents in Grid

```jsx
Component Features:
    - Renders document cards in grid layout
    - Shows summary: Title, Owner, Number, Type, Status, Priority
    - Expandable card reveals:
        * Full encrypted ID (with copy button 📋)
        * QR code image
        * Download QR button
    - Filter/search applied at parent level

Document Card Structure:
    ┌─────────────────────────────────┐
    │ Title                          ▼ │ (expandable)
    │ 👤 Owner: John Doe              │
    │ No: CIT-2026-A1B2C3D4          │
    │ Type: Memo                      │
    ├─────────────────────────────────┤
    │ 🆔 Enc ID: A1B2C3D4E5F6... (12 chars)     │
    │ 📅 Apr 10, 2026                 │
    │ Dept: Registrar                 │
    │ Status: Pending                 │
    │ Priority: High                  │
    ├─────────────────────────────────┤ (expanded)
    │ Encrypted ID (Full):            │
    │ [A1B2C3D4E5F6G7H8I9J0K1] 📋    │
    │                                 │
    │ 🔗 QR Code:                     │
    │ [QR Code Image - 200x200px]     │
    │ ⬇️ Download QR                   │
    └─────────────────────────────────┘

Functions:
    downloadQR(encrypted_id, title)
        → Gets canvas element
        → Converts to PNG
        → Saves as file: {title}_QR.png
        
    copyToClipboard(text)
        → Uses navigator.clipboard
        → Copies encrypted_id to clipboard
```

---

#### 4. **QrLookupPanel.jsx** - QR Resolution Component

```jsx
Input Fields:
    ✓ Encrypted ID (text)
    ✓ Access Key (password field)

Workflow:
    1. User scans QR or pastes encrypted ID
    2. Enters access key
    3. handleSubmit() validates both fields
    4. Calls onLookup(encryptedId, key)
    5. Backend validates key
    6. Frontend displays resolved document in modal

Validation:
    - Encrypted ID cannot be empty
    - Access Key cannot be empty
    - Shows appropriate error messages

States:
    [encryptedId]        → Scanned/Pasted hex string
    [accessKey]          → User-entered password
    loading: boolean     → Submit button loading state
    error: string        → Error message display

Response Handling:
    Success:
        → Sets selectedDocument in App state
        → Opens DocumentDetailModal
        → Shows toast: "QR code resolved successfully"
        
    Error:
        → Shows error message in panel
        → Toast with error text
        → Does not close the panel
```

---

#### 5. **DocumentDetailModal.jsx** - View/Edit Document

```jsx
Features:
    - Modal overlay (dark background)
    - Full document details display
    - Inline editing for selected fields
    - Save button to submit changes

Editable Fields:
    ✓ Status (dropdown)
    ✓ Priority (dropdown)
    ✓ Due Date (date picker)
    ✓ Remarks (textarea)

Read-Only Fields:
    ✓ ID (UUID)
    ✓ Encrypted ID
    ✓ Document Number
    ✓ Reference Code
    ✓ Department
    ✓ Title
    ✓ Type
    ✓ Sender
    ✓ Receiver
    ✓ Owner
    ✓ Description
    ✓ Attachment
    ✓ Created/Updated timestamps

Workflow:
    1. User opens document (via QR resolve or direct view)
    2. Modal displays with current values
    3. User clicks "Edit" → Forms appear on editable fields
    4. User modifies values
    5. User clicks "Save"
    6. Calls onSave(documentId, formState)
    7. Backend validates + saves with access key
    8. Updates document in list
    9. Closes modal

Structure:
    Modal Close Button (X)
    │
    ├─ Header: Document Title
    ├─ Section 1: Identifiers (read-only)
    ├─ Section 2: Metadata (title, type, dept, etc) (read-only)
    ├─ Section 3: Status & Priority (EDITABLE)
    ├─ Section 4: Due Date & Remarks (EDITABLE)
    ├─ Section 5: Transport (sent/receiver) (read-only)
    ├─ Section 6: Audit Trail (created/updated by/at)
    └─ Actions: Edit Toggle | Save Button | Close Button
```

---

#### 6. **DocumentStats.jsx** - Dashboard Cards

```jsx
Displays Statistics:
    
    Card 1: Total Documents
        Icon: 📊
        Value: {total_documents}
        Label: "Total Documents"
        
    Card 2: Unique Owners
        Icon: 👥
        Value: {unique_owners}
        Label: "Unique Owners"
        
    Card 3: This Month
        Icon: 📅
        Value: {documents_this_month}
        Label: "This Month"
        
    Card 4: Status Distribution
        Pending: {count}
        In Process: {count}
        Approved: {count}
        Rejected: {count}
        Completed: {count}

Styling:
    - Navy blue cards (#031B40)
    - White text
    - Large numbers
    - Icons for quick scanning
    - Responsive grid (1-4 columns)
```

---

#### 7. **App.css** - Styling & Responsive Design

```css
Key Styles:

Color Scheme (CIT Branding):
    Primary: #031B40 (Navy Blue)
    Secondary: #00a8ff (Light Blue)
    Background: White / #f8fafc (Light Gray)
    Error: #ef4444 (Red)
    Success: #10b981 (Green)
    Warning: #f59e0b (Amber)

Components:

.app
    min-height: 100vh
    background: #031B40
    
.app-header
    background: Linear gradient navy
    color: white
    padding: 30px 20px
    display: flex
    align-items: center
    
.container
    max-width: 1200px
    margin: 0 auto
    padding: 20px
    
.document-card
    border-radius: 12px
    background: white
    padding: 16px
    box-shadow: 0 4px 12px rgba(0,0,0,0.1)
    transition: all 0.3s ease
    
.document-card:hover
    transform: translateY(-4px)
    box-shadow: 0 8px 20px rgba(0,0,0,0.15)
    
.form-card
    background: white
    border-radius: 12px
    padding: 24px
    box-shadow: 0 4px 12px rgba(0,0,0,0.1)
    margin-bottom: 24px
    
.btn-primary
    background: #031B40
    color: white
    padding: 10px 20px
    border-radius: 8px
    cursor: pointer
    font-weight: 600
    
.btn-primary:hover
    background: #003d82
    
.modal
    position: fixed
    top: 0
    left: 0
    right: 0
    bottom: 0
    background: rgba(0,0,0,0.7)
    display: flex
    align-items: center
    justify-content: center
    z-index: 1000
    
.modal-card
    background: white
    border-radius: 12px
    padding: 24px
    max-width: 600px
    max-height: 90vh
    overflow-y: auto
    
@media (max-width: 768px)
    .document-list
        grid-template-columns: 1fr (mobile)
    
    .search-filter-section
        flex-direction: column
    
    .header-row
        flex-direction: column
```

---

## API Endpoints

### Complete API Reference

```
BASE URL: http://localhost:8000/api

DOCUMENT ENDPOINTS:

1. List Documents (summary)
   GET /documents/
   Query Params:
     - search: {title|doc_type|description|sender|receiver|owner|status|priority|remarks}
     - owner: {name} (case-insensitive)
     - ordering: {created_at|title|owner|due_date|status|priority}
   Response: { results: [ Document ] }

2. Create Document
   POST /documents/
   Headers: 
     - Content-Type: application/json
   Body: {
     title (req), owner (req), sender (req), receiver (req),
     access_key (req), department, doc_type, 
     description, status, priority, due_date, remarks, attachment
   }
   Response: { Document + encrypted_id, access_key_hash status:201 }

3. Get Document Details
   GET /documents/{id}/
   Headers: X-Document-Key: {access_key}
   Response: { Full Document } or { error: "Invalid key" } status:403

4. Update Document
   PATCH /documents/{id}/
   Headers: X-Document-Key: {access_key}
   Body: { status, priority, due_date, remarks, description, etc }
   Response: { Updated Document } status:200

5. Delete Document
   DELETE /documents/{id}/
   Headers: X-Document-Key: {access_key}
   Response: status:204 No Content

6. Resolve QR Code
   GET /documents/resolve_qr/
   Headers: X-Document-Key: {access_key}
   Query Params: encrypted_id
   Response: {
     document: { Full Document },
     resolved_document_id: "{uuid}",
     resolved_document_number: "CIT-...",
     resolved_reference_code: "REF-..."
   }

7. Get Statistics
   GET /documents/stats/
   Response: {
     total_documents: number,
     unique_owners: number,
     documents_this_month: number,
     status_counts: {
       pending, in_process, approved, rejected, completed
     }
   }

8. Get By Owner
   GET /documents/by_owner/
   Query Params: owner (required)
   Response: {
     owner: string,
     count: number,
     documents: [ Document ]
   }

ACTIVITY ENDPOINTS:

1. List All Activities
   GET /activities/
   Query Params: document_id (optional)
   Response: { results: [ Activity ] }

2. Get Activity Details
   GET /activities/{id}/
   Response: { Activity }
```

---

## Security Features (CIA Triad)

### 1. Confidentiality (Encryption)

**IDEA Block Cipher**
```
Algorithm: IDEA (International Data Encryption Algorithm)
Key Size: 128 bits
Block Size: 64 bits
Rounds: 8 + 1 final transformation
Use Case: Encrypts document IDs for non-reversible URL-safe identifiers

Process:
1. Django saves document with UUID
2. At save time, UUID[:8] → encrypted via IDEA cipher
3. Encrypted bytes → converted to hex string
4. Hex stored in encrypted_id field
5. QR code generated from encrypted_id
6. Scanning QR reveals encrypted value (not plaintext UUID)

Strength:
- UUID is unique and unpredictable
- IDEA encryption with 128-bit key extremely resistant to brute-force
- Ciphertext appears random; no information leakage
- Combined with access key, provides dual-layer protection
```

**Access Key Hashing**
```
Algorithm: bcrypt (PBKDF2 in Django default)
Hash Cost: 12 (default Django rounds)
Use Case: Authorization for document access

Process:
1. User creates document with access_key: "MySecretPassword"
2. Backend calls make_password("MySecretPassword")
3. Creates hash: "$2b$12$..." (bcrypt format)
4. Stores hash in access_key_hash field
5. On access attempt, check_password(provided_key, stored_hash)
6. Constant-time comparison prevents timing attacks

Security:
- Plaintext password NEVER stored or logged
- Hash is one-way (cryptographically irreversible)
- Brute-force resistant (expensive hash function)
- Each hash unique even for same password
```

### 2. Integrity (No Tampering)

**Audit Trail**
```
DocumentActivity Model logs:
- Every create, update, delete, lookup operation
- Timestamp of operation
- User (if available) who performed it
- Previous status → New status (for changes)
- Full message describing action
- Cannot be modified without database access

Example Logs:
[2026-04-10 20:25:15] ACTION: Created
  Document CIT-2026-A1B2C3D4 was created. (New: Pending)
  
[2026-04-10 20:27:42] ACTION: Looked Up
  Document CIT-2026-A1B2C3D4 was resolved from QR code.
  
[2026-04-10 20:30:18] ACTION: Updated
  Document CIT-2026-A1B2C3D4 was updated.
  (Status: Pending → In Process)
```

**Database Constraints**
```
Unique Fields:
- id (UUID) → Primary key uniqueness
- encrypted_id → Cannot duplicate encryption
- document_number → CIT-{year}-{uuid_prefix}
- reference_code → REF-{encrypted[:8]}

Non-nullable Fields:
- title, owner, sender, receiver (prevent null tampering)
- access_key_hash (required for security)
- encrypted_id (required for QR)
- created_at, updated_at (track all changes)
```

**Read-Only Fields in API**
```
Frontend cannot modify:
- id, document_number, reference_code (system-generated)
- encrypted_id (generated at creation)
- access_key_hash (write-only input only)
- created_at, updated_at (system timestamps)
- attachment reference (for data validation)

Attempts to modify these are safely ignored or rejected
```

### 3. Availability (No Single Point of Failure)

**No Authentication Bottleneck**
```
Traditional Diagram:
App → Login Server → DB
       (Single point of failure)

CIT System:
App → API (AllowAny) → DB
      (No login required; key-based per-document)

Benefits:
- No login server to crash
- No token expiry issues
- Multiple concurrent users
- QR scanning works offline (key visible in QR)
- Fallback: manual typed entry if scanner fails
```

**Multiple Access Methods**
```
Method 1: QR Code Scanning
- Physical QR printed on documents
- Scanner reads → extracts encrypted_id
- User enters access_key manually
- Fast, convenient

Method 2: Manual Copy-Paste
- User clicks 📋 button on document card
- Encrypted ID copied to clipboard
- Paste into lookup panel
- Enter access_key
- No scanner needed

Method 3: Direct URL (if known)
- GET /api/documents/{uuid}/ 
- Header: X-Document-Key
- Access document directly via REST

Redundancy:
- System stays available if ANY ONE method works
- If scanner broken: use copy-paste
- If network slow: QR still works (data is small)
```

---

## Usage Guide

### For Administrators/Users

#### 1. Create a Document
```
Step 1: Fill "Create Document" Form
  - Title: "Q3 Budget Report"
  - Owner: "John Doe"
  - Sender: "Finance Department"
  - Receiver: "Dean Office"
  - Department: Select from dropdown
  - Document Type: Select (Memo, Letter, Report)
  - Status: Pending
  - Priority: High
  - Due Date: Pick date
  - Access Key: "my-secure-key-123" (remember this!)
  - Description, Remarks: Optional
  - Attachment: Optional PDF/file
  
Step 2: Click "Create Document" button
  → Backend encrypts ID + hashes key
  → Document added to database
  → Success message appears
  → Document now appears in list
  
Important: Share access key with authorized personnel securely
```

#### 2. Find Document via QR Code
```
Step 1: Scan with Mobile Phone
  - Open any QR scanner app
  - Point at printed QR code
  - Scanner extracts encrypted ID (e.g., "A1B2C3D4E5F6G7H8")
  
Step 2: Type Encrypted ID & Access Key
  - Encrypted ID: Paste from scan or type manually
  - Access Key: "my-secure-key-123"
  - Click "Resolve QR Code"
  → Backend validates key
  → Document opens in modal if auth succeeds
  → Error message if key wrong
```

#### 3. Edit Document
```
Step 1: Open Document (via QR or list)
  - Use QR lookup OR Click document to view
  
Step 2: In Modal, Click "Edit"
  - Status dropdown → select new status
  - Priority → select new priority
  - Due Date → change date
  - Remarks → add notes
  
Step 3: Click "Save"
  → Backend validates access key
  → Updates fields in database
  → Audit trail records change
  → List view refreshes
```

#### 4. Copy QR for Distribution
```
Step 1: Open document card (click expand arrow ▶)
  → Shows full encrypted ID
  → Shows QR code image
  
Step 2: Click "📋" Button
  → Encrypted ID copied to clipboard
  → Can paste into messages, forms, etc
  
Step 3: Click "⬇️ Download QR"
  → QR image saved as PNG: "{title}_QR.png"
  → Can print or share digitally
  
Sharing:
  - Print QR on physical document
  - Email QR image to recipients
  - Share encrypted ID via chat + send key separately
```

#### 5. Dashboard Analytics
```
Top section shows:
  📊 Total Documents: 15
     → Sum of all documents ever created
  
  👥 Unique Owners: 8
     → Number of different people who created docs
  
  📅 This Month: 5
     → Documents created in current month
  
  Status Distribution:
     ● Pending: 3
     ● In Process: 2
     ● Approved: 5
     ● Rejected: 1
     ● Completed: 4
     
Insights:
  - Track document workflow progress
  - Monitor team productivity
  - See status bottlenecks
```

---

## File Structure

```
cit-document-tracker/
│
├── backend/
│   ├── db.sqlite3                      # Database
│   ├── manage.py                       # Django CLI
│   ├── requirements.txt                # Python dependencies
│   │
│   ├── document_tracker/
│   │   ├── __init__.py
│   │   ├── settings.py                 # DJ config (DB, apps, REST)
│   │   ├── urls.py                     # Route /api/ to docs.urls
│   │   └── wsgi.py                     # WSGI app
│   │
│   ├── documents/
│   │   ├── __init__.py
│   │   ├── models.py                   # Document + Activity models
│   │   ├── views.py                    # DocumentViewSet, activities
│   │   ├── serializers.py              # DocumentSerializer, activity
│   │   ├── urls.py                     # DRF router (documents, activities)
│   │   ├── admin.py                    # Django admin config
│   │   └── migrations/
│   │       ├── __init__.py
│   │       ├── 0001_initial.py
│   │       ├── 0002_document_description_...py
│   │       ├── 0003_document_attachment_...py
│   │       └── 0004_document_access_key_hash.py
│   │
│   └── encryption/
│       ├── __init__.py
│       └── idea.py                     # IDEA cipher implementation
│
├── frontend/
│   ├── package.json                    # npm dependencies
│   ├── vite.config.js                  # Vite config
│   ├── index.html                      # HTML entry
│   │
│   └── src/
│       ├── main.jsx                    # React entry
│       ├── App.jsx                     # Main app container
│       ├── App.css                     # App styles
│       ├── index.css                   # Global styles
│       │
│       ├── components/
│       │   ├── DocumentForm.jsx        # Create form
│       │   ├── DocumentForm.css        # Form styles
│       │   ├── DocumentList.jsx        # Grid + cards
│       │   ├── DocumentList.css        # Card styles
│       │   ├── DocumentStats.jsx       # Dashboard cards
│       │   ├── DocumentStats.css       # Stats styles
│       │   ├── DocumentDetailModal.jsx # View/edit modal
│       │   ├── QrLookupPanel.jsx       # QR resolution
│       │   └── LoginForm.jsx           # (unused)
│       │
│       └── assets/
│           ├── school-logo.png
│           └── college-logo.png
│
├── README.md                           # Project overview
├── DOCUMENTATION.md                    # This file
└── .gitignore
```

---

## Setup Instructions

### Prerequisites
```
- Python 3.10+
- Node.js 16+
- pip (Python package manager)
- npm (Node package manager)
```

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional, for Django admin)
python manage.py createsuperuser

# Start development server
python manage.py runserver 8000
# API available at http://localhost:8000/api/
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# App available at http://localhost:5173/
```

### Access Application
- Frontend: http://localhost:5173/
- API Docs: http://localhost:8000/api/ (browsable)
- Django Admin: http://localhost:8000/admin/

---

## Technical Specifications

| Aspect | Details |
|--------|---------|
| **Backend Framework** | Django 5.0.1 + DRF 3.14.0 |
| **Frontend Framework** | React 18 + Vite 5.4.21 |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Authentication** | Key-based (no users/tokens) |
| **Encryption** | IDEA cipher (128-bit) |
| **Hashing** | bcrypt via Django |
| **API Style** | RESTful (JSON) |
| **CORS** | Configured for localhost |
| **Styling** | CSS3 + Responsive Design |
| **QR Generation** | qrcode.react library |
| **HTTP Client** | Axios |
| **Notifications** | react-hot-toast |

---

This documentation provides complete technical coverage of the CIT Document Tracker system for reference and further development.
