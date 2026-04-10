# CIT Document Tracker - Documentation Index

## 📚 Complete Documentation Package

This directory contains comprehensive documentation for the CIT Document Tracker system. Use this index to navigate to the information you need.

---

## Files Overview

### 1. **README.md** (Project Overview)
   - Quick project description
   - Key features
   - Basic project structure
   - Setup instructions overview
   - **Use this for:** First-time project overview

### 2. **DOCUMENTATION.md** (Comprehensive Guide)
   - System overview and architecture
   - Core components breakdown (Backend & Frontend)
   - Complete API reference (all endpoints with parameters)
   - CIA Triad security analysis (Confidentiality, Integrity, Availability)
   - File structure and project organization
   - Technical specifications
   - **Use this for:** Understanding the complete system architecture and security implementation

### 3. **UI_GUIDE.md** (Visual Reference)
   - UI layout mockups with ASCII diagrams
   - Component visual descriptions
   - End-to-end workflow examples
   - QR scanning workflow
   - Security flow diagrams
   - Access control examples
   - Performance metrics
   - Browser compatibility
   - Accessibility features
   - **Use this for:** Understanding user interface, workflows, and visual design

### 4. **FRONTEND_SOURCE.md** (React Code)
   - Complete source code for all React components:
     - App.jsx (Main container)
     - DocumentForm.jsx (Create document)
     - DocumentList.jsx (Display grid)
     - DocumentDetailModal.jsx (View/Edit)
     - QrLookupPanel.jsx (QR resolution)
     - DocumentStats.jsx (Dashboard)
   - Fully annotated with comments
   - Function explanations
   - State management details
   - API call documentation
   - **Use this for:** Frontend development, component modification, understanding React implementation

### 5. **BACKEND_SOURCE.md** (Django Code)
   - Complete source code for backend:
     - models.py (Database models)
     - serializers.py (Input/Output)
     - views.py (API endpoints)
     - urls.py (URL routing)
     - settings.py (Configuration)
     - admin.py (Django admin)
   - Fully annotated with docstrings
   - Method explanations
   - Database schema details
   - **Use this for:** Backend development, API modification, database schema understanding

---

## Quick Navigation Guide

### 🎯 For Different Roles

#### **Project Manager / Stakeholder**
1. Start with: README.md
2. Review: UI_GUIDE.md (see the actual system)
3. Check: DOCUMENTATION.md (CIA security features)

#### **Frontend Developer**
1. Read: FRONTEND_SOURCE.md (complete React code)
2. Reference: UI_GUIDE.md (layout & design)
3. Understand: DOCUMENTATION.md (API endpoints section)

#### **Backend Developer**
1. Read: BACKEND_SOURCE.md (complete Django code)
2. Reference: DOCUMENTATION.md (API endpoints section)
3. Check: models.py (database schema)

#### **DevOps / System Administrator**
1. Read: DOCUMENTATION.md (architecture & setup)
2. Check: BACKEND_SOURCE.md (settings.py)
3. Review: Technical specifications (database, dependencies)

#### **QA / Tester**
1. Review: UI_GUIDE.md (workflows & features)
2. Read: DOCUMENTATION.md (API endpoints for testing)
3. Reference: FRONTEND_SOURCE.md (component behavior)

#### **Security Auditor**
1. Start with: DOCUMENTATION.md (CIA Triad section)
2. Review: BACKEND_SOURCE.md (encryption & serializers)
3. Check: Security flow diagrams in UI_GUIDE.md

---

## Key Concepts Quick Reference

### Architecture
- **Frontend**: React 18 + Vite + Axios
- **Backend**: Django 5.0.1 + Django REST Framework
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Encryption**: IDEA cipher (128-bit, 8 rounds)
- **Hashing**: bcrypt (for access keys)

### Core Entities
- **Document**: Main document with metadata, status, priority
- **DocumentActivity**: Audit trail for all operations
- **Encrypted ID**: IDEA-encrypted UUID (for QR codes)
- **Access Key**: User-defined password (bcrypt hashed)

### API Pattern
```
GET    /api/documents/              - List all documents
POST   /api/documents/              - Create document
GET    /api/documents/{id}/         - Get document (needs access key)
PATCH  /api/documents/{id}/         - Update document (needs access key)
DELETE /api/documents/{id}/         - Delete document (needs access key)
GET    /api/documents/resolve_qr/   - Resolve QR code (needs access key)
GET    /api/documents/stats/        - Get statistics
GET    /api/activities/             - List audit trail
```

### Security (CIA Triad)
- **Confidentiality**: IDEA encryption for IDs + bcrypt for keys
- **Integrity**: Audit trail + database constraints + read-only fields
- **Availability**: No auth bottleneck + multiple access methods (QR + manual)

---

## Setup Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- pip, npm

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Access Application
- Frontend: http://localhost:5173/
- API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

---

## File Structure

