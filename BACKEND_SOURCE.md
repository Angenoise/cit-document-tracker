# CIT Document Tracker - Complete Backend Source Code

## Backend Complete Source Files

---

## models.py - Database Models

```python
"""
Django models for document tracking with IDEA encryption
"""

from django.db import models
from encryption.idea import encrypt_document_id
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
import uuid


class Document(models.Model):
    """Document model with encryption support"""

    # Department choices
    DEPARTMENT_GENERAL = 'General'
    DEPARTMENT_REGISTRAR = 'Registrar'
    DEPARTMENT_DEAN = 'Dean Office'
    DEPARTMENT_GUIDANCE = 'Guidance Office'
    DEPARTMENT_ACCOUNTING = 'Accounting'
    DEPARTMENT_LIBRARY = 'Library'
    DEPARTMENT_CHOICES = [
        (DEPARTMENT_GENERAL, 'General'),
        (DEPARTMENT_REGISTRAR, 'Registrar'),
        (DEPARTMENT_DEAN, 'Dean Office'),
        (DEPARTMENT_GUIDANCE, 'Guidance Office'),
        (DEPARTMENT_ACCOUNTING, 'Accounting'),
        (DEPARTMENT_LIBRARY, 'Library'),
    ]

    # Document type choices
    DOC_TYPE_MEMO = 'Memo'
    DOC_TYPE_LETTER = 'Letter'
    DOC_TYPE_REPORT = 'Report'
    DOC_TYPE_CHOICES = [
        (DOC_TYPE_MEMO, 'Memo'),
        (DOC_TYPE_LETTER, 'Letter'),
        (DOC_TYPE_REPORT, 'Report'),
    ]

    # Status choices
    STATUS_PENDING = 'Pending'
    STATUS_IN_PROCESS = 'In Process'
    STATUS_APPROVED = 'Approved'
    STATUS_REJECTED = 'Rejected'
    STATUS_COMPLETED = 'Completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROCESS, 'In Process'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    # Priority choices
    PRIORITY_LOW = 'Low'
    PRIORITY_MEDIUM = 'Medium'
    PRIORITY_HIGH = 'High'
    PRIORITY_URGENT = 'Urgent'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_URGENT, 'Urgent'),
    ]

    # Primary Key & Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_number = models.CharField(max_length=32, unique=True, null=True, blank=True)
    reference_code = models.CharField(max_length=32, unique=True, null=True, blank=True)
    
    # Metadata
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default=DEPARTMENT_GENERAL)
    title = models.CharField(max_length=255, help_text="Document title")
    doc_type = models.CharField(max_length=50, choices=DOC_TYPE_CHOICES, default=DOC_TYPE_MEMO)
    description = models.TextField(blank=True, default='')
    
    # Transport
    sender = models.CharField(max_length=255, default='', help_text="Document sender")
    receiver = models.CharField(max_length=255, default='', help_text="Document receiver")
    owner = models.CharField(max_length=255, help_text="Document owner name")
    
    # Workflow
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True, default='')
    
    # Content & Attachment
    attachment = models.FileField(upload_to='documents/', null=True, blank=True)
    
    # Security
    access_key_hash = models.CharField(max_length=128, blank=True, default='')
    encrypted_id = models.CharField(
        max_length=32,
        unique=True,
        help_text="IDEA-encrypted document ID (hex format)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return f"{self.title} ({self.owner})"

    def set_access_key(self, key: str):
        """Hash and store the access key"""
        self.access_key_hash = make_password(key)

    def check_access_key(self, key: str) -> bool:
        """Verify the access key against stored hash"""
        if not key:
            return False

        # Backward compatibility for pre-key documents
        if not self.access_key_hash:
            return key == self.encrypted_id

        # Use Django's password verification (constant-time comparison)
        return check_password(key, self.access_key_hash)

    def save(self, *args, **kwargs):
        """Auto-generate fields and encrypt ID before saving"""
        # Generate document number if not set
        if not self.document_number:
            current_year = timezone.now().year
            self.document_number = f"CIT-{current_year}-{str(self.id).split('-')[0].upper()}"

        # Encrypt document ID if not already encrypted
        if not self.encrypted_id:
            doc_id_str = str(self.id)[:8]  # Use first 8 chars of UUID
            try:
                self.encrypted_id = encrypt_document_id(
                    doc_id_str,
                    settings.ENCRYPTION_KEY
                )
            except Exception as e:
                # Fallback if encryption fails
                self.encrypted_id = str(self.id)[:32]

        # Generate reference code if not set
        if not self.reference_code:
            self.reference_code = f"REF-{self.encrypted_id[:8]}"

        super().save(*args, **kwargs)


class DocumentActivity(models.Model):
    """Audit trail for document changes and QR lookups"""

    ACTION_CREATED = 'Created'
    ACTION_UPDATED = 'Updated'
    ACTION_DELETED = 'Deleted'
    ACTION_LOOKED_UP = 'Looked Up'
    ACTION_CHOICES = [
        (ACTION_CREATED, 'Created'),
        (ACTION_UPDATED, 'Updated'),
        (ACTION_DELETED, 'Deleted'),
        (ACTION_LOOKED_UP, 'Looked Up'),
    ]

    document = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities')
    document_title = models.CharField(max_length=255)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    message = models.TextField()
    previous_status = models.CharField(max_length=50, blank=True, default='')
    new_status = models.CharField(max_length=50, blank=True, default='')
    changed_by = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Document Activity'
        verbose_name_plural = 'Document Activities'

    def __str__(self):
        return f"{self.action}: {self.document_title} at {self.created_at}"
```

