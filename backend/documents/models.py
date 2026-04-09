"""
Django models for document tracking with IDEA encryption
"""

from django.db import models
from encryption.idea import encrypt_document_id
from django.conf import settings
from django.utils import timezone
import uuid


class Document(models.Model):
    """Document model with encryption support"""

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

    DOC_TYPE_MEMO = 'Memo'
    DOC_TYPE_LETTER = 'Letter'
    DOC_TYPE_REPORT = 'Report'
    DOC_TYPE_CHOICES = [
        (DOC_TYPE_MEMO, 'Memo'),
        (DOC_TYPE_LETTER, 'Letter'),
        (DOC_TYPE_REPORT, 'Report'),
    ]

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
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_number = models.CharField(max_length=32, unique=True, null=True, blank=True)
    reference_code = models.CharField(max_length=32, unique=True, null=True, blank=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default=DEPARTMENT_GENERAL)
    title = models.CharField(max_length=255, help_text="Document title")
    doc_type = models.CharField(max_length=50, choices=DOC_TYPE_CHOICES, default=DOC_TYPE_MEMO)
    description = models.TextField(blank=True, default='')
    sender = models.CharField(max_length=255, default='', help_text="Document sender")
    receiver = models.CharField(max_length=255, default='', help_text="Document receiver")
    owner = models.CharField(max_length=255, help_text="Document owner name")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True, default='')
    attachment = models.FileField(upload_to='documents/', null=True, blank=True)
    encrypted_id = models.CharField(
        max_length=32,
        unique=True,
        help_text="IDEA-encrypted document ID (hex format)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
    
    def __str__(self):
        return f"{self.title} ({self.owner})"
    
    def save(self, *args, **kwargs):
        """Encrypt document ID before saving if not already encrypted"""
        if not self.document_number:
            current_year = timezone.now().year
            self.document_number = f"CIT-{current_year}-{str(self.id).split('-')[0].upper()}"

        if not self.encrypted_id:
            # Use first 8 characters of UUID as plaintext for IDEA
            doc_id_str = str(self.id)[:8]
            try:
                self.encrypted_id = encrypt_document_id(
                    doc_id_str,
                    settings.ENCRYPTION_KEY
                )
            except Exception as e:
                # Fallback: store UUID in case of encryption error
                self.encrypted_id = str(self.id)[:32]

        if not self.reference_code:
            self.reference_code = f"REF-{self.encrypted_id[:8]}"
        
        super().save(*args, **kwargs)


class DocumentActivity(models.Model):
    """Audit trail for document changes and QR lookups."""

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

    def __str__(self):
        return f"{self.action} - {self.document_title}"
