# CIT Document Tracker with QR Generator and IDEA Encryption

A full-stack web application for tracking documents with IDEA encryption and QR code generation. Features a Django REST API backend, React frontend with Vite, and SQLite database.

## Features

- **Document Management**: Create, view, update, and delete documents
- **Realistic Workflow**: Department, document number, reference code, due date, status, and priority tracking
- **Attachments**: Optional document file uploads for a more realistic workflow
- **Audit Trail**: Track document activity such as create, update, delete, and QR lookup actions
- **Authentication**: User registration, login, token auth, and browsable API login
- **Admin Tools**: Manage users, groups, and auth tokens from the backend
- **IDEA Encryption**: 128-bit key encryption with 8 rounds + final transformation
- **QR Code Generation**: Automatic QR code generation for encrypted document IDs
- **QR Lookup**: Resolve an encrypted QR code value back into the stored document record
- **Dashboard Analytics**: View statistics (total documents, unique owners, monthly count)
- **Search & Filter**: Search by title/owner and filter by owner
- **Responsive UI**: Clean, modern interface that works on desktop and mobile
- **Secure Backend**: Encryption key never exposed to frontend
- **RESTful API**: Well-structured API endpoints with proper error handling

## Project Structure

```
cit-document-tracker/
├── backend/
│   ├── document_tracker/          # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py            # Database & app configuration
│   │   ├── urls.py                # URL routing
│   │   └── wsgi.py                # WSGI application
│   ├── documents/                 # Django app
│   │   ├── models.py              # Document model with encryption
│   │   ├── views.py               # API ViewSets
│   │   ├── serializers.py         # DRF serializers
│   │   ├── urls.py                # API routes
│   │   ├── admin.py               # Django admin config
│   │   └── migrations/            # Database migrations
│   ├── encryption/                # IDEA encryption module
│   │   ├── __init__.py
│   │   └── idea.py                # IDEA algorithm implementation
│   ├── manage.py                  # Django management script
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Environment variables template
│
├── frontend/
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── DocumentForm.jsx    # Create document form
│   │   │   ├── DocumentForm.css
│   │   │   ├── DocumentList.jsx    # Document cards with QR
│   │   │   ├── DocumentList.css
│   │   │   ├── DocumentStats.jsx   # Statistics display
│   │   │   └── DocumentStats.css
│   │   ├── App.jsx                 # Main app component
│   │   ├── App.css
│   │   ├── main.jsx                # React entry point
│   │   └── index.css               # Global styles
│   ├── index.html                 # HTML template
│   ├── package.json               # Node dependencies
│   ├── vite.config.js             # Vite configuration
│   ├── .env.example               # Frontend env vars
│   └── .gitignore
│
├── README.md                      # This file
└── SETUP.md                       # Detailed setup instructions
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- SQLite (included with Python)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env values if needed

# Generate encryption key
python -c "import os; print(os.urandom(16).hex().upper())"
# Add the output to the ENCRYPTION_KEY in .env

# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser for Django admin
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

The backend will be available at `http://localhost:8000/api`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Django Admin**: http://localhost:8000/admin (use superuser credentials)

## IDEA Encryption Algorithm

### Implementation Details

- **Key Size**: 128 bits (16 bytes)
- **Block Size**: 64 bits (8 bytes)
- **Rounds**: 8 + final transformation
- **Subkeys**: 52 total (6 per round × 8 + 4 for final)
- **Operations**: Modular addition, multiplication (mod 2^16 + 1), and XOR

### Encryption Process

1. Document is created with unique UUID
2. First 8 characters of UUID are extracted
3. UUID is padded to 8 bytes with null characters
4. IDEA cipher encrypts the 8-byte block using 128-bit key
5. Encrypted result is converted to hexadecimal string
6. QR code is generated with encrypted ID

### Key Features

- Modular multiplication uses modulus prime (2^16 + 1 = 65537)
- Full key schedule generates 52 subkeys from 128-bit key
- Each round applies complex transformations (MA-box operations)
- Final transformation doesn't include key mixing

## API Documentation

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### List Documents
```
GET /documents/
Query params: search=<term>, owner=<name>, ordering=<field>
Response: List of documents with pagination
```

