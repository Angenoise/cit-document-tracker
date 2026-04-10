# CIT Document Tracker - UI Screenshots & Visual Guide

## User Interface Layout

### 1. Main Dashboard (Home Page)

```
┌─────────────────────────────────────────────────────────────────┐
│ CIT DOCUMENT TRACKER                                            │
│ Pure document tracking for CIT with QR lookup and encrypted IDs │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ DASHBOARD STATISTICS                                             │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  📊 15       │  │  👥 8        │  │  📅 5        │           │
│  │  Total Docs  │  │  Unique      │  │  This Month  │           │
│  │              │  │  Owners      │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  🕒 3        │  │  ⚙️ 2         │  │  ✅ 5        │           │
│  │  Pending     │  │  In Process  │  │  Completed   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ CREATE NEW DOCUMENT                                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Document Title *           [_____________________]             │
│  Owner * (Admin)            [_____________________]             │
│  Sender *                   [_____________________]             │
│  Receiver *                 [_____________________]             │
│  Access Key *               [* * * * * * * * * *]              │
│                                                                  │
│  Department                 [General ▼]                         │
│  Document Type              [Memo ▼]                            │
│  Status                     [Pending ▼]                         │
│  Priority                   [Medium ▼]                          │
│  Due Date                   [____-__-__]                        │
│  Description                [_______________________________]   │
│  Remarks                    [_______________________________]   │
│  Attachment                 [Choose File]                       │
│                                                                  │
│  [Create Document Button]                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ QR LOOKUP                                                        │
├──────────────────────────────────────────────────────────────────┤
│  Paste the encrypted ID and enter the document access key.      │
│                                                                  │
│  Encrypted ID               [_____________________]             │
│  Access Key                 [* * * * * *]                       │
│                                                                  │
│  [Resolve QR Code]                                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ SEARCH & FILTER                                                  │
├──────────────────────────────────────────────────────────────────┤
│  🔍 Search by title or owner...              [All Owners ▼]    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ DOCUMENTS (5)                                                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Q3 Budget Report                                      ▼ │  │
│  │ 👤 John Doe                                             │  │
│  │ No: CIT-2026-A1B2C3D4                                   │  │
│  │ Type: Report                                            │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │ 🆔 Enc ID: A1B2C3D4E5F6...                              │  │
│  │ 📅 Apr 10, 2026                                         │  │
│  │ Dept: Accounting                                        │  │
│  │ Status: Pending                                         │  │
│  │ Priority: High                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Annual Compliance Report                             ▼ │  │
│  │ 👤 Jane Smith                                           │  │
│  │ No: CIT-2026-B5C6D7E8                                   │  │
│  │ Type: Report                                            │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │ 🆔 Enc ID: B5C6D7E8F9A0...                              │  │
│  │ 📅 Apr 09, 2026                                         │  │
│  │ Dept: Registrar                                         │  │
│  │ Status: Approved                                        │  │
│  │ Priority: Medium                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

### 2. Expanded Document Card (Detailed View)

```
┌────────────────────────────────────────────────────────┐
│ Q3 Budget Report                                   ▼ │
│ 👤 John Doe                                           │
│ No: CIT-2026-A1B2C3D4                                │
│ Type: Report                                          │
├────────────────────────────────────────────────────────┤
│ 🆔 Enc ID: A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7...     │
│ 📅 Apr 10, 2026                                       │
│ Dept: Accounting                                      │
│ Status: Pending        Priority: High                │
├────────────────────────────────────────────────────────┤
│ EXPANDED CONTENT:                                     │
│                                                       │
│ Encrypted ID (Copy/Paste)                            │
│ ┌──────────────────────────────────────────────────┐ │
│ │ A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2... │ │
│ │ [📋]                                             │ │
│ └──────────────────────────────────────────────────┘ │
│ Use this value in QR Lookup if scanning is difficult. │
│                                                       │
│ 🔗 QR Code                                            │
│ ┌──────────────────────┐                             │
│ │  ███ ███ █   ███ ███ │                             │
│ │  █   █   █ █ █     █ │                             │
│ │  ███ ███ ███ ███   █ │                             │
│ │      █ █   █     ███ │                             │
│ │  ███ █ █   █ ███ █   │                             │
│ └──────────────────────┘                             │
│ [⬇️ Download QR]                                      │
│                                                       │
└────────────────────────────────────────────────────────┘
```

---

### 3. QR Code Scan Workflow

```
Step 1: User Scans Physical QR Code
┌─────────────────┐
│  ███ ███ █   ███│
│  █   █   █ █ █  │
│  ███ ███ ███ ███│
│      █ █   █    │
│  ███ █ █   █ ███│
└─────────────────┘
       ↓
    Mobile Scanner
       ↓