---

## serializers.py - Input/Output Serialization

```python
"""
Django REST Framework serializers for documents
"""

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from encryption.idea import IDEA
from django.conf import settings
from .models import Document, DocumentActivity


class DocumentActivitySerializer(serializers.ModelSerializer):
    """Serializer for the document audit trail"""

    class Meta:
        model = DocumentActivity
        fields = [
            'id',
            'document_title',
            'action',
            'message',
            'previous_status',
            'new_status',
            'changed_by',
            'created_at',
        ]
        read_only_fields = fields


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model - full detail view"""

    idea_encrypted_internal_id = serializers.SerializerMethodField()
    access_key = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = Document
        fields = [
            'id',
            'document_number',
            'reference_code',
            'department',
            'title',
            'doc_type',
            'description',
            'sender',
            'receiver',
            'owner',
            'status',
            'priority',
            'due_date',
            'remarks',
            'attachment',
            'access_key',
            'encrypted_id',
            'idea_encrypted_internal_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'document_number', 'reference_code', 'encrypted_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'owner': {'required': False}
        }

    def validate_title(self, value):
        """Validate title is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

    def get_idea_encrypted_internal_id(self, instance):
        """Compute IDEA-encrypted UUID for display"""
        cipher = IDEA(settings.ENCRYPTION_KEY)
        encrypted = cipher.encrypt(str(instance.id).encode('ascii'))
        return encrypted.hex().upper()

    def validate_owner(self, value):
        """Validate owner is not empty if provided"""
        if value is None or not value.strip():
            raise serializers.ValidationError("Owner cannot be empty")
        return value.strip()

    def validate_sender(self, value):
        """Validate sender is not empty"""
        if value is None or not value.strip():
            raise serializers.ValidationError('Sender cannot be empty')
        return value.strip()

    def validate_receiver(self, value):
        """Validate receiver is not empty"""
        if value is None or not value.strip():
            raise serializers.ValidationError('Receiver cannot be empty')
        return value.strip()

    def create(self, validated_data):
        """Create document with access key hashing"""
        access_key = validated_data.pop('access_key', '').strip()
        if not access_key:
            raise serializers.ValidationError({'access_key': 'Access key is required.'})

        request = self.context.get('request')
        
        # Handle owner: use current user or provided owner
        if 'owner' not in validated_data or not validated_data['owner']:
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                validated_data['owner'] = str(request.user)
            else:
                validated_data['owner'] = 'System'

        # Create document instance
        document = Document(**validated_data)
        document.set_access_key(access_key)
        document.save()
        return document

    def update(self, instance, validated_data):
        """Update document - preserve access key"""
        # Don't allow changing access key via update
        validated_data.pop('access_key', None)
        
        return super().update(instance, validated_data)


class PublicDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document lists - summary only"""

    class Meta:
        model = Document
        fields = [
            'id',
            'document_number',
            'reference_code',
            'department',
            'title',
            'doc_type',
            'owner',
            'status',
            'priority',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
```