#### Create Document
```
POST /documents/
Body: {
    "department": "General|Registrar|Dean Office|Guidance Office|Accounting|Library",
    "title": "string",
    "doc_type": "Memo|Letter|Report",
    "description": "string",
    "sender": "string",
    "receiver": "string",
    "status": "Pending|In Process|Approved|Rejected|Completed",
    "priority": "Low|Medium|High|Urgent",
    "due_date": "YYYY-MM-DD",
    "remarks": "string",
    "owner": "string (admin only)",
    "attachment": "file (optional)"
}
Response: Created document with encrypted_id and QR code data
```

#### Resolve QR Code
```
GET /documents/resolve_qr/?encrypted_id=<qr-value>
Response: The matched document, resolved document ID, document number, and reference code
```

#### View Activities
```
GET /activities/?document_id=<uuid>
Response: Audit trail entries for a document
```

#### Retrieve Document
```
GET /documents/{id}/
Response: Single document details
```

#### Update Document
```
PUT /documents/{id}/
Body: { "title": "string", "owner": "string" }
```

#### Delete Document
```
DELETE /documents/{id}/
```

#### Get Statistics
```
GET /documents/stats/
Response: { "total_documents": int, "unique_owners": int, "documents_this_month": int }
```

#### Filter by Owner
```
GET /documents/by_owner/?owner=<name>
Response: Documents filtered by owner
```

## Database Schema

### Document Model

```sql
CREATE TABLE documents_document (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    doc_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    sender VARCHAR(255) NOT NULL,
    receiver VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    due_date DATE NULL,
    remarks TEXT NOT NULL,
    encrypted_id VARCHAR(32) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ON documents_document(owner);
CREATE INDEX ON documents_document(created_at);
```

## Environment Variables

### Backend (.env)

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

CORS_ALLOWED_ORIGINS=http://localhost:5173

ENCRYPTION_KEY=0123456789ABCDEF0123456789ABCDEF
```

### Frontend (.env.local)

```
VITE_API_BASE_URL=http://localhost:8000/api
```

## Backend Access Points

- Django admin: http://localhost:8000/admin/
- Browsable API login: http://localhost:8000/api-auth/login/
- API root: http://localhost:8000/api/
- Token management: Django admin Tokens section for superusers
- Group management: Django admin Groups section for superusers

## Development

### Adding New Features

1. **Backend**: Extend models in `documents/models.py`, then create migrations
2. **Frontend**: Add components in `src/components/`
3. **API**: Add endpoints in `documents/views.py`
4. **Encryption**: Modify `encryption/idea.py` (use with caution)

### Testing IDEA Encryption

```python
from encryption.idea import IDEA, encrypt_document_id, decrypt_document_id

# Generate key
key = bytes.fromhex('0123456789ABCDEF0123456789ABCDEF')

# Encrypt
encrypted = encrypt_document_id('doc12345', key)
print(f"Encrypted: {encrypted}")

# Decrypt
decrypted = decrypt_document_id(encrypted, key)
print(f"Decrypted: {decrypted}")
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in settings.py
- [ ] Generate strong SECRET_KEY
- [ ] Use environment variables for all sensitive data
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Set up HTTPS/SSL
- [ ] Use gunicorn as WSGI server
- [ ] Configure static files with whitenoise or CDN
- [ ] Set up logging
- [ ] Enable CORS only for trusted origins
- [ ] Back up encryption key
- [ ] Use a managed production database if deploying to cloud
- [ ] Review and simplify the IDEA decrypt implementation if true reversible decryption is required for production use

### Deploy with Gunicorn

```bash
gunicorn document_tracker.wsgi:application --bind 0.0.0.0:8000
```

### Frontend Build

```bash
npm run build
# Output: dist/ directory
```

## Troubleshooting

### Database Connection Issues

If SQLite database is missing or locked:
```bash
python manage.py migrate
```

### Backend Login and Admin Access

- Use `/admin/` for Django admin and `/api-auth/login/` for the browsable REST API login.
- Token authentication is used by the React frontend.
- Token records can be managed in Django admin after logging in as a superuser.

### CORS Errors

Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL in settings.py

### QR Code Not Generating

- Ensure qrcode and Pillow are installed: `pip install python-qrcode Pillow`
- Check that encrypted_id is not empty

### Encryption Key Issues

- Key must be exactly 32 hexadecimal characters
- To generate: `python -c "import os; print(os.urandom(16).hex().upper())"`

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, check the detailed setup guides:
- [SETUP.md](./SETUP.md) - Comprehensive setup instructions

## Learning Resources

- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev)
- [IDEA Encryption Algorithm](https://en.wikipedia.org/wiki/International_Data_Encryption_Algorithm)
- [QR Code Generation](https://github.com/davidshimjs/qrcodejs)