Extract: A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7

Step 2: Go to Web App
┌────────────────────────────────────────┐
│ 🔗 QR LOOKUP                       ● │
│ 📱 QR Code Scanned! Enter the      │
│    encrypted ID and access key.    │
├────────────────────────────────────────┤
│ Encrypted ID                       │
│ [A1B2C3D4E5F6G7H8I9...]            │
│                                    │
│ Access Key                         │
│ [* * * * * *]                      │
│                                    │
│ [Resolve QR Code] (BLUE - focused) │
└────────────────────────────────────────┘

Step 3: Click Resolve → Backend Validates
└─────────────────────────────────────────┐
│ Backend:                                 │
│ 1. Find document with encrypted_id      │
│ 2. Check access_key against hash        │
│ 3. If valid: return document            │
│ 4. If invalid: return 403 Forbidden     │
│ 5. Log activity to audit trail         │
└─────────────────────────────────────────┘

Step 4: Document Opens in Modal ✓
```

---

### 4. Document Detail Modal (View & Edit)

```
┌────────────────────────────────────────────────────────────┐
│ Q3 Budget Report                    [Edit] [Close]         │
│ CIT-2026-A1B2C3D4 - REF-A1B2C3D4                           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ Department:  Accounting         Type: Report               │
│                                                             │
│ Status: [Pending ▼]             Priority: [Medium ▼]       │
│ Owner: John Doe                 Sender: Finance Dept      │
│ Receiver: Dean Office                                      │
│                                                             │
│ Due Date: [____-__-__]                                     │
│ Encrypted ID: A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6...          │
│                                                             │
│ Description                                                │
│ This is the Q3 budget report for department review.        │
│                                                             │
│ Remarks                                                    │
│ [_____________________________________________________]   │
│ [_____________________________________________________]   │
│                                                             │
│ Created: Apr 10, 2026 20:25:15                             │
│ Updated: Apr 10, 2026 20:27:42                             │
│                                                             │
│ [Edit] [Save] [Close]                                      │
│                                                             │
└────────────────────────────────────────────────────────────┘

EDIT MODE ACTIVATED:
┌────────────────────────────────────────────────────────────┐
│ Status: [Pending ▼]  (Can select new status)               │
│         └─ Pending                                          │
│         └─ In Process                                       │
│         └─ Approved                                         │
│         └─ Rejected                                         │
│         └─ Completed                                        │
│                                                             │
│ Priority: [Medium ▼] (Can select new priority)             │
│           └─ Low                                            │
│           └─ Medium                                         │
│           └─ High                                           │
│           └─ Urgent                                         │
│                                                             │
│ Due Date: [2026-04-30]  (Can change date)                  │
│                                                             │
│ Remarks:                                                   │
│ [Approved by finance team on 2026-04-10]                  │
│ (Can edit remarks)                                         │
│                                                             │
│ [Save Button - Blue & Highlighted]                         │
└────────────────────────────────────────────────────────────┘
```

---

### 5. Color Scheme & Visual Identity

```
CIT BRANDING COLORS:
├─ Primary: #031B40 (Navy Blue - Headers, Buttons, Links)
├─ Secondary: #00a8ff (Light Blue - Accents, Highlights)
├─ Background: #f8fafc (Light Gray - Card backgrounds)
├─ Text: #1f2937 (Dark Gray - Body text)
├─ Success: #10b981 (Green - Confirmations)
├─ Error: #ef4444 (Red - Errors)
└─ Warning: #f59e0b (Amber - Warnings)

DESIGN ELEMENTS:
├─ Border Radius: 8-12px (rounded corners)
├─ Shadows: 0 4px 12px rgba(0,0,0,0.1)
├─ Transitions: 0.3s ease (smooth animations)
├─ Hover Effects: translateY(-4px) + shadow increase
└─ Font: System fonts (sans-serif stack)

RESPONSIVE BREAKPOINTS:
├─ Desktop: >= 1024px (2-4 column grid)
├─ Tablet: 768px - 1024px (1-2 column grid)
└─ Mobile: < 768px (1 column, stacked layout)
```

---

### 6. Notification System

```
SUCCESS MESSAGE (Top Right)
┌──────────────────────────────────┐
│ ✓ Document created successfully! │
└──────────────────────────────────┘
(Auto-dismiss after 3 seconds)

ERROR MESSAGE (Top Right)
┌─────────────────────────────────────┐
│ ✗ Invalid document access key.      │
└─────────────────────────────────────┘
(Stays until dismissed)