---

## views.py - API Endpoints

```python
"""
Django REST Framework views for document management
"""

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Document, DocumentActivity
from .serializers import DocumentSerializer, DocumentActivitySerializer, PublicDocumentSerializer


def create_document_activity(document, action, message, changed_by=None, previous_status='', new_status=''):
    """Helper to create audit trail entry"""
    DocumentActivity.objects.create(
        document=document,
        document_title=document.title,
        action=action,
        message=message,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=getattr(changed_by, 'username', '') if changed_by else '',
    )


class DocumentActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reading audit trail entries"""
    permission_classes = [AllowAny]
    serializer_class = DocumentActivitySerializer
    queryset = DocumentActivity.objects.select_related('document').all()

    def get_queryset(self):
        queryset = super().get_queryset()
        document_id = self.request.query_params.get('document_id')
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        return queryset


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing documents - no auth required"""

    permission_classes = [AllowAny]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'doc_type', 'description', 'sender', 'receiver', 'owner', 'status', 'priority', 'remarks']
    ordering_fields = ['created_at', 'title', 'owner', 'due_date', 'status', 'priority']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use summary serializer for list view"""
        if self.action == 'list':
            return PublicDocumentSerializer
        return DocumentSerializer

    def _get_access_key(self, request):
        """Extract access key from request headers or params"""
        key = request.headers.get('X-Document-Key') or request.query_params.get('access_key')
        if not key and hasattr(request, 'data'):
            if isinstance(request.data, dict):
                key = request.data.get('access_key')
            else:
                key = request.data.get('access_key', None)

        if isinstance(key, str):
            return key.strip()
        return key

    def _validate_document_access(self, request, document):
        """Verify access key for document"""
        access_key = self._get_access_key(request)
        if not access_key:
            return Response({'error': 'Document access key is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not document.check_access_key(access_key):
            return Response({'error': 'Invalid document access key.'}, status=status.HTTP_403_FORBIDDEN)

        return None

    def get_queryset(self):
        """Support owner filter"""
        queryset = super().get_queryset()
        owner = self.request.query_params.get('owner')
        if owner:
            queryset = queryset.filter(owner__iexact=owner)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Create document with audit logging"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            previous_status = ''
            self.perform_create(serializer)
            document = serializer.instance
            create_document_activity(
                document,
                DocumentActivity.ACTION_CREATED,
                f'Document {document.document_number} was created.',
                request.user if getattr(request, 'user', None) else None,
                previous_status=previous_status,
                new_status=document.status,
            )
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as exc:
            return Response({'error': f'Failed to create document: {str(exc)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics"""
        total_documents = Document.objects.count()
        owners = Document.objects.values('owner').distinct().count()
        recent_count = Document.objects.filter(created_at__gte=timezone.now().replace(day=1)).count()

        status_counts = {
            'pending': Document.objects.filter(status=Document.STATUS_PENDING).count(),
            'in_process': Document.objects.filter(status=Document.STATUS_IN_PROCESS).count(),
            'approved': Document.objects.filter(status=Document.STATUS_APPROVED).count(),
            'rejected': Document.objects.filter(status=Document.STATUS_REJECTED).count(),
            'completed': Document.objects.filter(status=Document.STATUS_COMPLETED).count(),
        }

        return Response({
            'total_documents': total_documents,
            'unique_owners': owners,
            'documents_this_month': recent_count,
            'status_counts': status_counts,
        })

    @action(detail=False, methods=['get'])
    def by_owner(self, request):
        """Get documents filtered by owner"""
        owner = request.query_params.get('owner')
        if not owner:
            return Response({'error': 'owner query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        documents = self.get_queryset().filter(owner__iexact=owner)
        serializer = self.get_serializer(documents, many=True)
        return Response({'owner': owner, 'count': documents.count(), 'documents': serializer.data})

    @action(detail=False, methods=['get'])
    def resolve_qr(self, request):
        """Resolve QR code (encrypted_id lookup with access key)"""
        encrypted_id = request.query_params.get('encrypted_id')
        if not encrypted_id:
            return Response({'error': 'encrypted_id query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        document = Document.objects.filter(encrypted_id=encrypted_id).first()
        if not document:
            return Response({'error': 'Document not found for the provided QR code'}, status=status.HTTP_404_NOT_FOUND)

        # Validate access key
        access_error = self._validate_document_access(request, document)
        if access_error:
            return access_error

        # Log the QR lookup
        create_document_activity(
            document,
            DocumentActivity.ACTION_LOOKED_UP,
            f'Document {document.document_number} was resolved from QR code.',
            request.user if getattr(request, 'user', None) else None,
            previous_status=document.status,
            new_status=document.status,
        )

        serializer = self.get_serializer(document)
        return Response({
            'document': serializer.data,
            'resolved_document_id': str(document.id),
            'resolved_document_number': document.document_number,
            'resolved_reference_code': document.reference_code,
        })

    def retrieve(self, request, *args, **kwargs):
        """Get single document - requires access key"""
        document = self.get_object()
        access_error = self._validate_document_access(request, document)
        if access_error:
            return access_error
        serializer = self.get_serializer(document)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update document - requires access key with audit logging"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        access_error = self._validate_document_access(request, instance)
        if access_error:
            return access_error

        previous_status = instance.status
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        create_document_activity(
            serializer.instance,
            DocumentActivity.ACTION_UPDATED,
            f'Document {serializer.instance.document_number} was updated.',
            request.user if getattr(request, 'user', None) else None,
            previous_status=previous_status,
            new_status=serializer.instance.status,
        )
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete document - requires access key with audit logging"""
        instance = self.get_object()
        access_error = self._validate_document_access(request, instance)
        if access_error:
            return access_error

        create_document_activity(
            instance,
            DocumentActivity.ACTION_DELETED,
            f'Document {instance.document_number} was deleted.',
            request.user if getattr(request, 'user', None) else None,
            previous_status=instance.status,
            new_status='Deleted',
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
```