```
cit-document-tracker/
├── README.md                    ← Project overview
├── DOCUMENTATION.md             ← Complete system docs (THIS IS THE MAIN REFERENCE)
├── UI_GUIDE.md                 ← Visual layouts & workflows
├── FRONTEND_SOURCE.md          ← React source code
├── BACKEND_SOURCE.md           ← Django source code
│
├── backend/
│   ├── documents/
│   │   ├── models.py           (See BACKEND_SOURCE.md)
│   │   ├── views.py            (See BACKEND_SOURCE.md)
│   │   ├── serializers.py      (See BACKEND_SOURCE.md)
│   │   ├── urls.py             (See BACKEND_SOURCE.md)
│   │   ├── admin.py            (See BACKEND_SOURCE.md)
│   │   └── migrations/
│   ├── encryption/
│   │   └── idea.py             (IDEA cipher implementation)
│   ├── manage.py
│   ├── requirements.txt
│   └── document_tracker/
│       ├── settings.py         (See BACKEND_SOURCE.md)
│       ├── urls.py
│       └── wsgi.py
│
└── frontend/
    ├── src/
    │   ├── App.jsx             (See FRONTEND_SOURCE.md)
    │   ├── App.css
    │   ├── main.jsx
    │   └── components/
    │       ├── DocumentForm.jsx         (See FRONTEND_SOURCE.md)
    │       ├── DocumentList.jsx         (See FRONTEND_SOURCE.md)
    │       ├── DocumentDetailModal.jsx  (See FRONTEND_SOURCE.md)
    │       ├── QrLookupPanel.jsx       (See FRONTEND_SOURCE.md)
    │       └── DocumentStats.jsx        (See FRONTEND_SOURCE.md)
    ├── package.json
    ├── vite.config.js
    └── index.html
```

---

## Common Questions & Where to Find Answers

### "How does the system work?"
→ Read: DOCUMENTATION.md (System Overview + Architecture sections)

### "How do I create a document?"
→ Read: UI_GUIDE.md (Feature Walkthrough Examples section)

### "How is encryption implemented?"
→ Read: DOCUMENTATION.md (CIA Triad - Confidentiality section) + BACKEND_SOURCE.md (models.py)

### "What are all the API endpoints?"
→ Read: DOCUMENTATION.md (API Endpoints section)

### "How do I modify the frontend?"
→ Read: FRONTEND_SOURCE.md + UI_GUIDE.md

### "How do I add a new backend feature?"
→ Read: BACKEND_SOURCE.md + DOCUMENTATION.md (Backend Architecture section)

### "How does QR code scanning work?"
→ Read: UI_GUIDE.md (QR Code Scan Workflow section) + FRONTEND_SOURCE.md (QrLookupPanel.jsx)

### "How is data secured?"
→ Read: DOCUMENTATION.md (Security Features - CIA Triad section)

### "How do I set up the project?"
→ Read: DOCUMENTATION.md (Setup Instructions section) or README.md

---

## Development Workflow

### Making Changes to Frontend
1. Locate component in: FRONTEND_SOURCE.md
2. Understand component structure
3. Reference UI design in: UI_GUIDE.md
4. Make changes to: `frontend/src/components/`
5. Verify against API in: DOCUMENTATION.md (API Endpoints section)

### Making Changes to Backend
1. Locate code in: BACKEND_SOURCE.md
2. Check affected models: models.py section
3. Update serializers if needed: serializers.py section
4. Check API spec: DOCUMENTATION.md (API Endpoints section)
5. Make changes to: `backend/documents/`

### Adding New Feature
1. Plan in: DOCUMENTATION.md (Core Components section)
2. Design UI in: UI_GUIDE.md
3. Implement frontend in: FRONTEND_SOURCE.md components
4. Implement backend in: BACKEND_SOURCE.md
5. Document in: Update relevant docs

---

## Performance & Optimization

### Current Benchmarks
- Page load: ~500-800ms
- API response: ~30-300ms (depending on operation)
- QR generation: ~20-30ms
- Database queries: ~5-100ms

See: UI_GUIDE.md (Performance Metrics section)

---

## Deployment Notes

### Database
- Development: SQLite
- Production: PostgreSQL (recommended)
- See: BACKEND_SOURCE.md (settings.py for configuration)

### Environment Variables
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
ENCRYPTION_KEY=16byte_key_12345
DATABASE_URL=postgresql://user:password@host/db
```

---

## Support & Troubleshooting

### Common Issues
1. **Port already in use**: Change port in runserver command
2. **CORS errors**: Check CORS_ALLOWED_ORIGINS in settings.py
3. **Database errors**: Run `python manage.py migrate`
4. **File not found**: Check file paths are relative to project root

### Getting Help
- Architecture questions: DOCUMENTATION.md
- Code questions: FRONTEND_SOURCE.md or BACKEND_SOURCE.md
- UI/UX questions: UI_GUIDE.md
- Setup issues: README.md

---

## Version Information

- **Django**: 5.0.1
- **Django REST Framework**: 3.14.0
- **React**: 18.x
- **Vite**: 5.4.21
- **Python**: 3.10+
- **Node.js**: 16+

---

## Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- React Documentation: https://react.dev/
- Vite Documentation: https://vitejs.dev/

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-10 | Initial comprehensive documentation package |

---

**Last Updated**: April 10, 2026

**Maintainer**: CIT Development Team

---

## Navigation Quick Links

| Document | Purpose | Best For |
|----------|---------|----------|
| [README.md](README.md) | Project overview | Getting started |
| [DOCUMENTATION.md](DOCUMENTATION.md) | Complete reference | Understanding system |
| [UI_GUIDE.md](UI_GUIDE.md) | Visual guide | UI/UX reference |
| [FRONTEND_SOURCE.md](FRONTEND_SOURCE.md) | React code | Frontend development |
| [BACKEND_SOURCE.md](BACKEND_SOURCE.md) | Django code | Backend development |

---

**Start here if you're**: 
- 🆕 **New to project**: README.md → DOCUMENTATION.md
- 👨‍💻 **Developer**: Your role's file (FRONTEND/BACKEND_SOURCE.md)
- 🎨 **Designer**: UI_GUIDE.md
- 🔒 **Security**: DOCUMENTATION.md (CIA section)
- 📊 **Manager**: README.md + DOCUMENTATION.md (Overview)