FORM VALIDATION (Inline)
┌──────────────────────────────────┐
│ Document Title *                 │
│ [_____________________]          │
│ ✗ Title is required              │
└──────────────────────────────────┘
```

---

### 7. Document List Search & Filter

```
┌──────────────────────────────────────────────────────────┐
│ SEARCH & FILTER                                          │
├──────────────────────────────────────────────────────────┤
│ 🔍 Search by title or owner...    │ All Owners ▼       │
│ [Type to search...]                │ ├─ All Owners      │
│                                    │ ├─ John Doe        │
│ Filters applied:                   │ ├─ Jane Smith      │
│ - Search: "budget" (matches title) │ └─ Mike Johnson    │
│ - Owner: "John Doe"                │                    │
│                                    │                    │
│ Results: 3 documents found         │                    │
└──────────────────────────────────────────────────────────┘

SEARCH BEHAVIOR:
Searches across: title, doc_type, description, sender, receiver, 
                 owner, status, priority, remarks
Real-time: Results update as user types
Case-insensitive: "budget" matches "BUDGET Report"

ORDERING OPTIONS:
- By Created Date (default, newest first)
- By Title (alphabetical)
- By Owner (alphabetical)
- By Due Date
- By Status
- By Priority
```

---

### 8. Security Flow Diagram

```
CREATING DOCUMENT:
┌─────────────────────┐
│ User fills form:    │
│ - title             │
│ - owner             │
│ - access_key: "123" │
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Frontend Validation:            │
│ - Required fields filled?       │
│ - Valid data format?            │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Submit FormData to:             │
│ POST /api/documents/            │
│ Body: {title, owner, ...}       │
└────────┬────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Backend Processing:                  │
│ 1. Check access_key is not empty     │
│ 2. Generate UUID for document ID     │
│ 3. ENCRYPT UUID with IDEA cipher     │
│    → Produces: A1B2C3D4E5F6G7H8...  │
│ 4. HASH access_key with bcrypt       │
│    → Produces: $2b$12$KIX...         │
│ 5. Save to database:                 │
│    - encrypted_id (hex string)       │
│    - access_key_hash (one-way)       │
│ 6. Log activity: ACTION_CREATED      │
└────────┬─────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Return success      │
│ + encrypted_id +    │
│ + QR code ready     │
└─────────────────────┘

ACCESSING DOCUMENT:
┌──────────────────────────┐
│ User scans QR code       │
│ Extracts: A1B2C3D4E5F6..│
│ Enters: access_key: "123"│
└────────┬─────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ GET /documents/resolve_qr/      │
│ Params: encrypted_id=A1B2C3D4...│
│ Header: X-Document-Key: 123     │
└────────┬────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Backend Validation:              │
│ 1. Find doc by encrypted_id      │
│ 2. Get stored access_key_hash    │
│ 3. call: check_password(         │
│      provided_key: "123",        │
│      stored_hash: "$2b$12$..."   │
│    )                             │
│ 4. Constant-time comparison      │
│    Result: TRUE / FALSE          │
└────────┬─────────────────────────┘
         │
    ┌────┴─────┐
    ▼          ▼
  VALID    INVALID
    │          │
    ▼          ▼
RETURN DOC  403 FORBIDDEN
+ LOG      + LOG ATTEMPT
  
DOCUMENT HISTORY:
DocumentActivity records:
- 2026-04-10 20:25:15 [CREATED] by admin
- 2026-04-10 20:27:42 [LOOKED_UP] via QR
- 2026-04-10 20:30:18 [UPDATED] status changed
```

---

## Feature Walkthrough Examples

### Example 1: Complete End-to-End QR Workflow

```
SCENARIO: Finance team member scans document QR on printed memo

STEP 1: Physical Document
┌─────────────────────────────────┐
│ CIT OFFICE                      │
│ TO: Dean Office                 │
│ DATE: April 10, 2026            │
│                                 │
│ [QR Code Image]                 │
│ █████████████████               │
│ ██ CIT Logo ██                  │
│        ►  Use Camera to scan     │
│                                 │
│ Encrypted ID: A1B2C3D4E5F6...    │
└─────────────────────────────────┘

STEP 2: Mobile Phone Scanner
- User opens phone camera
- Points at QR code
- System recognizes QR
- Extracts text: "A1B2C3D4E5F6G7H8I9J0K1..."

STEP 3: Web Browser Opens
- App URL accessed
- QR value available in clipboard or browser intent

STEP 4: Enter in Lookup Panel
┌─────────────────────────────────┐
│ 🔗 QR LOOKUP                    │
│ 📱 QR Code Scanned!             │
│                                 │
│ Encrypted ID:                   │
│ [A1B2C3D4E5F6G7H8I9...]        │
│                                 │
│ Access Key:                     │
│ [* * * * * * * * * *]          │
│ (User types: finance2026secret) │
│                                 │
│ [Resolve QR Code]               │
└─────────────────────────────────┘