---

## urls.py - URL Routing

```python
"""
URL routing for documents API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet,
    DocumentActivityViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'activities', DocumentActivityViewSet, basename='activity')

# Include router URLs
urlpatterns = [
    path('', include(router.urls)),
]
```

---

## settings.py - Django Configuration

```python
"""
Django settings for document_tracker project.
"""

from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'documents',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'document_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'document_tracker.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True

# Encryption Key
ENCRYPTION_KEY = config('ENCRYPTION_KEY', default=b'16byte_key_12345')
```

---

## admin.py - Django Admin Configuration

```python
"""
Django admin configuration for documents app
"""

from django.contrib import admin
from .models import Document, DocumentActivity


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin panel for Document model"""
    
    list_display = ('document_number', 'title', 'owner', 'status', 'priority', 'department', 'created_at')
    list_filter = ('status', 'priority', 'department', 'doc_type', 'created_at')
    search_fields = ('title', 'owner', 'sender', 'receiver', 'document_number')
    readonly_fields = ('id', 'encrypted_id', 'document_number', 'reference_code', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Identifiers', {
            'fields': ('id', 'document_number', 'reference_code', 'encrypted_id')
        }),
        ('Content', {
            'fields': ('title', 'doc_type', 'description', 'owner')
        }),
        ('Transport', {
            'fields': ('sender', 'receiver', 'department')
        }),
        ('Workflow', {
            'fields': ('status', 'priority', 'due_date', 'remarks')
        }),
        ('Security', {
            'fields': ('access_key_hash',),
            'classes': ('collapse',)
        }),
        ('Attachment', {
            'fields': ('attachment',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request):
        return request.user.is_superuser


@admin.register(DocumentActivity)
class DocumentActivityAdmin(admin.ModelAdmin):
    """Admin panel for DocumentActivity (audit trail)"""
    
    list_display = ('document_title', 'action', 'changed_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('document_title', 'message', 'changed_by')
    readonly_fields = ('document', 'document_title', 'action', 'message', 'previous_status', 'new_status', 'changed_by', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request):
        return request.user.is_superuser
```

---

This file contains the complete backend source code for all Django models, serializers, views, and configuration files.