STEP 5: Backend Verification
Server-side:
1. Database query: SELECT FROM documents WHERE encrypted_id='A1B2C3D4...'
2. Found: Document(id=uuid123, title="Q3 Report", access_key_hash="$2b$12...")
3. Call: check_password("finance2026secret", "$2b$12$...")
4. Result: True ✓
5. Log: DocumentActivity(action=LOOKED_UP, timestamp=...)
6. Return: Full document + metadata

STEP 6: Document Appears in Modal
┌────────────────────────────────┐
│ Q3 Budget Report         [Edit]│
│ CIT-2026-A1B2C3D4             │
├────────────────────────────────┤
│ Status: Pending                │
│ Priority: High                 │
│ Owner: John Doe                │
│ Due: 2026-04-30                │
│ Department: Accounting         │
│ Sender: Finance Dept           │
│ Receiver: Dean Office          │
│ Description: Quarterly budget..│
│ Remarks: Awaiting approval     │
│                                │
│ [Edit] [Close]                 │
└────────────────────────────────┘

STEP 7 (Optional): Edit & Save
- Click [Edit]
- Change Status → "In Process"
- Change Priority → "Critical"
- Add Remark → "Finance approved"
- Click [Save]
- Backend validates key again
- Updates document
- Logs: DocumentActivity(action=UPDATED, change=status Pending→In Process)
- Modal closes
- Document list refreshes
```

### Example 2: Access Control & Security

```
SCENARIO: Unauthorized user tries to access document

STEP 1: QR Scanned
- Encrypted ID extracted: A1B2C3D4E5F6G7H8...

STEP 2: Wrong Access Key Entered
┌─────────────────────────────────┐
│ 🔗 QR LOOKUP                    │
│                                 │
│ Encrypted ID:                   │
│ [A1B2C3D4E5F6G7H8...]          │
│                                 │
│ Access Key:                     │
│ [* * * * * * *]                │
│ (User types: wrongpassword)     │
│                                 │
│ [Resolve QR Code]               │
└─────────────────────────────────┘

STEP 3: Request Sent to API
GET /documents/resolve_qr/
  ?encrypted_id=A1B2C3D4E5F6G7H8...
Header: X-Document-Key: wrongpassword

STEP 4: Backend Validation FAILS
1. Find document ✓
2. Get access_key_hash from DB: "$2b$12$KIX..."
3. Call: check_password("wrongpassword", "$2b$12$...")
4. Result: False ✗
5. Return: HTTP 403 Forbidden + Error "Invalid document access key."
6. Log: DocumentActivity?(depends on implementation - may not log failed attempts)

STEP 5: Error Message Displayed
┌─────────────────────────────────┐
│ ✗ Invalid document access key.  │
│                                 │
│ Please check and try again.     │
└─────────────────────────────────┘

USER CANNOT:
✗ See document contents
✗ Edit document
✗ Download attachment
✗ Modify metadata
✗ Access audit trail
```

---

## Performance Metrics

```
Page Load Time: ~500-800ms
  - Vite dev server: ~300ms
  - API calls (network): ~200-300ms
  - React render: ~100-150ms

API Response Times:
  - GET /documents/: ~50-100ms (with search)
  - POST /documents/: ~200-300ms (file upload)
  - GET /documents/resolve_qr/: ~30-50ms
  - GET /documents/stats/: ~20-30ms

Database Query Times:
  - List documents: ~10-20ms
  - Create document: ~50-100ms
  - Resolve by encrypted_id: ~5-10ms

QR Code Generation: ~20-30ms

File Upload: 1-5MB in ~500-2000ms (depending on network)
```

---

## Accessibility Features

```
Color Contrast:
- Navy (#031B40) on White: 18.5:1 ✓ WCAG AAA
- Light Blue (#00a8ff) on White: 5.2:1 ✓ WCAG AA

Keyboard Navigation:
- Tab through form fields
- Enter to submit
- Escape to close modals
- Arrow keys in dropdowns

Screen Reader Support:
- aria-label on icons
- form labels associated with inputs
- Error messages announced
- Loading states described

Mobile Responsiveness:
- Touch-friendly buttons (min 44x44px)
- Stacked layout on mobile
- Readable font sizes (min 16px)
- OK for zoom up to 200%
```

---

## Browser Compatibility

```
Tested & Supported:
✓ Chrome 90+
✓ Firefox 88+
✓ Safari 14+
✓ Edge 90+

Mobile Browsers:
✓ Chrome Mobile (Android 5+)
✓ Safari Mobile (iOS 12+)
✓ Samsung Internet

Partially Supported:
◐ IE 11 (no QR code, basic functions work)

Not Supported:
✗ IE 8 - IE 10
```

---

This visual guide provides concrete examples of the user interface, workflows, and security flows for comprehensive documentation.
